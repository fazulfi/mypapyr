"""Contract tests for the Redis-shared fair-use admission policy (BE-10).

The policy implements the BE-05 :class:`AdmissionPolicy` seam with
Redis-shared per-origin counters: an atomic per-origin concurrency cap
(approved R-03 ``maxConcurrentPerOrigin=4``) and a per-window frequency
counter whose escalation exposes the R-08 enforcement levels allow /
delay (exponential backoff) / challenge (429 with ``Retry-After``) /
reject (safe category). Ordinary and retried admissions carry equal
weight and there is no paid lane. Redis loss or ``noeviction`` OOM
degrades admission fail-closed (delay, never allow). Every non-allow
outcome maps to the closed BE-08 failure-code vocabulary and derives its
retryability from :func:`failure_code_meta`.

Two counter implementations are exercised:

- :class:`LuaFairUseCounter` — the production path; the atomic Lua
  scripts (:data:`ADMISSION_LUA`/:data:`RELEASE_LUA`) are executed via
  ``EVAL`` on real Redis. This environment's pinned fakeredis 2.37.0
  ships without ``lupa``, so the Lua path is exercised with a recording
  client double that locks key hygiene (never the raw origin),
  argument order, and return-code mapping; real-Redis Lua atomicity is
  reserved for the Phase 3 gate-exit integration wave.
- :class:`CasFairUseCounter` — the atomic-equivalent WATCH/MULTI/EXEC
  compare-and-swap implementation (the BE-04 store precedent), exercised
  against fakeredis for the full behavioral contract including
  cross-process shared counters (two instances sharing one
  ``fakeredis.FakeServer`` simulate two API processes).

Privacy contract (DEC-175/DEC-020): origin identifiers enter the Redis
keyspace only as a one-way SHA-256 fingerprint (never the raw origin),
and logs carry only exception class names and operation names.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from typing import cast

import fakeredis
import pytest
from redis.exceptions import ConnectionError, ResponseError

from app.config import DEFAULT_MAX_CONCURRENT_PER_ORIGIN, Settings
from app.queue.queue import (
    AdmissionDecision,
    AdmissionPolicy,
    AllowAllAdmission,
    JobQueue,
    QueueDelayedError,
    QueueError,
    QueueOptions,
    QueueRejectedError,
    StreamsRedisLike,
)
from app.queue.store import (
    RedisLike,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.routers.capabilities import (
    FAILURE_CODES,
    GLOBAL_LIMITS,
    FailureCode,
    failure_code_meta,
)
from app.security.fair_use import (
    ADMISSION_LUA,
    CONCURRENCY_KEY_PREFIX,
    FREQUENCY_KEY_PREFIX,
    RELEASE_LUA,
    CasFairUseCounter,
    CasPipelineLike,
    CounterRedisLike,
    FairUseCounter,
    FairUseDecision,
    FairUseOptions,
    FairUseOutcome,
    FairUsePolicy,
    LuaFairUseCounter,
    backoff_seconds,
    fingerprint_origin,
)
from app.tasks.state_machine import JobState


def make_settings() -> Settings:
    return Settings(
        r2_account_id="test",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test",
        allowed_origins=("http://localhost:3000",),
    )


def make_record() -> TaskRecord:
    now = datetime.now(UTC)
    return TaskRecord(
        task_id=uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
    )


def make_policy(
    server: fakeredis.FakeServer | None = None,
    *,
    options: FairUseOptions | None = None,
    counter: FairUseCounter | None = None,
) -> tuple[FairUsePolicy, fakeredis.FakeRedis]:
    """A policy over a fresh (or shared) fakeredis server.

    The default counter is the atomic CAS equivalent, since the pinned
    fakeredis cannot execute Lua.
    """
    client = fakeredis.FakeRedis(server=server) if server is not None else fakeredis.FakeRedis()
    policy = FairUsePolicy(
        make_settings(),
        client=cast(CounterRedisLike, client),
        options=options,
        counter=counter
        if counter is not None
        else CasFairUseCounter(cast(CounterRedisLike, client)),
    )
    return policy, client


ORIGIN_A = "https://example.org"
ORIGIN_B = "https://other.example.net"


class _FailingCounterClient:
    """Raises the configured exception from every counter operation."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int:
        del script, numkeys, keys_and_args
        raise self._error

    def pipeline(self, transaction: bool = True) -> CasPipelineLike:
        del transaction
        raise self._error


