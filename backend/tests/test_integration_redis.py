"""Real-Redis integration tests for BE-04/05/07/10 (Phase 3 gate exit).

Opt-in by contract: every test in this module runs against a REAL Redis
server (never fakeredis) and is skipped when ``REDIS_URL`` is unset.
When ``REDIS_URL`` IS set the fixture fails hard on an unreachable
server, so CI (which always sets ``REDIS_URL`` to the pinned service
container) breaks loudly on configuration drift instead of silently
skipping.

Deterministic execution:
  * the fixture FLUSHDBs the database selected by ``REDIS_URL`` before
    and after every test, so ``REDIS_URL`` must point at a dedicated
    database — CI uses db 15 of the pinned service container; local runs
    can use Docker (``docker run -d -p 6379:6379 redis:7.4.10-alpine``
    and ``REDIS_URL=redis://localhost:6379/15``) or any real Redis.
  * clocks are injected wherever the contract is time-dependent (BE-04
    deadline discovery, BE-05 max-wait cap, BE-07 drain); sleeps are
    bounded and only used to let Redis itself reap TTLs or to age a PEL
    entry past the stale-claim idle threshold.
  * races (BE-04 WATCH abort, BE-10 Lua atomicity) are constructed with
    explicit interleavings or worker threads plus a sampler — never
    timing-dependent assertion windows.

Bytes protocol: every client is built with ``decode_responses=False``
exactly like the production clients, so assertions observe the raw
protocol surface (``dict[bytes, bytes]`` hashes, byte entry ids).

Proven semantics map (unit suites keep proving the same contracts
against fakeredis; this suite proves them against a real server):
  * BE-04 store: bytes round-trip, TTL bounds + expiry, WATCH/MULTI/EXEC
    abort, CAS stale-state conflicts, corrupt-bytes fail-closed,
    unreachable-server fail-closed, deadline discovery pages.
  * BE-05 queue/worker: durable entry fields, length cap + rollback,
    MAXLEN race backstop, max-wait cap, readiness pause, end-to-end
    claim/process/ack, one in-flight job, stale-claim XAUTOCLAIM
    recovery, terminal reconciliation without re-execution, deleted-PEL
    entry drop.
  * BE-10 fair use: Lua counter cap/release/window TTL, concurrency race
    without overshoot, escalation ladder, degraded-DELAY fail-closed,
    queue seam integration.
  * BE-07 cleanup: expired-record drain over the real store and a
    recording deleter, including drain termination on the second pass.
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Iterator, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast

import pytest
import redis
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.queue.queue import (
    _APPEND_LUA,
    GROUP_NAME,
    AdmissionDecision,
    AdmissionPolicy,
    JobQueue,
    LuaAppendMechanism,
    QueueDelayedError,
    QueueFullError,
    QueueOptions,
    QueueUnavailableError,
    StreamsRedisLike,
)
from app.queue.store import (
    CorruptRecordError,
    InvalidRecordError,
    LuaRedisLike,
    RedisLike,
    StoreUnavailableError,
    TaskConflictError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.schemas.job import ErrorSummary, ResultSummary
from app.security.fair_use import (
    CONCURRENCY_KEY_PREFIX,
    FREQUENCY_KEY_PREFIX,
    CounterLimits,
    CounterRedisLike,
    FairUseDecision,
    FairUseOptions,
    FairUsePolicy,
    LuaFairUseCounter,
    fingerprint_origin,
)
from app.tasks.cleanup import CleanupCoordinator
from app.tasks.state_machine import JobEvent, JobState
from app.worker.worker import (
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    JobWorker,
    ProgressReporter,
    WorkerOptions,
)

REDIS_URL = os.environ.get("REDIS_URL")

pytestmark = pytest.mark.skipif(
    not REDIS_URL,
    reason="REDIS_URL unset: real-Redis integration tests opt in "
    "(CI runs them against the pinned Redis service container)",
)

_RESULT = ResultSummary(output_count=1, total_bytes=2048)
_SEAM_OBJECT = "tmp/2026-08-03/" + "d" * 32 + ".pdf"


class FakeClock:
    """Deterministic injectable time source."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def __call__(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += timedelta(seconds=seconds)


class RealRedis(Protocol):
    """Typed surface of the real Redis client consumed by this suite."""

    def ping(self) -> bool: ...
    def flushdb(self) -> bool: ...
    def close(self) -> None: ...
    def hgetall(self, name: str) -> dict[bytes, bytes]: ...
    def hset(
        self,
        name: str,
        key: str | None = None,
        value: bytes | str | None = None,
        mapping: Mapping[str, str] | None = None,
    ) -> int: ...
    def exists(self, name: str) -> int: ...
    def ttl(self, name: str) -> int: ...
    def delete(self, name: str) -> int: ...
    def get(self, name: str) -> bytes | None: ...
    def incr(self, name: str) -> int: ...
    def decr(self, name: str) -> int: ...
    def expire(self, name: str, time: int) -> bool: ...
    def scan_iter(self, match: str | None = None, count: int = 100) -> Iterator[bytes]: ...
    def pipeline(self, transaction: bool = True) -> Any: ...
    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int: ...
    def xadd(
        self,
        name: str,
        fields: Mapping[str, str],
        id: str = "*",
        maxlen: int | None = None,
        approximate: bool = True,
    ) -> bytes: ...
    def xlen(self, name: str) -> int: ...
    def xrange(
        self,
        name: str,
        start: str = "-",
        end: str = "+",
        count: int | None = None,
    ) -> list[tuple[bytes, dict[bytes, bytes]]]: ...
    def xgroup_create(
        self, name: str, groupname: str, id: str = "0", mkstream: bool = False
    ) -> None: ...
    def xreadgroup(
        self,
        groupname: str,
        consumername: str,
        streams: Mapping[str, str],
        count: int | None = None,
        block: int | None = None,
    ) -> list[tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]]]]: ...
    def xack(self, name: str, groupname: str, *ids: bytes) -> int: ...
    def xautoclaim(
        self,
        name: str,
        groupname: str,
        consumername: str,
        min_idle_time: int,
        start_id: bytes = b"0-0",
    ) -> tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]], list[bytes]]: ...
    def xdel(self, name: str, *ids: bytes) -> int: ...
    def xpending(self, name: str, groupname: str) -> dict[str, Any]: ...


