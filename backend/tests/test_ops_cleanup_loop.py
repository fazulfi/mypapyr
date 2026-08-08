"""Contract tests for the cleanup loop entrypoint (U-OPS; PE-04).

``python -m app.ops.cleanup_loop`` is the operational activation surface of
the scheduled cleanup: a dedicated bounded process (never a request-handler
hook) that runs one cleanup pass per interval until SIGTERM/SIGINT.

Semantics under test:

* ``--once`` runs a single pass and maps outcomes to stable exit codes:
  0 success, 1 cleanup degradation (CleanupServiceError), 2 configuration
  error (missing/unusable environment);
* ``--dry-run`` is honored by every pass;
* loop mode repeats passes at the configured interval and stops gracefully
  on the stop event (signal wiring installed best-effort per platform);
* configuration is derived from the environment with bounded, documented
  defaults (interval, grace, batch, max records) and rejects unusable
  values fail-closed.
"""

from __future__ import annotations

import signal
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

import pytest

from app.config import InvalidSettingError, MissingEnvVarError
from app.ops.cleanup_loop import (
    DEFAULT_CLEANUP_INTERVAL_SECONDS,
    CleanupRuntime,
    _run_loop,
    build_runtime_from_env,
    install_signal_handlers,
    parse_cleanup_env,
)
from app.ops.cleanup_loop import (
    main as loop_main,
)
from app.ops.cleanup_service import CleanupService, CleanupServiceError


@dataclass
class ScriptedService:
    """Cleanup-service double with scripted pass outcomes."""

    outcomes: list[Any] = field(default_factory=list)
    passes: list[bool] = field(default_factory=list)
    after_pass: Callable[[], None] | None = None

    def run_once(self, *, dry_run: bool = False) -> Any:
        self.passes.append(dry_run)
        if not self.outcomes:
            result: Any = _ReportStub()
        else:
            outcome = self.outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            result = outcome
        if self.after_pass is not None:
            self.after_pass()
        return result


@dataclass
class _ReportStub:
    cleaned: int = 0
    already_clean: int = 0
    deferred_active: int = 0
    deferred_grace: int = 0
    examined: int = 0
    dry_run: bool = False
    outcome: str = "ok"
    error: str | None = None
    elapsed_seconds: float = 0.0


def _runtime(service: ScriptedService, *, interval: float = 0.0) -> CleanupRuntime:
    return CleanupRuntime(service=cast(CleanupService, service), interval_seconds=interval)


# --- --once exit codes --------------------------------------------------------


def test_once_returns_zero_on_successful_pass() -> None:
    service = ScriptedService()
    exit_code = loop_main(["--once"], runtime_factory=lambda: _runtime(service))
    assert exit_code == 0
    assert service.passes == [False]


def test_once_honors_dry_run() -> None:
    service = ScriptedService()
    exit_code = loop_main(["--once", "--dry-run"], runtime_factory=lambda: _runtime(service))
    assert exit_code == 0
    assert service.passes == [True]


def test_once_returns_one_on_cleanup_degradation() -> None:
    service = ScriptedService(outcomes=[CleanupServiceError("cleanup run failed")])
    exit_code = loop_main(["--once"], runtime_factory=lambda: _runtime(service))
    assert exit_code == 1
    assert service.passes == [False]


def test_once_returns_two_on_configuration_error() -> None:
    def broken_factory() -> CleanupRuntime:
        raise MissingEnvVarError("Required environment variable 'R2_BUCKET_NAME' is not set")

    exit_code = loop_main(["--once"], runtime_factory=broken_factory)
    assert exit_code == 2


def test_once_returns_two_on_invalid_settings() -> None:
    def broken_factory() -> CleanupRuntime:
        raise InvalidSettingError("Setting 'CLEANUP_INTERVAL_SECONDS' must be a positive integer")

    exit_code = loop_main(["--once"], runtime_factory=broken_factory)
    assert exit_code == 2


# --- loop mode ------------------------------------------------------------------


def test_loop_runs_repeated_passes_until_stopped() -> None:
    service = ScriptedService(outcomes=[_ReportStub(), _ReportStub(), _ReportStub()])

    stopper = threading.Event()

    def stop_after_third_pass() -> None:
        if len(service.passes) >= 3:
            stopper.set()

    service.after_pass = stop_after_third_pass
    exit_code = loop_main(
        [],
        runtime_factory=lambda: _runtime(service, interval=0.0),
        stop_event=stopper,
    )
    assert exit_code == 0
    assert len(service.passes) == 3