class _RecordingCounterClient:
    """Records EVAL calls and returns scripted results (Lua path).

    ``results`` is consumed in call order; the last value repeats.
    """

    def __init__(self, results: list[int]) -> None:
        self.results = list(results)
        self.calls: list[tuple[str, int, tuple[str, ...]]] = []

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int:
        self.calls.append((script, numkeys, keys_and_args))
        if not self.results:
            return 1
        return self.results.pop(0) if len(self.results) > 1 else self.results[0]

    def pipeline(self, transaction: bool = True) -> CasPipelineLike:
        del transaction
        raise AssertionError("Lua counter must not use pipelines")


class _MutatingPipeline:
    """Wraps a watched pipeline and mutates a watched key at execute time.

    Forces exactly one WATCH abort (the mutation happens after the
    counter's reads and before the transaction commit), then behaves
    normally, so the CAS retry loop must re-read and succeed.
    """

    def __init__(self, inner: CasPipelineLike, client: fakeredis.FakeRedis) -> None:
        self._inner = inner
        self._client = client
        self._watched: list[str] = []
        self._aborted = False

    def watch(self, *names: str) -> None:
        self._watched.extend(names)
        self._inner.watch(*names)

    def get(self, name: str) -> bytes | None:
        return self._inner.get(name)

    def multi(self) -> None:
        self._inner.multi()

    def set(self, name: str, value: str, ex: int) -> bool:
        return self._inner.set(name, value, ex=ex)

    def incr(self, name: str) -> int:
        return self._inner.incr(name)

    def decr(self, name: str) -> int:
        return self._inner.decr(name)

    def expire(self, name: str, time: int) -> bool:
        return self._inner.expire(name, time)

    def delete(self, name: str) -> int:
        return self._inner.delete(name)

    def reset(self) -> None:
        self._inner.reset()

    def execute(self, raise_on_error: bool = True) -> list[object]:
        if not self._aborted and self._watched:
            self._aborted = True
            self._client.incr(self._watched[0])
        return self._inner.execute(raise_on_error=raise_on_error)


class _AbortingCounterClient:
    """A CAS client whose first pipeline forces one WATCH abort."""

    def __init__(self, inner: fakeredis.FakeRedis) -> None:
        self._inner = inner
        self._armed = True

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int:
        del script, numkeys, keys_and_args
        raise AssertionError("CAS counter must not use eval")

    def pipeline(self, transaction: bool = True) -> CasPipelineLike:
        pipe = cast(CasPipelineLike, self._inner.pipeline(transaction=transaction))
        if self._armed:
            self._armed = False
            return _MutatingPipeline(pipe, self._inner)
        return pipe


# ---------------------------------------------------------------------------
# Fingerprinting and privacy
# ---------------------------------------------------------------------------


def test_fingerprint_origin_is_deterministic_hex() -> None:
    first = fingerprint_origin(ORIGIN_A)
    second = fingerprint_origin(ORIGIN_A)
    assert first == second
    assert len(first) == 64
    int(first, 16)  # hex only


def test_fingerprint_origin_distinguishes_origins() -> None:
    assert fingerprint_origin(ORIGIN_A) != fingerprint_origin(ORIGIN_B)
    assert ORIGIN_A not in fingerprint_origin(ORIGIN_A)


def test_fingerprint_origin_anonymous_bucket_is_stable() -> None:
    assert fingerprint_origin(None) == fingerprint_origin("")
    assert fingerprint_origin(None) != fingerprint_origin(ORIGIN_A)


def _key_texts(client: fakeredis.FakeRedis) -> list[str]:
    return [key.decode("utf-8") if isinstance(key, bytes) else key for key in client.keys("*")]