class TinyTimeoutPolicy:
    """Execution timeout seam sized for fast integration tests.

    The stale-claim idle threshold must sit strictly above the maximum
    execution timeout (JobWorker enforces this), so both are tiny here.
    """

    def timeout_for(self, tool: str) -> timedelta:
        del tool
        return timedelta(seconds=1)

    def max_timeout(self) -> timedelta:
        return timedelta(seconds=1)


class RecordingExecutor:
    """JobExecutor recording claims; optionally blocks until released."""

    def __init__(self, outcome: ExecutionOutcome, *, hold: bool = False) -> None:
        self.outcome = outcome
        self.hold = hold
        self.jobs: list[ClaimedJob] = []
        self.started = threading.Event()
        self.release = threading.Event()

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        del report
        self.jobs.append(job)
        self.started.set()
        if self.hold:
            self.release.wait()
        return self.outcome


class RecordingDeleter:
    """ObjectDeleter recording every delete request."""

    def __init__(self) -> None:
        self.deleted: list[str] = []

    def delete_object(self, key: str) -> bool:
        self.deleted.append(key)
        return True


class PendingIdleAdapter:
    """Concrete adapter exposing the narrow idle-pending query to the waiter.

    Wraps the concrete ``redis.Redis`` client so the ``RealRedis`` protocol
    does not have to re-express the extended ``XPENDING IDLE min max count``
    options (which would widen its surface to six arguments). The waiter
    only ever queries every pending entry's idle time, so the adapter fixes
    the extended-query arguments here.
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    def pending_idle_ms(self, name: str, groupname: str) -> list[int]:
        entries = self._client.xpending_range(name, groupname, idle=0, min="-", max="+", count=100)
        return [int(cast(bytes, entry["time_since_delivered"])) for entry in entries]


def _make_settings(
    *,
    retention_seconds: int = 3600,
    max_queue_length: int = 2000,
    max_wait_seconds: int = 900,
) -> Settings:
    if REDIS_URL is None:
        raise AssertionError("REDIS_URL must be set for integration tests")
    return Settings(
        r2_account_id="test-account",
        r2_access_key_id="test-access-key-id",
        r2_secret_access_key="test-secret-access-key",
        r2_bucket_name="test-bucket",
        allowed_origins=("http://localhost:3000",),
        redis_url=REDIS_URL,
        retention_seconds=retention_seconds,
        max_queue_length=max_queue_length,
        max_wait_seconds=max_wait_seconds,
    )


def _open_client() -> RealRedis:
    if REDIS_URL is None:
        raise AssertionError("REDIS_URL must be set for integration tests")
    return cast(
        RealRedis,
        redis.Redis.from_url(
            REDIS_URL,
            decode_responses=False,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        ),
    )


def _wait_ready(client: RealRedis) -> None:
    last_error: Exception | None = None
    for _ in range(10):
        try:
            client.ping()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.5)
    raise AssertionError(f"REDIS_URL is set but the server is unreachable: {last_error!r}")


def _wait_pending_idle(
    client: Any,
    group: str,
    *,
    min_idle: float,
    timeout: float = 10.0,
) -> None:
    adapter = PendingIdleAdapter(client)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        idle_ms_values = adapter.pending_idle_ms("jobs", group)
        if not idle_ms_values:
            return
        if max(idle_ms_values) / 1000.0 >= min_idle:
            return
        time.sleep(0.2)
    raise AssertionError(
        f"pending entries in group {group!r} did not reach min idle {min_idle}s within timeout"
    )


def _run_recover_until_handled(worker: JobWorker, *, timeout: float = 10.0) -> bool:
    """Drive *worker* until a recovery pass reports work handled.

    A stale-claim entry becomes claimable only once its PEL idle time crosses
    the worker's ``claim_min_idle``; a single ``run_once()`` may land just
    before the boundary and return False. Bounded polling removes that
    wall-clock race deterministically.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if worker.run_once():
            return True
        time.sleep(0.2)
    return False


def _record(
    task_id: str,
    *,
    tool: str = "compress",
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    now = created_at if created_at is not None else datetime.now(UTC)
    return TaskRecord(
        task_id=task_id,
        state=JobState.QUEUED,
        tool=tool,
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=expires_at if expires_at is not None else now + timedelta(seconds=3600),
        objects=objects,
    )


@pytest.fixture
def redis_client() -> Iterator[RealRedis]:
    client = _open_client()
    _wait_ready(client)
    client.flushdb()
    try:
        yield client
    finally:
        client.flushdb()
        client.close()


@pytest.fixture
def store(redis_client: RealRedis) -> TaskStore:
    return TaskStore(_make_settings(), client=cast(RedisLike, redis_client))


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC))


