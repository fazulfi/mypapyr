"""Bounded production monitor: executable checks, stable exits, safe output (U-OPS).

One-shot or watch-mode check runner for the production stack. Checks:
``api_ready`` (GET /health/ready answers 200 + ready), ``redis`` (PING),
``clamd`` (TCP zPING answers PONG), ``queue_backlog`` (XLEN vs warn/fail
thresholds under the R-07 cap), ``queue_pel`` (pending-entry count and idle
age), ``worker_health`` (consumer-group existence, PEL staleness, optional
worker /health probe), ``cleanup_freshness`` (the ops:cleanup marker's last
successful pass is recent and ok), and ``r2_ops`` (a read-only bounded R2
list probe).

Exit codes: 0 healthy or warn-only, 1 any failed check, 2 configuration
error. Output is machine-readable JSON; details carry counts, booleans,
enums, and exception class names only (DEC-175) — never URLs, credentials,
task ids, object keys, or exception messages.
"""

from __future__ import annotations

import importlib
import json
import os
import signal
import socket as socket_module
import sys
import threading
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, Protocol, cast

import redis as redis_lib

from app.config import Settings
from app.ops.cleanup_service import CleanupMarkerReader, read_cleanup_marker

CheckStatusLiteral = Literal["ok", "warn", "fail"]

DEFAULT_API_URL = "http://api:3000/health/ready"
DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_QUEUE_WARN_THRESHOLD = 1000
DEFAULT_QUEUE_FAIL_THRESHOLD = 1800
DEFAULT_PEL_FAIL_COUNT = 16
DEFAULT_PEL_IDLE_FAIL_MS = 900_000
DEFAULT_CLEANUP_MAX_AGE_SECONDS = 3600
HTTP_OK = 200

STREAM_KEY = "jobs"
GROUP_NAME = "workers"
_PEL_PAGE_SIZE = 64


class UrlOpener(Protocol):
    def __call__(self, url: str, timeout: float) -> tuple[int, bytes]: ...


class MonitorRedisLike(Protocol):
    def ping(self) -> bool: ...
    def xlen(self, name: str) -> int: ...
    def xpending_range(
        self, name: str, groupname: str, min: str, max: str, count: int
    ) -> list[dict[str, object]]: ...
    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]: ...


class ProbeSocket(Protocol):
    """Socket interface expected by clamd health probe."""

    def settimeout(self, value: float | None) -> None: ...
    def connect(self, address: tuple[str, int]) -> None: ...
    def sendall(self, data: bytes) -> None: ...
    def recv(self, bufsize: int) -> bytes: ...
    def close(self) -> None: ...


class SocketFactory(Protocol):
    def __call__(self) -> ProbeSocket: ...


class R2Probe(Protocol):
    def probe(self) -> bool: ...


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatusLiteral
    details: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "status": self.status, "details": dict(self.details)}


@dataclass(frozen=True)
class MonitorReport:
    status: Literal["healthy", "degraded", "failed"]
    checks: tuple[CheckResult, ...]
    generated_at: datetime

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(
            {
                "status": self.status,
                "generated_at": self.generated_at.isoformat(timespec="seconds"),
                "checks": [check.to_dict() for check in self.checks],
                "summary": {
                    "ok": sum(1 for check in self.checks if check.status == "ok"),
                    "warn": sum(1 for check in self.checks if check.status == "warn"),
                    "fail": sum(1 for check in self.checks if check.status == "fail"),
                },
            },
            indent=indent,
        )


def _default_url_open(url: str, timeout: float) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read() if exc.fp is not None else b""


def _default_socket_factory() -> socket_module.socket:
    return socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)


def check_api_ready(url_open: UrlOpener, api_url: str, *, timeout_seconds: float) -> CheckResult:
    try:
        status_code, body = url_open(api_url, timeout_seconds)
    except Exception as exc:
        return CheckResult("api_ready", "fail", {"error": type(exc).__name__})
    if status_code != HTTP_OK:
        return CheckResult("api_ready", "fail", {"status_code": status_code})
    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return CheckResult(
            "api_ready", "fail", {"status_code": status_code, "error": "UnparseableBody"}
        )
    if not isinstance(payload, Mapping) or payload.get("status") != "ready":
        return CheckResult("api_ready", "fail", {"status_code": status_code})
    return CheckResult("api_ready", "ok", {"status_code": status_code})


def check_redis(redis: MonitorRedisLike | None) -> CheckResult:
    if redis is None:
        return CheckResult("redis", "fail", {"error": "ClientNotConfigured"})
    try:
        redis.ping()
    except Exception as exc:
        return CheckResult("redis", "fail", {"error": type(exc).__name__})
    return CheckResult("redis", "ok")