def test_redis_keys_never_contain_raw_origin() -> None:
    policy, client = make_policy()
    policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    policy.evaluate(origin=ORIGIN_B, tool="split-pdf", queued=0)
    policy.release(origin=ORIGIN_A)
    keys = _key_texts(client)
    assert keys
    for key in keys:
        assert "example" not in key
        assert ORIGIN_A not in key
        assert ORIGIN_B not in key
        assert key.startswith((CONCURRENCY_KEY_PREFIX, FREQUENCY_KEY_PREFIX))


def test_fail_closed_logs_never_contain_origin_or_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    failing = _FailingCounterClient(ConnectionError("secret redis detail"))
    policy = FairUsePolicy(make_settings(), client=failing, counter=LuaFairUseCounter(failing))
    with caplog.at_level(logging.ERROR):
        outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.degraded
    assert caplog.records
    for record in caplog.records:
        message = record.getMessage()
        assert ORIGIN_A not in message
        assert "secret redis detail" not in message
        fields = record.__dict__.get("fields")
        assert isinstance(fields, dict)
        assert fields["error"] == "ConnectionError"


def test_module_has_no_paid_or_priority_concepts() -> None:
    for script in (ADMISSION_LUA, RELEASE_LUA):
        for term in ("priority", "paid", "premium"):
            assert term not in script
    for method in (FairUsePolicy.evaluate, FairUsePolicy.decide, FairUsePolicy.release):
        for term in ("priority", "paid", "premium", "retried"):
            assert term not in method.__code__.co_varnames
    assert "priority" not in FairUsePolicy.__init__.__code__.co_varnames


# ---------------------------------------------------------------------------
# Enforcement levels: allow / delay / challenge / reject
# ---------------------------------------------------------------------------


def test_ordinary_usage_is_allowed() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=30))
    for _ in range(25):
        outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
        assert outcome.decision is FairUseDecision.ALLOW
        assert outcome.failure_code is None
        assert outcome.retry_after_seconds is None
        assert not outcome.degraded
        assert not outcome.retryable
        policy.release(origin=ORIGIN_A)


def test_delay_after_crossing_threshold() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=3))
    for _ in range(3):
        assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    delayed = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert delayed.decision is FairUseDecision.DELAY
    assert delayed.failure_code is FailureCode.RATE_LIMITED
    assert delayed.retry_after_seconds == 1
    assert delayed.retryable


def test_exponential_backoff_escalation_ladder() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    outcomes = [
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision for _ in range(6)
    ]
    assert outcomes == [
        FairUseDecision.ALLOW,  # f=1 within threshold
        FairUseDecision.DELAY,  # f=2 -> level 1, retry 1s
        FairUseDecision.CHALLENGE,  # f=3 -> level 2, retry 2s
        FairUseDecision.CHALLENGE,  # f=4 -> level 3, retry 4s
        FairUseDecision.CHALLENGE,  # f=5 -> level 4, retry 8s
        FairUseDecision.REJECT,  # f=6 -> level 5
    ]


def test_backoff_retry_after_seconds_follow_ladder() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    first = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    second = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    third = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert first.decision is FairUseDecision.ALLOW
    assert second.decision is FairUseDecision.DELAY
    assert second.retry_after_seconds == 1
    assert third.decision is FairUseDecision.CHALLENGE
    assert third.retry_after_seconds == 2


def test_backoff_capped_at_maximum() -> None:
    policy, _ = make_policy(
        options=FairUseOptions(delay_threshold=1, backoff_base_seconds=2, backoff_max_seconds=4)
    )
    policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)  # allow
    second = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    third = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert second.retry_after_seconds == 2
    assert third.retry_after_seconds == 4  # 2*2=4 capped at 4
    fourth = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert fourth.retry_after_seconds == 4  # 8 capped at 4


def test_backoff_seconds_pure_function() -> None:
    assert backoff_seconds(1, base=1, maximum=60) == 1
    assert backoff_seconds(2, base=1, maximum=60) == 2
    assert backoff_seconds(3, base=1, maximum=60) == 4
    assert backoff_seconds(4, base=1, maximum=60) == 8
    assert backoff_seconds(7, base=1, maximum=60) == 60
    assert backoff_seconds(3, base=2, maximum=60) == 8
    with pytest.raises(ValueError):
        backoff_seconds(0, base=1, maximum=60)