# ---------------------------------------------------------------------------
# BE-04 — task store over real Redis
# ---------------------------------------------------------------------------


def test_store_bytes_protocol_round_trip_utf8(store: TaskStore, redis_client: RealRedis) -> None:
    created = _record("task-a1", tool="merge")
    stored = store.create(created)

    raw = redis_client.hgetall("task:task-a1")
    assert raw and all(isinstance(k, bytes) and isinstance(v, bytes) for k, v in raw.items())

    fetched = store.get("task-a1")
    assert fetched == stored
    assert fetched.tool == "merge"


def test_store_ttl_bounded_and_contract(
    store: TaskStore, redis_client: RealRedis, clock: FakeClock
) -> None:
    t0 = clock()
    ttl_store = TaskStore(
        _make_settings(retention_seconds=60), client=cast(RedisLike, redis_client), clock=clock
    )
    created = ttl_store.create(
        _record("task-ttl", created_at=t0, expires_at=t0 + timedelta(seconds=30))
    )

    ttl = ttl_store.ttl_seconds("task-ttl")
    assert 0 < ttl <= 30
    raw_ttl = redis_client.ttl("task:task-ttl")
    assert 0 < raw_ttl <= 30

    over_bound = _record("task-ttl-2", created_at=t0, expires_at=t0 + timedelta(seconds=61))
    with pytest.raises(Exception) as excinfo:
        ttl_store.create(over_bound)
    assert "expiry exceeds the retention bound" in str(excinfo.value)
    assert not redis_client.exists("task:task-ttl-2")
    assert created.expires_at > created.updated_at


def test_store_record_expires_by_ttl(store: TaskStore, redis_client: RealRedis) -> None:
    now = datetime.now(UTC)
    store.create(_record("task-exp", created_at=now, expires_at=now + timedelta(seconds=2)))

    assert store.ttl_seconds("task-exp") > 0
    time.sleep(2.2)
    with pytest.raises(TaskNotFoundError):
        store.get("task-exp")
    assert redis_client.exists("task:task-exp") == 0


def test_store_real_watch_abort(redis_client: RealRedis) -> None:
    key = "watch:target"
    redis_client.hset(key, mapping={"state": "queued"})

    pipeline = cast(Any, redis_client).pipeline(transaction=True)
    try:
        pipeline.watch(key)
        redis_client.hset(key, mapping={"state": "processing"})
        pipeline.multi()
        pipeline.hset(key, mapping={"state": "done"})
        with pytest.raises(redis.exceptions.WatchError):
            pipeline.execute()
    finally:
        pipeline.reset()

    assert redis_client.hgetall(key)[b"state"] == b"processing"


def test_store_cas_stale_expected_state_conflict(store: TaskStore) -> None:
    store.create(_record("task-cas", tool="split"))
    store.transition_state("task-cas", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)

    with pytest.raises(TaskConflictError):
        store.transition_state(
            "task-cas",
            JobEvent.RESULT_UPLOADED,
            expected_state=JobState.QUEUED,
            payload=TransitionPayload(result=_RESULT, objects=(_SEAM_OBJECT,)),
        )

    done = store.transition_state(
        "task-cas",
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=_RESULT, objects=(_SEAM_OBJECT,)),
    )
    assert done.state is JobState.DONE
    assert done.result == _RESULT


def test_store_duplicate_create_conflict(store: TaskStore) -> None:
    store.create(_record("task-dup"))
    with pytest.raises(TaskConflictError):
        store.create(_record("task-dup"))


def test_store_create_rejects_result_or_error_payload_on_new_record(
    store: TaskStore,
) -> None:
    with pytest.raises(InvalidRecordError):
        store.create(replace(_record("task-payload-result"), result=_RESULT))
    error = ErrorSummary(
        code="engine_error", category="engine", retryable=False, message_key="error.engine"
    )
    with pytest.raises(InvalidRecordError):
        store.create(replace(_record("task-payload-error"), error=error))


def test_store_corrupt_bytes_fail_closed(store: TaskStore, redis_client: RealRedis) -> None:
    store.create(_record("task-corrupt"))
    redis_client.hset("task:task-corrupt", "progress", b"\xff\xfe")
    with pytest.raises(CorruptRecordError):
        store.get("task-corrupt")


def test_store_unreachable_fail_closed() -> None:
    dead = Settings(
        r2_account_id="test-account",
        r2_access_key_id="test-access-key-id",
        r2_secret_access_key="test-secret-access-key",
        r2_bucket_name="test-bucket",
        allowed_origins=("http://localhost:3000",),
        redis_url="redis://127.0.0.1:1/0",
    )
    unreachable = TaskStore(dead)
    with pytest.raises(StoreUnavailableError):
        unreachable.create(_record("task-dead"))
    with pytest.raises(StoreUnavailableError):
        unreachable.get("task-dead")
    with pytest.raises(StoreUnavailableError):
        unreachable.delete("task-dead")


def test_store_list_expired_discovers_deadline_records(
    store: TaskStore, redis_client: RealRedis, clock: FakeClock
) -> None:
    deadline_store = TaskStore(_make_settings(), client=cast(RedisLike, redis_client), clock=clock)
    t0 = clock()
    for suffix in ("a", "b", "c"):
        deadline_store.create(
            _record(f"task-expired-{suffix}", created_at=t0, expires_at=t0 + timedelta(seconds=30))
        )
    deadline_store.create(
        _record("task-live", created_at=t0, expires_at=t0 + timedelta(seconds=300))
    )

    clock.advance(31)
    page = deadline_store.list_expired(clock(), limit=2)
    assert len(page) >= 1
    for record in deadline_store.list_expired(clock(), limit=100):
        assert record.task_id.startswith("task-expired-")

    for record in deadline_store.list_expired(clock(), limit=100):
        deadline_store.delete(record.task_id)
    assert deadline_store.list_expired(clock(), limit=100) == []