def test_loop_survives_a_failed_pass_and_continues() -> None:
    service = ScriptedService(
        outcomes=[CleanupServiceError("cleanup run failed"), _ReportStub(), _ReportStub()]
    )
    stopper = threading.Event()

    def stop_after_third_pass() -> None:
        if len(service.passes) >= 3:
            stopper.set()

    service.after_pass = stop_after_third_pass
    exit_code = loop_main(
        [],
        runtime_factory=lambda: _runtime(service, interval=0.0),
        stop_event=stopper,
    )
    assert exit_code == 0
    assert len(service.passes) == 3


def test_loop_honors_the_configured_nonzero_interval(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression guard: the configured interval is the actual pass cadence.

    The prior ``min(interval, 10)`` bug collapsed the effective cadence, so with
    the production 300 s interval the second pass must start at t=300, never at a
    shortened 10 s cadence. A fake clock and patched stop-event wait drive the
    loop deterministically without sleeping.
    """
    interval = float(DEFAULT_CLEANUP_INTERVAL_SECONDS)
    now = 0.0

    def fake_clock() -> float:
        return now

    pass_starts: list[float] = []
    service = ScriptedService()
    stopper = threading.Event()

    def record_and_stop() -> None:
        pass_starts.append(now)
        if len(pass_starts) >= 2:
            stopper.set()

    service.after_pass = record_and_stop

    def fake_wait(timeout: float | None = None) -> bool:
        nonlocal now
        now += timeout if timeout is not None else 0.0
        return stopper.is_set()

    monkeypatch.setattr(stopper, "wait", fake_wait)

    _run_loop(
        _runtime(service, interval=interval),
        dry_run=False,
        stop_event=stopper,
        interval_seconds=interval,
        clock=fake_clock,
    )

    assert pass_starts == [0.0, interval]


def test_signal_handler_sets_the_stop_event() -> None:
    stopper = threading.Event()
    service = ScriptedService()

    def install_and_fire() -> int:
        install_signal_handlers(stopper)
        signal.raise_signal(signal.SIGTERM)
        return loop_main(
            [],
            runtime_factory=lambda: _runtime(service, interval=0.0),
            stop_event=stopper,
        )

    exit_code = install_and_fire()
    assert exit_code == 0
    assert stopper.is_set()


# --- environment-derived configuration --------------------------------------------


def test_parse_cleanup_env_defaults() -> None:
    knobs = parse_cleanup_env({})
    assert knobs.interval_seconds == DEFAULT_CLEANUP_INTERVAL_SECONDS
    assert knobs.grace_seconds > 0
    assert knobs.batch_limit > 0
    assert knobs.max_records >= knobs.batch_limit
    assert knobs.marker_ttl_seconds > 0


def test_parse_cleanup_env_reads_overrides() -> None:
    knobs = parse_cleanup_env(
        {
            "CLEANUP_INTERVAL_SECONDS": "120",
            "CLEANUP_GRACE_SECONDS": "600",
            "CLEANUP_BATCH_LIMIT": "50",
            "CLEANUP_MAX_RECORDS": "250",
        }
    )
    assert knobs.interval_seconds == 120
    assert knobs.grace_seconds == 600
    assert knobs.batch_limit == 50
    assert knobs.max_records == 250


@pytest.mark.parametrize(
    "env",
    [
        pytest.param({"CLEANUP_INTERVAL_SECONDS": "0"}, id="zero-interval"),
        pytest.param({"CLEANUP_INTERVAL_SECONDS": "-5"}, id="negative-interval"),
        pytest.param({"CLEANUP_INTERVAL_SECONDS": "soon"}, id="non-integer-interval"),
        pytest.param({"CLEANUP_BATCH_LIMIT": "0"}, id="zero-batch"),
        pytest.param({"CLEANUP_MAX_RECORDS": "-1"}, id="negative-max-records"),
    ],
)
def test_parse_cleanup_env_rejects_unusable_values(env: dict[str, str]) -> None:
    with pytest.raises(InvalidSettingError):
        parse_cleanup_env(env)


def test_build_runtime_requires_the_standard_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    with pytest.raises(MissingEnvVarError):
        build_runtime_from_env()


def test_build_runtime_wires_a_cleanup_service(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("R2_ACCOUNT_ID", "test")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("R2_BUCKET_NAME", "test")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("CLEANUP_INTERVAL_SECONDS", "90")
    runtime = build_runtime_from_env()
    assert runtime.interval_seconds == 90
    assert isinstance(runtime.service, object)
    assert hasattr(runtime.service, "run_once")
