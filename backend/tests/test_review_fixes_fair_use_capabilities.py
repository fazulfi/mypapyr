"""Contract tests for review blockers F-4 and F-5.

F-4 wires FairUsePolicy into production JobQueue admission and releases every
successful ALLOW concurrency claim exactly once on terminal / cancel /
rollback outcomes. The stream entry carries only the opaque 64-hex origin
fingerprint (never the raw origin); a per-claim release marker makes the
release idempotent across the worker terminal path, reconciliation,
cancellation, and enqueue rollback.

F-5 derives the advertised /api/v1/capabilities global contract from runtime
Settings so it cannot diverge from the enforced queue/store/fair-use limits,
never advertises a per-tool execution ceiling below the enforced default
timeout, and maps every QueueError deterministically to a BE-08 FailureCode.
"""

from __future__ import annotations

import dataclasses
import uuid as _uuid
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import cast

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.queue.queue import (
    STREAM_KEY,
    AppendMechanism,
    JobQueue,
    QueueDelayedError,
    QueueError,
    QueueFullError,
    QueueMaxWaitError,
    QueueOptions,
    QueueRejectedError,
    QueueUnavailableError,
    StreamsRedisLike,
)
from app.queue.store import (
    CasCancelMechanism,
    RedisLike,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.routers.capabilities import (
    CACHE_CONTROL,
    FailureCode,
    capabilities_payload,
    failure_code_for_queue_error,
    failure_code_meta,
)
from app.schemas.job import ResultSummary
from app.security.fair_use import (
    CONCURRENCY_KEY_PREFIX,
    CasFairUseCounter,
    CounterRedisLike,
    FairUseOptions,
    FairUsePolicy,
    fingerprint_origin,
)
from app.tasks.state_machine import JobEvent, JobState
from app.worker.worker import (
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    JobWorker,
    ProgressReporter,
    WorkerOptions,
)

ORIGIN_A = "https://origin-a.example"

RESULT = ResultSummary(output_count=1, total_bytes=2048)


def make_settings(*, max_queue_length: int = 2000) -> Settings:
    return Settings(
        r2_account_id="test",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test",
        allowed_origins=("http://localhost:3000",),
        max_queue_length=max_queue_length,
    )


def make_record(now: datetime, *, task_id: str | None = None) -> TaskRecord:
    return TaskRecord(
        task_id=task_id or _uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
    )


def conc_value(raw: fakeredis.FakeRedis, origin: str) -> int:
    value = raw.get(f"{CONCURRENCY_KEY_PREFIX}:{fingerprint_origin(origin)}")
    return int(value) if value is not None else 0


def policy_over(raw: fakeredis.FakeRedis, *, cap: int = 4) -> FairUsePolicy:
    return FairUsePolicy(
        make_settings(),
        client=cast(CounterRedisLike, raw),
        options=FairUseOptions(delay_threshold=100, max_concurrent_per_origin=cap),
        counter=CasFairUseCounter(cast(CounterRedisLike, raw)),
    )


def make_queue(
    raw: fakeredis.FakeRedis,
    store: TaskStore,
    *,
    policy: FairUsePolicy | None = None,
    append: AppendMechanism | None = None,
) -> JobQueue:
    return JobQueue(
        make_settings(),
        store,
        client=cast(StreamsRedisLike, raw),
        options=QueueOptions(policy=policy),
        append=append,
    )


def make_worker(raw: fakeredis.FakeRedis, store: TaskStore, *, policy: FairUsePolicy) -> JobWorker:
    return JobWorker(
        make_settings(),
        store,
        client=cast(StreamsRedisLike, raw),
        executor=SuccessExecutor(),
        options=WorkerOptions(releaser=policy),
    )


class SuccessExecutor:
    def __init__(self) -> None:
        self.jobs: list[ClaimedJob] = []

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        del report
        self.jobs.append(job)
        return ExecutionOutcome(kind=ExecutionKind.SUCCESS, result=RESULT)


class FailingAppend:
    def append(self, key: str, fields: Mapping[str, str], *, maxlen: int) -> bool:
        del key, fields, maxlen
        raise QueueUnavailableError("atomic append failed")


def _fixture_raw() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis()


def _fixture_store(raw: fakeredis.FakeRedis) -> TaskStore:
    return TaskStore(make_settings(), client=cast(RedisLike, raw))


def _fixture_cancel_store(raw: fakeredis.FakeRedis) -> TaskStore:
    client = cast(RedisLike, raw)
    return TaskStore(
        make_settings(),
        client=client,
        cancel=CasCancelMechanism(client, make_settings().retention_seconds),
    )


# ---------------------------------------------------------------------------
# F-4: production admission default and the stream-entry origin fingerprint
# ---------------------------------------------------------------------------


def test_production_queue_admission_default_is_settings_backed_fair_use() -> None:
    settings = make_settings(max_queue_length=50)
    store = _fixture_store(_fixture_raw())
    queue = JobQueue(settings, store)
    policy = queue.admission_policy
    assert isinstance(policy, FairUsePolicy)
    assert policy.max_concurrent_per_origin == settings.max_concurrent_per_origin
    assert type(policy).__name__ != "AllowAllAdmission"


def test_stream_entry_carries_opaque_origin_fingerprint_never_origin() -> None:
    raw = _fixture_raw()
    store = _fixture_store(raw)
    queue = make_queue(raw, store)
    queue.enqueue(make_record(datetime.now(UTC), task_id="fp-1"), origin=ORIGIN_A)
    entries = cast("list[tuple[bytes, dict[bytes, bytes]]]", raw.xrange(STREAM_KEY, "-", "+"))
    fields = entries[0][1]
    decoded = {key.decode(): value.decode() for key, value in fields.items()}
    assert set(decoded) == {"task_id", "tool", "route", "origin"}
    assert decoded["origin"] == fingerprint_origin(ORIGIN_A)
    assert len(decoded["origin"]) == 64
    int(decoded["origin"], 16)
    assert ORIGIN_A not in decoded["origin"]
    assert "example" not in decoded["origin"]


# ---------------------------------------------------------------------------
# F-4: exactly-once release on all lifecycle outcomes
# ---------------------------------------------------------------------------


def test_enqueue_failure_after_allow_releases_claim_once() -> None:
    now = datetime.now(UTC)
    raw = _fixture_raw()
    store = _fixture_store(raw)
    policy = policy_over(raw, cap=4)
    queue = make_queue(raw, store, policy=policy)
    failing = make_queue(raw, store, policy=policy, append=FailingAppend())
    for index in range(3):
        queue.enqueue(make_record(now, task_id=f"hold-{index}"), origin=ORIGIN_A)
    with pytest.raises(QueueUnavailableError):
        failing.enqueue(make_record(now, task_id="rollback-task"), origin=ORIGIN_A)
    with pytest.raises(TaskNotFoundError):
        store.get("rollback-task")
    assert conc_value(raw, ORIGIN_A) == 3
    queue.enqueue(make_record(now, task_id="after-1"), origin=ORIGIN_A)
    with pytest.raises(QueueDelayedError):
        queue.enqueue(make_record(now, task_id="after-2"), origin=ORIGIN_A)
    policy.release_fingerprint_claim(
        fingerprint=fingerprint_origin(ORIGIN_A), claim="rollback-task"
    )
    assert conc_value(raw, ORIGIN_A) == 4


def test_challenged_admission_reserves_no_claim() -> None:
    now = datetime.now(UTC)
    raw = _fixture_raw()
    store = _fixture_store(raw)
    policy = policy_over(raw, cap=3)
    queue = make_queue(raw, store, policy=policy)
    for index in range(3):
        queue.enqueue(make_record(now, task_id=f"full-{index}"), origin=ORIGIN_A)
    with pytest.raises(QueueDelayedError):
        queue.enqueue(make_record(now, task_id="overflow"), origin=ORIGIN_A)
    assert conc_value(raw, ORIGIN_A) == 3


def test_cancel_queued_releases_claim_exactly_once() -> None:
    now = datetime.now(UTC)
    raw = _fixture_raw()
    store = _fixture_cancel_store(raw)
    queue = make_queue(raw, store, policy=policy_over(raw, cap=4))
    queue.enqueue(make_record(now, task_id="cancel-task"), origin=ORIGIN_A)
    assert conc_value(raw, ORIGIN_A) == 1
    queue.cancel("cancel-task")
    assert conc_value(raw, ORIGIN_A) == 0
    for index in range(4):
        queue.enqueue(make_record(now, task_id=f"post-{index}"), origin=ORIGIN_A)
    with pytest.raises(QueueDelayedError):
        queue.enqueue(make_record(now, task_id="post-overflow"), origin=ORIGIN_A)


def test_release_marker_keys_never_contain_raw_origin() -> None:
    now = datetime.now(UTC)
    raw = _fixture_raw()
    store = _fixture_cancel_store(raw)
    queue = make_queue(raw, store, policy=policy_over(raw, cap=1))
    queue.enqueue(make_record(now, task_id="mk-1"), origin=ORIGIN_A)
    queue.cancel("mk-1")
    keys = {k.decode() if isinstance(k, bytes) else k for k in raw.keys("*")}
    assert keys
    for key in keys:
        assert ORIGIN_A not in key
        assert "example" not in key


def test_worker_terminal_release_exactly_once() -> None:
    now = datetime.now(UTC)
    raw = _fixture_raw()
    store = _fixture_store(raw)
    policy = policy_over(raw, cap=4)
    queue = make_queue(raw, store, policy=policy)
    queue.enqueue(make_record(now, task_id="w-1"), origin=ORIGIN_A)
    assert conc_value(raw, ORIGIN_A) == 1
    worker = make_worker(raw, store, policy=policy)
    assert worker.run_once() is True
    assert store.get("w-1").state is JobState.DONE
    assert conc_value(raw, ORIGIN_A) == 0
    policy.release_fingerprint_claim(fingerprint=fingerprint_origin(ORIGIN_A), claim="w-1")
    assert conc_value(raw, ORIGIN_A) == 0


def test_worker_reconciliation_release_is_idempotent() -> None:
    now = datetime.now(UTC)
    raw = _fixture_raw()
    store = _fixture_store(raw)
    policy = policy_over(raw, cap=4)
    queue = make_queue(raw, store, policy=policy)
    queue.enqueue(make_record(now, task_id="recon-1"), origin=ORIGIN_A)
    assert conc_value(raw, ORIGIN_A) == 1
    store.transition_state("recon-1", JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    store.transition_state(
        "recon-1",
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=RESULT),
    )
    policy.release_fingerprint_claim(fingerprint=fingerprint_origin(ORIGIN_A), claim="recon-1")
    assert conc_value(raw, ORIGIN_A) == 0
    worker = make_worker(raw, store, policy=policy)
    assert worker.run_once() is True
    assert store.get("recon-1").state is JobState.DONE
    assert conc_value(raw, ORIGIN_A) == 0


# ---------------------------------------------------------------------------
# F-5: advertised capabilities derived from Settings
# ---------------------------------------------------------------------------


def test_capabilities_payload_derives_global_limits_from_settings() -> None:
    overridden = dataclasses.replace(
        Settings.from_env(),
        retention_seconds=99,
        max_wait_seconds=7,
        max_queue_length=3,
        max_concurrent_per_origin=1,
        default_timeout_seconds=5,
    )
    payload = capabilities_payload(overridden)
    assert payload.global_limits.max_queue_length == 3
    assert payload.global_limits.max_wait_seconds == 7
    assert payload.global_limits.max_concurrent_per_origin == 1
    assert payload.global_limits.retention_seconds == 99
    assert payload.global_limits.default_timeout_seconds == 5


def test_capabilities_payload_without_settings_uses_canonical() -> None:
    payload = capabilities_payload()
    assert payload.global_limits.max_queue_length == 2000
    assert payload.global_limits.max_wait_seconds == 900
    assert payload.global_limits.max_concurrent_per_origin == 4


def test_advertised_timeout_never_below_enforced_default() -> None:
    overridden = dataclasses.replace(Settings.from_env(), default_timeout_seconds=240)
    payload = capabilities_payload(overridden)
    for limits in payload.tools.values():
        assert limits.max_execution_seconds >= 240


def test_capabilities_endpoint_reflects_runtime_settings_and_cache() -> None:
    settings = dataclasses.replace(Settings.from_env(), max_queue_length=77, max_wait_seconds=66)
    response = TestClient(create_app(settings)).get("/api/v1/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["global"]["maxQueueLength"] == 77
    assert body["global"]["maxWaitSeconds"] == 66
    assert response.headers["cache-control"] == CACHE_CONTROL


def test_capabilities_endpoint_defaults_match_approved() -> None:
    body = TestClient(create_app(Settings.from_env())).get("/api/v1/capabilities").json()
    assert body["global"] == {
        "retentionSeconds": 3600,
        "maxWaitSeconds": 900,
        "maxQueueLength": 2000,
        "maxConcurrentPerOrigin": 4,
        "defaultTimeoutSeconds": 180,
    }


def test_fair_use_policy_cap_derives_from_settings() -> None:
    settings = dataclasses.replace(Settings.from_env(), max_concurrent_per_origin=2)
    policy = FairUsePolicy(settings, client=cast(CounterRedisLike, fakeredis.FakeRedis()))
    assert policy.max_concurrent_per_origin == 2


# ---------------------------------------------------------------------------
# F-5: typed QueueError -> FailureCode bridge
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (QueueFullError, FailureCode.QUEUE_FULL),
        (QueueMaxWaitError, FailureCode.MAX_WAIT_EXCEEDED),
        (QueueUnavailableError, FailureCode.RATE_LIMITED),
        (QueueDelayedError, FailureCode.RATE_LIMITED),
        (QueueRejectedError, FailureCode.RATE_LIMITED),
    ],
)
def test_queue_error_bridge_is_deterministic(
    error: type[QueueError], expected: FailureCode
) -> None:
    assert failure_code_for_queue_error(error()) is expected


def test_queue_error_bridge_metadata_agrees_with_retryable() -> None:
    for error in (
        QueueFullError(),
        QueueMaxWaitError(),
        QueueDelayedError(),
        QueueUnavailableError(),
    ):
        code = failure_code_for_queue_error(error)
        assert failure_code_meta(code).retryable is error.retryable


def test_queue_error_bridge_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown queue error"):
        failure_code_for_queue_error(RuntimeError("boom"))