# ---------------------------------------------------------------------------
# BE-05 — queue and worker over real Redis
# ---------------------------------------------------------------------------


def test_queue_enqueue_durable_entry_fields(store: TaskStore, redis_client: RealRedis) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-q1", tool="compress"), origin="origin-a", route="compress")

    assert redis_client.xlen("jobs") == 1
    entries = redis_client.xrange("jobs", "-", "+")
    entry_id, fields = entries[0]
    assert isinstance(entry_id, bytes)
    assert dict(fields) == {
        b"task_id": b"task-q1",
        b"tool": b"compress",
        b"route": b"compress",
        b"origin": fingerprint_origin("origin-a").encode("utf-8"),
    }

    with pytest.raises(redis.exceptions.ResponseError):
        redis_client.xgroup_create("jobs", GROUP_NAME, id="0")


def test_queue_length_cap_full_and_rollback(store: TaskStore, redis_client: RealRedis) -> None:
    settings = _make_settings(max_queue_length=3)
    queue = JobQueue(settings, store, client=cast(StreamsRedisLike, redis_client))
    for suffix in ("1", "2", "3"):
        queue.enqueue(_record(f"task-cap-{suffix}"))

    with pytest.raises(QueueFullError):
        queue.enqueue(_record("task-cap-4"))

    assert redis_client.xlen("jobs") == 3
    with pytest.raises(TaskNotFoundError):
        store.get("task-cap-4")


def test_queue_maxlen_race_backstop(redis_client: RealRedis) -> None:
    for index in range(5):
        redis_client.xadd(
            "jobs",
            {"task_id": f"task-race-{index}", "tool": "compress", "route": "compress"},
            maxlen=3,
            approximate=False,
        )
    assert redis_client.xlen("jobs") == 3


def test_queue_atomic_append_rejects_at_cap_never_trims(
    redis_client: RealRedis,
) -> None:
    append = LuaAppendMechanism(cast(LuaRedisLike, redis_client))
    for index in range(3):
        redis_client.xadd(
            "jobs",
            {"task_id": f"filler-{index}", "tool": "compress", "route": "compress"},
        )
    appended = append.append(
        "jobs",
        {
            "task_id": "task-admitted-last",
            "tool": "compress",
            "route": "compress",
            "origin": fingerprint_origin("origin-a"),
        },
        maxlen=3,
    )
    assert appended is False
    assert redis_client.xlen("jobs") == 3
    assert redis_client.xrange("jobs", "-", "+")[0][1][b"task_id"] == b"filler-0"


def test_lua_append_below_cap_succeeds_and_writes_exact_four_fields(
    redis_client: RealRedis,
) -> None:
    """Production Lua append below the cap succeeds and writes exactly the
    DEC-174 four-field entry layout.

    ``LuaAppendMechanism`` is the production EVAL path (the queue's
    injected-client CAS seam never executes it, so this test is the only
    real-Redis proof that a below-cap production enqueue can admit).
    """
    append = LuaAppendMechanism(cast(LuaRedisLike, redis_client))
    appended = append.append(
        "jobs",
        {
            "task_id": "task-lua-below",
            "tool": "compress",
            "route": "compress",
            "origin": fingerprint_origin("https://lua.example"),
        },
        maxlen=3,
    )
    assert appended is True
    entries = redis_client.xrange("jobs", "-", "+")
    assert len(entries) == 1
    _, fields = entries[0]
    assert dict(fields) == {
        b"task_id": b"task-lua-below",
        b"tool": b"compress",
        b"route": b"compress",
        b"origin": fingerprint_origin("https://lua.example").encode("utf-8"),
    }


def test_production_lua_append_script_evals_supplied_field_values(
    redis_client: RealRedis,
) -> None:
    """The exact production ``_APPEND_LUA`` EVALs with the exact argument
    layout ``LuaAppendMechanism.append`` supplies.

    ``KEYS[1]`` plus five ARGV values (cap, task_id, tool, route, origin)
    is the entire argument surface; any drift — such as the script
    referencing ``ARGV[6]..ARGV[9]`` — fails the XADD with a Lua
    ``ResponseError`` instead of admitting the entry.
    """
    origin = fingerprint_origin("https://lua.example")
    result = redis_client.eval(
        _APPEND_LUA,
        1,
        "jobs",
        "3",
        "task-lua-script",
        "compress",
        "compress",
        origin,
    )
    assert int(result) == 1
    entries = redis_client.xrange("jobs", "-", "+")
    assert len(entries) == 1
    _, fields = entries[0]
    assert dict(fields) == {
        b"task_id": b"task-lua-script",
        b"tool": b"compress",
        b"route": b"compress",
        b"origin": origin.encode("utf-8"),
    }


