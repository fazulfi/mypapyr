"""Contract tests for the one-job worker substrate (BE-05).

The worker owns claim/execute/acknowledge: XREADGROUP with ``>`` and no
NOACK, one in-flight job per instance, an explicit per-job timeout, and
XACK only after the task store records a terminal state. Stale pending
entries are reclaimed with a cursor-aware XAUTOCLAIM loop (deleted-entry
IDs dropped, ``0-0`` terminates); a reclaimed entry whose record is
PROCESSING past its execution timeout fails as TIMEOUT without
re-execution. Redis/store unavailability degrades the worker and pauses
admission (fail-closed).

``fakeredis`` implements the consumed command surface including PEL
ownership, XAUTOCLAIM idle/claim/deleted-IDs, and BUSYGROUP. Real-Redis
gaps (reserved for the gate-exit integration wave): blocking-read behavior,
cross-process claim races, and persistence/restart recovery.
"""

from __future__ import annotations

import ctypes
import logging
import os
import signal
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import fakeredis
import pytest
from redis.exceptions import ConnectionError

from app.config import Settings
from app.queue.queue import GROUP_NAME, STREAM_KEY, JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import (
    CasCancelMechanism,
    PipelineLike,
    RedisLike,
    StoreUnavailableError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.schemas.job import ErrorSummary, Progress, ResultSummary
from app.tasks.state_machine import JobEvent, JobState
from app.worker.worker import (
    ENGINE_ERROR_FALLBACK,
    BoundedBackoffTerminalRetryPolicy,
    ClaimedJob,
    DaemonThreadJobRunner,
    DefaultTimeoutPolicy,
    ExecutionKind,
    ExecutionOutcome,
    JobExecutor,
    JobWorker,
    SubprocessJobRunner,
    WorkerError,
    WorkerOptions,
    WorkerUnavailableError,
)

_REAL_NOW = datetime.now(UTC)

XReadResult = list[tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]]]]

SUCCESS_RESULT = ResultSummary(output_count=1, total_bytes=1024)


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


def make_record(clock: FakeClock, *, task_id: str | None = None) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
    )


class SuccessExecutor:
    """Executor returning a fixed success outcome; records invocations."""

    def __init__(self, result: ResultSummary = SUCCESS_RESULT) -> None:
        self.result = result
        self.calls: list[ClaimedJob] = []

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del report
        self.calls.append(job)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=self.result)


class FailureExecutor:
    """Executor returning a fixed failure outcome."""

    def __init__(self, error: ErrorSummary) -> None:
        self.error = error
        self.calls: list[ClaimedJob] = []

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        self.calls.append(job)
        return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=self.error)


class EmptySuccessExecutor:
    """Executor violating the outcome contract: success without a result."""

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=None)


class RaisingExecutor:
    """Executor raising an unexpected exception (fail-closed path)."""

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        raise RuntimeError("engine exploded")


class HangingExecutor:
    """Executor that blocks until released or the bound elapses."""

    def __init__(self, release: threading.Event) -> None:
        self.release = release

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        self.release.wait(2)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class BlockingExecutor:
    """Executor that signals start and blocks until released."""

    def __init__(self, started: threading.Event, release: threading.Event) -> None:
        self.started = started
        self.release = release

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        self.started.set()
        self.release.wait(5)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class ProgressExecutor:
    """Executor reporting progress through the worker's reporter."""

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job
        report(Progress(unit="engine_progress", value=5, total=10))
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class SpawnSuccessExecutor:
    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class SpawnProgressExecutor:
    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job
        report(Progress(unit="engine_progress", value=5, total=10))
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class SpawnRaisingExecutor:
    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        raise RuntimeError("private engine detail")


class SpawnCrashingExecutor:
    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        os._exit(3)


class SpawnHangingExecutor:
    def __init__(self, pid_path: str) -> None:
        self._pid_path = pid_path

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        Path(self._pid_path).write_text(str(os.getpid()), encoding="utf-8")
        time.sleep(60)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class SpawnSigtermIgnoringExecutor:
    def __init__(self, pid_path: str) -> None:
        self._pid_path = pid_path

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del job, report
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        Path(self._pid_path).write_text(str(os.getpid()), encoding="utf-8")
        time.sleep(60)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class SpawnFirstHangsThenSucceedsExecutor:
    def __init__(self, first_task_id: str, pid_path: str) -> None:
        self._first_task_id = first_task_id
        self._pid_path = pid_path

    def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
        del report
        if job.task_id == self._first_task_id:
            Path(self._pid_path).write_text(str(os.getpid()), encoding="utf-8")
            time.sleep(60)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


class StubRunner:
    """Deterministic runner: returns pre-arranged outcomes, never threads."""

    def __init__(self, outcomes: list[ExecutionOutcome | None]) -> None:
        self._outcomes = outcomes
        self.calls: list[tuple[ClaimedJob, timedelta]] = []

    def run(
        self, job: ClaimedJob, report: Callable[[Progress], None], timeout: timedelta
    ) -> ExecutionOutcome | None:
        del report
        self.calls.append((job, timeout))
        outcome = (
            self._outcomes.pop(0)
            if self._outcomes
            else ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)
        )
        return outcome


