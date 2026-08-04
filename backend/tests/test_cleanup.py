"""Contract tests for the cleanup coordinator (BE-07).

The coordinator owns the temporary-object lifecycle safety net on the
application side (arch 8, arch 12, arch 23): for every candidate task id
supplied by the caller it deletes the record's R2 objects **by the
absolute deadline** (``expires_at``), then removes the Redis record —
idempotently, tolerating already-missing objects and already-gone
records, failing safely on provider/store degradation, and emitting
telemetry with counts and timing only (DEC-166).

Semantics under test:

* ``run(task_ids)`` sweeps explicit candidates (direct API);
* ``run_expired(limit)`` drains the store's expired keyspace with bounded
  discovery passes (BE-04 ``list_expired``); pages are SCAN-based — no
  snapshot, keys may be revisited — so progress comes from deletion, and
  the drain terminates on an empty page;
* restart recovery: a crashed sweep leaves no in-memory state; a fresh
  coordinator re-discovers and completes pending deletions;
* logs carry counts, timing, and exception class names only — never
  task ids, object keys, bucket names, or exception messages.

Expired records are set up the way they exist in production: the store
only *creates* records with a future deadline (TTL = remaining lifetime,
BE-04), so an expired-but-not-yet-reaped record is modeled by advancing
the injectable clock past ``expires_at`` — fakeredis reaps keys on the
real clock, mirroring Redis's lazy/active expiry window.
"""

from __future__ import annotations

import io
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import fakeredis
import pytest

from app.config import Settings
from app.queue.store import (
    CorruptRecordError,
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.tasks.cleanup import (
    CleanupCoordinator,
    CleanupError,
    CleanupOutcome,
    CleanupRun,
    CleanupUnavailableError,
    TaskCleanupResult,
)
from app.tasks.state_machine import JobState
from app.utils.logging import PapyrJsonHandler
from app.utils.r2 import R2Client

T0 = datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC)

_FIXTURE_KEY_A = "tmp/2026-08-03/" + "a" * 32 + ".pdf"
_FIXTURE_KEY_B = "tmp/2026-08-03/" + "b" * 32 + ".pdf"
_SENSITIVE_TASK_ID = "task-with-sensitive-identifier"
_SENSITIVE_OBJECT = "tmp/2026-08-03/" + "c" * 32 + ".pdf"


class FakeClock:
    """Injectable coordinator clock: fixed start, explicit advances."""

    def __init__(self, start: datetime) -> None:
        self._now = start

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)

    def __call__(self) -> datetime:
        return self._now


def make_settings(*, retention_seconds: int = 3600) -> Settings:
    return Settings(
        r2_account_id="test",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test",
        allowed_origins=("http://localhost:3000",),
        retention_seconds=retention_seconds,
    )


def make_record(
    clock: FakeClock,
    *,
    task_id: str | None = None,
    expires_in: int = 3600,
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    """A store-valid record with a future deadline (``create`` rejects
    past expiry, BE-04); ``expires_in`` is relative to the clock."""
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=expires_in),
        objects=objects,
    )


def create_expired_record(
    store: TaskStore,
    clock: FakeClock,
    *,
    task_id: str | None = None,
    objects: tuple[str, ...] = (),
    expires_in: int = 3600,
) -> TaskRecord:
    """Create a record whose deadline has passed on the injectable clock.

    The key itself survives (fakeredis reaps on the real clock), exactly
    like a Redis key inside the lazy-expiry window after its TTL elapsed.
    """
    record = make_record(clock, task_id=task_id, expires_in=expires_in, objects=objects)
    store.create(record)
    clock.advance(expires_in)
    return record


@dataclass
class _FakeR2:
    """Minimal object-deleter double recording calls and injected failures."""

    delete_error: Exception | None = None
    clock: FakeClock | None = None
    deleted_keys: list[str] = field(default_factory=list)

    def delete_object(self, key: str) -> bool:
        self.deleted_keys.append(key)
        if self.clock is not None:
            self.clock.advance(5)
        if self.delete_error is not None:
            raise self.delete_error
        # Mirrors BE-03's idempotent contract: a missing object counts as
        # success, so the coordinator never distinguishes the two.
        return True


