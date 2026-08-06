"""Contract tests for the Redis-backed minimal task store (BE-04).

Semantics are exercised against ``fakeredis`` (pinned 2.37.0), which
implements the Redis command surface this store consumes: hashes, TTL
expiry against the wall clock, and WATCH/MULTI/EXEC compare-and-swap with
``WatchError`` raised on abort (redis-py 8.x raises it from
``Pipeline.execute``). Two clients sharing one ``FakeServer`` simulate
concurrent writers.

Real-Redis gaps (reserved for the Phase 3 gate-exit integration wave, not
claimed here): cross-process WATCH semantics under load, persistence and
restart behavior, the exact OOM ``ResponseError`` wording, and TTL clock
behavior under real network latency.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Iterator, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import fakeredis
import pytest
from pydantic import ValidationError
from redis.exceptions import ConnectionError, ResponseError

from app.config import Settings
from app.queue.store import (
    CasCancelMechanism,
    CorruptRecordError,
    InvalidRecordError,
    LuaCancelMechanism,
    LuaRedisLike,
    PipelineLike,
    ProhibitedFieldError,
    RedisLike,
    StoreUnavailableError,
    TaskConflictError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.schemas.job import ErrorSummary, Progress, ResultSummary
from app.tasks.state_machine import JobEvent, JobState

T0 = datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC)

# Exact hash field-name vocabulary the store persists (locked by tests so
# BE-05/BE-06/BE-07/BE-10 can rely on the shape; DEC-174 minimal metadata).
REQUIRED_FIELDS = frozenset(
    {
        "task_id",
        "state",
        "tool",
        "created_at",
        "accepted_at",
        "updated_at",
        "expires_at",
    }
)
OPTIONAL_FIELDS = frozenset(
    {
        "queued_at",
        "started_at",
        "completed_at",
        "progress",
        "result",
        "error",
        "objects",
    }
)
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

_TASK_KEY = "task:{task_id}"
_FIXTURE_OBJECT = "tmp/2026-08-03/0123456789abcdef0123456789abcdef.pdf"


class FakeClock:
    """Injectable store clock: fixed start, explicit advances."""

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
    state: JobState = JobState.QUEUED,
    expires_in: int = 3600,
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=state,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=expires_in),
    )


def _construct_with_foreign_fields(record: TaskRecord, **fields: object) -> None:
    """Cross the typed boundary so the dataclass must refuse extra kwargs.

    ``TaskRecord`` is a frozen dataclass: any field outside its declared
    vocabulary raises ``TypeError`` at construction. The cast is the single
    justified crossing point (repo pattern, cf. ``test_state_machine``).
    """
    TaskRecord(
        task_id=record.task_id,
        state=record.state,
        tool=record.tool,
        created_at=record.created_at,
        accepted_at=record.accepted_at,
        updated_at=record.updated_at,
        expires_at=record.expires_at,
        **cast(dict[str, Any], fields),
    )


class _FailingClient:
    """Raises the configured exception from every store-facing operation."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def hgetall(self, name: str) -> dict[bytes, bytes]:
        raise self._error

    def pipeline(self, transaction: bool = True) -> Any:
        raise self._error

    def ttl(self, name: str) -> int:
        raise self._error

    def delete(self, name: str) -> int:
        raise self._error

    def scan_iter(self, match: str | None = None, count: int = 100) -> Iterator[bytes]:
        raise self._error

    def ping(self) -> bool:
        raise self._error

    def close(self) -> None:
        raise self._error


class _AbortingPipeline:
    """Pipeline whose execute first mutates the watched key, forcing WatchError."""

    def __init__(self, inner: PipelineLike, other: fakeredis.FakeRedis, task_id: str) -> None:
        self._inner = inner
        self._other = other
        self._task_id = task_id

    def watch(self, name: str) -> None:
        self._inner.watch(name)

    def hgetall(self, name: str) -> dict[bytes, bytes]:
        return self._inner.hgetall(name)

    def multi(self) -> None:
        self._inner.multi()

    def hset(self, name: str, mapping: Mapping[str, str]) -> int:
        return self._inner.hset(name, mapping=mapping)

    def hdel(self, name: str, *fields: str) -> int:
        return self._inner.hdel(name, *fields)

    def expire(self, name: str, time: int) -> bool:
        return self._inner.expire(name, time)

    def reset(self) -> None:
        self._inner.reset()

    def execute(self) -> list[object]:
        # A concurrent writer mutates the watched key with a harmless,
        # record-valid field; the store must detect the change and abort.
        self._other.hset(
            _TASK_KEY.format(task_id=self._task_id),
            "progress",
            '{"unit": "engine_progress", "value": 1, "total": 10}',
        )
        return self._inner.execute()