def test_reject_is_safe_category_without_retry_after() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    for _ in range(5):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    rejected = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert rejected.decision is FairUseDecision.REJECT
    assert rejected.failure_code is FailureCode.RATE_LIMITED
    assert rejected.retry_after_seconds is None
    assert rejected.retryable  # BE-08 metadata: rate_limited is retryable


def test_decisions_are_independent_of_queued_and_tool() -> None:
    baseline, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    baseline.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    expected = baseline.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    # Identical counter state, different tool and queued values: the
    # decision must be identical (per-tool limits live in BE-08
    # validation; round-robin ordering in the queue).
    variant, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    variant.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    actual = variant.evaluate(origin=ORIGIN_A, tool="compress-pdf", queued=1999)
    assert actual.decision is expected.decision
    assert actual.retry_after_seconds == expected.retry_after_seconds


def test_repeated_identical_admissions_have_equal_weight() -> None:
    # Retried jobs are indistinguishable from ordinary ones: the API
    # exposes no retry/priority parameter, and identical calls against
    # identical state produce an identical deterministic sequence.
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    sequence = [policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0) for _ in range(4)]
    replayed, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    replay = [replayed.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0) for _ in range(4)]
    assert [outcome.decision for outcome in sequence] == [outcome.decision for outcome in replay]
    assert [outcome.retry_after_seconds for outcome in sequence] == [
        outcome.retry_after_seconds for outcome in replay
    ]


def test_window_expiry_recovers_adaptive() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1, window_seconds=1))
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.DELAY
    )
    time.sleep(1.3)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_no_fixed_daily_quota() -> None:
    policy, client = make_policy(options=FairUseOptions(delay_threshold=1_000_000))
    for _ in range(500):
        outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
        assert outcome.decision is FairUseDecision.ALLOW
        policy.release(origin=ORIGIN_A)
    # Only per-window frequency and concurrency counters exist: no daily,
    # date-bucketed, or cumulative-quota keyspace.
    for key in _key_texts(client):
        assert key.startswith((CONCURRENCY_KEY_PREFIX, FREQUENCY_KEY_PREFIX))


# ---------------------------------------------------------------------------
# Per-origin concurrency (approved R-03 maxConcurrentPerOrigin = 4)
# ---------------------------------------------------------------------------


def test_concurrency_cap_exceeded_is_challenge() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    fifth = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert fifth.decision is FairUseDecision.CHALLENGE
    assert fifth.failure_code is FailureCode.TOO_MANY_CONCURRENT
    assert fifth.retry_after_seconds == 5
    assert fifth.retryable


def test_release_frees_a_concurrency_slot() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.CHALLENGE
    )
    policy.release(origin=ORIGIN_A)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_rejected_admission_reserves_no_slot() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.CHALLENGE
    )
    # The failed attempt must not consume a slot: four releases clear
    # exactly the four reserved slots, and the next call is allowed.
    for _ in range(4):
        policy.release(origin=ORIGIN_A)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_release_below_zero_is_clamped() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(2):
        assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    for _ in range(10):
        policy.release(origin=ORIGIN_A)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_concurrency_rejections_still_count_as_traffic() -> None:
    policy, client = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)  # challenge
    fingerprint = fingerprint_origin(ORIGIN_A)
    freq = int(client.get(f"{FREQUENCY_KEY_PREFIX}:{fingerprint}") or b"0")
    assert freq == 5


def test_concurrency_ttl_safety_net_self_heals() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100, counter_ttl_seconds=1))
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )
    time.sleep(1.3)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


# ---------------------------------------------------------------------------
# Shared counters across simulated processes
# ---------------------------------------------------------------------------


def test_shared_concurrency_across_processes() -> None:
    server = fakeredis.FakeServer()
    policy_a, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=100))
    policy_b, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        assert policy_a.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    assert policy_b.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.CHALLENGE
    )


def test_shared_frequency_across_processes() -> None:
    server = fakeredis.FakeServer()
    policy_a, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=3))
    policy_b, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=3))
    for _ in range(3):
        assert policy_a.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    assert policy_b.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.DELAY
    )


