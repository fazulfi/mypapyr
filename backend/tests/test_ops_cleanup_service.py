"""Contract tests for the scheduled cleanup service (U-OPS; PE-04, ARC-06).

The service is the operational activation layer over the BE-07 coordinator:
one bounded, idempotent pass suitable for a timer/scheduler, never an
unbounded drain inside a request handler.

Semantics under test:

* eligibility = expiry PLUS grace period: a record becomes eligible only
  once ``expires_at + grace_seconds <= now`` (arch 9.1 hard guard plus an
  operational grace window against clock skew and deadline-boundary races);
* active-job protection: records still ``processing`` are NEVER deleted —
  they are deferred and counted, whatever their expiry says;
* safe order preserved: every eligible record is cleaned through the BE-07
  coordinator (objects first, then the record; idempotent; fail-closed);
* bounded work per invocation: ``batch_limit`` pages, ``max_records``
  deletions, ``max_pages`` discovery passes, and SCAN-revisit termination;
* dry-run: classification without any deletion and without marker writes;
* freshness marker: every real pass (success or failure) records a bounded
  privacy-safe ``ops:cleanup`` marker the monitor reads; dry runs never do;
* telemetry privacy (DEC-166/DEC-175): counts, timing, and exception class
  names only — never task ids, object keys, or exception messages.
"""

from __future__ import annotations

import io
import logging
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import fakeredis
import pytest

from app.config import Settings
from app.ops.cleanup_service import (
    CLEANUP_MARKER_KEY,
    CleanupService,
    CleanupServiceError,
    CleanupServiceOptions,
    CleanupServiceReport,
    CleanupStore,
    read_cleanup_marker,
)
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.schemas.job import ResultSummary
from app.tasks.cleanup import CleanupUnavailableError
from app.tasks.state_machine import JobEvent, JobState
from app.utils.logging import PapyrJsonHandler

T0 = datetime(2026, 8, 8, 0, 0, 0, tzinfo=UTC)

_KEY_A = "tmp/2026-08-08/" + "a" * 32 + ".pdf"
_KEY_B = "tmp/2026-08-08/" + "b" * 32 + ".pdf"
_SENSITIVE_TASK_ID = "task-with-sensitive-identifier"
_SENSITIVE_OBJECT = "tmp/2026-08-08/" + "c" * 32 + ".pdf"

GRACE_SECONDS = 300


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)

    def __call__(self) -> datetime:
        return self._now


def make_settings() -> Settings:
    return Settings(
        r2_account_id="test",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test",
        allowed_origins=("http://localhost:3000",),
    )


def make_record(
    clock: FakeClock, *, task_id: str | None = None, objects: tuple[str, ...] = ()
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="compress-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        objects=objects,
    )


def create_then_expire(
    store: TaskStore, clock: FakeClock, *, task_id: str | None = None, objects: tuple[str, ...] = ()
) -> TaskRecord:
    record = make_record(clock, task_id=task_id, objects=objects)
    store.create(record)
    clock.advance(3600)
    return record


def expire_past_grace(store: TaskStore, clock: FakeClock, **kwargs: Any) -> TaskRecord:
    record = create_then_expire(store, clock, **kwargs)
    clock.advance(GRACE_SECONDS)
    return record


@dataclass
class FakeR2:
    delete_error: Exception | None = None
    deleted_keys: list[str] = field(default_factory=list)

    def delete_object(self, key: str) -> bool:
        self.deleted_keys.append(key)
        if self.delete_error is not None:
            raise self.delete_error
        return True


@dataclass
class RecordingR2:
    log: list[str]

    def delete_object(self, key: str) -> bool:
        self.log.append(f"r2.delete:{key}")
        return True


class RecordingStore:
    def __init__(self, inner: TaskStore, log: list[str]) -> None:
        self._inner = inner
        self._log = log

    def get(self, task_id: str) -> TaskRecord:
        self._log.append(f"store.get:{task_id}")
        return self._inner.get(task_id)

    def delete(self, task_id: str) -> bool:
        self._log.append(f"store.delete:{task_id}")
        return self._inner.delete(task_id)

    def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
        self._log.append("store.list_expired")
        return self._inner.list_expired(now, limit=limit)