def test_queue_concurrent_admissions_never_exceed_cap_nor_trim(
    store: TaskStore, redis_client: RealRedis
) -> None:
    settings = _make_settings(max_queue_length=3)
    queue = JobQueue(settings, store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-seed-1"))
    queue.enqueue(_record("task-seed-2"))

    barrier = threading.Barrier(4)
    outcomes: list[tuple[str, str]] = []

    def admit(name: str) -> None:
        barrier.wait()
        try:
            queue.enqueue(_record(name))
            outcomes.append(("ok", name))
        except QueueFullError:
            outcomes.append(("full", name))

    threads = [threading.Thread(target=admit, args=(f"task-race-{index}",)) for index in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert all(not thread.is_alive() for thread in threads)

    admitted = [name for status, name in outcomes if status == "ok"]
    rejected = [name for status, name in outcomes if status == "full"]
    assert len(outcomes) == 4
    assert len(admitted) == 1
    assert len(rejected) == 3
    for name in rejected:
        with pytest.raises(TaskNotFoundError):
            store.get(name)
    assert store.get(admitted[0]).state is JobState.QUEUED
    assert redis_client.xlen("jobs") == 3
    assert redis_client.xrange("jobs", "-", "+")[0][1][b"task_id"] == b"task-seed-1"


class _ExplodingPolicy:
    """Admission seam raising a non-QueueError (a misbehaving policy)."""

    def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision:
        del origin, tool, queued
        raise RuntimeError("admission policy bug")


def test_queue_non_queue_error_enqueue_rolls_back(
    store: TaskStore, redis_client: RealRedis
) -> None:
    queue = JobQueue(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        options=QueueOptions(policy=_ExplodingPolicy()),
    )
    with pytest.raises(RuntimeError):
        queue.enqueue(_record("task-boom"))
    with pytest.raises(TaskNotFoundError):
        store.get("task-boom")
    assert redis_client.xlen("jobs") == 0


def test_queue_max_wait_cap(store: TaskStore, redis_client: RealRedis) -> None:
    settings = _make_settings(max_queue_length=2000, max_wait_seconds=900)
    clock = FakeClock(datetime.now(UTC))
    queue = JobQueue(
        settings,
        store,
        client=cast(StreamsRedisLike, redis_client),
        options=QueueOptions(clock=clock),
    )
    queue.enqueue(_record("task-wait-1"))

    clock.advance(901)
    with pytest.raises(QueueFullError):
        queue.enqueue(_record("task-wait-2"))
    with pytest.raises(TaskNotFoundError):
        store.get("task-wait-2")


def test_queue_readiness_probe_pauses_admission(store: TaskStore, redis_client: RealRedis) -> None:
    queue = JobQueue(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        options=QueueOptions(readiness=lambda: False),
    )
    with pytest.raises(QueueUnavailableError):
        queue.enqueue(_record("task-paused"))
    with pytest.raises(TaskNotFoundError):
        store.get("task-paused")


def test_worker_end_to_end_claim_process_ack(store: TaskStore, redis_client: RealRedis) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-e2e", tool="compress"), route="compress")

    executor = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
    )
    worker = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=executor,
        options=WorkerOptions(consumer_name="worker-e2e"),
    )
    assert worker.run_once() is True

    record = store.get("task-e2e")
    assert record.state is JobState.DONE
    assert record.result == _RESULT
    assert executor.jobs[0].task_id == "task-e2e"
    pending = redis_client.xpending("jobs", GROUP_NAME)
    assert int(cast(bytes, pending["pending"])) == 0
    assert worker.healthy


def test_queue_capacity_recovers_after_successful_terminal_ack(
    store: TaskStore, redis_client: RealRedis
) -> None:
    settings = _make_settings(max_queue_length=1)
    queue = JobQueue(settings, store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-cap-terminal-1", tool="compress"), route="compress")

    worker = JobWorker(
        settings,
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=RecordingExecutor(
            ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
        ),
        options=WorkerOptions(consumer_name="worker-cap-terminal"),
    )
    assert worker.run_once() is True
    assert store.get("task-cap-terminal-1").state is JobState.DONE
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0

    queue.enqueue(_record("task-cap-terminal-2", tool="compress"), route="compress")
    assert store.get("task-cap-terminal-2").state is JobState.QUEUED
    assert redis_client.xlen("jobs") == 1


def test_queue_max_wait_ignores_terminally_acked_completed_entry(
    store: TaskStore, redis_client: RealRedis
) -> None:
    settings = _make_settings(max_queue_length=2000, max_wait_seconds=30)
    clock = FakeClock(datetime.now(UTC))
    queue = JobQueue(
        settings,
        store,
        client=cast(StreamsRedisLike, redis_client),
        options=QueueOptions(clock=clock),
    )
    queue.enqueue(_record("task-wait-terminal-1", tool="compress"), route="compress")

    worker = JobWorker(
        settings,
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=RecordingExecutor(
            ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
        ),
        options=WorkerOptions(consumer_name="worker-wait-terminal"),
    )
    assert worker.run_once() is True
    assert store.get("task-wait-terminal-1").state is JobState.DONE
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0

    clock.advance(31)
    queue.enqueue(_record("task-wait-terminal-2", tool="compress"), route="compress")
    assert store.get("task-wait-terminal-2").state is JobState.QUEUED
    assert redis_client.xlen("jobs") == 1


def test_worker_single_in_flight_job(store: TaskStore, redis_client: RealRedis) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-once", tool="merge"))

    executor = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,)),
        hold=True,
    )
    worker = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=executor,
        options=WorkerOptions(consumer_name="worker-once"),
    )
    runner = threading.Thread(target=worker.run_once)
    runner.start()
    assert executor.started.wait(timeout=5)
    assert worker.in_flight

    assert worker.run_once() is False
    assert len(executor.jobs) == 1

    executor.release.set()
    runner.join(timeout=5)
    assert not runner.is_alive()
    assert not worker.in_flight
    assert store.get("task-once").state is JobState.DONE
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