def check_clamd(
    socket_factory: SocketFactory | None, host: str, port: int, *, timeout_seconds: float
) -> CheckResult:
    if socket_factory is None:
        return CheckResult("clamd", "fail", {"error": "SocketNotConfigured"})
    sock = socket_factory()
    try:
        sock.settimeout(timeout_seconds)
        sock.connect((host, port))
        sock.sendall(b"zPING\x00")
        reply = sock.recv(1024)
    except OSError as exc:
        return CheckResult("clamd", "fail", {"error": type(exc).__name__})
    finally:
        sock.close()
    if not reply.startswith(b"PONG"):
        return CheckResult("clamd", "fail", {"error": "UnexpectedReply"})
    return CheckResult("clamd", "ok")


def check_queue_backlog(
    redis: MonitorRedisLike | None,
    *,
    warn_threshold: int = DEFAULT_QUEUE_WARN_THRESHOLD,
    fail_threshold: int = DEFAULT_QUEUE_FAIL_THRESHOLD,
) -> CheckResult:
    if redis is None:
        return CheckResult("queue_backlog", "fail", {"error": "ClientNotConfigured"})
    try:
        backlog = redis.xlen(STREAM_KEY)
    except Exception as exc:
        return CheckResult("queue_backlog", "fail", {"error": type(exc).__name__})
    if backlog >= fail_threshold:
        return CheckResult("queue_backlog", "fail", {"count": backlog})
    if backlog >= warn_threshold:
        return CheckResult("queue_backlog", "warn", {"count": backlog})
    return CheckResult("queue_backlog", "ok", {"count": backlog})


def _pending_summary(redis: MonitorRedisLike) -> tuple[bool, int, int] | CheckResult:
    """Return (group_exists, pending_count, max_idle_ms) or an error result."""
    try:
        entries = redis.xpending_range(STREAM_KEY, GROUP_NAME, "-", "+", _PEL_PAGE_SIZE)
    except Exception as exc:
        if "NOGROUP" in str(exc):
            return (False, 0, 0)
        return CheckResult("queue_pel", "fail", {"error": type(exc).__name__})
    max_idle_ms = 0
    for entry in entries:
        idle = entry.get("time_since_delivered", 0)
        if isinstance(idle, int) and idle > max_idle_ms:
            max_idle_ms = idle
    return (True, len(entries), max_idle_ms)


def check_queue_pel(
    redis: MonitorRedisLike | None,
    *,
    fail_count_threshold: int = DEFAULT_PEL_FAIL_COUNT,
    idle_fail_ms: int = DEFAULT_PEL_IDLE_FAIL_MS,
) -> CheckResult:
    if redis is None:
        return CheckResult("queue_pel", "fail", {"error": "ClientNotConfigured"})
    summary = _pending_summary(redis)
    if isinstance(summary, CheckResult):
        return CheckResult("queue_pel", summary.status, dict(summary.details))
    group_exists, pending, max_idle_ms = summary
    details = {"pending": pending, "oldest_idle_ms": max_idle_ms, "group_exists": group_exists}
    if not group_exists:
        return CheckResult("queue_pel", "ok", details)
    if pending > fail_count_threshold or max_idle_ms > idle_fail_ms:
        return CheckResult("queue_pel", "fail", details)
    return CheckResult("queue_pel", "ok", details)


def check_worker_health(
    redis: MonitorRedisLike | None,
    *,
    url_open: UrlOpener | None = None,
    worker_health_url: str | None = None,
    idle_fail_ms: int = DEFAULT_PEL_IDLE_FAIL_MS,
) -> CheckResult:
    if redis is None:
        return CheckResult("worker_health", "fail", {"error": "ClientNotConfigured"})
    summary = _pending_summary(redis)
    if isinstance(summary, CheckResult):
        return CheckResult("worker_health", "fail", dict(summary.details))
    group_exists, pending, max_idle_ms = summary
    details: dict[str, object] = {
        "group_exists": group_exists,
        "pending": pending,
        "oldest_idle_ms": max_idle_ms,
    }
    if not group_exists:
        return CheckResult("worker_health", "fail", details)
    if max_idle_ms > idle_fail_ms:
        return CheckResult("worker_health", "fail", details)
    if worker_health_url is not None and url_open is not None:
        probe = check_api_ready(
            url_open, worker_health_url, timeout_seconds=DEFAULT_TIMEOUT_SECONDS
        )
        if probe.status != "ok":
            details["worker_probe"] = "unavailable"
            return CheckResult("worker_health", "fail", details)
        details["worker_probe"] = "ok"
    return CheckResult("worker_health", "ok", details)