class _AbortClient:
    """Client whose pipeline aborts the WATCH on execute (concurrent writer)."""

    def __init__(self, inner: fakeredis.FakeRedis, task_id: str) -> None:
        self._inner = inner
        self._task_id = task_id

    def hgetall(self, name: str) -> dict[bytes, bytes]:
        # decode_responses=False in the store client, so fakeredis returns
        # bytes at runtime; the stubs union bytes|str, hence the cast.
        return cast(dict[bytes, bytes], self._inner.hgetall(name))

    def pipeline(self, transaction: bool = True) -> _AbortingPipeline:
        inner = cast(PipelineLike, self._inner.pipeline(transaction=transaction))
        return _AbortingPipeline(inner, self._inner, self._task_id)

    def ttl(self, name: str) -> int:
        return self._inner.ttl(name)

    def delete(self, name: str) -> int:
        return self._inner.delete(name)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(T0)


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def raw_client(server: fakeredis.FakeServer) -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(server=server)


@pytest.fixture
def client_a(server: fakeredis.FakeServer) -> RedisLike:
    return cast(RedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def client_b(server: fakeredis.FakeServer) -> RedisLike:
    return cast(RedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def store(client_a: RedisLike, clock: FakeClock) -> TaskStore:
    return TaskStore(make_settings(), client=client_a, clock=clock)


@pytest.fixture
def short_ttl_store(client_a: RedisLike, clock: FakeClock) -> TaskStore:
    return TaskStore(make_settings(retention_seconds=60), client=client_a, clock=clock)


# --- Create / get round-trips -----------------------------------------------


def test_create_and_get_round_trips_all_fields(store: TaskStore, clock: FakeClock) -> None:
    progress = Progress(unit="engine_progress", value=5, total=10)
    record = replace(
        make_record(clock, task_id="full"),
        queued_at=clock(),
        progress=progress,
        objects=(_FIXTURE_OBJECT,),
    )
    created = store.create(record)
    assert created == record
    assert created.queued_at == record.created_at
    fetched = store.get(record.task_id)
    assert fetched == record
    assert fetched.progress == progress
    assert fetched.objects == (_FIXTURE_OBJECT,)
    assert fetched.state is JobState.QUEUED


def test_minimal_record_round_trip(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    created = store.create(record)
    fetched = store.get(record.task_id)
    assert fetched == created
    assert fetched.queued_at == record.created_at
    assert fetched.progress is None
    assert fetched.result is None
    assert fetched.error is None
    assert fetched.objects == ()


def test_get_unknown_id_raises_not_found(store: TaskStore) -> None:
    with pytest.raises(TaskNotFoundError):
        store.get("does-not-exist")


def test_create_duplicate_id_conflicts_and_preserves_original(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock, task_id="dup")
    created = store.create(record)
    clone = make_record(clock, task_id="dup")
    with pytest.raises(TaskConflictError):
        store.create(clone)
    assert store.get("dup") == created


# --- Create validation ------------------------------------------------------


def test_create_rejects_non_queued_state(store: TaskStore, clock: FakeClock) -> None:
    with pytest.raises(InvalidRecordError):
        store.create(make_record(clock, state=JobState.PROCESSING))


def test_create_rejects_past_expiry(store: TaskStore, clock: FakeClock) -> None:
    with pytest.raises(InvalidRecordError):
        store.create(make_record(clock, expires_in=-5))


def test_create_rejects_expiry_beyond_retention(
    short_ttl_store: TaskStore, clock: FakeClock
) -> None:
    with pytest.raises(InvalidRecordError):
        short_ttl_store.create(make_record(clock, expires_in=61))


def test_create_rejects_naive_datetime(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    naive = TaskRecord(
        task_id=record.task_id,
        state=record.state,
        tool=record.tool,
        created_at=datetime(2026, 8, 3, 12, 0, 0),
        accepted_at=record.accepted_at,
        updated_at=record.updated_at,
        expires_at=record.expires_at,
    )
    with pytest.raises(InvalidRecordError):
        store.create(naive)


def test_create_rejects_started_or_completed_on_queued_record(
    store: TaskStore, clock: FakeClock
) -> None:
    with pytest.raises(InvalidRecordError):
        store.create(replace(make_record(clock), started_at=clock()))
    with pytest.raises(InvalidRecordError):
        store.create(replace(make_record(clock), completed_at=clock()))


def test_create_rejects_result_or_error_on_queued_record(
    store: TaskStore, clock: FakeClock
) -> None:
    result = ResultSummary(output_count=1, total_bytes=1024)
    with pytest.raises(InvalidRecordError):
        store.create(replace(make_record(clock), result=result))
    error = ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )
    with pytest.raises(InvalidRecordError):
        store.create(replace(make_record(clock), error=error))


def test_create_rejects_inconsistent_timestamp_order(store: TaskStore, clock: FakeClock) -> None:
    now = clock()
    with pytest.raises(InvalidRecordError):
        store.create(
            TaskRecord(
                task_id="bad-order",
                state=JobState.QUEUED,
                tool="merge-pdf",
                created_at=now,
                accepted_at=now - timedelta(seconds=1),
                updated_at=now,
                expires_at=now + timedelta(seconds=3600),
            )
        )


def test_create_rejects_empty_task_id(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    with pytest.raises(InvalidRecordError):
        store.create(
            TaskRecord(
                task_id="",
                state=record.state,
                tool=record.tool,
                created_at=record.created_at,
                accepted_at=record.accepted_at,
                updated_at=record.updated_at,
                expires_at=record.expires_at,
            )
        )


# --- TTL / expiry -----------------------------------------------------------


def test_create_sets_ttl_to_remaining_lifetime(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock, expires_in=3600)
    store.create(record)
    assert store.ttl_seconds(record.task_id) == 3600


def test_ttl_never_exceeds_retention(short_ttl_store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock, expires_in=60)
    short_ttl_store.create(record)
    assert short_ttl_store.ttl_seconds(record.task_id) == 60


def test_transition_recomputes_ttl_from_remaining_lifetime(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock, expires_in=3600)
    store.create(record)
    clock.advance(300)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    assert store.ttl_seconds(record.task_id) == 3300


def test_record_expires_at_recorded_ttl(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock, expires_in=2)
    store.create(record)
    assert store.ttl_seconds(record.task_id) == 2
    time.sleep(2.4)
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)
    with pytest.raises(TaskNotFoundError):
        store.ttl_seconds(record.task_id)


def test_ttl_seconds_missing_key_raises_not_found(store: TaskStore) -> None:
    with pytest.raises(TaskNotFoundError):
        store.ttl_seconds("missing")


def test_key_without_ttl_is_reported_as_corrupt(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock)
    store.create(record)
    raw_client.persist(_TASK_KEY.format(task_id=record.task_id))
    with pytest.raises(CorruptRecordError):
        store.ttl_seconds(record.task_id)


# --- Transitions (state-machine legality + atomic CAS) ----------------------


def test_worker_claimed_sets_started_at_and_advances_updated_at(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock)
    store.create(record)
    clock.advance(10)
    claimed = store.transition_state(
        record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
    )
    assert claimed.state is JobState.PROCESSING
    assert claimed.started_at == clock()
    assert claimed.updated_at == clock()
    assert claimed.completed_at is None
    assert claimed.progress is None


def test_result_uploaded_sets_result_and_completed_at(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    result = ResultSummary(output_count=1, total_bytes=1024)
    clock.advance(10)
    done = store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=result, objects=(_FIXTURE_OBJECT,)),
    )
    assert done.state is JobState.DONE
    assert done.result == result
    assert done.completed_at == clock()
    assert done.error is None


@pytest.mark.parametrize(
    "event",
    [JobEvent.ENGINE_ERROR, JobEvent.TIMEOUT, JobEvent.SAFETY_SHUTDOWN],
)
def test_failure_events_transition_to_failed_with_error(
    store: TaskStore, clock: FakeClock, event: JobEvent
) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    error = ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )
    failed = store.transition_state(
        record.task_id,
        event,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(error=error),
    )
    assert failed.state is JobState.FAILED
    assert failed.error == error
    assert failed.completed_at == clock()
    assert failed.result is None


def test_user_cancelled_while_queued(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    clock.advance(10)
    cancelled = store.transition_state(
        record.task_id, JobEvent.USER_CANCELLED, expected_state=JobState.QUEUED
    )
    assert cancelled.state is JobState.CANCELLED
    assert cancelled.completed_at is None
    assert cancelled.error is None
    assert cancelled.result is None


def test_guarded_transition_raises_conflict(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    with pytest.raises(TaskConflictError):
        store.transition_state(
            record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.PROCESSING
        )
    with pytest.raises(TaskConflictError):
        store.transition_state(
            record.task_id, JobEvent.USER_CANCELLED, expected_state=JobState.PROCESSING
        )


def test_deadline_reached_is_not_a_persisted_transition(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    with pytest.raises(TaskConflictError):
        store.transition_state(
            record.task_id, JobEvent.DEADLINE_REACHED, expected_state=JobState.QUEUED
        )
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    result = ResultSummary(output_count=1, total_bytes=1024)
    store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=result, objects=(_FIXTURE_OBJECT,)),
    )
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id, JobEvent.DEADLINE_REACHED, expected_state=JobState.DONE
        )


def test_result_required_for_done(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id, JobEvent.RESULT_UPLOADED, expected_state=JobState.PROCESSING
        )


def test_error_required_for_failed(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id, JobEvent.ENGINE_ERROR, expected_state=JobState.PROCESSING
        )


def test_result_and_error_forbidden_on_non_terminal_targets(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock)
    store.create(record)
    result = ResultSummary(output_count=1, total_bytes=1024)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id,
            JobEvent.WORKER_CLAIMED,
            expected_state=JobState.QUEUED,
            payload=TransitionPayload(result=result),
        )
    error = ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id,
            JobEvent.USER_CANCELLED,
            expected_state=JobState.QUEUED,
            payload=TransitionPayload(error=error),
        )