def test_worker_reclaims_stale_claim(store: TaskStore, redis_client: RealRedis) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-stale", tool="split"), route="split")

    crashed = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=RecordingExecutor(
            ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
        ),
        options=WorkerOptions(consumer_name="worker-crashed"),
    )
    assert crashed.run_once() is True  # claims and processes normally
    # simulate a second worker that reads the next job but crashes before
    # any store transition, leaving the entry pending in its PEL
    queue.enqueue(_record("task-stale-2", tool="split"), route="split")
    claims = redis_client.xreadgroup(GROUP_NAME, "worker-stuck", {"jobs": ">"}, count=1)
    assert claims and claims[0][1]
    assert store.get("task-stale-2").state is JobState.QUEUED

    _wait_pending_idle(redis_client, GROUP_NAME, min_idle=2.0)
    recorder = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
    )
    recoverer = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=recorder,
        options=WorkerOptions(
            consumer_name="worker-recoverer",
            timeout_policy=TinyTimeoutPolicy(),
            claim_min_idle=timedelta(seconds=2),
        ),
    )
    assert _run_recover_until_handled(recoverer)

    assert store.get("task-stale-2").state is JobState.DONE
    assert [job.task_id for job in recorder.jobs] == ["task-stale-2"]
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


def test_worker_acknowledges_terminal_without_reexecution(
    store: TaskStore, redis_client: RealRedis
) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-terminal", tool="compress"), route="compress")

    claims = redis_client.xreadgroup(GROUP_NAME, "worker-finished", {"jobs": ">"}, count=1)
    assert claims and claims[0][1]

    store.transition_state("task-terminal", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    store.transition_state(
        "task-terminal",
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=_RESULT, objects=(_SEAM_OBJECT,)),
    )

    _wait_pending_idle(redis_client, GROUP_NAME, min_idle=2.0)
    recorder = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
    )
    recoverer = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=recorder,
        options=WorkerOptions(
            consumer_name="worker-recoverer-2",
            timeout_policy=TinyTimeoutPolicy(),
            claim_min_idle=timedelta(seconds=2),
        ),
    )
    assert _run_recover_until_handled(recoverer)

    assert recorder.jobs == []
    assert store.get("task-terminal").state is JobState.DONE
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


def test_worker_drops_deleted_pending_entry(store: TaskStore, redis_client: RealRedis) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-deleted", tool="compress"), route="compress")

    claims = redis_client.xreadgroup(GROUP_NAME, "worker-dropped", {"jobs": ">"}, count=1)
    assert claims and claims[0][1]
    entry_id = claims[0][1][0][0]
    assert redis_client.xdel("jobs", entry_id) == 1

    _wait_pending_idle(redis_client, GROUP_NAME, min_idle=2.0)
    recorder = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
    )
    recoverer = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=recorder,
        options=WorkerOptions(
            consumer_name="worker-recoverer-3",
            timeout_policy=TinyTimeoutPolicy(),
            claim_min_idle=timedelta(seconds=2),
        ),
    )
    assert _run_recover_until_handled(recoverer)

    assert recorder.jobs == []
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


# ---------------------------------------------------------------------------
# BE-10 — fair-use Lua counters over real Redis
# ---------------------------------------------------------------------------


def test_lua_counter_cap_release_and_window(redis_client: RealRedis, clock: FakeClock) -> None:
    settings = _make_settings()
    policy = FairUsePolicy(
        settings,
        client=cast(CounterRedisLike, redis_client),
        options=FairUseOptions(
            max_concurrent_per_origin=2,
            window_seconds=60,
            delay_threshold=100,
            counter_ttl_seconds=60,
        ),
    )
    origin = "https://origin.example"
    fp = fingerprint_origin(origin)
    conc_key = f"{CONCURRENCY_KEY_PREFIX}:{fp}"
    freq_key = f"{FREQUENCY_KEY_PREFIX}:{fp}"

    decision = policy.evaluate(origin=origin, tool="compress", queued=0).decision
    assert decision is FairUseDecision.ALLOW
    decision = policy.evaluate(origin=origin, tool="compress", queued=0).decision
    assert decision is FairUseDecision.ALLOW
    decision = policy.evaluate(origin=origin, tool="compress", queued=0).decision
    assert decision is FairUseDecision.CHALLENGE

    assert int(redis_client.get(conc_key) or 0) == 2
    assert int(redis_client.get(freq_key) or 0) == 3
    assert redis_client.ttl(conc_key) > 0
    assert redis_client.ttl(freq_key) > 0

    policy.release(origin=origin)
    assert int(redis_client.get(conc_key) or 0) == 1
    policy.release(origin=origin)
    assert int(redis_client.get(conc_key) or 0) == 0
    policy.release(origin=origin)
    assert redis_client.get(conc_key) is None


def test_lua_counter_ttl_safety_net(redis_client: RealRedis) -> None:
    settings = _make_settings()
    policy = FairUsePolicy(
        settings,
        client=cast(CounterRedisLike, redis_client),
        options=FairUseOptions(
            window_seconds=1,
            delay_threshold=100,
            counter_ttl_seconds=1,
        ),
    )
    origin = "https://origin.example"
    fp = fingerprint_origin(origin)
    conc_key = f"{CONCURRENCY_KEY_PREFIX}:{fp}"

    policy.evaluate(origin=origin, tool="compress", queued=0)
    assert redis_client.exists(conc_key) == 1
    time.sleep(1.2)
    assert redis_client.exists(conc_key) == 0


