"""Cleanup loop entrypoint: dedicated bounded scheduler for passes (U-OPS; PE-04).

``python -m app.ops.cleanup_loop`` runs one bounded pass per interval until
SIGTERM/SIGINT. Supports ``--once`` for drills (including ``--dry-run``),
``--watch SECONDS`` for continuous mode with graceful shutdown. Exit codes:
    0 — pass succeeded or watch ended (signal/stop event)
    1 — pass failed (service error during execution)
    2 — configuration error (missing environment or invalid knobs)
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

import redis

from app.config import InvalidSettingError, MissingEnvVarError, Settings
from app.ops.cleanup_service import (
    CleanupService,
    CleanupServiceError,
    CleanupServiceOptions,
    CleanupServiceReport,
)
from app.queue.store import TaskStore
from app.utils.logging import PapyrJsonHandler
from app.utils.r2 import R2Client

logger = logging.getLogger(__name__)

RESPONSIVE_WAIT_CHUNK_SECONDS = 5.0

DEFAULT_CLEANUP_INTERVAL_SECONDS = 300
DEFAULT_GRACE_SECONDS = 300
DEFAULT_BATCH_LIMIT = 100
DEFAULT_MAX_RECORDS = 500
DEFAULT_MARKER_TTL_SECONDS = 7 * 86400


@dataclass(frozen=True)
class CleanupEnvKnobs:
    interval_seconds: int
    grace_seconds: int
    batch_limit: int
    max_records: int
    marker_ttl_seconds: int


def _positive_int(name: str, source: Mapping[str, str], default: int) -> int:
    raw = source.get(name)
    if raw is None:
        return default
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise InvalidSettingError(f"Setting {name!r} must be an integer") from exc
    if value <= 0:
        raise InvalidSettingError(f"Setting {name!r} must be positive")
    return value


def parse_cleanup_env(source: Mapping[str, str] | None = None) -> CleanupEnvKnobs:
    env: Mapping[str, str] = dict(os.environ) if source is None else dict(source)
    return CleanupEnvKnobs(
        interval_seconds=_positive_int(
            "CLEANUP_INTERVAL_SECONDS", env, DEFAULT_CLEANUP_INTERVAL_SECONDS
        ),
        grace_seconds=_positive_int("CLEANUP_GRACE_SECONDS", env, DEFAULT_GRACE_SECONDS),
        batch_limit=_positive_int("CLEANUP_BATCH_LIMIT", env, DEFAULT_BATCH_LIMIT),
        max_records=_positive_int("CLEANUP_MAX_RECORDS", env, DEFAULT_MAX_RECORDS),
        marker_ttl_seconds=_positive_int(
            "CLEANUP_MARKER_TTL_SECONDS", env, DEFAULT_MARKER_TTL_SECONDS
        ),
    )


@dataclass(frozen=True)
class CleanupRuntime:
    service: CleanupService
    interval_seconds: float


def _ensure_logging() -> None:
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = PapyrJsonHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)


class RedisMarkerStore:
    """Protocol-exact adapter over a redis-py client for the cleanup marker."""

    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    def hset(self, name: str, mapping: Mapping[str, str]) -> int:
        widened: dict[
            bytes | bytearray | memoryview[int] | str | int | float,
            bytes | bytearray | memoryview[int] | str | int | float,
        ] = {k: v for k, v in mapping.items()}
        return int(self._client.hset(name, mapping=widened))

    def expire(self, name: str, seconds: int) -> bool:
        return bool(self._client.expire(name, seconds))

    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]:
        raw = self._client.hgetall(name)
        decoded: dict[bytes | str, bytes | str] = {key: value for key, value in raw.items()}
        return decoded


def build_runtime_from_env(env: Mapping[str, str] | None = None) -> CleanupRuntime:
    settings = Settings.from_env(dict(os.environ) if env is None else env)
    store = TaskStore(settings)
    r2_client = R2Client(settings)
    marker_redis = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=False,
        socket_timeout=5.0,
        socket_connect_timeout=5.0,
    )
    knobs = parse_cleanup_env(env)
    service = CleanupService(
        store,
        r2_client,
        clock=lambda: datetime.now(UTC),
        marker_store=RedisMarkerStore(marker_redis),
        options=CleanupServiceOptions(
            grace_seconds=knobs.grace_seconds,
            batch_limit=knobs.batch_limit,
            max_records=knobs.max_records,
            marker_ttl_seconds=knobs.marker_ttl_seconds,
        ),
    )
    return CleanupRuntime(service=service, interval_seconds=float(knobs.interval_seconds))


def install_signal_handlers(stop_event: threading.Event) -> None:
    def handle(signum: int, frame: object) -> None:
        stop_event.set()

    try:
        signal.signal(signal.SIGTERM, handle)
        signal.signal(signal.SIGINT, handle)
    except ValueError:
        pass


@dataclass(frozen=True)
class _LoopArgs:
    once_mode: bool
    dry_run: bool
    watch_seconds: float | None
    usage_error: bool


def _parse_loop_args(args: list[str]) -> _LoopArgs:
    once_mode = False
    dry_run = False
    watch_seconds: float | None = None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--once":
            once_mode = True
        elif arg == "--dry-run":
            dry_run = True
        elif arg == "--watch":
            if index + 1 >= len(args):
                return _LoopArgs(once_mode, dry_run, None, usage_error=True)
            try:
                watch_seconds = float(args[index + 1])
            except ValueError:
                return _LoopArgs(once_mode, dry_run, None, usage_error=True)
            index += 1
        index += 1
    return _LoopArgs(once_mode, dry_run, watch_seconds, usage_error=False)


def _pass_report_fields(report: CleanupServiceReport) -> dict[str, object]:
    return {
        "pass": "ok",
        "outcome": report.outcome,
        "cleaned": report.cleaned,
        "examined": report.examined,
        "elapsed_ms": int(report.elapsed_seconds * 1000),
    }


def _print_pass_report(service: CleanupService, *, dry_run: bool) -> int:
    try:
        report = service.run_once(dry_run=dry_run)
    except CleanupServiceError as exc:
        cause_name = type(exc.__cause__).__name__ if exc.__cause__ else type(exc).__name__
        print(json.dumps({"pass": "failed", "error": cause_name}))
        return 1
    print(json.dumps(_pass_report_fields(report)))
    return 0


def _build_runtime(
    runtime_factory: Callable[[], CleanupRuntime] | None,
) -> CleanupRuntime | None:
    try:
        return (runtime_factory if runtime_factory is not None else build_runtime_from_env)()
    except MissingEnvVarError as exc:
        print(json.dumps({"error": "missing_env", "field": str(exc)}))
        return None
    except InvalidSettingError as exc:
        print(json.dumps({"error": "invalid_setting", "message": str(exc)}))
        return None
    except Exception as exc:
        logger.error("cleanup init failed", extra={"fields": {"error": type(exc).__name__}})
        print(json.dumps({"error": "init_error"}))
        return None


def _run_loop(
    runtime: CleanupRuntime,
    *,
    dry_run: bool,
    stop_event: threading.Event,
    interval_seconds: float,
    clock: Callable[[], float] = time.monotonic,
) -> None:
    service = runtime.service
    while not stop_event.is_set():
        started = clock()
        try:
            report = service.run_once(dry_run=dry_run)
            print(json.dumps(_pass_report_fields(report)))
        except CleanupServiceError:
            print(json.dumps({"pass": "failed", "error": "unavailable"}))
        deadline = started + interval_seconds
        while not stop_event.is_set():
            remaining = deadline - clock()
            if remaining <= 0:
                break
            if stop_event.wait(min(RESPONSIVE_WAIT_CHUNK_SECONDS, remaining)):
                return


def main(
    argv: list[str] | None = None,
    *,
    runtime_factory: Callable[[], CleanupRuntime] | None = None,
    stop_event: threading.Event | None = None,
) -> int:
    loop_args = _parse_loop_args(list(sys.argv[1:] if argv is None else argv))
    if loop_args.usage_error:
        print("--watch requires a numeric interval", file=sys.stderr)
        return 2
    runtime = _build_runtime(runtime_factory)
    if runtime is None:
        return 2
    _ensure_logging()
    if loop_args.once_mode and loop_args.watch_seconds is None:
        return _print_pass_report(runtime.service, dry_run=loop_args.dry_run)
    event = stop_event if stop_event is not None else threading.Event()
    if stop_event is None:
        install_signal_handlers(event)
    interval = (
        loop_args.watch_seconds if loop_args.watch_seconds is not None else runtime.interval_seconds
    )
    _run_loop(runtime, dry_run=loop_args.dry_run, stop_event=event, interval_seconds=interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