def check_cleanup_freshness(
    marker_client: CleanupMarkerReader | None,
    *,
    max_age_seconds: int,
    clock: Callable[[], datetime],
) -> CheckResult:
    if marker_client is None:
        return CheckResult("cleanup_freshness", "fail", {"reason": "marker_absent"})
    fields = read_cleanup_marker(marker_client)
    if fields is None:
        return CheckResult("cleanup_freshness", "fail", {"reason": "marker_absent"})
    if fields.get("last_outcome") != "ok":
        return CheckResult("cleanup_freshness", "fail", {"reason": "last_run_failed"})
    raw_timestamp = fields.get("last_success_at", "")
    try:
        last_success = datetime.fromisoformat(raw_timestamp)
    except ValueError:
        return CheckResult("cleanup_freshness", "fail", {"reason": "unparseable_timestamp"})
    age_seconds = int((clock() - last_success).total_seconds())
    if age_seconds > max_age_seconds:
        return CheckResult(
            "cleanup_freshness", "fail", {"reason": "stale", "age_seconds": age_seconds}
        )
    return CheckResult("cleanup_freshness", "ok", {"age_seconds": age_seconds})


def check_r2_ops(r2_probe: R2Probe | None) -> CheckResult:
    if r2_probe is None:
        return CheckResult("r2_ops", "fail", {"error": "ProbeNotConfigured"})
    if r2_probe.probe():
        return CheckResult("r2_ops", "ok")
    return CheckResult("r2_ops", "fail", {"error": "ProbeUnavailable"})


@dataclass(frozen=True)
class MonitorOptions:
    clock: Callable[[], datetime] | None = None
    url_open: UrlOpener | None = None
    redis: MonitorRedisLike | None = None
    socket_factory: SocketFactory | None = None
    r2_probe: R2Probe | None = None
    api_url: str = DEFAULT_API_URL
    clamd_host: str = "localhost"
    clamd_port: int = 3310
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    queue_warn_threshold: int = DEFAULT_QUEUE_WARN_THRESHOLD
    queue_fail_threshold: int = DEFAULT_QUEUE_FAIL_THRESHOLD
    pel_fail_count: int = DEFAULT_PEL_FAIL_COUNT
    pel_idle_fail_ms: int = DEFAULT_PEL_IDLE_FAIL_MS
    cleanup_max_age_seconds: int = DEFAULT_CLEANUP_MAX_AGE_SECONDS
    worker_health_url: str | None = None


class Monitor:
    """Dependency-injected runner aggregating the eight production checks."""

    def __init__(self, *, options: MonitorOptions | None = None) -> None:
        opts = options if options is not None else MonitorOptions()
        self._clock = opts.clock or (lambda: datetime.now(UTC))
        self._url_open = opts.url_open or _default_url_open
        self._redis = opts.redis
        self._socket_factory = opts.socket_factory or _default_socket_factory
        self._r2_probe = opts.r2_probe
        self._options = opts

    def run_checks(self) -> MonitorReport:
        opts = self._options
        checks = (
            check_api_ready(self._url_open, opts.api_url, timeout_seconds=opts.timeout_seconds),
            check_redis(self._redis),
            check_clamd(
                self._socket_factory,
                opts.clamd_host,
                opts.clamd_port,
                timeout_seconds=opts.timeout_seconds,
            ),
            check_queue_backlog(
                self._redis,
                warn_threshold=opts.queue_warn_threshold,
                fail_threshold=opts.queue_fail_threshold,
            ),
            check_queue_pel(
                self._redis,
                fail_count_threshold=opts.pel_fail_count,
                idle_fail_ms=opts.pel_idle_fail_ms,
            ),
            check_worker_health(
                self._redis,
                url_open=self._url_open,
                worker_health_url=opts.worker_health_url,
                idle_fail_ms=opts.pel_idle_fail_ms,
            ),
            check_cleanup_freshness(
                self._redis, max_age_seconds=opts.cleanup_max_age_seconds, clock=self._clock
            ),
            check_r2_ops(self._r2_probe),
        )
        if any(check.status == "fail" for check in checks):
            status: Literal["healthy", "degraded", "failed"] = "failed"
        elif any(check.status == "warn" for check in checks):
            status = "degraded"
        else:
            status = "healthy"
        return MonitorReport(status=status, checks=checks, generated_at=self._clock())


class R2LivenessProbe:
    """Read-only bounded R2 probe: list tmp/ with MaxKeys=1 (never mutates)."""

    def __init__(self, client: Any, bucket_name: str) -> None:
        self._client = client
        self._bucket_name = bucket_name

    def probe(self) -> bool:
        try:
            self._client.list_objects_v2(Bucket=self._bucket_name, Prefix="tmp/", MaxKeys=1)
        except Exception:
            return False
        return True