def test_lua_concurrency_race_never_overshoots(redis_client: RealRedis) -> None:
    counter = LuaFairUseCounter(cast(CounterRedisLike, redis_client))
    limits = CounterLimits(cap=4, window_seconds=60, threshold=100, counter_ttl_seconds=60)
    fp = fingerprint_origin("https://race.example")
    conc_key = f"{CONCURRENCY_KEY_PREFIX}:{fp}"
    freq_key = f"{FREQUENCY_KEY_PREFIX}:{fp}"

    allowed = 0
    lock = threading.Lock()
    samples: list[int] = []

    def sampler() -> None:
        for _ in range(200):
            raw = redis_client.get(conc_key)
            with lock:
                samples.append(int(raw) if raw is not None else 0)
            time.sleep(0.001)

    def admit_burst() -> None:
        nonlocal allowed
        local = 0
        for _ in range(5):
            code = counter.admit(conc_key, freq_key, limits)
            if code == 1:
                local += 1
        with lock:
            allowed += local

    threads = [threading.Thread(target=admit_burst) for _ in range(8)]
    watcher = threading.Thread(target=sampler)
    watcher.start()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    watcher.join()

    assert allowed == limits.cap
    assert max(samples) <= limits.cap
    assert int(redis_client.get(conc_key) or 0) == limits.cap


def test_policy_escalation_ladder(redis_client: RealRedis) -> None:
    settings = _make_settings()
    policy = FairUsePolicy(
        settings,
        client=cast(CounterRedisLike, redis_client),
        options=FairUseOptions(
            window_seconds=60,
            delay_threshold=3,
            backoff_base_seconds=1,
            backoff_max_seconds=60,
            challenge_after_delays=1,
            reject_after_delays=3,
        ),
    )
    origin = "https://ladder.example"

    for _ in range(3):
        decision = policy.evaluate(origin=origin, tool="compress", queued=0).decision
    assert decision is FairUseDecision.ALLOW

    first = policy.evaluate(origin=origin, tool="compress", queued=0)
    assert first.decision is FairUseDecision.CHALLENGE
    assert first.retry_after_seconds == 1

    second = policy.evaluate(origin=origin, tool="compress", queued=0)
    assert second.decision is FairUseDecision.CHALLENGE
    assert second.retry_after_seconds == 2

    third = policy.evaluate(origin=origin, tool="compress", queued=0)
    assert third.decision is FairUseDecision.REJECT
    assert third.retry_after_seconds is None


def test_policy_degraded_delay_on_redis_loss() -> None:
    dead = Settings(
        r2_account_id="test-account",
        r2_access_key_id="test-access-key-id",
        r2_secret_access_key="test-secret-access-key",
        r2_bucket_name="test-bucket",
        allowed_origins=("http://localhost:3000",),
        redis_url="redis://127.0.0.1:1/0",
    )
    policy = FairUsePolicy(dead)
    outcome = policy.evaluate(origin="https://dead.example", tool="compress", queued=0)
    assert outcome.decision is FairUseDecision.DELAY
    assert outcome.degraded
    assert outcome.retryable
    policy.release(origin="https://dead.example")  # best-effort, never raises


def test_policy_admission_seam_through_queue(store: TaskStore, redis_client: RealRedis) -> None:
    settings = _make_settings()
    policy = FairUsePolicy(
        settings,
        client=cast(CounterRedisLike, redis_client),
        options=FairUseOptions(
            max_concurrent_per_origin=1,
            window_seconds=60,
            delay_threshold=100,
        ),
    )
    queue = JobQueue(
        settings,
        store,
        client=cast(StreamsRedisLike, redis_client),
        options=QueueOptions(policy=cast(AdmissionPolicy, policy)),
    )
    origin = "https://seam.example"

    queue.enqueue(_record("task-seam-1"), origin=origin, route="compress")
    with pytest.raises(QueueDelayedError):
        queue.enqueue(_record("task-seam-2"), origin=origin, route="compress")
    with pytest.raises(TaskNotFoundError):
        store.get("task-seam-2")
    assert redis_client.xlen("jobs") == 1


# ---------------------------------------------------------------------------
# BE-07 — cleanup drain over the real store
# ---------------------------------------------------------------------------


def test_cleanup_drain_real_store(
    store: TaskStore, redis_client: RealRedis, clock: FakeClock
) -> None:
    deadline_store = TaskStore(_make_settings(), client=cast(RedisLike, redis_client), clock=clock)
    t0 = clock()
    deleter = RecordingDeleter()
    coordinator = CleanupCoordinator(deadline_store, deleter, clock=clock)

    for index in range(3):
        deadline_store.create(
            _record(
                f"task-clean-{index}",
                created_at=t0,
                expires_at=t0 + timedelta(seconds=30),
                objects=(f"tmp/2026-08-03/{'a' * 32}-{index}.pdf",),
            )
        )
    deadline_store.create(
        _record(
            "task-clean-live",
            created_at=t0,
            expires_at=t0 + timedelta(seconds=300),
            objects=("tmp/2026-08-03/live.pdf",),
        )
    )

    clock.advance(31)
    run = coordinator.run_expired(limit=2)

    assert run.cleaned == 3
    assert run.already_clean == 0
    assert run.skipped == 0
    assert sorted(deleter.deleted) == [
        f"tmp/2026-08-03/{'a' * 32}-{index}.pdf" for index in range(3)
    ]
    for index in range(3):
        with pytest.raises(TaskNotFoundError):
            deadline_store.get(f"task-clean-{index}")
    assert deadline_store.get("task-clean-live").state is JobState.QUEUED

    second = coordinator.run_expired(limit=2)
    assert second.cleaned == 0
    assert second.already_clean == 0
    assert second.skipped == 0