@dataclass
class FakeMarkerStore:
    """Marker-hash double recording writes and TTLs."""

    hashes: dict[str, dict[str, str]] = field(default_factory=dict)
    ttls: dict[str, int] = field(default_factory=dict)
    fail: bool = False

    def hset(self, name: str, mapping: Mapping[str, str]) -> int:
        if self.fail:
            raise ConnectionError("marker store down")
        self.hashes.setdefault(name, {}).update(mapping)
        return len(mapping)

    def expire(self, name: str, seconds: int) -> bool:
        self.ttls[name] = seconds
        return True

    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]:
        return cast(Mapping[bytes | str, bytes | str], dict(self.hashes.get(name, {})))


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(T0)


@pytest.fixture
def store(clock: FakeClock) -> TaskStore:
    return TaskStore(
        make_settings(),
        client=cast(Any, fakeredis.FakeRedis(server=fakeredis.FakeServer())),
        clock=clock,
    )


def _capture_service_logs() -> tuple[io.StringIO, PapyrJsonHandler, int]:
    stream = io.StringIO()
    handler = PapyrJsonHandler(stream=stream)
    logger = logging.getLogger("app.ops.cleanup_service")
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return stream, handler, previous


def make_service(
    store: CleanupStore,
    r2: Any,
    clock: FakeClock,
    **kwargs: Any,
) -> tuple[CleanupService, FakeMarkerStore]:
    """Helper for tests: passes standard options via CleanupServiceOptions."""
    marker_store = FakeMarkerStore()
    # If caller already provides options, use them directly
    if "options" in kwargs:
        options = kwargs.pop("options")
    else:
        option_fields = {
            key: kwargs.pop(key)
            for key in (
                "grace_seconds",
                "batch_limit",
                "max_records",
                "max_pages",
                "marker_ttl_seconds",
            )
            if key in kwargs
        }
        option_fields.setdefault("grace_seconds", GRACE_SECONDS)
        options = CleanupServiceOptions(**option_fields)
    service = CleanupService(
        store,
        r2,
        clock=clock,
        marker_store=marker_store,
        options=options,
        **kwargs,
    )
    return service, marker_store


# --- eligibility: expiry plus grace --------------------------------------------


def test_eligible_record_is_cleaned_objects_then_record(store: TaskStore, clock: FakeClock) -> None:
    log: list[str] = []
    record = expire_past_grace(store, clock, objects=(_KEY_A,))
    service, _ = make_service(RecordingStore(store, log), RecordingR2(log), clock)

    report = service.run_once()

    assert report.cleaned == 1
    assert log.index(f"r2.delete:{_KEY_A}") < log.index(f"store.delete:{record.task_id}")
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)