def _build_r2_probe(settings: Settings) -> R2Probe | None:
    try:
        boto3 = cast(Any, importlib.import_module("boto3"))
        botocore_config = cast(Any, importlib.import_module("botocore.config"))
        endpoint = settings.r2_endpoint or (
            f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
        )
        s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name=settings.r2_region,
            config=botocore_config.Config(signature_version="s3v4"),
        )
    except Exception:
        return None
    return R2LivenessProbe(s3_client, settings.r2_bucket_name)


def _env_int(source: Mapping[str, str], name: str, default: int) -> int:
    raw = source.get(name)
    return default if raw is None or not raw.strip() else int(raw.strip())


class RedisMonitorClient:
    """Protocol-exact adapter over redis-py client for the monitor checks."""

    def __init__(self, client: redis_lib.Redis) -> None:
        self._client = client

    def ping(self) -> bool:
        return bool(self._client.ping())

    def xlen(self, name: str) -> int:
        return int(self._client.xlen(name))

    def xpending_range(
        self,
        name: str,
        groupname: str,
        min: str,
        max: str,
        count: int,
    ) -> list[dict[str, object]]:
        raw = self._client.xpending_range(name, groupname, min, max, count)
        entries: list[dict[str, object]] = []
        for entry in raw:
            entries.append(
                {
                    "message_id": entry.get("message_id"),
                    "consumer": entry.get("consumer"),
                    "time_since_delivered": entry.get("time_since_delivered"),
                    "times_delivered": entry.get("times_delivered"),
                }
            )
        return entries

    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]:
        raw = self._client.hgetall(name)
        decoded: dict[bytes | str, bytes | str] = {k: v for k, v in raw.items()}
        return decoded


def _build_monitor_from_env(env: Mapping[str, str] | None = None) -> Monitor:
    source: Mapping[str, str] = os.environ if env is None else env
    settings = Settings.from_env(source)
    redis_client = redis_lib.Redis.from_url(
        settings.redis_url,
        decode_responses=False,
        socket_timeout=DEFAULT_TIMEOUT_SECONDS,
        socket_connect_timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    options = MonitorOptions(
        clock=None,
        url_open=None,
        redis=RedisMonitorClient(redis_client),
        socket_factory=None,
        r2_probe=_build_r2_probe(settings),
        api_url=source.get("MONITOR_API_URL", DEFAULT_API_URL),
        clamd_host=settings.clamd_host,
        clamd_port=settings.clamd_port,
        timeout_seconds=float(settings.scanner_timeout_seconds),
        queue_warn_threshold=_env_int(source, "MONITOR_QUEUE_WARN", DEFAULT_QUEUE_WARN_THRESHOLD),
        queue_fail_threshold=_env_int(source, "MONITOR_QUEUE_FAIL", DEFAULT_QUEUE_FAIL_THRESHOLD),
        pel_fail_count=_env_int(source, "MONITOR_PEL_FAIL_COUNT", DEFAULT_PEL_FAIL_COUNT),
        pel_idle_fail_ms=_env_int(source, "MONITOR_PEL_IDLE_FAIL_MS", DEFAULT_PEL_IDLE_FAIL_MS),
        cleanup_max_age_seconds=_env_int(
            source, "MONITOR_CLEANUP_MAX_AGE_SECONDS", DEFAULT_CLEANUP_MAX_AGE_SECONDS
        ),
        worker_health_url=source.get("MONITOR_WORKER_HEALTH_URL") or None,
    )
    return Monitor(options=options)


def _install_signal_handlers(stop_event: threading.Event) -> None:
    def handler(signum: int, frame: object) -> None:
        stop_event.set()

    try:
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
    except ValueError:
        pass


def _parse_watch_interval(args: list[str]) -> float | None | Literal["error"]:
    index = 0
    while index < len(args):
        if args[index] == "--watch":
            if index + 1 >= len(args):
                return "error"
            try:
                return float(args[index + 1])
            except ValueError:
                return "error"
        index += 1
    return None


def main(
    argv: list[str] | None = None,
    *,
    monitor_factory: Callable[[], Monitor] | None = None,
    stop_event: threading.Event | None = None,
) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    watch_seconds = _parse_watch_interval(args)
    if watch_seconds == "error":
        print("usage: python -m app.ops.monitor [--watch SECONDS]", file=sys.stderr)
        return 2
    try:
        monitor = (monitor_factory if monitor_factory is not None else _build_monitor_from_env)()
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__}))
        return 2
    if watch_seconds is None:
        report = monitor.run_checks()
        print(report.to_json(indent=2))
        return 1 if report.status == "failed" else 0
    event = stop_event if stop_event is not None else threading.Event()
    if stop_event is None:
        _install_signal_handlers(event)
    while True:
        report = monitor.run_checks()
        print(report.to_json(), flush=True)
        if event.wait(watch_seconds):
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
