"""Contract tests for the Redis Streams job queue (BE-05).

The queue owns admission: idempotent consumer-group creation, bounded XADD
entries carrying only the opaque task id/tool/route (DEC-174), the approved
R-07 queue caps (length 2000, max wait 900 s) enforced fail-closed, and the
per-origin/round-robin admission seam (R-08) whose Redis-backed counters
arrive with BE-10. Stream semantics are exercised against ``fakeredis``
(pinned 2.37.0), which implements XGROUP CREATE / XADD / XREADGROUP /
XACK / XAUTOCLAIM / XLEN / XRANGE / XDEL including BusyGroup errors and
MAXLEN trimming.

Real-Redis gaps (reserved for the Phase 3 gate-exit integration wave, not
claimed here): cross-process admission races between the XLEN check and the
MAXLEN backstop, true per-origin round-robin ordering (requires per-origin
queues or a Lua reorder — out of scope), and real socket failure behavior.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import cast

import fakeredis
import pytest
from redis.exceptions import ConnectionError

from app.config import Settings
from app.queue.queue import (
    _APPEND_LUA,
    GROUP_NAME,
    STREAM_KEY,
    AdmissionDecision,
    AllowAllAdmission,
    CasAppendMechanism,
    JobQueue,
    LuaAppendMechanism,
    QueueDelayedError,
    QueueError,
    QueueFullError,
    QueueOptions,
    QueueRejectedError,
    QueueUnavailableError,
    StreamsRedisLike,
)
from app.queue.store import (
    CasCancelMechanism,
    RedisLike,
    StoreUnavailableError,
    TaskConflictError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.security.fair_use import fingerprint_origin
from app.tasks.state_machine import JobEvent, JobState

# The exact entry field vocabulary the queue writes (locked so BE-05's
# worker and later tool handlers can rely on the shape): the opaque task
# id, tool, route, and the opaque 64-hex origin fingerprint (DEC-174 /
# DEC-175 — the raw origin never enters the stream).
ENTRY_FIELDS = frozenset({"task_id", "tool", "route", "origin"})


class FakeClock:
    """Injectable queue clock: fixed start, explicit advances."""

    def __init__(self, start: datetime) -> None:
        self._now = start

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)

    def __call__(self) -> datetime:
        return self._now


def make_settings(*, max_queue_length: int = 2000, max_wait_seconds: int = 900) -> Settings:
    return Settings(
        r2_account_id="test",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test",
        allowed_origins=("http://localhost:3000",),
        max_queue_length=max_queue_length,
        max_wait_seconds=max_wait_seconds,
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


class _FailingClient:
    """Raises the configured exception from every queue-facing operation.

    Also implements the BE-04 store surface (hgetall/pipeline/ttl/delete)
    so it can double as a broken store client for the propagation test.
    """

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

    def xgroup_create(
        self, name: str, groupname: str, id: str = "0", mkstream: bool = False
    ) -> None:
        raise self._error

    def xadd(
        self, name: str, fields: dict[str, str], id: str = "*", maxlen: int | None = None
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
        start_id: str = "0-0",
    ) -> tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]], list[bytes]]:
        raise self._error

    def xlen(self, name: str) -> int:
        raise self._error

    def xrange(
        self, name: str, start: str = "-", end: str = "+", count: int | None = None
    ) -> list[tuple[bytes, dict[bytes, bytes]]]:
        raise self._error

    def xdel(self, name: str, *ids: bytes) -> int:
        raise self._error


class _RecordingPolicy:
    """Admission stub recording every call; behavior configured per test."""

    def __init__(self, decisions: list[AdmissionDecision]) -> None:
        self._decisions = decisions
        self.calls: list[tuple[str | None, str, int]] = []

    def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision:
        self.calls.append((origin, tool, queued))
        decision = self._decisions.pop(0) if self._decisions else AdmissionDecision.ALLOW
        return decision


@pytest.fixture
def clock() -> FakeClock:
    # Starts at the real now so the max-wait cap (which compares the stream
    # entry id, stamped by fakeredis's wall clock, against this clock) is
    # deterministic: advancing by > max_wait always ages the oldest entry.
    return FakeClock(datetime.now(UTC))


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def raw_client(server: fakeredis.FakeServer) -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(server=server)


@pytest.fixture
def stream_client(server: fakeredis.FakeServer) -> StreamsRedisLike:
    return cast(StreamsRedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def store_client(server: fakeredis.FakeServer) -> RedisLike:
    return cast(RedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def store(store_client: RedisLike, clock: FakeClock) -> TaskStore:
    return TaskStore(make_settings(), client=store_client, clock=clock)


@pytest.fixture
def queue(stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock) -> JobQueue:
    return JobQueue(make_settings(), store, client=stream_client, options=QueueOptions(clock=clock))


def _stream_fields(client: StreamsRedisLike) -> list[Mapping[bytes, bytes]]:
    entries = client.xrange(STREAM_KEY, "-", "+", count=100)
    return [fields for _, fields in entries]


# --- Enqueue and entry vocabulary -------------------------------------------


def test_enqueue_creates_record_and_exact_stream_entry(
    queue: JobQueue, store: TaskStore, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock, task_id="job-1")
    returned = queue.enqueue(record, origin="http://origin-a")
    assert returned.task_id == "job-1"
    assert store.get("job-1").state is JobState.QUEUED
    entries = _stream_fields(cast(StreamsRedisLike, raw_client))
    assert len(entries) == 1
    fields = {key.decode("utf-8"): value.decode("utf-8") for key, value in entries[0].items()}
    assert fields == {
        "task_id": "job-1",
        "tool": "merge-pdf",
        "route": "merge-pdf",
        "origin": fingerprint_origin("http://origin-a"),
    }
    assert set(fields) == ENTRY_FIELDS


def test_enqueue_accepts_explicit_route_override(
    queue: JobQueue, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock)
    queue.enqueue(record, route="compress-pdf")
    fields = _stream_fields(cast(StreamsRedisLike, raw_client))[0]
    assert fields[b"route"] == b"compress-pdf"
    assert fields[b"tool"] == record.tool.encode("utf-8")


def test_enqueue_duplicate_task_id_conflicts_and_preserves_first_entry(
    queue: JobQueue, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    record = make_record(clock, task_id="dup")
    queue.enqueue(record)
    with pytest.raises(TaskConflictError):
        queue.enqueue(make_record(clock, task_id="dup"))
    assert len(_stream_fields(cast(StreamsRedisLike, raw_client))) == 1


def test_group_creation_is_idempotent_across_instances(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    first = JobQueue(
        make_settings(), store, client=stream_client, options=QueueOptions(clock=clock)
    )
    second = JobQueue(
        make_settings(), store, client=stream_client, options=QueueOptions(clock=clock)
    )
    first.enqueue(make_record(clock))
    # A second instance must not fail on the already-existing group.
    second.enqueue(make_record(clock))
    assert stream_client.xlen(STREAM_KEY) == 2


def test_stream_and_group_names_are_locked() -> None:
    assert STREAM_KEY == "jobs"
    assert GROUP_NAME == "workers"


# --- Approved R-07 caps -----------------------------------------------------


def test_queue_rejects_above_approved_length_cap(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    capped = JobQueue(
        make_settings(max_queue_length=3),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock),
    )
    for _ in range(3):
        capped.enqueue(make_record(clock))
    assert stream_client.xlen(STREAM_KEY) == 3
    with pytest.raises(QueueFullError) as exc_info:
        capped.enqueue(make_record(clock))
    assert exc_info.value.retryable is True
    # The bound is enforced by admission: the stream never exceeds the cap.
    assert stream_client.xlen(STREAM_KEY) == 3


def test_queue_rejects_above_approved_wait_cap(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    capped = JobQueue(
        make_settings(max_wait_seconds=30),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock),
    )
    capped.enqueue(make_record(clock))
    clock.advance(31)
    with pytest.raises(QueueFullError):
        capped.enqueue(make_record(clock))
    assert stream_client.xlen(STREAM_KEY) == 1


def test_rejected_enqueue_rolls_back_the_store_record(
    queue: JobQueue, store: TaskStore, stream_client: StreamsRedisLike, clock: FakeClock
) -> None:
    capped = JobQueue(
        make_settings(max_queue_length=1),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock),
    )
    capped.enqueue(make_record(clock))
    record = make_record(clock)
    with pytest.raises(QueueFullError):
        capped.enqueue(record)
    # The unadmitted record must not survive as queued (phantom task).
    with pytest.raises(TaskNotFoundError):
        store.get(record.task_id)


def test_default_caps_come_from_approved_settings() -> None:
    settings = make_settings()
    assert settings.max_queue_length == 2000
    assert settings.max_wait_seconds == 900


# --- F-1: atomic check-and-XADD (admission rejects at cap, never trims) -----


def _fill_stream(client: StreamsRedisLike, *, count: int, prefix: str = "filler") -> None:
    for index in range(count):
        client.xadd(
            STREAM_KEY,
            {"task_id": f"{prefix}-{index}", "tool": "merge-pdf", "route": "merge-pdf"},
        )


def test_atomic_append_rejects_at_cap_and_never_trims(
    stream_client: StreamsRedisLike,
) -> None:
    append = CasAppendMechanism(stream_client)
    _fill_stream(stream_client, count=3)
    appended = append.append(
        STREAM_KEY,
        {"task_id": "admitted-last", "tool": "merge-pdf", "route": "merge-pdf"},
        maxlen=3,
    )
    assert appended is False
    entries = stream_client.xrange(STREAM_KEY, "-", "+")
    assert len(entries) == 3
    assert entries[0][1][b"task_id"] == b"filler-0"


def test_atomic_append_appends_when_below_cap(
    stream_client: StreamsRedisLike,
) -> None:
    append = CasAppendMechanism(stream_client)
    _fill_stream(stream_client, count=1)
    appended = append.append(
        STREAM_KEY,
        {"task_id": "job-2", "tool": "merge-pdf", "route": "merge-pdf"},
        maxlen=2,
    )
    assert appended is True
    entries = stream_client.xrange(STREAM_KEY, "-", "+")
    assert len(entries) == 2
    assert entries[1][1][b"task_id"] == b"job-2"


class _ScalarEvalClient:
    """EVAL seam replying with a scalar int exactly like real redis-py.

    ``redis-py`` decodes the Lua script's ``return 0``/``return 1`` as a
    scalar RESP integer (``int``), not a one-element list; this client
    records the script arguments so the entry vocabulary is locked too.
    """

    def __init__(self, reply: int) -> None:
        self._reply = reply
        self.calls: list[tuple[object, ...]] = []

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int:
        self.calls.append((script, numkeys, *keys_and_args))
        return self._reply


def test_lua_append_accepts_scalar_int_reply(
    clock: FakeClock,
) -> None:
    client = _ScalarEvalClient(1)
    append = LuaAppendMechanism(client)
    assert (
        append.append(
            STREAM_KEY,
            {
                "task_id": "job-1",
                "tool": "merge-pdf",
                "route": "merge-pdf",
                "origin": fingerprint_origin(None),
            },
            maxlen=3,
        )
        is True
    )
    script, numkeys, *args = client.calls[0]
    assert script == _APPEND_LUA
    assert numkeys == 1
    assert args == [
        "jobs",
        "3",
        "job-1",
        "merge-pdf",
        "merge-pdf",
        fingerprint_origin(None),
    ]

    rejected = _ScalarEvalClient(0)
    assert (
        LuaAppendMechanism(rejected).append(
            STREAM_KEY,
            {
                "task_id": "job-2",
                "tool": "merge-pdf",
                "route": "merge-pdf",
                "origin": fingerprint_origin(None),
            },
            maxlen=3,
        )
        is False
    )


def test_lua_append_accepts_list_reply(
    clock: FakeClock,
) -> None:
    class _ListEvalClient:
        def __init__(self, reply: int) -> None:
            self._reply = reply

        def eval(self, script: str, numkeys: int, *keys_and_args: str) -> list[bytes | int]:
            del script, numkeys, keys_and_args
            return [self._reply]

    assert (
        LuaAppendMechanism(_ListEvalClient(1)).append(
            STREAM_KEY,
            {
                "task_id": "job-1",
                "tool": "merge-pdf",
                "route": "merge-pdf",
                "origin": fingerprint_origin(None),
            },
            maxlen=3,
        )
        is True
    )
    assert (
        LuaAppendMechanism(_ListEvalClient(0)).append(
            STREAM_KEY,
            {
                "task_id": "job-2",
                "tool": "merge-pdf",
                "route": "merge-pdf",
                "origin": fingerprint_origin(None),
            },
            maxlen=3,
        )
        is False
    )


def test_lua_append_unknown_reply_fails_closed() -> None:
    append = LuaAppendMechanism(_ScalarEvalClient(7))
    with pytest.raises(QueueUnavailableError):
        append.append(
            STREAM_KEY,
            {
                "task_id": "job-1",
                "tool": "merge-pdf",
                "route": "merge-pdf",
                "origin": fingerprint_origin(None),
            },
            maxlen=3,
        )


class _BoomPolicy:
    """Admission seam raising a non-QueueError (a misbehaving policy)."""

    def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision:
        del origin, tool, queued
        raise RuntimeError("admission policy bug")


def test_non_queue_error_enqueue_rolls_back_and_re_raises(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    gated = JobQueue(
        make_settings(),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock, policy=_BoomPolicy()),
    )
    record = make_record(clock, task_id="phantom-1")
    with pytest.raises(RuntimeError):
        gated.enqueue(record)
    with pytest.raises(TaskNotFoundError):
        store.get("phantom-1")


# --- R-08 admission seam (round-robin / per-origin arrives with BE-10) ------


def test_admission_policy_seam_allow_delay_reject(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    policy = _RecordingPolicy(
        [AdmissionDecision.ALLOW, AdmissionDecision.DELAY, AdmissionDecision.REJECT]
    )
    gated = JobQueue(
        make_settings(),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock, policy=policy),
    )
    gated.enqueue(make_record(clock))
    with pytest.raises(QueueDelayedError) as delayed:
        gated.enqueue(make_record(clock))
    assert delayed.value.retryable is True
    with pytest.raises(QueueRejectedError) as rejected:
        gated.enqueue(make_record(clock))
    assert rejected.value.retryable is False


def test_admission_policy_receives_origin_tool_and_queued_count(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    policy = _RecordingPolicy([])
    gated = JobQueue(
        make_settings(),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock, policy=policy),
    )
    gated.enqueue(make_record(clock, task_id="a"), origin="http://origin-a")
    gated.enqueue(make_record(clock, task_id="b"), origin="http://origin-b")
    assert policy.calls == [
        ("http://origin-a", "merge-pdf", 0),
        ("http://origin-b", "merge-pdf", 1),
    ]


def test_round_robin_rotation_is_deterministic_through_the_seam(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    class RotatingPolicy:
        """Deterministic round-robin over origins: one allow per origin per
        cycle, delay on the second pass; no Redis counters involved.
        """

        def __init__(self) -> None:
            self._turns: dict[str | None, int] = {}
            self.allowed: list[str | None] = []

        def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision:
            del tool, queued
            turn = self._turns.get(origin, 0)
            if turn == 0:
                self._turns[origin] = turn + 1
                self.allowed.append(origin)
                return AdmissionDecision.ALLOW
            return AdmissionDecision.DELAY

    policy = RotatingPolicy()
    gated = JobQueue(
        make_settings(),
        store,
        client=stream_client,
        options=QueueOptions(clock=clock, policy=policy),
    )
    for task_id in ("a1", "b1", "a2", "b2"):
        record = make_record(clock, task_id=task_id)
        if task_id in ("a2", "b2"):
            with pytest.raises(QueueDelayedError):
                gated.enqueue(record, origin="http://origin-" + task_id[0])
        else:
            gated.enqueue(record, origin="http://origin-" + task_id[0])
    assert policy.allowed == ["http://origin-a", "http://origin-b"]
    assert [entry[b"task_id"].decode() for entry in _stream_fields(stream_client)] == [
        "a1",
        "b1",
    ]


def test_allow_all_admission_is_the_deterministic_default(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    policy = AllowAllAdmission()
    for origin in ("http://origin-a", "http://origin-b", None):
        assert policy.decide(origin=origin, tool="merge-pdf", queued=0) is AdmissionDecision.ALLOW
    # The queue constructed without a policy behaves identically.
    queue = JobQueue(
        make_settings(), store, client=stream_client, options=QueueOptions(clock=clock)
    )
    queue.enqueue(make_record(clock))
    assert stream_client.xlen(STREAM_KEY) == 1


# --- Fail-closed behavior ---------------------------------------------------


def test_redis_unavailable_fails_closed(store: TaskStore, clock: FakeClock) -> None:
    failing = cast(StreamsRedisLike, _FailingClient(ConnectionError("connection refused")))
    broken = JobQueue(make_settings(), store, client=failing, options=QueueOptions(clock=clock))
    with pytest.raises(QueueUnavailableError) as exc_info:
        broken.enqueue(make_record(clock))
    assert exc_info.value.retryable is True


def test_redis_unavailable_probes_fail_closed(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    failing = cast(StreamsRedisLike, _FailingClient(ConnectionError("connection refused")))
    broken = JobQueue(make_settings(), store, client=failing, options=QueueOptions(clock=clock))
    with pytest.raises(QueueUnavailableError):
        broken.stream_length()
    with pytest.raises(QueueUnavailableError):
        broken.enqueue(make_record(clock))


def test_store_unavailable_propagates_fail_closed(clock: FakeClock) -> None:
    failing = cast(RedisLike, _FailingClient(ConnectionError("connection refused")))
    broken_store = TaskStore(make_settings(), client=failing, clock=clock)
    stream = cast(StreamsRedisLike, fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    queue = JobQueue(
        make_settings(), broken_store, client=stream, options=QueueOptions(clock=clock)
    )
    with pytest.raises(StoreUnavailableError):
        queue.enqueue(make_record(clock))


def test_worker_degredation_probe_pauses_admission(
    stream_client: StreamsRedisLike, store: TaskStore, clock: FakeClock
) -> None:
    def probe() -> bool:
        return False

    gated = JobQueue(
        make_settings(), store, client=stream_client, options=QueueOptions(readiness=probe)
    )
    with pytest.raises(QueueUnavailableError):
        gated.enqueue(make_record(clock))
    # Recovery of the probe re-opens admission.
    gated = JobQueue(
        make_settings(),
        store,
        client=stream_client,
        options=QueueOptions(readiness=lambda: True),
    )
    gated.enqueue(make_record(clock))
    assert stream_client.xlen(STREAM_KEY) == 1


def test_failures_log_only_safe_class_names(
    caplog: pytest.LogCaptureFixture, store: TaskStore, clock: FakeClock
) -> None:
    task_id = "sensitive-queue-task-77"
    failing = cast(StreamsRedisLike, _FailingClient(ConnectionError("secret redis detail")))
    broken = JobQueue(make_settings(), store, client=failing, options=QueueOptions(clock=clock))
    with caplog.at_level(logging.ERROR), pytest.raises(QueueUnavailableError):
        broken.enqueue(make_record(clock, task_id=task_id))
    assert caplog.records
    for record in caplog.records:
        message = record.getMessage()
        assert task_id not in message
        assert "secret redis detail" not in message
        assert isinstance(record.__dict__.get("fields"), dict)


def test_stream_entries_never_carry_sensitive_fields(
    queue: JobQueue, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    queue.enqueue(make_record(clock, task_id="opaque-task-1"))
    fields = _stream_fields(cast(StreamsRedisLike, raw_client))[0]
    keys = {key.decode("utf-8") for key in fields}
    assert keys == ENTRY_FIELDS
    for key in keys:
        assert key not in ("filename", "password", "signed_url", "content", "preview", "token")


def test_queue_error_hierarchy_is_typed() -> None:
    assert issubclass(QueueUnavailableError, QueueError)
    assert issubclass(QueueFullError, QueueError)
    assert issubclass(QueueDelayedError, QueueError)
    assert issubclass(QueueRejectedError, QueueError)


# --- Cancellation surface (DEC-069) ---


def _make_cas_store(server: fakeredis.FakeServer, clock: FakeClock) -> TaskStore:
    """TaskStore whose cancel uses the CAS mechanism (fakeredis has no EVAL)."""
    settings = make_settings()
    client = cast(RedisLike, fakeredis.FakeRedis(server=server))
    return TaskStore(
        settings,
        client=client,
        clock=clock,
        cancel=CasCancelMechanism(client, settings.retention_seconds),
    )


def _make_cancel_queue(
    server: fakeredis.FakeServer,
    clock: FakeClock,
    store: TaskStore,
    client: StreamsRedisLike,
) -> JobQueue:
    return JobQueue(make_settings(), store, client=client, options=QueueOptions(clock=clock))


def test_cancel_queued_task_purges_entry_and_marks_terminal(
    server: fakeredis.FakeServer, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    store = _make_cas_store(server, clock)
    queue = _make_cancel_queue(server, clock, store, cast(StreamsRedisLike, raw_client))
    queue.enqueue(make_record(clock, task_id="cancel-q1"))

    cancelled = queue.cancel("cancel-q1")

    assert cancelled.state is JobState.CANCELLED
    assert store.get("cancel-q1").state is JobState.CANCELLED
    assert raw_client.xlen("jobs") == 0


def test_cancel_after_pickup_reports_no_longer_available(
    server: fakeredis.FakeServer, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    store = _make_cas_store(server, clock)
    queue = _make_cancel_queue(server, clock, store, cast(StreamsRedisLike, raw_client))
    queue.enqueue(make_record(clock, task_id="cancel-q2"))
    store.transition_state("cancel-q2", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)

    with pytest.raises(TaskConflictError):
        queue.cancel("cancel-q2")

    assert store.get("cancel-q2").state is JobState.PROCESSING
    assert raw_client.xlen("jobs") == 1


def test_cancel_unknown_task_raises_not_found_and_touches_nothing(
    server: fakeredis.FakeServer, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    store = _make_cas_store(server, clock)
    queue = _make_cancel_queue(server, clock, store, cast(StreamsRedisLike, raw_client))
    queue.enqueue(make_record(clock, task_id="cancel-keep"))

    with pytest.raises(TaskNotFoundError):
        queue.cancel("missing")

    assert raw_client.xlen("jobs") == 1
    assert store.get("cancel-keep").state is JobState.QUEUED


def test_cancel_second_attempt_conflicts_and_entry_stays_purged(
    server: fakeredis.FakeServer, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    store = _make_cas_store(server, clock)
    queue = _make_cancel_queue(server, clock, store, cast(StreamsRedisLike, raw_client))
    queue.enqueue(make_record(clock, task_id="cancel-q4"))
    queue.cancel("cancel-q4")

    with pytest.raises(TaskConflictError):
        queue.cancel("cancel-q4")

    assert raw_client.xlen("jobs") == 0
    assert store.get("cancel-q4").state is JobState.CANCELLED


def test_cancel_purge_failure_is_best_effort_and_never_raises(
    server: fakeredis.FakeServer, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    store = _make_cas_store(server, clock)
    good = _make_cancel_queue(server, clock, store, cast(StreamsRedisLike, raw_client))
    good.enqueue(make_record(clock, task_id="cancel-q5"))
    failing_stream = cast(StreamsRedisLike, _FailingClient(ConnectionError("secret redis detail")))
    queue = _make_cancel_queue(server, clock, store, failing_stream)

    cancelled = queue.cancel("cancel-q5")

    # the atomic record transition is authoritative; the purge is best-effort
    assert cancelled.state is JobState.CANCELLED
    assert store.get("cancel-q5").state is JobState.CANCELLED
    assert raw_client.xlen("jobs") == 1


def test_cancel_store_failure_propagates_and_preserves_entry(
    server: fakeredis.FakeServer, raw_client: fakeredis.FakeRedis, clock: FakeClock
) -> None:
    good_store = _make_cas_store(server, clock)
    good = _make_cancel_queue(server, clock, good_store, cast(StreamsRedisLike, raw_client))
    good.enqueue(make_record(clock, task_id="cancel-q6"))

    failing = cast(RedisLike, _FailingClient(ConnectionError("secret redis detail")))
    settings = make_settings()
    failing_store = TaskStore(
        settings,
        client=failing,
        clock=clock,
        cancel=CasCancelMechanism(failing, settings.retention_seconds),
    )
    queue = _make_cancel_queue(server, clock, failing_store, cast(StreamsRedisLike, raw_client))

    with pytest.raises(StoreUnavailableError):
        queue.cancel("cancel-q6")

    assert raw_client.xlen("jobs") == 1
    assert good_store.get("cancel-q6").state is JobState.QUEUED


def test_cancel_failures_log_only_safe_class_names(
    caplog: pytest.LogCaptureFixture,
    server: fakeredis.FakeServer,
    raw_client: fakeredis.FakeRedis,
    clock: FakeClock,
) -> None:
    task_id = "sensitive-cancel-task"
    good_store = _make_cas_store(server, clock)
    good = _make_cancel_queue(server, clock, good_store, cast(StreamsRedisLike, raw_client))
    good.enqueue(make_record(clock, task_id=task_id))

    failing = cast(RedisLike, _FailingClient(ConnectionError("secret redis detail")))
    settings = make_settings()
    failing_store = TaskStore(
        settings,
        client=failing,
        clock=clock,
        cancel=CasCancelMechanism(failing, settings.retention_seconds),
    )
    queue = _make_cancel_queue(server, clock, failing_store, cast(StreamsRedisLike, raw_client))
    with caplog.at_level(logging.ERROR), pytest.raises(StoreUnavailableError):
        queue.cancel(task_id)
    lines = [record.getMessage() for record in caplog.records]
    for line in lines:
        assert task_id not in line
        assert "secret redis detail" not in line