class TinyTimeoutPolicy:
    """Test policy: instant staleness, zero max timeout for tiny claim idle."""

    def timeout_for(self, tool: str) -> timedelta:
        del tool
        return timedelta(milliseconds=1)

    def max_timeout(self) -> timedelta:
        return timedelta(0)


class SlowTimeoutPolicy:
    """Real-time timeout policy for the wall-clock timeout test."""

    def __init__(self, timeout: timedelta) -> None:
        self._timeout = timeout

    def timeout_for(self, tool: str) -> timedelta:
        del tool
        return self._timeout

    def max_timeout(self) -> timedelta:
        return self._timeout


class _VerifyingAckClient:
    """Wraps the stream client and proves ack discipline at ack time.

    ``xack`` asserts the task store already records a terminal state for
    the acked entry, mechanically locking "XACK only after the task store
    records a terminal state".
    """

    def __init__(self, inner: StreamsRedisLike, store: TaskStore) -> None:
        self._inner = inner
        self._store = store
        self._task_by_entry: dict[bytes, str] = {}
        self.xack_calls: list[bytes] = []

    def xgroup_create(
        self, name: str, groupname: str, id: str = "0", mkstream: bool = False
    ) -> None:
        self._inner.xgroup_create(name, groupname, id=id, mkstream=mkstream)

    def xadd(
        self,
        name: str,
        fields: dict[str, str],
        id: str = "*",
        maxlen: int | None = None,
        approximate: bool = True,
    ) -> bytes:
        entry = self._inner.xadd(name, fields, id=id, maxlen=maxlen, approximate=approximate)
        self._task_by_entry[entry] = fields["task_id"]
        return entry

    def pipeline(self, transaction: bool = True) -> PipelineLike:
        # Forward the watched-pipeline surface the queue's atomic CAS
        # append requires (F-1); entries appended through the pipeline
        # bypass this wrapper's ``xadd``, so ``xack`` resolves them from
        # the stream before verifying the terminal store write.
        return self._inner.pipeline(transaction=transaction)

    def xreadgroup(
        self,
        groupname: str,
        consumername: str,
        streams: dict[str, str],
        count: int | None = None,
        block: int | None = None,
    ) -> list[tuple[bytes, list[tuple[bytes, Mapping[bytes, bytes]]]]]:
        return self._inner.xreadgroup(groupname, consumername, streams, count=count, block=block)

    def xack(self, name: str, groupname: str, *ids: bytes) -> int:
        for entry_id in ids:
            task_id = self._task_by_entry.get(entry_id)
            if task_id is None:
                task_id = self._resolve_task_id(name, entry_id)
            record = self._store.get(task_id)
            assert record.state in (JobState.DONE, JobState.FAILED, JobState.CANCELLED)
        self.xack_calls.extend(ids)
        return self._inner.xack(name, groupname, *ids)

    def _resolve_task_id(self, name: str, entry_id: bytes) -> str:
        for eid, fields in self._inner.xrange(name, "-", "+"):
            if eid == entry_id:
                task_id = fields.get(b"task_id")
                if task_id is not None:
                    return task_id.decode("utf-8")
        raise AssertionError(f"ack verification: entry {entry_id!r} not found in {name!r}")

    def xautoclaim(
        self,
        name: str,
        groupname: str,
        consumername: str,
        min_idle_time: int,
        start_id: bytes = b"0-0",
    ) -> tuple[bytes, list[tuple[bytes, Mapping[bytes, bytes]]], list[bytes]]:
        return self._inner.xautoclaim(
            name, groupname, consumername, min_idle_time, start_id=start_id
        )

    def xlen(self, name: str) -> int:
        return self._inner.xlen(name)

    def xrange(
        self, name: str, start: str = "-", end: str = "+", count: int | None = None
    ) -> list[tuple[bytes, Mapping[bytes, bytes]]]:
        return self._inner.xrange(name, start, end, count=count)

    def xdel(self, name: str, *ids: bytes) -> int:
        # Terminal release deletes the stream entry BEFORE acking it; cache
        # the entry->task mapping so the follow-up ``xack`` can still verify
        # the terminal store write after the entry no longer exists.
        for entry_id in ids:
            task_id = self._task_by_entry.get(entry_id)
            if task_id is None:
                task_id = self._resolve_task_id(name, entry_id)
                self._task_by_entry[entry_id] = task_id
        return self._inner.xdel(name, *ids)


class _FlakyXdelClient(_VerifyingAckClient):
    """Verifying client whose xdel fails once, then behaves normally."""

    def __init__(self, inner: StreamsRedisLike, store: TaskStore) -> None:
        super().__init__(inner, store)
        self._fail_next = True

    def xdel(self, name: str, *ids: bytes) -> int:
        if self._fail_next:
            self._fail_next = False
            raise ConnectionError("socket closed mid-delete")
        return super().xdel(name, *ids)