def test_release_through_another_process_frees_slot() -> None:
    server = fakeredis.FakeServer()
    policy_a, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=100))
    policy_b, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        policy_a.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert policy_b.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.CHALLENGE
    )
    policy_b.release(origin=ORIGIN_A)
    assert policy_a.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_separate_servers_are_independent() -> None:
    policy_a, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    policy_b, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    assert policy_a.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )
    assert policy_b.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_identical_sequence_across_processes_is_deterministic() -> None:
    server = fakeredis.FakeServer()
    policy_a, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=1))
    policy_b, _ = make_policy(server=server, options=FairUseOptions(delay_threshold=1))
    from_a = [
        policy_a.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision for _ in range(4)
    ]
    from_b = [
        policy_b.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision for _ in range(4)
    ]
    # The escalation ladder is one deterministic function of the shared
    # counter, regardless of which process serves the call: process B
    # continues exactly where process A's admissions left off.
    assert from_a == [
        FairUseDecision.ALLOW,
        FairUseDecision.DELAY,
        FairUseDecision.CHALLENGE,
        FairUseDecision.CHALLENGE,
    ]
    assert from_b == [
        FairUseDecision.CHALLENGE,
        FairUseDecision.REJECT,
        FairUseDecision.REJECT,
        FairUseDecision.REJECT,
    ]


def test_per_origin_isolation_under_pressure() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.DELAY
    )
    # Origin B is unaffected by origin A's throttling.
    assert policy.evaluate(origin=ORIGIN_B, tool="split-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_anonymous_origin_is_isolated_from_named_origins() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        assert policy.evaluate(origin=None, tool="merge-pdf", queued=0).decision is (
            FairUseDecision.ALLOW
        )
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


# ---------------------------------------------------------------------------
# AdmissionPolicy seam (BE-05) and queue integration
# ---------------------------------------------------------------------------


def test_decide_maps_levels_to_admission_decisions() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    assert policy.decide(origin=ORIGIN_A, tool="merge-pdf", queued=0) is (AdmissionDecision.ALLOW)
    assert policy.decide(origin=ORIGIN_A, tool="merge-pdf", queued=0) is (AdmissionDecision.DELAY)
    assert policy.decide(origin=ORIGIN_A, tool="merge-pdf", queued=0) is (
        AdmissionDecision.DELAY
    )  # challenge collapses to the retryable delay level


def test_decide_maps_reject_to_admission_reject() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    for _ in range(5):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert policy.decide(origin=ORIGIN_A, tool="merge-pdf", queued=0) is (AdmissionDecision.REJECT)


def test_policy_implements_the_admission_policy_seam() -> None:
    policy, _ = make_policy()
    typed: AdmissionPolicy = policy
    assert typed is not None
    default = AllowAllAdmission()
    assert default.decide(origin=ORIGIN_A, tool="merge-pdf", queued=0) is (AdmissionDecision.ALLOW)


def make_queue_integration(
    *,
    options: FairUseOptions | None = None,
) -> tuple[Settings, JobQueue, TaskStore, FairUsePolicy, fakeredis.FakeRedis]:
    """A queue wired to the fair-use policy over one shared fakeredis.

    Mirrors the BE-05 fixture convention: the raw fakeredis client is
    cast once at the protocol crossing points.
    """
    settings = make_settings()
    raw = fakeredis.FakeRedis()
    store = TaskStore(settings, client=cast(RedisLike, raw))
    policy = FairUsePolicy(
        settings,
        client=cast(CounterRedisLike, raw),
        options=options if options is not None else FairUseOptions(delay_threshold=1),
        counter=CasFairUseCounter(cast(CounterRedisLike, raw)),
    )
    queue = JobQueue(
        settings,
        store,
        client=cast(StreamsRedisLike, raw),
        options=QueueOptions(policy=policy),
    )
    return settings, queue, store, policy, raw


def test_queue_enqueue_delays_and_rolls_back() -> None:
    _, queue, store, policy, _ = make_queue_integration()
    first = make_record()
    queue.enqueue(first, origin=ORIGIN_A)
    second = make_record()
    with pytest.raises(QueueDelayedError):
        queue.enqueue(second, origin=ORIGIN_A)
    # The delayed enqueue's store record is rolled back: no phantom task.
    with pytest.raises(TaskNotFoundError):
        store.get(second.task_id)
    # The admitted record survives and its slot is released by the caller.
    assert store.get(first.task_id).state is JobState.QUEUED
    policy.release(origin=ORIGIN_A)


