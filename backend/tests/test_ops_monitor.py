"""Contract tests for the bounded health/monitor script (U-OPS; PE-01..PE-04).

The monitor is a bounded, dependency-injected check runner with stable exit
codes and machine-readable JSON output. Checks implemented:

* ``api_ready`` — GET /health/ready must answer 200 with status ready;
* ``redis`` — PING on the monitor's own bounded client;
* ``clamd`` — TCP zPING must answer PONG on the configured daemon;
* ``queue_backlog`` — XLEN against warn/fail thresholds (R-07 cap 2000);
* ``queue_pel`` — pending-entry count and idle age against thresholds;
* ``worker_health`` — consumer-group existence, PEL staleness, and the
  optional worker /health probe;
* ``cleanup_freshness`` — the ops:cleanup marker's last successful pass is
  recent and its last outcome is ok;
* ``r2_ops`` — a read-only bounded R2 list probe succeeds.

Exit codes: 0 healthy (or warn-only), 1 any failed check, 2 monitor
configuration error. Output carries counts/booleans/enums only (DEC-175):
no URLs, credentials, task ids, or object keys.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest

from app.config import MissingEnvVarError
from app.ops.monitor import (
    Monitor,
    MonitorOptions,
    MonitorRedisLike,
    MonitorReport,
    R2Probe,
    check_api_ready,
    check_clamd,
    check_cleanup_freshness,
    check_queue_backlog,
    check_queue_pel,
    check_r2_ops,
    check_redis,
    check_worker_health,
)
from app.ops.monitor import (
    main as monitor_main,
)

T0 = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)


class FixedClock:
    def __init__(self, now: datetime = T0) -> None:
        self._now = now

    def __call__(self) -> datetime:
        return self._now


class ScriptedUrlOpen:
    def __init__(self, responses: dict[str, tuple[int, bytes]] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[str] = []

    def __call__(self, url: str, timeout: float) -> tuple[int, bytes]:
        self.calls.append(url)
        response = self.responses.get(url)
        if response is None:
            raise TimeoutError("connect timed out")
        return response


class FakeSocket:
    def __init__(
        self,
        *,
        reply: bytes = b"PONG",
        connect_error: Exception | None = None,
        send_error: Exception | None = None,
    ) -> None:
        self._reply = reply
        self._connect_error = connect_error
        self._send_error = send_error
        self.sent: list[bytes] = []
        self.timeout: float | None = None
        self.closed = False

    def connect(self, address: tuple[str, int]) -> None:
        if self._connect_error is not None:
            raise self._connect_error

    def settimeout(self, value: float | None) -> None:
        self.timeout = value

    def sendall(self, data: bytes) -> None:
        if self._send_error is not None:
            raise self._send_error
        self.sent.append(data)

    def recv(self, bufsize: int) -> bytes:
        return self._reply

    def close(self) -> None:
        self.closed = True


class ScriptedRedis:
    """Redis double with scripted stream/marker behavior."""

    def __init__(
        self,
        *,
        stream_length: int = 0,
        pending_entries: Sequence[Mapping[str, Any]] | None = None,
        errors: Mapping[str, Exception] | None = None,
        marker: dict[bytes, bytes] | None = None,
    ) -> None:
        if errors is None:
            errors = {}
        self._ping_error = errors.get("ping")
        self._stream_length = stream_length
        self._xlen_error = errors.get("xlen")
        self._pending_entries = pending_entries
        self._pending_error = errors.get("pending")
        self._marker = marker

    def ping(self) -> bool:
        if self._ping_error is not None:
            raise self._ping_error
        return True

    def xlen(self, name: str) -> int:
        if self._xlen_error is not None:
            raise self._xlen_error
        return self._stream_length

    def xpending_range(
        self, name: str, groupname: str, min: str, max: str, count: int
    ) -> list[dict[str, object]]:
        if self._pending_error is not None:
            raise self._pending_error
        entries = self._pending_entries or []
        return [dict(entry) for entry in entries[:count]]

    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]:
        if self._marker is None:
            return {}
        return cast(Mapping[bytes | str, bytes | str], self._marker)


class ScriptedR2Probe:
    def __init__(self, *, available: bool = True) -> None:
        self._available = available
        self.calls = 0

    def probe(self) -> bool:
        self.calls += 1
        return self._available


# --- api_ready --------------------------------------------------------------------


def test_api_ready_ok_requires_200_and_ready_status() -> None:
    url_open = ScriptedUrlOpen(
        {"http://api:3000/health/ready": (200, b'{"status":"ready","checks":{}}')}
    )
    result = check_api_ready(url_open, "http://api:3000/health/ready", timeout_seconds=2)
    assert result.status == "ok"
    assert result.details["status_code"] == 200


def test_api_ready_fails_when_api_reports_not_ready() -> None:
    url_open = ScriptedUrlOpen(
        {"http://api:3000/health/ready": (200, b'{"status":"not_ready","checks":{}}')}
    )
    result = check_api_ready(url_open, "http://api:3000/health/ready", timeout_seconds=2)
    assert result.status == "fail"


def test_api_ready_fails_on_non_200() -> None:
    url_open = ScriptedUrlOpen({"http://api:3000/health/ready": (503, b'{"status":"not_ready"}')})
    result = check_api_ready(url_open, "http://api:3000/health/ready", timeout_seconds=2)
    assert result.status == "fail"
    assert result.details["status_code"] == 503


def test_api_ready_fails_on_timeout_with_class_name_only() -> None:
    url_open = ScriptedUrlOpen({})
    result = check_api_ready(url_open, "http://api:3000/health/ready", timeout_seconds=2)
    assert result.status == "fail"
    assert result.details["error"] == "TimeoutError"
    assert "connect timed out" not in json.dumps(result.details)


def test_api_ready_fails_on_unparseable_body() -> None:
    url_open = ScriptedUrlOpen({"http://api:3000/health/ready": (200, b"<html>nope</html>")})
    result = check_api_ready(url_open, "http://api:3000/health/ready", timeout_seconds=2)
    assert result.status == "fail"


# --- redis ---------------------------------------------------------------------------


def test_redis_ok_on_successful_ping() -> None:
    result = check_redis(ScriptedRedis())
    assert result.status == "ok"


def test_redis_fails_on_unreachable_server() -> None:
    result = check_redis(ScriptedRedis(errors={"ping": ConnectionError("connection refused")}))
    assert result.status == "fail"
    assert result.details["error"] == "ConnectionError"
    assert "connection refused" not in json.dumps(result.details)


# --- clamd -----------------------------------------------------------------------------


def test_clamd_ok_on_pong() -> None:
    created: list[FakeSocket] = []

    def factory() -> FakeSocket:
        created.append(FakeSocket(reply=b"PONG"))
        return created[-1]

    result = check_clamd(factory, "clamd", 3310, timeout_seconds=2)
    assert result.status == "ok"
    assert created[0].sent == [b"zPING\x00"]
    assert created[0].timeout == 2
    assert created[0].closed


def test_clamd_fails_on_connection_refused() -> None:
    def factory() -> FakeSocket:
        return FakeSocket(connect_error=ConnectionRefusedError("refused"))

    result = check_clamd(factory, "clamd", 3310, timeout_seconds=2)
    assert result.status == "fail"
    assert result.details["error"] == "ConnectionRefusedError"
    assert "refused" not in json.dumps(result.details)


def test_clamd_fails_on_unexpected_reply() -> None:
    def factory() -> FakeSocket:
        return FakeSocket(reply=b"VERSION-ROGUE")

    result = check_clamd(factory, "clamd", 3310, timeout_seconds=2)
    assert result.status == "fail"


# --- queue backlog / PEL ----------------------------------------------------------------


def test_queue_backlog_thresholds() -> None:
    assert check_queue_backlog(ScriptedRedis(stream_length=0)).status == "ok"
    assert check_queue_backlog(ScriptedRedis(stream_length=999)).status == "ok"
    assert check_queue_backlog(ScriptedRedis(stream_length=1000)).status == "warn"
    assert check_queue_backlog(ScriptedRedis(stream_length=1799)).status == "warn"
    assert check_queue_backlog(ScriptedRedis(stream_length=1800)).status == "fail"
    assert check_queue_backlog(ScriptedRedis(stream_length=2000)).status == "fail"


def test_queue_backlog_custom_thresholds() -> None:
    result = check_queue_backlog(
        ScriptedRedis(stream_length=50), warn_threshold=10, fail_threshold=100
    )
    assert result.status == "warn"


def test_queue_backlog_fails_on_redis_error() -> None:
    result = check_queue_backlog(ScriptedRedis(errors={"xlen": ConnectionError("gone")}))
    assert result.status == "fail"


def _pending_entry(idle_ms: int) -> dict[str, Any]:
    return {
        "message_id": b"1754654400000-0",
        "consumer": b"worker",
        "time_since_delivered": idle_ms,
        "times_delivered": 1,
    }


def test_queue_pel_ok_when_empty() -> None:
    result = check_queue_pel(ScriptedRedis(pending_entries=[]))
    assert result.status == "ok"
    assert result.details["pending"] == 0


def test_queue_pel_fails_when_count_exceeds_threshold() -> None:
    entries = [_pending_entry(1000) for _ in range(17)]
    result = check_queue_pel(ScriptedRedis(pending_entries=entries), fail_count_threshold=16)
    assert result.status == "fail"
    assert result.details["pending"] == 17


def test_queue_pel_fails_when_entries_are_stale() -> None:
    entries = [_pending_entry(900_001)]
    result = check_queue_pel(ScriptedRedis(pending_entries=entries), idle_fail_ms=900_000)
    assert result.status == "fail"
    assert result.details["oldest_idle_ms"] == 900_001


def test_queue_pel_reports_absent_consumer_group() -> None:
    nogroup = type("ResponseError", (RuntimeError,), {})("NOGROUP No such consumer group")
    result = check_queue_pel(ScriptedRedis(errors={"pending": nogroup}))
    assert result.status == "ok"
    assert result.details["group_exists"] is False


# --- worker health ------------------------------------------------------------------------


def test_worker_health_ok_with_group_and_fresh_pel() -> None:
    redis = ScriptedRedis(pending_entries=[_pending_entry(1000)])
    result = check_worker_health(redis)
    assert result.status == "ok"
    assert result.details["group_exists"] is True


def test_worker_health_fails_when_no_consumer_group_ever_formed() -> None:
    nogroup = type("ResponseError", (RuntimeError,), {})("NOGROUP No such consumer group")
    result = check_worker_health(ScriptedRedis(errors={"pending": nogroup}))
    assert result.status == "fail"
    assert result.details["group_exists"] is False


def test_worker_health_fails_on_stale_pending_entries() -> None:
    redis = ScriptedRedis(pending_entries=[_pending_entry(2_000_000)])
    result = check_worker_health(redis, idle_fail_ms=900_000)
    assert result.status == "fail"


def test_worker_health_probes_optional_http_endpoint() -> None:
    redis = ScriptedRedis(pending_entries=[])
    url_open = ScriptedUrlOpen({"http://workers:8000/health": (200, b'{"status":"ready"}')})
    healthy = check_worker_health(
        redis, url_open=url_open, worker_health_url="http://workers:8000/health"
    )
    assert healthy.status == "ok"
    failing = check_worker_health(
        redis, url_open=ScriptedUrlOpen({}), worker_health_url="http://workers:8000/health"
    )
    assert failing.status == "fail"


# --- cleanup freshness ----------------------------------------------------------------------


def _marker_bytes(fields: dict[str, str]) -> dict[bytes, bytes]:
    return {key.encode(): value.encode() for key, value in fields.items()}


def test_cleanup_freshness_ok_when_recent_success() -> None:
    marker = _marker_bytes(
        {
            "last_outcome": "ok",
            "last_success_at": (T0 - timedelta(seconds=60)).isoformat(timespec="seconds"),
        }
    )
    result = check_cleanup_freshness(
        ScriptedRedis(marker=marker), max_age_seconds=900, clock=FixedClock()
    )
    assert result.status == "ok"
    assert result.details["age_seconds"] == 60


def test_cleanup_freshness_fails_when_marker_absent() -> None:
    result = check_cleanup_freshness(
        ScriptedRedis(marker=None), max_age_seconds=900, clock=FixedClock()
    )
    assert result.status == "fail"
    assert result.details["reason"] == "marker_absent"


def test_cleanup_freshness_fails_when_success_is_stale() -> None:
    marker = _marker_bytes(
        {
            "last_outcome": "ok",
            "last_success_at": (T0 - timedelta(seconds=3700)).isoformat(timespec="seconds"),
        }
    )
    result = check_cleanup_freshness(
        ScriptedRedis(marker=marker), max_age_seconds=3600, clock=FixedClock()
    )
    assert result.status == "fail"
    assert result.details["reason"] == "stale"


def test_cleanup_freshness_fails_when_last_run_failed() -> None:
    marker = _marker_bytes(
        {
            "last_outcome": "failed",
            "last_success_at": (T0 - timedelta(seconds=10)).isoformat(timespec="seconds"),
            "last_finished_at": T0.isoformat(timespec="seconds"),
        }
    )
    result = check_cleanup_freshness(
        ScriptedRedis(marker=marker), max_age_seconds=900, clock=FixedClock()
    )
    assert result.status == "fail"
    assert result.details["reason"] == "last_run_failed"


def test_cleanup_freshness_fails_on_unparseable_timestamp() -> None:
    marker = _marker_bytes({"last_outcome": "ok", "last_success_at": "not-a-timestamp"})
    result = check_cleanup_freshness(
        ScriptedRedis(marker=marker), max_age_seconds=900, clock=FixedClock()
    )
    assert result.status == "fail"


# --- r2 ops -----------------------------------------------------------------------------------


def test_r2_ops_ok_when_probe_succeeds() -> None:
    probe = ScriptedR2Probe(available=True)
    result = check_r2_ops(probe)
    assert result.status == "ok"
    assert probe.calls == 1


def test_r2_ops_fails_when_probe_unavailable() -> None:
    result = check_r2_ops(ScriptedR2Probe(available=False))
    assert result.status == "fail"


def test_r2_ops_fails_when_probe_not_configured() -> None:
    result = check_r2_ops(None)
    assert result.status == "fail"
    assert result.details["error"] == "ProbeNotConfigured"


# --- aggregation, JSON output, exit codes --------------------------------------------------------


class _UseDefault:
    """Sentinel distinguishing 'use the healthy default' from an override."""


_USE_DEFAULT = _UseDefault()


def _healthy_options(
    *,
    redis: MonitorRedisLike | _UseDefault = _USE_DEFAULT,
    r2_probe: R2Probe | _UseDefault = _USE_DEFAULT,
) -> MonitorOptions:
    resolved_redis: MonitorRedisLike
    if isinstance(redis, _UseDefault):
        resolved_redis = ScriptedRedis(
            marker=_marker_bytes(
                {
                    "last_outcome": "ok",
                    "last_success_at": (T0 - timedelta(seconds=60)).isoformat(timespec="seconds"),
                }
            )
        )
    else:
        resolved_redis = redis
    resolved_probe: R2Probe
    if isinstance(r2_probe, _UseDefault):
        resolved_probe = ScriptedR2Probe(available=True)
    else:
        resolved_probe = r2_probe
    return MonitorOptions(
        clock=FixedClock(),
        url_open=ScriptedUrlOpen({"http://api:3000/health/ready": (200, b'{"status":"ready"}')}),
        redis=resolved_redis,
        socket_factory=lambda: FakeSocket(reply=b"PONG"),
        r2_probe=resolved_probe,
    )


def _healthy_monitor(
    *,
    redis: MonitorRedisLike | _UseDefault = _USE_DEFAULT,
    r2_probe: R2Probe | _UseDefault = _USE_DEFAULT,
) -> Monitor:
    return Monitor(options=_healthy_options(redis=redis, r2_probe=r2_probe))


def test_monitor_reports_healthy_when_all_checks_pass() -> None:
    report = _healthy_monitor().run_checks()
    assert report.status == "healthy"
    names = {check.name for check in report.checks}
    assert names == {
        "api_ready",
        "redis",
        "clamd",
        "queue_backlog",
        "queue_pel",
        "worker_health",
        "cleanup_freshness",
        "r2_ops",
    }
    assert all(check.status == "ok" for check in report.checks)


def test_monitor_reports_degraded_on_warn_only() -> None:
    redis = ScriptedRedis(
        stream_length=1500,
        marker=_marker_bytes(
            {
                "last_outcome": "ok",
                "last_success_at": (T0 - timedelta(seconds=60)).isoformat(timespec="seconds"),
            }
        ),
    )
    report = _healthy_monitor(redis=redis).run_checks()
    assert report.status == "degraded"


def test_monitor_reports_failed_on_any_failed_check() -> None:
    report = _healthy_monitor(r2_probe=ScriptedR2Probe(available=False)).run_checks()
    assert report.status == "failed"


def test_report_json_is_stable_and_machine_readable() -> None:
    report = _healthy_monitor().run_checks()
    payload = json.loads(report.to_json())
    assert payload["status"] == "healthy"
    assert payload["generated_at"]
    assert isinstance(payload["checks"], list)
    for check in payload["checks"]:
        assert set(check) == {"name", "status", "details"}
        assert check["status"] in {"ok", "warn", "fail"}
    assert payload["summary"] == {"ok": 8, "warn": 0, "fail": 0}


def test_report_json_never_leaks_configuration_or_identifiers() -> None:
    report = _healthy_monitor().run_checks()
    rendered = report.to_json()
    for sensitive in (
        "redis://",
        "localhost:6379",
        "r2.cloudflarestorage.com",
        "test-secret",
        "connection refused",
    ):
        assert sensitive not in rendered


def test_monitor_main_exit_zero_when_healthy(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = monitor_main([], monitor_factory=_healthy_monitor)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["status"] == "healthy"


def test_monitor_main_exit_one_when_failed(capsys: pytest.CaptureFixture[str]) -> None:
    monitor = _healthy_monitor(r2_probe=ScriptedR2Probe(available=False))
    exit_code = monitor_main([], monitor_factory=lambda: monitor)
    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out)["status"] == "failed"


def test_monitor_main_exit_zero_on_warn_only(capsys: pytest.CaptureFixture[str]) -> None:
    redis = ScriptedRedis(
        stream_length=1500,
        marker=_marker_bytes(
            {
                "last_outcome": "ok",
                "last_success_at": (T0 - timedelta(seconds=60)).isoformat(timespec="seconds"),
            }
        ),
    )
    exit_code = monitor_main([], monitor_factory=lambda: _healthy_monitor(redis=redis))
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["status"] == "degraded"


def test_monitor_main_exit_two_on_configuration_error() -> None:
    def broken_factory() -> Monitor:
        raise MissingEnvVarError("Required environment variable 'R2_BUCKET_NAME' is not set")

    exit_code = monitor_main([], monitor_factory=broken_factory)
    assert exit_code == 2


def test_monitor_watch_mode_stops_on_event(capsys: pytest.CaptureFixture[str]) -> None:
    stopper = threading.Event()

    class CountingMonitor(Monitor):
        def __init__(self, options: MonitorOptions, stop_event: threading.Event) -> None:
            super().__init__(options=options)
            self._stop_event = stop_event
            self.reports = 0

        def run_checks(self) -> MonitorReport:
            self.reports += 1
            if self.reports >= 2:
                self._stop_event.set()
            return super().run_checks()

    monitor = CountingMonitor(_healthy_options(), stopper)
    exit_code = monitor_main(["--watch", "0"], monitor_factory=lambda: monitor, stop_event=stopper)
    assert exit_code == 0
    assert monitor.reports == 2
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 2
    assert all(json.loads(line)["status"] == "healthy" for line in lines)
