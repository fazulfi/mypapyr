"""Objects-publication seam tests for the task store (FOUND-01).

The additive ``objects`` field on :class:`TransitionPayload` lets a
terminal transition to ``done`` publish the executor's output object keys
(binding output-publication decision, hardening H-2). The store enforces
the pairing: objects are REQUIRED on ``RESULT_UPLOADED`` (and must match
``result.output_count``), forbidden on failure events and on non-terminal
transitions, and never mutated by transitions that carry no payload
objects.

Semantics are exercised against ``fakeredis`` exactly like the neighboring
``test_store.py`` contract tests.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

import fakeredis
import pytest

from app.config import Settings
from app.queue.store import InvalidRecordError, RedisLike, TaskRecord, TaskStore, TransitionPayload
from app.schemas.job import ErrorSummary, ResultSummary
from app.tasks.state_machine import JobEvent, JobState

T0 = datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC)

_OUTPUT_KEY_A = "tmp/2026-08-03/" + "a" * 32 + ".pdf"
_OUTPUT_KEY_B = "tmp/2026-08-03/" + "b" * 32 + ".pdf"
_INPUT_KEY = "tmp/2026-08-03/" + "f" * 32 + ".pdf"


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
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=state,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        objects=objects,
    )


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(T0)


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def client(server: fakeredis.FakeServer) -> RedisLike:
    return cast(RedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def store(client: RedisLike, clock: FakeClock) -> TaskStore:
    return TaskStore(make_settings(), client=client, clock=clock)


def _claim(store: TaskStore, record: TaskRecord) -> None:
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)


def _engine_error() -> ErrorSummary:
    return ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )


def test_result_uploaded_publishes_objects(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock, objects=(_INPUT_KEY,))
    store.create(record)
    _claim(store, record)
    result = ResultSummary(output_count=2, total_bytes=2048)
    done = store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=result, objects=(_OUTPUT_KEY_A, _OUTPUT_KEY_B)),
    )
    assert done.state is JobState.DONE
    assert done.objects == (_OUTPUT_KEY_A, _OUTPUT_KEY_B)


def test_result_uploaded_requires_objects(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    _claim(store, record)
    result = ResultSummary(output_count=1, total_bytes=1024)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id,
            JobEvent.RESULT_UPLOADED,
            expected_state=JobState.PROCESSING,
            payload=TransitionPayload(result=result, objects=None),
        )


def test_result_uploaded_zero_outputs_accepts_empty_objects(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock)
    store.create(record)
    _claim(store, record)
    result = ResultSummary(output_count=0, total_bytes=0)
    done = store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=result, objects=()),
    )
    assert done.state is JobState.DONE
    assert done.objects == ()


def test_result_uploaded_rejects_output_count_mismatch(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    _claim(store, record)
    result = ResultSummary(output_count=2, total_bytes=2048)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id,
            JobEvent.RESULT_UPLOADED,
            expected_state=JobState.PROCESSING,
            payload=TransitionPayload(result=result, objects=(_OUTPUT_KEY_A,)),
        )


def test_failure_event_forbids_objects(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    _claim(store, record)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id,
            JobEvent.ENGINE_ERROR,
            expected_state=JobState.PROCESSING,
            payload=TransitionPayload(error=_engine_error(), objects=(_OUTPUT_KEY_A,)),
        )


def test_non_terminal_transition_forbids_objects(store: TaskStore, clock: FakeClock) -> None:
    record = make_record(clock)
    store.create(record)
    with pytest.raises(InvalidRecordError):
        store.transition_state(
            record.task_id,
            JobEvent.WORKER_CLAIMED,
            expected_state=JobState.QUEUED,
            payload=TransitionPayload(objects=(_OUTPUT_KEY_A,)),
        )


def test_transitions_without_objects_preserve_record_objects(
    store: TaskStore, clock: FakeClock
) -> None:
    record = make_record(clock, objects=(_INPUT_KEY,))
    store.create(record)
    claimed = store.transition_state(
        record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
    )
    assert claimed.objects == (_INPUT_KEY,)
    failed = store.transition_state(
        record.task_id,
        JobEvent.ENGINE_ERROR,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(error=_engine_error()),
    )
    assert failed.objects == (_INPUT_KEY,)