class _FailingStore:
    """Raises the configured exception from every store-facing operation."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def get(self, task_id: str) -> TaskRecord:
        raise self._error

    def delete(self, task_id: str) -> bool:
        raise self._error

    def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
        raise self._error


class _DeleteFailingStore:
    """Reads through to a real store but fails record deletion."""

    def __init__(self, inner: TaskStore) -> None:
        self._inner = inner

    def get(self, task_id: str) -> TaskRecord:
        return self._inner.get(task_id)

    def delete(self, task_id: str) -> bool:
        raise StoreUnavailableError()

    def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
        return self._inner.list_expired(now, limit=limit)


class _RecordingStore:
    """Wraps a real store and appends every store operation to *log*."""

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


class _RecordingR2:
    """Appends every object deletion to the shared operation log."""

    def __init__(self, log: list[str]) -> None:
        self._log = log

    def delete_object(self, key: str) -> bool:
        self._log.append(f"r2.delete:{key}")
        return True


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(T0)


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def store(server: fakeredis.FakeServer, clock: FakeClock) -> TaskStore:
    return TaskStore(
        make_settings(),
        client=cast(Any, fakeredis.FakeRedis(server=server)),
        clock=clock,
    )


def _capture_cleanup_logs() -> tuple[io.StringIO, PapyrJsonHandler, int]:
    stream = io.StringIO()
    handler = PapyrJsonHandler(stream=stream)
    logger = logging.getLogger("app.tasks.cleanup")
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return stream, handler, previous


# --- per-task cleanup --------------------------------------------------------


def test_cleanup_task_deletes_objects_then_removes_record(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A, _FIXTURE_KEY_B))

    result = coordinator.cleanup_task(record.task_id)

    assert result.outcome is CleanupOutcome.CLEANED
    assert r2.deleted_keys == [_FIXTURE_KEY_A, _FIXTURE_KEY_B]
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)


def test_cleanup_task_deletes_objects_before_the_record(store: TaskStore, clock: FakeClock) -> None:
    log: list[str] = []
    coordinator = CleanupCoordinator(_RecordingStore(store, log), _RecordingR2(log), clock=clock)
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))

    coordinator.cleanup_task(record.task_id)

    assert log.index("r2.delete:" + _FIXTURE_KEY_A) < log.index("store.delete:" + record.task_id)


def test_cleanup_task_is_idempotent(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))

    first = coordinator.cleanup_task(record.task_id)
    second = coordinator.cleanup_task(record.task_id)

    assert first.outcome is CleanupOutcome.CLEANED
    assert second.outcome is CleanupOutcome.ALREADY_CLEAN
    # The second pass never re-attempts object deletion for a gone record.
    assert r2.deleted_keys == [_FIXTURE_KEY_A]


def test_cleanup_task_removes_record_without_objects(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = create_expired_record(store, clock)

    result = coordinator.cleanup_task(record.task_id)

    assert result.outcome is CleanupOutcome.CLEANED
    assert r2.deleted_keys == []
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)


def test_cleanup_task_tolerates_missing_objects(store: TaskStore, clock: FakeClock) -> None:
    # The object is referenced by the record but was never uploaded (or was
    # already deleted by a previous sweep); BE-03's delete_object counts a
    # missing object as success, and the coordinator treats that as cleaned.
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A, _FIXTURE_KEY_B))

    result = coordinator.cleanup_task(record.task_id)

    assert result.outcome is CleanupOutcome.CLEANED
    assert r2.deleted_keys == [_FIXTURE_KEY_A, _FIXTURE_KEY_B]
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)


def test_cleanup_task_already_gone_record_counts_as_clean(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)

    result = coordinator.cleanup_task("never-created")

    assert result.outcome is CleanupOutcome.ALREADY_CLEAN
    assert r2.deleted_keys == []


def test_cleanup_task_skips_record_before_the_deadline(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = make_record(clock, expires_in=3600, objects=(_FIXTURE_KEY_A,))
    store.create(record)
    clock.advance(100)

    result = coordinator.cleanup_task(record.task_id)

    # arch 9.1: objects stay downloadable until the absolute expiry; a live
    # job's objects are never deleted early.
    assert result.outcome is CleanupOutcome.SKIPPED
    assert r2.deleted_keys == []
    assert store.get(record.task_id).objects == (_FIXTURE_KEY_A,)


def test_cleanup_task_cleans_at_the_deadline(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = make_record(clock, expires_in=3600, objects=(_FIXTURE_KEY_A,))
    store.create(record)
    clock.advance(3600)

    result = coordinator.cleanup_task(record.task_id)

    assert result.outcome is CleanupOutcome.CLEANED
    assert r2.deleted_keys == [_FIXTURE_KEY_A]


def test_cleanup_task_preserves_record_when_object_delete_fails(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = _FakeR2(delete_error=RuntimeError("simulated r2 outage"))
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))

    with pytest.raises(CleanupUnavailableError) as excinfo:
        coordinator.cleanup_task(record.task_id)

    # Fail closed: the record is preserved (its TTL will still expire it),
    # so a later sweep can retry the deletion.
    assert r2.deleted_keys == [_FIXTURE_KEY_A]
    assert store.get(record.task_id).objects == (_FIXTURE_KEY_A,)
    assert isinstance(excinfo.value.__cause__, RuntimeError)


def test_cleanup_task_fails_safely_when_store_unavailable(clock: FakeClock) -> None:
    r2 = _FakeR2()
    cause = StoreUnavailableError()
    coordinator = CleanupCoordinator(_FailingStore(cause), r2, clock=clock)

    with pytest.raises(CleanupUnavailableError) as excinfo:
        coordinator.cleanup_task("any-task")

    assert excinfo.value.__cause__ is cause
    assert r2.deleted_keys == []


def test_cleanup_task_fails_safely_on_corrupt_record(clock: FakeClock) -> None:
    r2 = _FakeR2()
    cause = CorruptRecordError()
    coordinator = CleanupCoordinator(_FailingStore(cause), r2, clock=clock)

    with pytest.raises(CleanupUnavailableError) as excinfo:
        coordinator.cleanup_task("any-task")

    assert excinfo.value.__cause__ is cause
    assert r2.deleted_keys == []


def test_cleanup_task_object_deletion_done_then_record_delete_failure_is_safe(
    store: TaskStore, clock: FakeClock
) -> None:
    # Objects are already gone when the record deletion fails; the stale
    # record still dies by TTL at the deadline — a safe outcome.
    r2 = _FakeR2()
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))
    coordinator = CleanupCoordinator(_DeleteFailingStore(store), r2, clock=clock)

    with pytest.raises(CleanupUnavailableError):
        coordinator.cleanup_task(record.task_id)

    assert r2.deleted_keys == [_FIXTURE_KEY_A]
    assert store.get(record.task_id).objects == (_FIXTURE_KEY_A,)


# --- batch run ---------------------------------------------------------------


def test_run_aggregates_counts(store: TaskStore, clock: FakeClock) -> None:
    coordinator = CleanupCoordinator(store, _FakeR2(), clock=clock)
    create_expired_record(store, clock, task_id="to-clean", objects=(_FIXTURE_KEY_A,))
    live = make_record(clock, task_id="still-live", expires_in=3600)
    store.create(live)

    run = coordinator.run(["to-clean", "never-created", "still-live"])

    assert run.cleaned == 1
    assert run.already_clean == 1
    assert run.skipped == 1
    assert run.started_at == T0 + timedelta(seconds=3600)
    assert run.completed_at == run.started_at


def test_run_empty_batch(store: TaskStore, clock: FakeClock) -> None:
    run = CleanupCoordinator(store, _FakeR2(), clock=clock).run([])
    assert run.cleaned == 0
    assert run.already_clean == 0
    assert run.skipped == 0


def test_run_measures_elapsed_time(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2(clock=clock)  # each object deletion advances the clock 5 s
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    first = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))
    second = create_expired_record(store, clock, objects=(_FIXTURE_KEY_B,))

    run = coordinator.run([first.task_id, second.task_id])

    assert run.elapsed_seconds == 10.0
    assert run.cleaned == 2


def test_run_fails_fast_on_degradation(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2(delete_error=RuntimeError("simulated r2 outage"))
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    first = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))
    second = create_expired_record(store, clock, objects=(_FIXTURE_KEY_B,))

    with pytest.raises(CleanupUnavailableError):
        coordinator.run([first.task_id, second.task_id])

    # Fail fast: the failure aborts the sweep, so the later candidate is
    # left for the next run (its record still exists for retry).
    assert r2.deleted_keys == [_FIXTURE_KEY_A]
    assert store.get(first.task_id).objects == (_FIXTURE_KEY_A,)
    assert store.get(second.task_id).objects == (_FIXTURE_KEY_B,)


def test_run_failure_message_has_counts_only(store: TaskStore, clock: FakeClock) -> None:
    coordinator = CleanupCoordinator(
        store, _FakeR2(delete_error=RuntimeError("simulated r2 outage")), clock=clock
    )
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))

    with pytest.raises(CleanupUnavailableError) as excinfo:
        coordinator.run([record.task_id])

    message = str(excinfo.value)
    assert record.task_id not in message
    assert _FIXTURE_KEY_A not in message
    assert "simulated r2 outage" not in message
    assert "1" in message  # the failed count is the only identifier


# --- discovery drain (run_expired) ------------------------------------------


def test_run_expired_drains_all_expired_records(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2()
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    records = [create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,)) for _ in range(5)]
    live = make_record(clock, expires_in=3600, objects=(_FIXTURE_KEY_B,))
    store.create(live)

    run = coordinator.run_expired(limit=2)

    assert run.cleaned == 5
    assert run.already_clean == 0
    assert run.skipped == 0
    assert r2.deleted_keys == [_FIXTURE_KEY_A] * 5
    for record in records:
        with pytest.raises(TaskNotFoundError):
            store.get(record.task_id)
    assert store.get(live.task_id).objects == (_FIXTURE_KEY_B,)


def test_run_expired_uses_bounded_pages(store: TaskStore, clock: FakeClock) -> None:
    calls: list[int] = []

    class _SpyStore:
        def get(self, task_id: str) -> TaskRecord:
            return store.get(task_id)

        def delete(self, task_id: str) -> bool:
            return store.delete(task_id)

        def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
            calls.append(limit)
            return store.list_expired(now, limit=limit)

    for _ in range(5):
        create_expired_record(store, clock)

    run = CleanupCoordinator(_SpyStore(), _FakeR2(), clock=clock).run_expired(limit=2)

    assert run.cleaned == 5
    assert calls
    assert all(call == 2 for call in calls)


def test_run_expired_makes_progress_with_revisited_pages(
    store: TaskStore, clock: FakeClock
) -> None:
    # SCAN gives no snapshot: a page may hand the coordinator records it
    # already cleaned, so the drain must not assume disjoint pages. Every
    # returned page is delivered twice (fresh, then stale) to force
    # revisits; progress comes from deletion, revisits count as
    # already_clean, and the drain still terminates on an empty page.
    for _ in range(3):
        create_expired_record(store, clock)

    class _RevisitingStore:
        def __init__(self) -> None:
            self._cached: list[TaskRecord] | None = None

        def get(self, task_id: str) -> TaskRecord:
            return store.get(task_id)

        def delete(self, task_id: str) -> bool:
            return store.delete(task_id)

        def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
            if self._cached is not None:
                cached, self._cached = self._cached, None
                return cached
            page = store.list_expired(now, limit=limit)
            if page:
                self._cached = page
            return page

    run = CleanupCoordinator(_RevisitingStore(), _FakeR2(), clock=clock).run_expired(limit=2)

    assert run.cleaned == 3
    assert run.already_clean == 3
    assert store.list_expired(clock()) == []


def test_run_expired_restart_recovery_completes_pending_deletions(
    store: TaskStore, clock: FakeClock
) -> None:
    # A transient outage mid-drain aborts the sweep; a fresh coordinator
    # over the same store — the keyspace is the only state — re-discovers
    # the survivors and completes every pending deletion (DEC-166).
    class _FlakyR2:
        def __init__(self) -> None:
            self.failed = False
            self.deleted_keys: list[str] = []

        def delete_object(self, key: str) -> bool:
            if not self.failed:
                self.failed = True
                raise RuntimeError("transient r2 outage")
            self.deleted_keys.append(key)
            return True

    first = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))
    second = create_expired_record(store, clock, objects=(_FIXTURE_KEY_B,))

    flaky = _FlakyR2()
    with pytest.raises(CleanupUnavailableError):
        CleanupCoordinator(store, flaky, clock=clock).run_expired()
    assert len(store.list_expired(clock())) == 2  # nothing was lost

    healthy = _FakeR2()
    resumed = CleanupCoordinator(store, healthy, clock=clock).run_expired()

    assert resumed.cleaned == 2
    assert set(healthy.deleted_keys) == {_FIXTURE_KEY_A, _FIXTURE_KEY_B}
    assert store.list_expired(clock()) == []
    for task_id in (first.task_id, second.task_id):
        with pytest.raises(TaskNotFoundError):
            store.get(task_id)


def test_run_expired_fails_closed_on_discovery_failure(clock: FakeClock) -> None:
    r2 = _FakeR2()
    cause = StoreUnavailableError()
    coordinator = CleanupCoordinator(_FailingStore(cause), r2, clock=clock)

    with pytest.raises(CleanupUnavailableError) as excinfo:
        coordinator.run_expired()

    assert excinfo.value.__cause__ is cause
    assert r2.deleted_keys == []


def test_run_expired_empty_store(store: TaskStore, clock: FakeClock) -> None:
    run = CleanupCoordinator(store, _FakeR2(), clock=clock).run_expired()
    assert run.cleaned == 0
    assert run.already_clean == 0
    assert run.skipped == 0


def test_run_expired_deletes_objects_before_records(store: TaskStore, clock: FakeClock) -> None:
    log: list[str] = []
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))
    coordinator = CleanupCoordinator(_RecordingStore(store, log), _RecordingR2(log), clock=clock)

    coordinator.run_expired()

    assert log.index("r2.delete:" + _FIXTURE_KEY_A) < log.index("store.delete:" + record.task_id)


def test_run_expired_success_telemetry_counts_and_timing_only(
    store: TaskStore, clock: FakeClock
) -> None:
    r2 = _FakeR2(clock=clock)
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    create_expired_record(store, clock, task_id=_SENSITIVE_TASK_ID, objects=(_SENSITIVE_OBJECT,))

    stream, handler, previous = _capture_cleanup_logs()
    logger = logging.getLogger("app.tasks.cleanup")
    try:
        run = coordinator.run_expired()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)

    assert run.cleaned == 1
    output = stream.getvalue()
    assert "cleanup run ok" in output
    assert '"cleaned":1' in output
    assert '"elapsed_ms":5000' in output
    for identifier in (_SENSITIVE_TASK_ID, _SENSITIVE_OBJECT, "test"):
        assert identifier not in output


# --- telemetry privacy (DEC-166, DEC-175) ------------------------------------


def test_run_success_telemetry_counts_and_timing_only(store: TaskStore, clock: FakeClock) -> None:
    r2 = _FakeR2(clock=clock)
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    create_expired_record(store, clock, task_id=_SENSITIVE_TASK_ID, objects=(_SENSITIVE_OBJECT,))
    live = make_record(clock, expires_in=3600)
    store.create(live)

    stream, handler, previous = _capture_cleanup_logs()
    logger = logging.getLogger("app.tasks.cleanup")
    try:
        run = coordinator.run([_SENSITIVE_TASK_ID, "never-created", live.task_id])
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)

    assert run.cleaned == 1
    output = stream.getvalue()
    assert "cleanup run ok" in output
    assert '"cleaned":1' in output
    assert '"already_clean":1' in output
    assert '"skipped":1' in output
    assert '"elapsed_ms":5000' in output
    for identifier in (
        _SENSITIVE_TASK_ID,
        "never-created",
        live.task_id,
        _SENSITIVE_OBJECT,
        "test",
    ):
        assert identifier not in output


def test_run_failure_telemetry_has_no_identifiers(store: TaskStore, clock: FakeClock) -> None:
    coordinator = CleanupCoordinator(
        store, _FakeR2(delete_error=RuntimeError("simulated r2 outage")), clock=clock
    )
    create_expired_record(store, clock, task_id=_SENSITIVE_TASK_ID, objects=(_SENSITIVE_OBJECT,))

    stream, handler, previous = _capture_cleanup_logs()
    logger = logging.getLogger("app.tasks.cleanup")
    try:
        with pytest.raises(CleanupUnavailableError):
            coordinator.run([_SENSITIVE_TASK_ID])
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)

    output = stream.getvalue()
    assert "cleanup run failed" in output
    assert '"error":"CleanupUnavailableError"' in output
    for identifier in (_SENSITIVE_TASK_ID, _SENSITIVE_OBJECT, "simulated r2 outage", "test"):
        assert identifier not in output


# --- typed surface and error taxonomy ----------------------------------------


def test_coordinator_consumes_real_store_and_r2_client(store: TaskStore, clock: FakeClock) -> None:
    class _S3Double:
        def __init__(self) -> None:
            self.deleted: list[str] = []

        def put_object(self, **kwargs: object) -> dict[str, object]:
            return {}

        def delete_object(self, **kwargs: object) -> dict[str, object]:
            key = kwargs.get("Key")
            if isinstance(key, str):
                self.deleted.append(key)
            return {}

        def generate_presigned_url(self, *args: object, **kwargs: object) -> str:
            return "https://example.invalid/presigned"

    s3 = _S3Double()
    r2 = R2Client(make_settings(), client=s3)
    coordinator = CleanupCoordinator(store, r2, clock=clock)
    record = create_expired_record(store, clock, objects=(_FIXTURE_KEY_A,))
    drained = create_expired_record(store, clock, objects=(_FIXTURE_KEY_B,))

    result = coordinator.cleanup_task(record.task_id)
    run = coordinator.run_expired()

    assert result.outcome is CleanupOutcome.CLEANED
    assert run.cleaned == 1
    assert s3.deleted == [_FIXTURE_KEY_A, _FIXTURE_KEY_B]
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)
    with pytest.raises(TaskNotFoundError):
        store.get(drained.task_id)


def test_cleanup_errors_share_typed_base() -> None:
    assert issubclass(CleanupUnavailableError, CleanupError)
    assert issubclass(CleanupError, RuntimeError)
    assert CleanupOutcome.CLEANED.value == "cleaned"
    assert CleanupOutcome.ALREADY_CLEAN.value == "already_clean"
    assert CleanupOutcome.SKIPPED.value == "skipped"
    assert CleanupRun(0, 0, 0, T0, T0).elapsed_seconds == 0.0


def test_cleanup_task_result_is_typed_and_frozen(clock: FakeClock) -> None:
    result = TaskCleanupResult(CleanupOutcome.SKIPPED)
    assert result.outcome is CleanupOutcome.SKIPPED
    with pytest.raises(AttributeError):
        cast(Any, result).outcome = CleanupOutcome.CLEANED  # frozen dataclass