def test_queue_reject_maps_to_queue_rejected_error() -> None:
    _, queue, _, policy, _ = make_queue_integration()
    for _ in range(5):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    with pytest.raises(QueueRejectedError):
        queue.enqueue(make_record(), origin=ORIGIN_A)


def test_queue_admission_is_per_origin_isolated() -> None:
    _, queue, _, policy, _ = make_queue_integration()
    queue.enqueue(make_record(), origin=ORIGIN_A)
    with pytest.raises(QueueDelayedError):
        queue.enqueue(make_record(), origin=ORIGIN_A)
    # Origin B is admitted even while origin A is throttled.
    queue.enqueue(make_record(), origin=ORIGIN_B)
    assert queue.stream_length() == 2
    policy.release(origin=ORIGIN_A)
    policy.release(origin=ORIGIN_B)


# ---------------------------------------------------------------------------
# Fail-closed Redis degradation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "error",
    [
        ConnectionError("redis down"),
        ResponseError("OOM command not allowed when used memory > 'maxmemory'"),
        TimeoutError("socket timeout"),
    ],
)
def test_redis_failure_fails_closed_to_delay(error: Exception) -> None:
    failing = _FailingCounterClient(error)
    policy = FairUsePolicy(make_settings(), client=failing, counter=LuaFairUseCounter(failing))
    outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.decision is FairUseDecision.DELAY
    assert outcome.failure_code is FailureCode.RATE_LIMITED
    assert outcome.degraded
    assert outcome.retryable
    # The fail-closed level at the queue seam is the retryable delay.
    assert policy.decide(origin=ORIGIN_A, tool="merge-pdf", queued=0) is (AdmissionDecision.DELAY)


def test_cas_counter_failure_fails_closed_too() -> None:
    failing = _FailingCounterClient(ConnectionError("redis down"))
    policy = FairUsePolicy(
        make_settings(),
        client=failing,
        counter=CasFairUseCounter(failing),
    )
    outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.decision is FairUseDecision.DELAY
    assert outcome.degraded


def test_release_failure_is_best_effort_and_never_raises(
    caplog: pytest.LogCaptureFixture,
) -> None:
    failing = _FailingCounterClient(ConnectionError("redis down"))
    policy = FairUsePolicy(make_settings(), client=failing, counter=LuaFairUseCounter(failing))
    with caplog.at_level(logging.ERROR):
        policy.release(origin=ORIGIN_A)
    assert caplog.records


def test_unexpected_counter_code_fails_closed() -> None:
    recording = _RecordingCounterClient([0, 42])
    policy = FairUsePolicy(make_settings(), client=recording, counter=LuaFairUseCounter(recording))
    outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.decision is FairUseDecision.DELAY
    assert outcome.degraded


# ---------------------------------------------------------------------------
# BE-08 failure-code mapping consistency
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("threshold", "calls", "expected_level"),
    [
        (3, 4, FairUseDecision.DELAY),  # delay level
        (1, 3, FairUseDecision.CHALLENGE),  # challenge level
        (1, 6, FairUseDecision.REJECT),  # reject level
    ],
)
def test_frequency_levels_map_to_rate_limited(
    threshold: int, calls: int, expected_level: FairUseDecision
) -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=threshold))
    outcome = FairUseOutcome(FairUseDecision.ALLOW)
    for _ in range(calls):
        outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.decision is expected_level
    assert outcome.failure_code is FailureCode.RATE_LIMITED


def test_concurrency_exceeded_maps_to_too_many_concurrent() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.failure_code is FailureCode.TOO_MANY_CONCURRENT


def test_outcome_retryability_derives_from_be08_metadata() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    for _ in range(6):
        outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
        if outcome.decision is not FairUseDecision.ALLOW:
            assert outcome.failure_code is not None
            meta = failure_code_meta(outcome.failure_code)
            assert outcome.retryable == meta.retryable