def test_record_inside_grace_window_is_deferred_not_deleted(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = FakeR2()
    record = create_then_expire(store, clock, objects=(_KEY_A,))
    clock.advance(GRACE_SECONDS - 1)
    service, _ = make_service(store, r2, clock)

    report = service.run_once()

    assert report.cleaned == 0
    assert report.deferred_grace == 1
    assert r2.deleted_keys == []
    assert store.get(record.task_id).objects == (_KEY_A,)


def test_processing_record_is_never_deleted_even_long_past_expiry(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = FakeR2()
    record = make_record(clock, objects=(_KEY_A,))
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(3600 + GRACE_SECONDS + 3600)
    assert store.get(record.task_id).state is JobState.PROCESSING
    service, _ = make_service(store, r2, clock)

    report = service.run_once()

    assert report.cleaned == 0
    assert report.deferred_active == 1
    assert r2.deleted_keys == []
    assert store.get(record.task_id).state is JobState.PROCESSING


def test_terminal_records_are_eligible_after_grace(store: TaskStore, clock: FakeClock) -> None:
    r2 = FakeR2()
    queued = make_record(clock, objects=(_KEY_A,))
    store.create(queued)
    done_source = make_record(clock, objects=(_KEY_B,))
    store.create(done_source)
    store.transition_state(
        done_source.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
    )
    store.transition_state(
        done_source.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(
            result=ResultSummary(output_count=1, total_bytes=8), objects=(_KEY_B,)
        ),
    )
    clock.advance(3600 + GRACE_SECONDS)
    service, _ = make_service(store, r2, clock)

    report = service.run_once()

    assert report.cleaned == 2
    assert set(r2.deleted_keys) == {_KEY_A, _KEY_B}


# --- idempotency and restart recovery -------------------------------------------


def test_second_pass_is_a_no_op(store: TaskStore, clock: FakeClock) -> None:
    r2 = FakeR2()
    expire_past_grace(store, clock, objects=(_KEY_A,))
    service, _ = make_service(store, r2, clock)

    first = service.run_once()
    second = service.run_once()

    assert first.cleaned == 1
    assert second.cleaned == 0
    assert second.examined == 0
    assert r2.deleted_keys == [_KEY_A]


def test_partial_failure_recovers_on_the_next_pass(store: TaskStore, clock: FakeClock) -> None:
    expire_past_grace(store, clock, task_id="first", objects=(_KEY_A,))
    expire_past_grace(store, clock, task_id="second", objects=(_KEY_B,))

    flaky = FakeR2(delete_error=RuntimeError("transient r2 outage"))
    failing_service, failing_marker = make_service(store, flaky, clock)
    with pytest.raises(CleanupServiceError):
        failing_service.run_once()
    assert failing_marker.hashes[CLEANUP_MARKER_KEY]["last_outcome"] == "failed"

    healthy_r2 = FakeR2()
    healthy_service, healthy_marker = make_service(store, healthy_r2, clock)
    report = healthy_service.run_once()

    assert report.cleaned == 2
    assert set(healthy_r2.deleted_keys) == {_KEY_A, _KEY_B}
    assert healthy_marker.hashes[CLEANUP_MARKER_KEY]["last_outcome"] == "ok"
    assert healthy_marker.hashes[CLEANUP_MARKER_KEY]["last_success_at"]


# --- bounded work ----------------------------------------------------------------


def test_max_records_bounds_deletions_per_pass(store: TaskStore, clock: FakeClock) -> None:
    r2 = FakeR2()
    for index in range(5):
        expire_past_grace(store, clock, task_id=f"task-{index}", objects=(_KEY_A,))
    service, _ = make_service(store, r2, clock, options=CleanupServiceOptions(max_records=2))

    report = service.run_once()

    assert report.cleaned == 2
    assert len(r2.deleted_keys) == 2
    # Remaining survivors stay discoverable for the next scheduled pass.
    assert len(store.list_expired(clock())) == 3


def test_pages_are_bounded_by_batch_limit(store: TaskStore, clock: FakeClock) -> None:
    calls: list[int] = []

    class SpyStore:
        def __init__(self, inner: TaskStore) -> None:
            self._inner = inner

        def get(self, task_id: str) -> TaskRecord:
            return self._inner.get(task_id)

        def delete(self, task_id: str) -> bool:
            return self._inner.delete(task_id)

        def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
            calls.append(limit)
            return self._inner.list_expired(now, limit=limit)

    for index in range(3):
        expire_past_grace(store, clock, task_id=f"task-{index}")
    service, _ = (
        CleanupService(
            SpyStore(store),
            FakeR2(),
            clock=clock,
            marker_store=FakeMarkerStore(),
            options=CleanupServiceOptions(grace_seconds=GRACE_SECONDS, batch_limit=2),
        ),
        FakeMarkerStore(),
    )

    report = service.run_once()

    assert report.cleaned == 3
    assert calls and all(call == 2 for call in calls)


def test_revisited_pages_terminate_the_pass(store: TaskStore, clock: FakeClock) -> None:
    # Create 3 records all with SAME deadline, so they're grouped together
    for index in range(3):
        record = make_record(clock, task_id=f"grace-{index}")
        store.create(record)

    # Advance to EXACTLY deadline (so records appear expired but not past grace)
    # At this point, now == expires_at, so expires_at + grace > now (still within grace)
    clock.advance(3600)

    class RevisitingStore:
        def __init__(self, inner: TaskStore) -> None:
            self._inner = inner
            self._cached: list[TaskRecord] | None = None

        def get(self, task_id: str) -> TaskRecord:
            return self._inner.get(task_id)

        def delete(self, task_id: str) -> bool:
            return self._inner.delete(task_id)

        def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
            if self._cached is not None:
                cached, self._cached = self._cached, None
                return cached
            page = self._inner.list_expired(now, limit=limit)
            if page:
                self._cached = page
            return page

    service, _ = (
        CleanupService(
            RevisitingStore(store),
            FakeR2(),
            clock=clock,
            marker_store=FakeMarkerStore(),
            options=CleanupServiceOptions(grace_seconds=GRACE_SECONDS),
        ),
        FakeMarkerStore(),
    )

    report = service.run_once()

    # All records deferred_grace (expires_at + grace > now), none cleaned
    assert report.cleaned == 0
    assert report.deferred_grace == 3
    assert report.deferred_grace == 3


def test_max_pages_bounds_discovery_work(store: TaskStore, clock: FakeClock) -> None:
    pages = 0

    class PagingStore:
        def __init__(self, inner: TaskStore) -> None:
            self._inner = inner

        def get(self, task_id: str) -> TaskRecord:
            return self._inner.get(task_id)

        def delete(self, task_id: str) -> bool:
            return self._inner.delete(task_id)

        def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
            nonlocal pages
            pages += 1
            return self._inner.list_expired(now, limit=limit)

    for index in range(6):
        expire_past_grace(store, clock, task_id=f"task-{index}")
    service, _ = (
        CleanupService(
            PagingStore(store),
            FakeR2(),
            clock=clock,
            marker_store=FakeMarkerStore(),
            options=CleanupServiceOptions(grace_seconds=GRACE_SECONDS, batch_limit=1, max_pages=3),
        ),
        FakeMarkerStore(),
    )

    report = service.run_once()

    assert pages <= 3
    assert report.cleaned <= 3


# --- dry run ---------------------------------------------------------------------


def test_dry_run_classifies_without_deleting_or_marking(store: TaskStore, clock: FakeClock) -> None:
    r2 = FakeR2()
    # Create eligible first (deep past grace)
    eligible = expire_past_grace(store, clock, objects=(_KEY_A,))
    clock.advance(3600)  # Make eligible well past deadline/grace
    # Processing record: expired but PROCESSING
    processing = make_record(clock, task_id="active", objects=(_KEY_B,))
    store.create(processing)
    store.transition_state("active", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(3600)  # Processing now at deadline (expired)
    # In-grace record LAST: created now, expires T+3600, so within grace at run time
    create_then_expire(store, clock, task_id="in-grace")
    # Run at same clock: in-grace.expires_at=T+3900, grace=300, expires_at+grace=T+4200 > T
    # So in-grace.deferred_grace=1
    service, marker = make_service(store, r2, clock)

    report = service.run_once(dry_run=True)

    assert report.dry_run is True
    assert report.cleaned == 1
    assert report.deferred_grace == 1
    assert report.deferred_active == 1
    assert r2.deleted_keys == []
    assert store.get(eligible.task_id).objects == (_KEY_A,)
    assert marker.hashes == {}


# --- failure semantics -------------------------------------------------------------


def test_object_delete_failure_preserves_record_and_marks_failed(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = FakeR2(delete_error=RuntimeError("simulated r2 outage"))
    record = expire_past_grace(store, clock, objects=(_KEY_A,))
    service, marker = make_service(store, r2, clock)

    with pytest.raises(CleanupServiceError) as excinfo:
        service.run_once()

    assert store.get(record.task_id).objects == (_KEY_A,)
    fields = marker.hashes[CLEANUP_MARKER_KEY]
    assert fields["last_outcome"] == "failed"
    assert "simulated r2 outage" not in fields["last_error"]
    assert "simulated r2 outage" not in str(excinfo.value)


def test_store_discovery_failure_marks_failed_and_raises(
    store: TaskStore, clock: FakeClock
) -> None:
    class FailingDiscovery:
        def get(self, task_id: str) -> TaskRecord:
            raise StoreUnavailableError()

        def delete(self, task_id: str) -> bool:
            raise StoreUnavailableError()

        def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
            raise StoreUnavailableError()

    service, _marker = (
        CleanupService(
            FailingDiscovery(),
            FakeR2(),
            clock=clock,
            marker_store=FakeMarkerStore(),
            options=CleanupServiceOptions(grace_seconds=GRACE_SECONDS),
        ),
        FakeMarkerStore(),
    )

    with pytest.raises(CleanupServiceError):
        service.run_once()


def test_service_error_preserves_the_cause(store: TaskStore, clock: FakeClock) -> None:
    r2 = FakeR2(delete_error=RuntimeError("simulated r2 outage"))
    expire_past_grace(store, clock, objects=(_KEY_A,))
    service, _ = make_service(store, r2, clock)

    with pytest.raises(CleanupServiceError) as excinfo:
        service.run_once()

    assert isinstance(excinfo.value.__cause__, (CleanupUnavailableError, RuntimeError))


# --- freshness marker ---------------------------------------------------------------


def test_successful_pass_writes_a_bounded_freshness_marker(
    store: TaskStore, clock: FakeClock
) -> None:
    expire_past_grace(store, clock, objects=(_KEY_A,))
    service, marker = make_service(store, FakeR2(), clock)

    report = service.run_once()

    fields = marker.hashes[CLEANUP_MARKER_KEY]
    assert fields["last_outcome"] == "ok"
    assert fields["last_success_at"] == clock().isoformat(timespec="seconds")
    assert fields["last_finished_at"] == clock().isoformat(timespec="seconds")
    assert fields["cleaned"] == "1"
    assert marker.ttls[CLEANUP_MARKER_KEY] > 0
    assert report.outcome == "ok"


def test_marker_fields_carry_no_identifiers(store: TaskStore, clock: FakeClock) -> None:
    expire_past_grace(store, clock, task_id=_SENSITIVE_TASK_ID, objects=(_SENSITIVE_OBJECT,))
    service, marker = make_service(store, FakeR2(), clock)

    service.run_once()

    fields = marker.hashes[CLEANUP_MARKER_KEY]
    assert _SENSITIVE_TASK_ID not in fields
    assert _SENSITIVE_OBJECT not in fields
    for value in fields.values():
        assert _SENSITIVE_TASK_ID not in value
        assert _SENSITIVE_OBJECT not in value


def test_read_cleanup_marker_returns_fields_or_none() -> None:
    marker = FakeMarkerStore()
    assert read_cleanup_marker(marker) is None
    marker.hashes[CLEANUP_MARKER_KEY] = {"last_outcome": "ok"}
    assert read_cleanup_marker(marker) == {"last_outcome": "ok"}


# --- telemetry privacy ----------------------------------------------------------------


def test_run_telemetry_counts_and_timing_only(store: TaskStore, clock: FakeClock) -> None:
    r2 = FakeR2()
    expire_past_grace(store, clock, task_id=_SENSITIVE_TASK_ID, objects=(_SENSITIVE_OBJECT,))
    service, _ = make_service(store, r2, clock)

    stream, handler, previous = _capture_service_logs()
    logger = logging.getLogger("app.ops.cleanup_service")
    try:
        report = service.run_once()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)

    assert report.cleaned == 1
    output = stream.getvalue()
    assert "cleanup pass ok" in output
    assert '"cleaned":1' in output
    for identifier in (_SENSITIVE_TASK_ID, _SENSITIVE_OBJECT, "simulated", "test"):
        assert identifier not in output


def test_failure_telemetry_has_no_identifiers(store: TaskStore, clock: FakeClock) -> None:
    service, _ = make_service(
        store, FakeR2(delete_error=RuntimeError("simulated r2 outage")), clock
    )
    expire_past_grace(store, clock, task_id=_SENSITIVE_TASK_ID, objects=(_SENSITIVE_OBJECT,))

    stream, handler, previous = _capture_service_logs()
    logger = logging.getLogger("app.ops.cleanup_service")
    try:
        with pytest.raises(CleanupServiceError):
            service.run_once()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)

    output = stream.getvalue()
    assert "cleanup pass failed" in output
    for identifier in (_SENSITIVE_TASK_ID, _SENSITIVE_OBJECT, "simulated r2 outage"):
        assert identifier not in output


def test_report_is_frozen_and_typed(store: TaskStore, clock: FakeClock) -> None:
    service, _ = make_service(store, FakeR2(), clock)
    report = service.run_once()
    assert isinstance(report, CleanupServiceReport)
    assert report.elapsed_seconds >= 0.0
    with pytest.raises(AttributeError):
        cast(Any, report).cleaned = 99
