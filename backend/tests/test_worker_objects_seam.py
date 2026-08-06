"""Objects-publication seam tests for the worker (FOUND-01).

The worker maps a SUCCESS outcome with published ``objects`` to a
``RESULT_UPLOADED`` terminal transition carrying those keys (hardening
H-1): a SUCCESS outcome with ``objects=None`` is treated as an engine
error instead, so the record fails closed with a safe error payload and
the stream entry is acknowledged normally. Failure outcomes keep the
record's objects (the input keys) untouched.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import cast

import fakeredis
import pytest

from app.config import Settings
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskRecord, TaskStore
from app.schemas.job import ErrorSummary, Progress, ResultSummary
from app.tasks.state_machine import JobState
from app.worker.worker import (
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    JobExecutor,
    JobWorker,
    WorkerOptions,
)

_REAL_NOW = datetime.now(UTC)

SUCCESS_RESULT = ResultSummary(output_count=1, total_bytes=1024)
OUTPUT_OBJECT = "tmp/2026-08-03/" + "a" * 32 + ".pdf"
INPUT_OBJECT = "tmp/2026-08-03/" + "f" * 32 + ".pdf"


class FakeClock:
    """Injectable worker clock: fixed start, explicit advances."""

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
    clock: FakeClock,
    *,
    task_id: str | None = None,
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        objects=objects,
    )


class PublishingSuccessExecutor:
    """Executor returning SUCCESS with published output objects."""

    def __init__(self) -> None:
        self.calls: list[ClaimedJob] = []

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del report
        self.calls.append(job)
        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT, objects=(OUTPUT_OBJECT,)
        )


class MissingObjectsSuccessExecutor:
    """Executor returning SUCCESS without published objects (H-1)."""

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT, objects=None)


class FailureExecutor:
    """Executor returning a failure outcome."""

    def __init__(self, error: ErrorSummary) -> None:
        self.error = error

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=self.error)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(_REAL_NOW)


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def store_client(server: fakeredis.FakeServer) -> RedisLike:
    return cast(RedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def stream_client(server: fakeredis.FakeServer) -> StreamsRedisLike:
    return cast(StreamsRedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def store(store_client: RedisLike, clock: FakeClock) -> TaskStore:
    return TaskStore(make_settings(), client=store_client, clock=clock)


def make_queue(stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock) -> JobQueue:
    return JobQueue(make_settings(), store, client=stream_client, options=QueueOptions(clock=clock))


def make_worker(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    executor: JobExecutor,
    clock: FakeClock,
) -> JobWorker:
    return JobWorker(
        make_settings(),
        store,
        client=stream_client,
        executor=executor,
        options=replace(WorkerOptions(), clock=clock),
    )


def enqueue_job(
    queue: JobQueue,
    clock: FakeClock,
    task_id: str | None = None,
    *,
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    record = make_record(clock, task_id=task_id, objects=objects)
    queue.enqueue(record)
    return record


def test_success_with_objects_publishes_terminal_objects(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock, objects=(INPUT_OBJECT,))
    worker = make_worker(store, stream_client, PublishingSuccessExecutor(), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.DONE
    assert fetched.objects == (OUTPUT_OBJECT,)


def test_success_without_objects_fails_closed_with_engine_error(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    worker = make_worker(store, stream_client, MissingObjectsSuccessExecutor(), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.error is not None
    assert fetched.error.code == "engine_error"


def test_failure_keeps_record_objects_unchanged(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock, objects=(INPUT_OBJECT,))
    error = ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )
    worker = make_worker(store, stream_client, FailureExecutor(error), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.objects == (INPUT_OBJECT,)