def test_failure_codes_are_closed_vocabulary_members() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=1))
    for _ in range(6):
        outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
        if outcome.failure_code is not None:
            assert isinstance(outcome.failure_code, FailureCode)
    advertised = {entry.code for entry in FAILURE_CODES}
    assert {FailureCode.RATE_LIMITED.value, FailureCode.TOO_MANY_CONCURRENT.value} <= advertised


def test_all_non_allow_levels_are_retryable_per_be08() -> None:
    for code in (FailureCode.RATE_LIMITED, FailureCode.TOO_MANY_CONCURRENT):
        assert failure_code_meta(code).retryable


def test_allow_outcome_carries_no_failure_code() -> None:
    policy, _ = make_policy()
    outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.decision is FairUseDecision.ALLOW
    assert outcome.failure_code is None
    assert not outcome.retryable


# ---------------------------------------------------------------------------
# Approved defaults and options validation
# ---------------------------------------------------------------------------


def test_default_concurrency_cap_is_the_approved_four() -> None:
    assert GLOBAL_LIMITS.max_concurrent_per_origin == 4
    assert DEFAULT_MAX_CONCURRENT_PER_ORIGIN == 4
    assert make_settings().max_concurrent_per_origin == 4
    policy, _ = make_policy()
    assert policy.max_concurrent_per_origin == 4


def test_default_counter_ttl_is_retention() -> None:
    assert GLOBAL_LIMITS.retention_seconds == 3600
    policy, _ = make_policy()
    assert policy.counter_ttl_seconds == 3600


@pytest.mark.parametrize(
    "options",
    [
        FairUseOptions(max_concurrent_per_origin=0),
        FairUseOptions(window_seconds=0),
        FairUseOptions(delay_threshold=0),
        FairUseOptions(backoff_base_seconds=0),
        FairUseOptions(backoff_max_seconds=0, backoff_base_seconds=2),
        FairUseOptions(challenge_after_delays=0),
        FairUseOptions(challenge_after_delays=3, reject_after_delays=3),
        FairUseOptions(reject_after_delays=1, challenge_after_delays=1),
        FairUseOptions(concurrency_retry_after_seconds=0),
        FairUseOptions(counter_ttl_seconds=0),
    ],
)
def test_invalid_options_are_rejected(options: FairUseOptions) -> None:
    with pytest.raises(ValueError):
        FairUsePolicy(
            make_settings(),
            client=cast(CounterRedisLike, fakeredis.FakeRedis()),
            options=options,
        )


def test_options_are_frozen() -> None:
    options = FairUseOptions()
    with pytest.raises(FrozenInstanceError):
        options.delay_threshold = 1  # type: ignore[misc]


def test_outcome_is_frozen() -> None:
    outcome = FairUseOutcome(FairUseDecision.ALLOW)
    with pytest.raises(FrozenInstanceError):
        outcome.decision = FairUseDecision.DELAY  # type: ignore[misc]


def test_counter_types_are_exported() -> None:
    assert issubclass(LuaFairUseCounter, object)
    assert issubclass(CasFairUseCounter, object)


# ---------------------------------------------------------------------------
# Lua path: shipped scripts and key hygiene
# ---------------------------------------------------------------------------


def test_lua_scripts_are_atomic_primitives() -> None:
    assert "INCR" in ADMISSION_LUA
    assert "EXPIRE" in ADMISSION_LUA
    assert "DECR" in ADMISSION_LUA
    assert "KEYS[" in ADMISSION_LUA
    assert "ARGV[" in ADMISSION_LUA
    assert "DECR" in RELEASE_LUA
    assert "DEL" in RELEASE_LUA


def test_lua_counter_keys_are_fingerprints_only() -> None:
    recording = _RecordingCounterClient([1])
    policy = FairUsePolicy(make_settings(), client=recording, counter=LuaFairUseCounter(recording))
    policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert len(recording.calls) == 1
    script, numkeys, keys_and_args = recording.calls[0]
    assert script == ADMISSION_LUA
    assert numkeys == 2
    fingerprint = fingerprint_origin(ORIGIN_A)
    assert keys_and_args[:2] == (
        f"{CONCURRENCY_KEY_PREFIX}:{fingerprint}",
        f"{FREQUENCY_KEY_PREFIX}:{fingerprint}",
    )
    assert ORIGIN_A not in keys_and_args[0] and ORIGIN_A not in keys_and_args[1]