def test_transition_on_unknown_id_raises_not_found(store: TaskStore) -> None:
    with pytest.raises(TaskNotFoundError):
        store.transition_state("missing", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)


def test_transition_on_logically_expired_record_raises_not_found(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock, expires_in=3600)
    store.create(record)
    clock.advance(4000)
    with pytest.raises(TaskNotFoundError):
        store.transition_state(
            record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
        )


def test_stale_expected_state_conflicts_atomically(
    store: TaskStore, server: fakeredis.FakeServer, clock: FakeClock
) -> None:
    other = TaskStore(
        make_settings(),
        client=cast(RedisLike, fakeredis.FakeRedis(server=server)),
        clock=clock,
    )
    record = make_record(clock, task_id="cas")
    store.create(record)
    store.transition_state("cas", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    with pytest.raises(TaskConflictError):
        other.transition_state("cas", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    assert store.get("cas").state is JobState.PROCESSING


def test_stale_expected_updated_at_conflicts(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    clock.advance(5)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    with pytest.raises(TaskConflictError):
        store.update_progress(
            record.task_id,
            Progress(unit="engine_progress", value=1, total=10),
            expected_state=JobState.PROCESSING,
            expected_updated_at=record.updated_at,
        )


def test_concurrent_write_aborts_with_conflict(
    store: TaskStore, client_b: RedisLike, clock: FakeClock
) -> None:
    record = make_record(clock, task_id="concurrent")
    store.create(record)
    aborter = _AbortClient(cast(fakeredis.FakeRedis, client_b), "concurrent")
    racing = TaskStore(make_settings(), client=cast(RedisLike, aborter), clock=clock)
    with pytest.raises(TaskConflictError):
        racing.transition_state(
            "concurrent", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
        )
    assert store.get("concurrent").state is JobState.QUEUED


# --- update_progress --------------------------------------------------------


def test_update_progress_sets_and_reads_back(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    progress = Progress(unit="engine_progress", value=7, total=10)
    clock.advance(10)
    updated = store.update_progress(record.task_id, progress, expected_state=JobState.PROCESSING)
    assert updated.progress == progress
    assert updated.updated_at == clock()
    assert store.get(record.task_id).progress == progress


def test_update_progress_clears_with_none(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    store.update_progress(
        record.task_id,
        Progress(unit="engine_progress", value=3, total=10),
        expected_state=JobState.PROCESSING,
    )
    cleared = store.update_progress(record.task_id, None, expected_state=JobState.PROCESSING)
    assert cleared.progress is None
    assert store.get(record.task_id).progress is None


def test_update_progress_stale_state_conflicts(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    with pytest.raises(TaskConflictError):
        store.update_progress(
            record.task_id,
            Progress(unit="engine_progress", value=1, total=10),
            expected_state=JobState.PROCESSING,
        )


def test_update_progress_unknown_id_raises_not_found(store: TaskStore) -> None:
    with pytest.raises(TaskNotFoundError):
        store.update_progress("missing", None, expected_state=JobState.QUEUED)


# --- delete -----------------------------------------------------------------


def test_delete_removes_record_and_is_idempotent(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    assert store.delete(record.task_id) is True
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)
    assert store.delete(record.task_id) is False


def test_delete_unknown_id_returns_false(store: TaskStore) -> None:
    assert store.delete("missing") is False


# --- DEC-174 prohibited fields ----------------------------------------------


@pytest.mark.parametrize(
    "field",
    [
        "filename",
        "name",
        "password",
        "signed_url",
        "preview",
        "content",
        "token",
        "authorization",
        "cookie",
    ],
)
def test_record_type_structurally_rejects_prohibited_fields(clock: FakeClock, field: str) -> None:
    record = make_record(clock)
    with pytest.raises(TypeError):
        _construct_with_foreign_fields(record, **{field: "x"})


@pytest.mark.parametrize(
    "field",
    ["filename", "password", "signed_url", "preview", "content", "token", "cookie"],
)
def test_nested_summary_models_reject_prohibited_fields(field: str) -> None:
    # Cast crossing point: the extra kwargs are deliberately outside the
    # models' typed field sets; runtime enforcement (extra="forbid") is
    # what is under test.
    with pytest.raises(ValidationError):
        cast(Any, Progress)(unit="engine_progress", value=1, **{field: "x"})
    with pytest.raises(ValidationError):
        cast(Any, ResultSummary)(output_count=1, total_bytes=2, **{field: "x"})
    with pytest.raises(ValidationError):
        cast(Any, ErrorSummary)(
            code="engine_error",
            category="engine",
            retryable=False,
            message_key="error.engine",
            **{field: "x"},
        )


@pytest.mark.parametrize(
    "bad_field",
    [
        "FileName",
        "PASSWORD",
        "signed_url",
        "content_bytes",
        "preview",
        "token",
        "Authorization",
        "cookie",
        "name",
    ],
)
def test_tampered_prohibited_storage_field_fails_closed(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock, bad_field: str
) -> None:
    record = make_record(clock)
    store.create(record)
    raw_client.hset(_TASK_KEY.format(task_id=record.task_id), bad_field, "x")
    with pytest.raises(ProhibitedFieldError):
        store.get(record.task_id)


# --- Corrupt data -----------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("state", b"\xff\xfe"),
        ("state", "bogus"),
        ("created_at", "not-a-date"),
        ("created_at", "2026-08-03T12:00:00"),
        ("progress", "{not json"),
        ("progress", "[1, 2]"),
        ("result", '{"output_count": 1, "total_bytes": 2, "filename": "x"}'),
        ("task_id", "some-other-id"),
        ("objects", '"not-a-list"'),
        ("objects", "[1, 2]"),
    ],
)
def test_corrupt_storage_fails_closed(
    store: TaskStore,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
    field: str,
    value: str | bytes,
) -> None:
    record = make_record(clock)
    store.create(record)
    raw_client.hset(_TASK_KEY.format(task_id=record.task_id), field, value)
    with pytest.raises(CorruptRecordError):
        store.get(record.task_id)


def test_missing_required_field_fails_closed(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock)
    store.create(record)
    raw_client.hdel(_TASK_KEY.format(task_id=record.task_id), "state")
    with pytest.raises(CorruptRecordError):
        store.get(record.task_id)


# --- Schema lock ------------------------------------------------------------


def test_full_record_writes_exact_field_vocabulary(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = replace(
        make_record(clock),
        progress=Progress(unit="engine_progress", value=1, total=10),
        objects=(_FIXTURE_OBJECT,),
    )
    store.create(record)
    stored = raw_client.hgetall(_TASK_KEY.format(task_id=record.task_id))
    # started_at/completed_at are stamped only by transitions, and
    # result/error belong only to terminal transitions; all four are
    # rejected on created records, so the create-time vocabulary excludes
    # them. Their presence after transitions is covered by the transition
    # contract tests.
    assert {cast(bytes, key).decode("utf-8") for key in stored} == ALL_FIELDS - {
        "started_at",
        "completed_at",
        "result",
        "error",
    }


def test_minimal_record_writes_only_required_fields(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock)
    store.create(record)
    stored = raw_client.hgetall(_TASK_KEY.format(task_id=record.task_id))
    # queued_at is always materialized (defaults to created_at), so the
    # minimal vocabulary is the required set plus queued_at.
    assert {cast(bytes, key).decode("utf-8") for key in stored} == REQUIRED_FIELDS | {"queued_at"}


# --- Redis unavailable / fail closed ----------------------------------------


def test_all_operations_fail_closed_when_redis_unavailable(clock: FakeClock) -> None:
    failing = cast(RedisLike, _FailingClient(ConnectionError("connection refused")))
    broken = TaskStore(make_settings(), client=failing, clock=clock)
    with pytest.raises(StoreUnavailableError):
        broken.create(make_record(clock))
    with pytest.raises(StoreUnavailableError):
        broken.get("any")
    with pytest.raises(StoreUnavailableError):
        broken.transition_state("any", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    with pytest.raises(StoreUnavailableError):
        broken.update_progress("any", None, expected_state=JobState.PROCESSING)
    with pytest.raises(StoreUnavailableError):
        broken.delete("any")
    with pytest.raises(StoreUnavailableError):
        broken.ttl_seconds("any")


def test_oom_write_failure_fails_closed_and_is_never_silently_dropped(
    clock: FakeClock,
) -> None:
    oom = ResponseError("OOM command not allowed when used memory > 'maxmemory'")
    failing = cast(RedisLike, _FailingClient(oom))
    broken = TaskStore(make_settings(), client=failing, clock=clock)
    with pytest.raises(StoreUnavailableError):
        broken.create(make_record(clock))


def test_failures_log_only_safe_class_names(
    caplog: pytest.LogCaptureFixture, clock: FakeClock
) -> None:
    task_id = "sensitive-task-42"
    failing = cast(RedisLike, _FailingClient(ConnectionError("secret connection detail")))
    broken = TaskStore(make_settings(), client=failing, clock=clock)
    with caplog.at_level(logging.ERROR), pytest.raises(StoreUnavailableError):
        broken.get(task_id)
    lines = [record.getMessage() for record in caplog.records]
    assert any("task store" in line for line in lines)
    for line in lines:
        assert task_id not in line
        assert "secret connection detail" not in line


# --- list_expired (BE-07 enumeration seam) ----------------------------------


def test_list_expired_returns_only_deadline_passed_records(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    expired = make_record(clock, task_id="expired", expires_in=3600)
    store.create(expired)
    clock.advance(3601)
    live = make_record(clock, task_id="live", expires_in=3600)
    store.create(live)
    assert [r.task_id for r in store.list_expired(clock())] == ["expired"]


def test_list_expired_is_bounded_and_drains_to_empty(store: TaskStore, clock: FakeClock) -> None:
    for index in range(5):
        record = make_record(clock, task_id=f"exp-{index}", expires_in=3600)
        store.create(record)
        clock.advance(3601)
    seen: set[str] = set()
    total = 0
    # SCAN gives no snapshot: pages may revisit keys, so the drain contract
    # is "bounded pages; delete processed records; loop until an empty
    # page" — exactly the coordinator wiring ``run(...)`` + ``delete``.
    while True:
        page = store.list_expired(clock(), limit=2)
        assert len(page) <= 2
        if not page:
            break
        total += len(page)
        seen.update(record.task_id for record in page)
        for record in page:
            store.delete(record.task_id)
    assert total == 5
    assert seen == {"exp-0", "exp-1", "exp-2", "exp-3", "exp-4"}


def test_list_expired_skips_keys_removed_between_scan_and_read(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    for index in range(3):
        record = make_record(clock, task_id=f"gone-{index}", expires_in=3600)
        store.create(record)
        clock.advance(3601)
    raw_client.delete("task:gone-1")
    found = [r.task_id for r in store.list_expired(clock())]
    assert "gone-1" not in found and len(found) == 2


def test_list_expired_fails_closed_on_corrupt_record(
    store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock, task_id="corrupt", expires_in=3600)
    store.create(record)
    clock.advance(3601)
    raw_client.hset("task:corrupt", "state", "bogus")
    with pytest.raises(CorruptRecordError):
        store.list_expired(clock())


def test_list_expired_fails_closed_when_redis_unavailable(clock: FakeClock) -> None:
    failing = cast(RedisLike, _FailingClient(ConnectionError("connection refused")))
    broken = TaskStore(make_settings(), client=failing, clock=clock)
    with pytest.raises(StoreUnavailableError):
        broken.list_expired(clock())


# --- Cancellation surface (DEC-069) -----------------------------------------


class _LuaEvalFailingClient:
    """Store-shaped client whose eval raises (Lua mechanism fail-closed path)."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def hgetall(self, name: str) -> dict[bytes, bytes]:
        raise self._error

    def pipeline(self, transaction: bool = True) -> object:
        raise self._error

    def ttl(self, name: str) -> int:
        raise self._error

    def delete(self, name: str) -> int:
        raise self._error

    def scan_iter(self, match: str | None = None, count: int = 100) -> Iterator[bytes]:
        raise self._error

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> list[bytes | int]:
        raise self._error


def _make_cas_store(
    client: RedisLike, clock: FakeClock, *, retention_seconds: int = 3600
) -> TaskStore:
    """TaskStore whose cancel uses the CAS mechanism (fakeredis has no EVAL)."""
    settings = make_settings(retention_seconds=retention_seconds)
    return TaskStore(
        settings,
        client=client,
        clock=clock,
        cancel=CasCancelMechanism(client, retention_seconds),
    )


def test_cancel_queued_record_transitions_to_cancelled(
    client_a: RedisLike, clock: FakeClock
) -> None:
    store = _make_cas_store(client_a, clock)
    created = store.create(make_record(clock, task_id="cancel-me"))
    clock.advance(10)

    cancelled = store.cancel("cancel-me")

    assert cancelled.state is JobState.CANCELLED
    assert cancelled.completed_at is None
    assert cancelled.error is None
    assert cancelled.result is None
    assert cancelled.updated_at == clock()
    assert cancelled.queued_at == created.queued_at
    assert store.get("cancel-me") == cancelled
    assert store.ttl_seconds("cancel-me") > 0


def test_cancel_raises_conflict_when_not_queued_and_preserves_state(
    client_a: RedisLike, clock: FakeClock
) -> None:
    store = _make_cas_store(client_a, clock)
    store.create(make_record(clock, task_id="cancel-late"))
    claimed = store.transition_state(
        "cancel-late", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
    )

    with pytest.raises(TaskConflictError):
        store.cancel("cancel-late")
    with pytest.raises(TaskConflictError):
        store.cancel("cancel-late")

    assert store.get("cancel-late") == claimed


def test_cancel_terminal_record_conflicts(client_a: RedisLike, clock: FakeClock) -> None:
    store = _make_cas_store(client_a, clock)
    store.create(make_record(clock, task_id="cancel-done"))
    store.transition_state("cancel-done", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    result = ResultSummary(output_count=1, total_bytes=1024)
    store.transition_state(
        "cancel-done",
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=result, objects=(_FIXTURE_OBJECT,)),
    )

    with pytest.raises(TaskConflictError):
        store.cancel("cancel-done")

    assert store.get("cancel-done").state is JobState.DONE


def test_cancel_unknown_id_raises_not_found(client_a: RedisLike, clock: FakeClock) -> None:
    store = _make_cas_store(client_a, clock)
    with pytest.raises(TaskNotFoundError):
        store.cancel("missing")


def test_cancel_logically_expired_record_raises_not_found(
    client_a: RedisLike, clock: FakeClock
) -> None:
    store = _make_cas_store(client_a, clock)
    store.create(make_record(clock, task_id="cancel-stale", expires_in=30))
    clock.advance(31)
    with pytest.raises(TaskNotFoundError):
        store.cancel("cancel-stale")


def test_cancel_rejects_empty_task_id(client_a: RedisLike, clock: FakeClock) -> None:
    store = _make_cas_store(client_a, clock)
    with pytest.raises(InvalidRecordError):
        store.cancel("")


def test_cancel_corrupt_record_fails_closed(
    client_a: RedisLike, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    store = _make_cas_store(client_a, clock)
    store.create(make_record(clock, task_id="cancel-corrupt"))
    raw_client.hset("task:cancel-corrupt", "state", b"\xff\xfe")
    with pytest.raises(CorruptRecordError):
        store.cancel("cancel-corrupt")


def test_cancel_fails_closed_and_logs_only_class_names(
    caplog: pytest.LogCaptureFixture, clock: FakeClock
) -> None:
    task_id = "sensitive-cancel-task"
    failing = cast(RedisLike, _FailingClient(ConnectionError("secret connection detail")))
    broken = _make_cas_store(failing, clock)
    with caplog.at_level(logging.ERROR), pytest.raises(StoreUnavailableError):
        broken.cancel(task_id)
    lines = [record.getMessage() for record in caplog.records]
    assert any("task store" in line for line in lines)
    for line in lines:
        assert task_id not in line
        assert "secret connection detail" not in line


def test_lua_cancel_mechanism_fails_closed_on_redis_error(
    caplog: pytest.LogCaptureFixture, clock: FakeClock
) -> None:
    task_id = "sensitive-lua-task"
    failing = _LuaEvalFailingClient(ConnectionError("secret connection detail"))
    mechanism = LuaCancelMechanism(cast(LuaRedisLike, failing))
    with caplog.at_level(logging.ERROR), pytest.raises(StoreUnavailableError):
        mechanism.cancel(task_id, now=clock())
    lines = [record.getMessage() for record in caplog.records]
    assert any("task store" in line for line in lines)
    for line in lines:
        assert task_id not in line
        assert "secret connection detail" not in line


# --- connectivity probe (readiness) and safe shutdown ------------------------


def test_ping_succeeds_against_reachable_client(store: TaskStore) -> None:
    store.ping()


def test_ping_fails_closed_when_redis_unreachable(
    caplog: pytest.LogCaptureFixture,
) -> None:
    failing = cast(RedisLike, _FailingClient(ConnectionError("secret connection detail")))
    broken = TaskStore(make_settings(), client=failing, clock=FakeClock(T0))
    with caplog.at_level(logging.ERROR), pytest.raises(StoreUnavailableError):
        broken.ping()
    lines = [record.getMessage() for record in caplog.records]
    assert any("task store" in line for line in lines)
    for line in lines:
        assert "secret connection detail" not in line


class _RecordingCloseClient:
    """Client recording whether close() was called on it."""

    closed = False

    def close(self) -> None:
        type(self).closed = True


def test_close_releases_the_client_connection(store: TaskStore) -> None:
    _RecordingCloseClient.closed = False
    recording = cast(RedisLike, _RecordingCloseClient())
    wrapped = TaskStore(make_settings(), client=recording, clock=FakeClock(T0))
    assert _RecordingCloseClient.closed is False
    wrapped.close()
    assert _RecordingCloseClient.closed is True


def test_close_is_idempotent_on_reusable_stores(store: TaskStore) -> None:
    store.close()
    store.close()