def test_cancel_queued_wins_atomically_real_redis(
    store: TaskStore, redis_client: RealRedis
) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-cancel-queued", tool="compress"), route="compress")

    cancelled = queue.cancel("task-cancel-queued")

    assert cancelled.state is JobState.CANCELLED
    assert store.get("task-cancel-queued").state is JobState.CANCELLED
    # the atomic record cancel purged the still-unclaimed stream entry
    assert redis_client.xrange("jobs", "-", "+") == []

    executor = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
    )
    worker = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=executor,
        options=WorkerOptions(consumer_name="worker-cancel-queued"),
    )
    assert worker.run_once() is False
    assert executor.jobs == []
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


def test_cancel_after_pickup_reports_no_longer_available_real_redis(
    store: TaskStore, redis_client: RealRedis
) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    queue.enqueue(_record("task-cancel-picked", tool="split"), route="split")

    executor = RecordingExecutor(
        ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,)),
        hold=True,
    )
    worker = JobWorker(
        _make_settings(),
        store,
        client=cast(StreamsRedisLike, redis_client),
        executor=executor,
        options=WorkerOptions(consumer_name="worker-cancel-picked"),
    )
    runner = threading.Thread(target=worker.run_once)
    runner.start()
    assert executor.started.wait(timeout=5)
    assert store.get("task-cancel-picked").state is JobState.PROCESSING

    with pytest.raises(TaskConflictError):
        queue.cancel("task-cancel-picked")

    assert store.get("task-cancel-picked").state is JobState.PROCESSING
    executor.release.set()
    runner.join(timeout=5)
    assert not runner.is_alive()
    assert store.get("task-cancel-picked").state is JobState.DONE
    assert [job.task_id for job in executor.jobs] == ["task-cancel-picked"]
    assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


def test_cancel_worker_race_single_terminal_state(
    store: TaskStore, redis_client: RealRedis
) -> None:
    """Cancel racing worker pickup under real Redis: exactly one outcome.

    The worker's claim CAS and the Lua cancel serialize on the record
    hash, so the race has exactly two legal outcomes — cancelled without
    execution, or executed to done. Assertions are invariant-based
    post-conditions, never timing windows.
    """
    for index in range(6):
        task_id = f"task-cancel-race-{index}"
        queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
        queue.enqueue(_record(task_id, tool="compress"), route="compress")
        executor = RecordingExecutor(
            ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=_RESULT, objects=(_SEAM_OBJECT,))
        )
        worker = JobWorker(
            _make_settings(),
            store,
            client=cast(StreamsRedisLike, redis_client),
            executor=executor,
            options=WorkerOptions(consumer_name=f"worker-cancel-race-{index}"),
        )
        outcome: dict[str, object] = {}

        def claim_once(worker: JobWorker = worker, outcome: dict[str, object] = outcome) -> None:
            outcome["ran"] = worker.run_once()

        def cancel_once(
            queue: JobQueue = queue,
            task_id: str = task_id,
            outcome: dict[str, object] = outcome,
        ) -> None:
            try:
                outcome["cancelled"] = queue.cancel(task_id)
            except TaskConflictError:
                outcome["cancelled"] = None

        claimer = threading.Thread(target=claim_once)
        canceller = threading.Thread(target=cancel_once)
        claimer.start()
        canceller.start()
        claimer.join(timeout=10)
        canceller.join(timeout=10)
        assert not claimer.is_alive()
        assert not canceller.is_alive()

        record = store.get(task_id)
        if record.state is JobState.CANCELLED:
            assert executor.jobs == []
            assert outcome["cancelled"] is not None
        elif record.state is JobState.DONE:
            assert [job.task_id for job in executor.jobs] == [task_id]
            assert outcome["cancelled"] is None
        else:
            raise AssertionError(f"unexpected terminal state {record.state}")
        assert int(cast(bytes, redis_client.xpending("jobs", GROUP_NAME)["pending"])) == 0


def test_cancel_unknown_task_fails_closed_real_redis(
    store: TaskStore, redis_client: RealRedis
) -> None:
    queue = JobQueue(_make_settings(), store, client=cast(StreamsRedisLike, redis_client))
    with pytest.raises(TaskNotFoundError):
        queue.cancel("task-missing-cancel")


# ---------------------------------------------------------------------------
# Hotfix — production reproduction: create_app + readiness + BE-06/09 404
# ---------------------------------------------------------------------------


def test_factory_wires_store_and_readiness_against_real_redis(
    redis_client: RealRedis,
) -> None:
    """The production reproduction: ``create_app`` with production-style
    settings (compose Redis binding) wires the task store, readiness probes
    it accurately, and unknown tasks return the BE-06 404 contract instead
    of an internal_error."""
    app = create_app(settings=_make_settings())
    client = TestClient(app)

    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["checks"] == {"foundation": "ok", "redis": "ok"}
    assert ready.json()["deferred"] == ["worker"]

    response = client.get("/api/v1/tools/compress-pdf/tasks/does-not-exist/status")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_unknown_download_returns_404_through_wired_store(
    redis_client: RealRedis,
) -> None:
    """BE-09 download for an unknown task through the wired store returns the
    same stable 404 envelope as status (never internal_error)."""
    app = create_app(settings=_make_settings())
    client = TestClient(app)
    response = client.get("/api/v1/tools/compress-pdf/tasks/does-not-exist/download/0")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["error"]["category"] == "not_found"