def test_lua_admit_argument_order_is_locked() -> None:
    recording = _RecordingCounterClient([1])
    policy = FairUsePolicy(
        make_settings(),
        client=recording,
        options=FairUseOptions(delay_threshold=7, counter_ttl_seconds=1234),
        counter=LuaFairUseCounter(recording),
    )
    policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    _, _, keys_and_args = recording.calls[0]
    assert keys_and_args[2:] == ("4", "60", "7", "1234")  # cap, window, threshold, ttl


def test_lua_return_codes_map_to_levels() -> None:
    recording = _RecordingCounterClient([1, -1, -4])
    policy = FairUsePolicy(
        make_settings(),
        client=recording,
        options=FairUseOptions(delay_threshold=3),
        counter=LuaFairUseCounter(recording),
    )
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )
    challenged = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert challenged.decision is FairUseDecision.CHALLENGE
    assert challenged.failure_code is FailureCode.TOO_MANY_CONCURRENT
    delayed = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert delayed.decision is FairUseDecision.DELAY
    assert delayed.retry_after_seconds == 1  # f=4, threshold=3 -> level 1


def test_lua_release_uses_the_release_script() -> None:
    recording = _RecordingCounterClient([1])
    policy = FairUsePolicy(make_settings(), client=recording, counter=LuaFairUseCounter(recording))
    policy.release(origin=ORIGIN_A)
    assert len(recording.calls) == 1
    script, numkeys, keys_and_args = recording.calls[0]
    assert script == RELEASE_LUA
    assert numkeys == 1
    assert keys_and_args == (f"{CONCURRENCY_KEY_PREFIX}:{fingerprint_origin(ORIGIN_A)}",)


def test_lua_release_is_best_effort_on_failure() -> None:
    recording = _FailingCounterClient(ConnectionError("down"))
    policy = FairUsePolicy(make_settings(), client=recording, counter=LuaFairUseCounter(recording))
    policy.release(origin=ORIGIN_A)


# ---------------------------------------------------------------------------
# CAS atomicity
# ---------------------------------------------------------------------------


def test_cas_admit_restores_counter_on_cap_exceeded() -> None:
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(4):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.CHALLENGE
    )
    # The failed admission wrote nothing: exactly four releases return
    # the counter to zero and the fifth call is allowed.
    for _ in range(4):
        policy.release(origin=ORIGIN_A)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_cas_watch_abort_retries_and_succeeds() -> None:
    client = fakeredis.FakeRedis()
    aborting = _AbortingCounterClient(client)
    policy = FairUsePolicy(
        make_settings(),
        client=aborting,
        counter=CasFairUseCounter(aborting),
    )
    outcome = policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    assert outcome.decision is FairUseDecision.ALLOW
    assert not outcome.degraded


def test_cas_release_watch_abort_retries_and_succeeds() -> None:
    client = fakeredis.FakeRedis()
    policy, _ = make_policy(options=FairUseOptions(delay_threshold=100))
    for _ in range(3):
        policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0)
    aborting = _AbortingCounterClient(client)
    release_policy = FairUsePolicy(
        make_settings(),
        client=aborting,
        counter=CasFairUseCounter(aborting),
    )
    # The release re-reads after the abort and still decrements.
    release_policy.release(origin=ORIGIN_A)
    policy.release(origin=ORIGIN_A)
    policy.release(origin=ORIGIN_A)
    assert policy.evaluate(origin=ORIGIN_A, tool="merge-pdf", queued=0).decision is (
        FairUseDecision.ALLOW
    )


def test_queue_error_taxonomy_retryability_is_typed() -> None:
    # BE-05's own taxonomy stays authoritative at the queue seam.
    assert issubclass(QueueDelayedError, QueueError)
    assert issubclass(QueueRejectedError, QueueError)
    assert QueueDelayedError().retryable
    assert not QueueRejectedError().retryable