class _FailingStreamClient:
    """Raises the configured exception from every stream-facing operation."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def xgroup_create(
        self, name: str, groupname: str, id: str = "0", mkstream: bool = False
    ) -> None:
        raise self._error

    def xadd(
        self,
        name: str,
        fields: dict[str, str],
        id: str = "*",
        maxlen: int | None = None,
        approximate: bool = True,
    ) -> bytes:
        raise self._error

    def xreadgroup(
        self,
        groupname: str,
        consumername: str,
        streams: dict[str, str],
        count: int | None = None,
        block: int | None = None,
    ) -> list[tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]]]]:
        raise self._error

    def xack(self, name: str, groupname: str, *ids: bytes) -> int:
        raise self._error

    def xautoclaim(
        self,
        name: str,
        groupname: str,
        consumername: str,
        min_idle_time: int,
        start_id: bytes = b"0-0",
    ) -> tuple[bytes, list[tuple[bytes, Mapping[bytes, bytes]]], list[bytes]]:
        raise self._error

    def xlen(self, name: str) -> int:
        raise self._error

    def xrange(
        self, name: str, start: str = "-", end: str = "+", count: int | None = None
    ) -> list[tuple[bytes, dict[bytes, bytes]]]:
        raise self._error

    def xdel(self, name: str, *ids: bytes) -> int:
        raise self._error


class _RetryRecorder:
    """Sleep seam recording every backoff delay without blocking."""

    def __init__(self) -> None:
        self.sleeps: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.sleeps.append(seconds)


class _FlakyTerminalStore:
    """TaskStore proxy whose terminal transitions fail with StoreUnavailableError.

    ``failures`` is the number of terminal ``transition_state`` calls that
    raise :class:`StoreUnavailableError` before the proxy persists normally;
    ``-1`` fails every terminal call (never recovers). Claim transitions
    (``WORKER_CLAIMED``), progress updates, and reads delegate unchanged, so
    the executor runs exactly once while only terminal persistence flaps —
    reproducing the F-3 transient-outage shape.
    """

    def __init__(self, inner: TaskStore, failures: int) -> None:
        self._inner = inner
        self._remaining = failures
        self.terminal_attempts: list[tuple[str, JobEvent]] = []

    def transition_state(
        self,
        task_id: str,
        event: JobEvent,
        *,
        expected_state: JobState,
        payload: TransitionPayload | None = None,
    ) -> TaskRecord:
        if event is not JobEvent.WORKER_CLAIMED:
            self.terminal_attempts.append((task_id, event))
            if self._remaining != 0:
                if self._remaining > 0:
                    self._remaining -= 1
                raise StoreUnavailableError()
        return self._inner.transition_state(
            task_id, event, expected_state=expected_state, payload=payload
        )

    def get(self, task_id: str) -> TaskRecord:
        return self._inner.get(task_id)

    def update_progress(
        self,
        task_id: str,
        progress: Progress | None,
        *,
        expected_state: JobState,
        expected_updated_at: datetime | None = None,
    ) -> TaskRecord:
        return self._inner.update_progress(
            task_id,
            progress,
            expected_state=expected_state,
            expected_updated_at=expected_updated_at,
        )


@pytest.fixture
def clock() -> FakeClock:
    # Starts at the real now: the max-wait cap compares stream entry ids
    # (stamped by fakeredis's wall clock) against this clock, so a fixed
    # past start would spuriously age entries; the stale-processing tests
    # advance the clock explicitly and remain deterministic either way.
    return FakeClock(_REAL_NOW)


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def raw_client(server: fakeredis.FakeServer) -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(server=server)


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
    *,
    options: WorkerOptions | None = None,
) -> JobWorker:
    merged = options if options is not None else WorkerOptions()
    return JobWorker(
        make_settings(),
        store,
        client=stream_client,
        executor=executor,
        options=replace(merged, clock=clock),
    )


def enqueue_job(queue: JobQueue, clock: FakeClock, task_id: str | None = None) -> TaskRecord:
    record = make_record(clock, task_id=task_id)
    queue.enqueue(record)
    return record


def _deliver(raw_client: fakeredis.FakeRedis) -> bytes:
    """Deliver one new entry to consumer 'w1' without acking (crash sim)."""
    result = cast(
        XReadResult,
        raw_client.xreadgroup(GROUP_NAME, "w1", {STREAM_KEY: ">"}, count=1),
    )
    assert result, "expected a deliverable entry"
    return result[0][1][0][0]


def _pending_count(raw_client: fakeredis.FakeRedis) -> int:
    summary = raw_client.xpending(STREAM_KEY, GROUP_NAME)
    return int(cast(int, summary["pending"]))


def _claimed_job() -> ClaimedJob:
    return ClaimedJob(task_id="spawn-job-1", tool="merge-pdf", route="merge-pdf", entry_id=b"1-0")


def _discard_report(_progress: Progress) -> None:
    return None


def _wait_for_file(path: Path, *, deadline: float) -> None:
    end = time.monotonic() + deadline
    while time.monotonic() < end:
        if path.exists():
            return
        time.sleep(0.02)
    raise AssertionError(f"timed out waiting for {path}")


def _process_alive(pid: int) -> bool:
    if os.name == "nt":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(0x0400, False, pid)
        if not handle:
            return False
        exit_code = ctypes.c_ulong()
        try:
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == 259
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _assert_process_gone(pid: int) -> None:
    end = time.monotonic() + 5.0
    while time.monotonic() < end:
        if not _process_alive(pid):
            return
        time.sleep(0.02)
    raise AssertionError(f"process {pid} is still alive")


def _assert_thread_gone(thread: threading.Thread) -> None:
    thread.join(10.0)
    assert thread.is_alive() is False


def _run_in_thread(
    runner: SubprocessJobRunner, timeout: timedelta
) -> tuple[threading.Thread, dict[str, object]]:
    box: dict[str, object] = {}

    def drive() -> None:
        box["outcome"] = runner.run(_claimed_job(), _discard_report, timeout)

    driver = threading.Thread(target=drive, daemon=True)
    driver.start()
    return driver, box


# --- Happy path: claim -> execute -> terminal store -> ack ------------------


def test_success_acks_only_after_terminal_store_update(
    store: TaskStore, server: fakeredis.FakeServer, clock: FakeClock
) -> None:
    stream = cast(StreamsRedisLike, fakeredis.FakeRedis(server=server))
    verifying = _VerifyingAckClient(stream, store)
    queue = JobQueue(
        make_settings(),
        store,
        client=cast(StreamsRedisLike, verifying),
        options=QueueOptions(clock=clock),
    )
    record = enqueue_job(queue, clock)
    worker = make_worker(store, cast(StreamsRedisLike, verifying), SuccessExecutor(), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.DONE
    assert fetched.result == SUCCESS_RESULT
    assert fetched.started_at is not None
    assert fetched.completed_at is not None
    assert verifying.xack_calls


def test_success_flow_leaves_no_pending_entries(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    worker = make_worker(store, stream_client, SuccessExecutor(), clock)
    assert worker.run_once() is True
    assert store.get(record.task_id).state is JobState.DONE
    assert _pending_count(cast(fakeredis.FakeRedis, stream_client)) == 0


def test_failure_records_safe_error_and_acks(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    error = ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )
    worker = make_worker(store, stream_client, FailureExecutor(error), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.error == error
    assert fetched.completed_at is not None
    assert _pending_count(cast(fakeredis.FakeRedis, stream_client)) == 0


def test_executor_exception_fails_closed_with_safe_error(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    worker = make_worker(store, stream_client, RaisingExecutor(), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.error is not None
    assert fetched.error.code == "engine_error"
    assert fetched.error.category == "engine"
    assert fetched.error.retryable is False


def test_executor_success_without_result_fails_closed(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    worker = make_worker(store, stream_client, EmptySuccessExecutor(), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.error is not None
    assert fetched.error.code == "engine_error"


def test_explicit_timeout_fails_the_job(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    release = threading.Event()
    worker = make_worker(
        store,
        stream_client,
        HangingExecutor(release),
        clock,
        options=WorkerOptions(timeout_policy=SlowTimeoutPolicy(timedelta(milliseconds=50))),
    )
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.error is not None
    assert fetched.error.code == "timeout"
    assert fetched.error.retryable is True
    assert _pending_count(cast(fakeredis.FakeRedis, stream_client)) == 0


def test_progress_is_reported_to_the_store(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    worker = make_worker(store, stream_client, ProgressExecutor(), clock)
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.progress == Progress(unit="engine_progress", value=5, total=10)


# --- One in-flight job per worker instance ----------------------------------


def test_one_in_flight_job_per_worker_instance(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    queue = make_queue(stream_client, store, clock)
    first = enqueue_job(queue, clock)
    second = enqueue_job(queue, clock)
    started = threading.Event()
    release = threading.Event()
    worker = make_worker(store, stream_client, BlockingExecutor(started, release), clock)
    # run_once blocks until the job completes; drive it from a thread so
    # the busy guard and the one-job posture can be observed mid-flight.
    first_result: dict[str, bool] = {}

    def drive() -> None:
        first_result["done"] = worker.run_once()

    driver = threading.Thread(target=drive, daemon=True)
    driver.start()
    assert started.wait(1)
    assert worker.in_flight is True
    # Busy: a concurrent call claims nothing and runs no recovery.
    assert worker.run_once() is False
    assert store.get(second.task_id).state is JobState.QUEUED
    release.set()
    driver.join(2)
    assert first_result["done"] is True
    assert worker.in_flight is False
    assert store.get(first.task_id).state is JobState.DONE
    assert worker.run_once() is True
    assert store.get(second.task_id).state is JobState.DONE
    assert worker.in_flight is False


# --- Recovery: stale-claim reclaim (XAUTOCLAIM) -----------------------------


def test_crash_before_store_claim_is_reclaimed_and_retried(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    _deliver(raw_client)
    pending = cast(
        "list[dict[str, object]]",
        raw_client.xpending_range(STREAM_KEY, GROUP_NAME, min="-", max="+", count=10),
    )
    assert pending and int(cast(int, pending[0]["times_delivered"])) == 1
    # Not idle enough yet: nothing to reclaim.
    idle_worker = make_worker(
        store,
        stream_client,
        SuccessExecutor(),
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(hours=1),
            timeout_policy=TinyTimeoutPolicy(),
            runner=StubRunner([]),
        ),
    )
    assert idle_worker.run_once() is False
    time.sleep(0.05)
    executor = SuccessExecutor()
    reclaimer = make_worker(
        store,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert reclaimer.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.DONE
    assert fetched.result == SUCCESS_RESULT
    assert len(executor.calls) == 1
    assert _pending_count(raw_client) == 0


def test_crash_after_claim_stale_processing_fails_as_timeout_without_reexecution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    entry_id = _deliver(raw_client)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(0.002)
    time.sleep(0.05)
    executor = SuccessExecutor()
    worker = make_worker(
        store,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert worker.run_once() is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.FAILED
    assert fetched.error is not None and fetched.error.code == "timeout"
    assert fetched.completed_at is not None
    assert executor.calls == []
    assert _pending_count(raw_client) == 0
    assert entry_id


def test_deleted_pending_entry_is_dropped_without_execution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    entry_id = _deliver(raw_client)
    raw_client.xdel(STREAM_KEY, entry_id)
    time.sleep(0.05)
    executor = SuccessExecutor()
    worker = make_worker(
        store,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert worker.run_once() is True
    assert executor.calls == []
    assert store.get(record.task_id).state is JobState.QUEUED
    assert _pending_count(raw_client) == 0


def test_empty_claim_returns_false(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    worker = make_worker(store, stream_client, SuccessExecutor(), clock)
    assert worker.run_once() is False
    assert worker.run_once() is False


def test_crash_after_terminal_before_stream_release_is_recovered(
    store: TaskStore, server: fakeredis.FakeServer, clock: FakeClock
) -> None:
    stream = cast(StreamsRedisLike, fakeredis.FakeRedis(server=server))
    flaky = _FlakyXdelClient(stream, store)
    queue = JobQueue(
        make_settings(),
        store,
        client=cast(StreamsRedisLike, flaky),
        options=QueueOptions(clock=clock),
    )
    record = enqueue_job(queue, clock)
    worker = make_worker(store, cast(StreamsRedisLike, flaky), SuccessExecutor(), clock)
    with pytest.raises(WorkerUnavailableError):
        worker.run_once()
    # The terminal state was durably recorded before the failed stream
    # release (XDEL), so the entry remains pending for recovery.
    assert store.get(record.task_id).state is JobState.DONE
    assert _pending_count(cast(fakeredis.FakeRedis, stream)) == 1
    assert (
        len(
            cast(
                "list[tuple[bytes, dict[bytes, bytes]]]",
                cast(fakeredis.FakeRedis, stream).xrange(STREAM_KEY, "-", "+"),
            )
        )
        == 1
    )
    time.sleep(0.05)
    reclaimer = make_worker(
        store,
        cast(StreamsRedisLike, flaky),
        SuccessExecutor(),
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert reclaimer.run_once() is True
    assert _pending_count(cast(fakeredis.FakeRedis, stream)) == 0
    # Recovery completes the bounded release: the completed entry no longer
    # consumes a queue slot.
    assert (
        len(
            cast(
                "list[tuple[bytes, dict[bytes, bytes]]]",
                cast(fakeredis.FakeRedis, stream).xrange(STREAM_KEY, "-", "+"),
            )
        )
        == 0
    )
    assert store.get(record.task_id).state is JobState.DONE


# --- Claim conflicts with the store -----------------------------------------


def test_claim_conflict_terminal_done_acks_without_execution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=SUCCESS_RESULT),
    )
    _deliver(raw_client)
    time.sleep(0.05)
    executor = SuccessExecutor()
    worker = make_worker(
        store,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert worker.run_once() is True
    assert executor.calls == []
    assert store.get(record.task_id).state is JobState.DONE
    assert _pending_count(raw_client) == 0


def test_claim_conflict_cancelled_acks_without_execution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    store.transition_state(record.task_id, JobEvent.USER_CANCELLED, expected_state=JobState.QUEUED)
    _deliver(raw_client)
    time.sleep(0.05)
    executor = SuccessExecutor()
    worker = make_worker(
        store,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert worker.run_once() is True
    assert executor.calls == []
    assert store.get(record.task_id).state is JobState.CANCELLED
    assert _pending_count(raw_client) == 0


def test_claim_not_found_deletes_the_entry_without_execution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    entry_id = _deliver(raw_client)
    store.delete(record.task_id)
    time.sleep(0.05)
    executor = SuccessExecutor()
    worker = make_worker(
        store,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            claim_min_idle=timedelta(milliseconds=1),
            timeout_policy=TinyTimeoutPolicy(),
        ),
    )
    assert worker.run_once() is True
    assert executor.calls == []
    assert raw_client.xrange(STREAM_KEY, "-", "+", count=10) == []
    assert entry_id


# --- Malformed minimal messages ---------------------------------------------


@pytest.mark.parametrize(
    "fields",
    [
        {"task_id": "t1"},
        {"task_id": "t1", "tool": "merge-pdf"},
        {"task_id": "t1", "tool": "merge-pdf", "route": "merge-pdf", "extra": "x"},
        {"task_id": "", "tool": "merge-pdf", "route": "merge-pdf"},
    ],
)
def test_malformed_entries_are_deleted_without_execution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
    fields: dict[str, str],
) -> None:
    queue = make_queue(stream_client, store, clock)
    queue.enqueue(make_record(clock, task_id="good"))
    stream_client.xadd(STREAM_KEY, fields)
    executor = SuccessExecutor()
    worker = make_worker(store, stream_client, executor, clock)
    # One entry per pass: the well-formed one executes and is released
    # (XDEL then XACK removes it from the stream), then the malformed one
    # is dropped without execution. No entry survives a pass.
    assert worker.run_once() is True
    assert worker.run_once() is True
    assert len(executor.calls) == 1
    remaining = cast(
        "list[tuple[bytes, dict[bytes, bytes]]]",
        raw_client.xrange(STREAM_KEY, "-", "+", count=10),
    )
    assert remaining == []


def test_non_utf8_entry_is_dropped_without_execution(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    queue = make_queue(stream_client, store, clock)
    queue.enqueue(make_record(clock, task_id="good"))
    raw_client.xadd(STREAM_KEY, {"task_id": b"\xff\xfe", "tool": b"merge", "route": b"merge-pdf"})
    executor = SuccessExecutor()
    worker = make_worker(store, stream_client, executor, clock)
    assert worker.run_once() is True
    assert worker.run_once() is True
    assert len(executor.calls) == 1
    remaining = cast(
        "list[tuple[bytes, dict[bytes, bytes]]]",
        raw_client.xrange(STREAM_KEY, "-", "+", count=10),
    )
    assert remaining == []


# --- Degradation and fail-closed behavior -----------------------------------


def test_redis_unavailable_degrades_the_worker(store: TaskStore, clock: FakeClock) -> None:
    failing = cast(StreamsRedisLike, _FailingStreamClient(ConnectionError("connection refused")))
    worker = make_worker(store, failing, SuccessExecutor(), clock)
    with pytest.raises(WorkerUnavailableError):
        worker.run_once()
    assert worker.healthy is False
    assert worker.in_flight is False


def test_store_unavailable_degrades_the_worker(clock: FakeClock) -> None:
    failing_store_client = cast(RedisLike, _FailingStreamClient(ConnectionError("store down")))
    broken_store = TaskStore(make_settings(), client=failing_store_client, clock=clock)
    stream = cast(StreamsRedisLike, fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    stream.xadd(STREAM_KEY, {"task_id": "job-1", "tool": "merge-pdf", "route": "merge-pdf"})
    worker = make_worker(broken_store, stream, SuccessExecutor(), clock)
    with pytest.raises(WorkerUnavailableError):
        worker.run_once()
    assert worker.healthy is False


def test_failures_log_only_safe_class_names(
    caplog: pytest.LogCaptureFixture, store: TaskStore, clock: FakeClock
) -> None:
    task_id = "sensitive-worker-task-99"
    failing = cast(StreamsRedisLike, _FailingStreamClient(ConnectionError("secret redis detail")))
    worker = make_worker(store, failing, SuccessExecutor(), clock)
    with caplog.at_level(logging.ERROR), pytest.raises(WorkerUnavailableError):
        worker.run_once()
    assert caplog.records
    for record in caplog.records:
        message = record.getMessage()
        assert task_id not in message
        assert "secret redis detail" not in message
        assert isinstance(record.__dict__.get("fields"), dict)


# --- F-3: bounded retry for terminal store outages --------------------------


def test_terminal_store_outage_retries_then_persists_and_acks(
    store: TaskStore, server: fakeredis.FakeServer, clock: FakeClock
) -> None:
    """A transient terminal-store outage retries with backoff and never
    loses the completed result; XACK fires only after the terminal write
    finally persists."""
    stream = cast(StreamsRedisLike, fakeredis.FakeRedis(server=server))
    flaky_proxy = _FlakyTerminalStore(store, failures=2)
    flaky = cast(TaskStore, flaky_proxy)
    verifying = _VerifyingAckClient(stream, flaky)
    queue = JobQueue(
        make_settings(),
        store,
        client=cast(StreamsRedisLike, verifying),
        options=QueueOptions(clock=clock),
    )
    record = enqueue_job(queue, clock)
    recorder = _RetryRecorder()
    worker = make_worker(
        flaky,
        cast(StreamsRedisLike, verifying),
        SuccessExecutor(),
        clock,
        options=WorkerOptions(
            terminal_retry=BoundedBackoffTerminalRetryPolicy(max_attempts=5, sleep=recorder),
        ),
    )
    assert worker.run_once() is True
    # Two failures, then the third terminal attempt persists.
    assert len(flaky_proxy.terminal_attempts) == 3
    assert [attempt[1] for attempt in flaky_proxy.terminal_attempts] == [
        JobEvent.RESULT_UPLOADED,
        JobEvent.RESULT_UPLOADED,
        JobEvent.RESULT_UPLOADED,
    ]
    # Bounded deterministic backoff: 0.25 s then 0.5 s, no wall-clock sleep.
    assert recorder.sleeps == [0.25, 0.5]
    assert worker.healthy is True
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.DONE
    assert fetched.result == SUCCESS_RESULT
    assert verifying.xack_calls
    assert _pending_count(cast(fakeredis.FakeRedis, stream)) == 0


def test_terminal_store_outage_exhausted_fails_closed_and_retains_pel(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    """Exhausting the bounded retries fails closed: the worker degrades,
    the executor is never re-invoked, the record stays processing, and the
    entry remains unacked in the PEL for later recovery."""
    flaky_proxy = _FlakyTerminalStore(store, failures=-1)
    flaky = cast(TaskStore, flaky_proxy)
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock)
    recorder = _RetryRecorder()
    executor = SuccessExecutor()
    worker = make_worker(
        flaky,
        stream_client,
        executor,
        clock,
        options=WorkerOptions(
            terminal_retry=BoundedBackoffTerminalRetryPolicy(max_attempts=3, sleep=recorder),
        ),
    )
    with pytest.raises(WorkerUnavailableError):
        worker.run_once()
    assert worker.healthy is False
    assert worker.in_flight is False
    # First attempt plus two retries, then the bound is exhausted.
    assert len(flaky_proxy.terminal_attempts) == 3
    assert recorder.sleeps == [0.25, 0.5]
    # At-most-once: exactly one executor invocation.
    assert len(executor.calls) == 1
    # The record is untouched: still processing, never converted to TIMEOUT
    # by the worker itself.
    fetched = store.get(record.task_id)
    assert fetched.state is JobState.PROCESSING
    assert fetched.result is None
    # Ack discipline: no terminal write -> no XACK, no XDEL; the entry is
    # retained in the PEL (fail-closed).
    assert _pending_count(cast(fakeredis.FakeRedis, stream_client)) == 1
    remaining = cast(
        "list[tuple[bytes, dict[bytes, bytes]]]",
        stream_client.xrange(STREAM_KEY, "-", "+", count=10),
    )
    assert [entry[1][b"task_id"] for entry in remaining] == [record.task_id.encode()]


# --- Timeout bound and lifecycle --------------------------------------------


def test_claim_min_idle_is_strictly_above_approved_max_timeout(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    default = make_worker(store, stream_client, SuccessExecutor(), clock)
    assert default.claim_min_idle > timedelta(seconds=180)
    approved_max = DefaultTimeoutPolicy(timedelta(seconds=300))
    worker = make_worker(
        store,
        stream_client,
        SuccessExecutor(),
        clock,
        options=WorkerOptions(timeout_policy=approved_max),
    )
    assert worker.claim_min_idle > timedelta(seconds=300)


def test_injected_claim_min_idle_must_exceed_policy_max(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    policy = DefaultTimeoutPolicy(timedelta(seconds=180))
    with pytest.raises(WorkerError):
        make_worker(
            store,
            stream_client,
            SuccessExecutor(),
            clock,
            options=WorkerOptions(
                timeout_policy=policy,
                claim_min_idle=timedelta(seconds=180),
            ),
        )


def test_worker_rejects_work_after_close(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    worker = make_worker(store, stream_client, SuccessExecutor(), clock)
    worker.close()
    assert worker.healthy is True
    with pytest.raises(WorkerError):
        worker.run_once()


def test_worker_error_hierarchy_is_typed() -> None:
    assert issubclass(WorkerUnavailableError, WorkerError)
    assert isinstance(WorkerUnavailableError(), WorkerError)


def test_worker_never_executes_a_cancelled_queued_job(
    server: fakeredis.FakeServer,
    stream_client: StreamsRedisLike,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    """DEC-069: a cancelled record is terminal; a raced pickup reconciles
    to an ack and never reaches the executor."""
    settings = make_settings()
    cas_client = cast(RedisLike, fakeredis.FakeRedis(server=server))
    store = TaskStore(
        settings,
        client=cas_client,
        clock=clock,
        cancel=CasCancelMechanism(cas_client, settings.retention_seconds),
    )
    queue = make_queue(stream_client, store, clock)
    record = enqueue_job(queue, clock, task_id="cancel-raced")
    store.cancel(record.task_id)
    assert store.get(record.task_id).state is JobState.CANCELLED

    executor = SuccessExecutor()
    worker = make_worker(store, stream_client, executor, clock)

    # the still-unpurged entry is picked up, the claim CAS loses, and the
    # worker reconciles against the terminal state: ack, no execution
    assert worker.run_once() is True
    assert executor.calls == []
    assert store.get(record.task_id).state is JobState.CANCELLED
    assert _pending_count(cast(fakeredis.FakeRedis, stream_client)) == 0


_SPAWN_TIMEOUT = timedelta(seconds=4)


def test_subprocess_runner_success_round_trip() -> None:
    runner = SubprocessJobRunner(SpawnSuccessExecutor())
    outcome = runner.run(_claimed_job(), _discard_report, _SPAWN_TIMEOUT)
    assert outcome == ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)


def test_subprocess_runner_forwards_progress() -> None:
    received: list[Progress] = []
    runner = SubprocessJobRunner(SpawnProgressExecutor())
    outcome = runner.run(_claimed_job(), received.append, _SPAWN_TIMEOUT)
    assert outcome == ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)
    assert received == [Progress(unit="engine_progress", value=5, total=10)]


def test_subprocess_runner_child_exception_fails_closed() -> None:
    runner = SubprocessJobRunner(SpawnRaisingExecutor())
    outcome = runner.run(_claimed_job(), _discard_report, _SPAWN_TIMEOUT)
    assert outcome is not None
    assert outcome.kind is ExecutionKind.FAILURE
    assert outcome.error == ENGINE_ERROR_FALLBACK


def test_subprocess_runner_child_crash_fails_closed() -> None:
    runner = SubprocessJobRunner(SpawnCrashingExecutor())
    outcome = runner.run(_claimed_job(), _discard_report, _SPAWN_TIMEOUT)
    assert outcome is not None
    assert outcome.kind is ExecutionKind.FAILURE
    assert outcome.error == ENGINE_ERROR_FALLBACK


def test_subprocess_runner_rejects_unpicklable_executor() -> None:
    class LocalExecutor:
        def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
            del job, report
            return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)

    with pytest.raises(WorkerError):
        SubprocessJobRunner(LocalExecutor())


def test_subprocess_runner_timeout_kills_and_reaps_child(tmp_path: Path) -> None:
    pid_path = tmp_path / "child.pid"
    runner = SubprocessJobRunner(SpawnHangingExecutor(str(pid_path)))
    driver, box = _run_in_thread(runner, _SPAWN_TIMEOUT)
    _wait_for_file(pid_path, deadline=10.0)
    _assert_thread_gone(driver)
    assert box["outcome"] is None
    pid = int(pid_path.read_text(encoding="utf-8"))
    _assert_process_gone(pid)


@pytest.mark.skipif(not hasattr(os, "killpg"), reason="POSIX process groups only")
def test_subprocess_runner_kill_fallback_reaps_sigterm_ignoring_child(tmp_path: Path) -> None:
    pid_path = tmp_path / "child.pid"
    runner = SubprocessJobRunner(
        SpawnSigtermIgnoringExecutor(str(pid_path)),
        terminate_grace=timedelta(seconds=0.2),
        kill_grace=timedelta(seconds=2.0),
    )
    driver, box = _run_in_thread(runner, _SPAWN_TIMEOUT)
    _wait_for_file(pid_path, deadline=10.0)
    _assert_thread_gone(driver)
    assert box["outcome"] is None
    pid = int(pid_path.read_text(encoding="utf-8"))
    _assert_process_gone(pid)


def test_worker_production_default_subprocess_injected_thread_explicit_runner(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    production = JobWorker(
        make_settings(),
        store,
        client=None,
        executor=SpawnSuccessExecutor(),
    )
    assert isinstance(production._runner, SubprocessJobRunner)
    test_built = make_worker(store, stream_client, SpawnSuccessExecutor(), clock)
    assert isinstance(test_built._runner, DaemonThreadJobRunner)
    stub = StubRunner([])
    explicit = make_worker(
        store,
        stream_client,
        SpawnSuccessExecutor(),
        clock,
        options=WorkerOptions(runner=stub),
    )
    assert isinstance(explicit._runner, StubRunner)


def test_worker_production_construction_fails_fast_on_unpicklable_executor(
    store: TaskStore,
) -> None:
    class LocalExecutor:
        def execute(self, job: ClaimedJob, report: Callable[[Progress], None]) -> ExecutionOutcome:
            del job, report
            return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=SUCCESS_RESULT)

    with pytest.raises(WorkerError):
        JobWorker(make_settings(), store, client=None, executor=LocalExecutor())


def test_worker_next_job_starts_only_after_prior_child_is_reaped(
    store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock, tmp_path: Path
) -> None:
    queue = make_queue(stream_client, store, clock)
    first = enqueue_job(queue, clock)
    second = enqueue_job(queue, clock)
    pid_path = tmp_path / "child.pid"
    runner = SubprocessJobRunner(SpawnFirstHangsThenSucceedsExecutor(first.task_id, str(pid_path)))
    worker = make_worker(
        store,
        stream_client,
        SpawnFirstHangsThenSucceedsExecutor(first.task_id, str(pid_path)),
        clock,
        options=WorkerOptions(
            runner=runner,
            timeout_policy=SlowTimeoutPolicy(_SPAWN_TIMEOUT),
        ),
    )
    assert worker.run_once() is True
    assert worker.in_flight is False
    assert store.get(first.task_id).state is JobState.FAILED
    first_record = store.get(first.task_id)
    assert first_record.error is not None
    assert first_record.error.code == "timeout"
    pid = int(pid_path.read_text(encoding="utf-8"))
    _assert_process_gone(pid)
    assert worker.run_once() is True
    assert store.get(second.task_id).state is JobState.DONE
    assert _pending_count(cast(fakeredis.FakeRedis, stream_client)) == 0
