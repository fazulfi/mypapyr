"""Redis-shared adaptive fair-use admission policy (BE-10).

Consumed by the BE-05 :class:`AdmissionPolicy` seam and the upload path:
per-origin counters live in Redis so every API process enforces the same
decision (DEC-020). Two counter implementations execute the same
deterministic contract:

- :class:`LuaFairUseCounter` — the production path. The atomic Lua
  scripts :data:`ADMISSION_LUA` / :data:`RELEASE_LUA` run inside the
  Redis Lua interpreter (``EVAL``), so increment, conditional restore,
  and TTL-on-first are one atomic step even under concurrent API
  processes (redis-reference-audit: TTL counters must be atomic; Lua
  for conditional quota checks). EVAL is stateless (no script cache
  dependency); the audit lists ``EVAL`` first among the atomic options.
- :class:`CasFairUseCounter` — the atomic-equivalent WATCH/MULTI/EXEC
  compare-and-swap (the BE-04 store precedent) used in unit tests,
  because the pinned fakeredis 2.37.0 ships without ``lupa`` and cannot
  execute Lua. Every operation is still atomic: reads happen under
  WATCH and a concurrent writer aborts the transaction, which the
  bounded retry loop re-runs. Real-Redis Lua atomicity and load races
  are reserved for the Phase 3 gate-exit integration wave.

Enforcement levels (R-08, gate-entry.md section 4): allow / delay
(exponential backoff with clear messaging) / challenge (429 with
``Retry-After``) / reject (safe category). Frequency is a fixed-window
counter (``INCR`` + ``EXPIRE`` exactly as the approved C1 mechanism
prescribes); crossing the delay threshold escalates through the ladder
until the window expires and ordinary usage recovers. There is no
fixed daily quota: the only counters are the per-window frequency
counter and the per-origin concurrency counter, both TTLed.

Fairness (R-08): ordinary and retried admissions carry equal weight and
no paid class exists — the API exposes no priority/paid parameter and
the counters store no such field. Round-robin ordering is the queue's
concern (BE-05); this policy gates per-origin concurrency and frequency
with per-origin keys, so throttling one origin never affects another.

Fail-closed posture: Redis loss or ``noeviction`` OOM during a counter
operation degrades the decision to DELAY (deny with retryable BE-08
semantics — never allow), marked ``degraded`` on the outcome. The
policy never raises from :meth:`FairUsePolicy.decide`, so the BE-05
queue always rolls back cleanly (a raised non-QueueError would leave a
phantom store record). Releases are best-effort: a lost release is
reclaimed by the counter TTL safety net (every key TTLed, R-09).

Privacy (DEC-175, DEC-020): origins enter the Redis keyspace only as a
one-way SHA-256 fingerprint (:func:`fingerprint_origin`) — never the
raw origin — and logs carry only exception class names and operation
names.

The default knobs are conservative design/safety defaults (DEC-066),
not approved-table values and not benchmarks: the approved axes are the
per-origin concurrency cap (R-03 ``maxConcurrentPerOrigin=4``, sourced
from :class:`app.config.Settings` so the enforced cap always matches the
advertised capabilities contract) and the counter TTL bounded by the
approved retention (3600 s). The frequency window, threshold, and
backoff ladder are adaptive fair-use tunables. The release-marker
keyspace makes claim releases at-most-once for the F-4 lifecycle.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, cast

import redis
from redis.exceptions import WatchError

from app.config import Settings
from app.queue.contracts import AdmissionDecision
from app.routers.capabilities import FailureCode, failure_code_meta

logger = logging.getLogger(__name__)

# Keyspace prefixes for the shared counters; the suffix is the origin
# fingerprint (never the raw origin). Distinct from the store's task:*
# keyspace and the queue's jobs stream. The release-marker suffix is the
# opaque task id, so a claim is released at most once per lifecycle.
CONCURRENCY_KEY_PREFIX = "fuse:conc"
FREQUENCY_KEY_PREFIX = "fuse:freq"
RELEASE_MARKER_PREFIX = "fuse:rel"

# Default socket bounds for the constructed client (mirrors BE-04/BE-05).
_SOCKET_TIMEOUT_SECONDS = 5.0
_SOCKET_CONNECT_TIMEOUT_SECONDS = 5.0

# Bounded WATCH-abort retries for the CAS counter; exhaustion fails
# closed at the policy (degraded DELAY) instead of looping forever.
_CAS_RETRIES = 4

#: Atomic per-origin admission script (Redis Lua interpreter).
#:
#: Return codes (locked by tests): ``1`` allow (both counters
#: incremented, the concurrency counter TTLed on first use); ``-1`` the
#: per-origin concurrency cap is already held (counter restored, no
#: slot taken); ``-f`` with ``f >= 2`` the window frequency ``f``
#: exceeded the delay threshold (no slot taken). The frequency counter
#: counts every request — including concurrency-rejected ones — because
#: every request is traffic; the concurrency counter increments only
#: when admission is allowed.
ADMISSION_LUA = """\
-- KEYS[1] concurrency counter; KEYS[2] frequency counter
-- ARGV[1] concurrency cap; ARGV[2] frequency window TTL (s)
-- ARGV[3] delay threshold; ARGV[4] counter TTL (s)
local f = redis.call('INCR', KEYS[2])
if f == 1 then redis.call('EXPIRE', KEYS[2], ARGV[2]) end
if f > tonumber(ARGV[3]) then
  return 0 - f
end
local c = redis.call('INCR', KEYS[1])
if c == 1 then redis.call('EXPIRE', KEYS[1], ARGV[4]) end
if c > tonumber(ARGV[1]) then
  redis.call('DECR', KEYS[1])
  return -1
end
return 1
"""

#: Atomic per-origin concurrency release script; a stray release below
#: zero deletes the key (clamped, never negative).
RELEASE_LUA = """\
local c = redis.call('DECR', KEYS[1])
if c < 0 then
  redis.call('DEL', KEYS[1])
  return 0
end
return c
"""

#: Atomic at-most-once claim release (F-4). KEYS[2] is the per-claim
#: release marker; when it already exists the release is a no-op (-2), so
#: a claim released by the worker terminal path is never decremented again
#: by the reconciliation recovery path (or by cancel/rollback retries).
#: The marker is TTLed by the same retention bound as the counters (R-09)
#: and its suffix is the opaque task id, never an origin.
RELEASE_CLAIM_LUA = """\
if redis.call('EXISTS', KEYS[2]) == 1 then
  return -2
end
redis.call('SET', KEYS[2], '1', 'EX', ARGV[1])
local c = redis.call('DECR', KEYS[1])
if c < 0 then
  redis.call('DEL', KEYS[1])
  return 0
end
return c
"""


class FairUseDecision(StrEnum):
    """R-08 enforcement levels exposed by :class:`FairUsePolicy`."""

    ALLOW = "allow"
    DELAY = "delay"
    CHALLENGE = "challenge"
    REJECT = "reject"


@dataclass(frozen=True)
class FairUseOutcome:
    """One deterministic fair-use decision with its BE-08 mapping."""

    decision: FairUseDecision
    failure_code: FailureCode | None = None
    retry_after_seconds: int | None = None
    degraded: bool = False

    @property
    def retryable(self) -> bool:
        """Retryability from the BE-08 failure-code metadata (single source)."""
        if self.failure_code is None:
            return False
        return failure_code_meta(self.failure_code).retryable

    def to_admission(self) -> AdmissionDecision:
        """The BE-05 seam level; challenge collapses to the retryable delay."""
        if self.decision is FairUseDecision.ALLOW:
            return AdmissionDecision.ALLOW
        if self.decision is FairUseDecision.REJECT:
            return AdmissionDecision.REJECT
        return AdmissionDecision.DELAY


@dataclass(frozen=True)
class FairUseOptions:
    """Injection knobs; all values are design/safety defaults (DEC-066).

    ``max_concurrent_per_origin`` and ``counter_ttl_seconds`` default to
    the runtime :class:`app.config.Settings` axes (approved R-03 cap 4
    and retention 3600 s), keeping the enforced limits aligned with the
    advertised capabilities contract (F-5).
    """

    max_concurrent_per_origin: int | None = None
    window_seconds: int = 60
    delay_threshold: int = 30
    backoff_base_seconds: int = 1
    backoff_max_seconds: int = 60
    challenge_after_delays: int = 2
    reject_after_delays: int = 5
    concurrency_retry_after_seconds: int = 5
    counter_ttl_seconds: int | None = None


def fingerprint_origin(origin: str | None) -> str:
    """One-way, deterministic origin identifier for the Redis keyspace.

    SHA-256 is non-reversible and stable across processes, so shared
    counters behave identically from any API process while the raw
    origin never enters Redis keys or logs. ``None`` (no Origin
    header) maps to one stable anonymous bucket.
    """
    return hashlib.sha256((origin or "").encode("utf-8")).hexdigest()


def backoff_seconds(level: int, *, base: int, maximum: int) -> int:
    """Deterministic exponential backoff: ``base * 2 ** (level - 1)``, capped."""
    if level < 1:
        raise ValueError(f"backoff level must be >= 1, got {level}")
    return min(maximum, base << (level - 1))


@dataclass(frozen=True)
class CounterLimits:
    """Resolved counter tunables handed to a :class:`FairUseCounter`."""

    cap: int
    window_seconds: int
    threshold: int
    counter_ttl_seconds: int


class FairUseCounter(Protocol):
    """Atomic counter surface; return codes follow :data:`ADMISSION_LUA`."""

    def admit(self, conc_key: str, freq_key: str, limits: CounterLimits) -> int: ...
    def release(self, conc_key: str) -> int: ...
    def release_claim(self, conc_key: str, marker_key: str, marker_ttl: int) -> int: ...


class CasPipelineLike(Protocol):
    """Watched pipeline surface the CAS counter consumes."""

    def watch(self, *names: str) -> None: ...
    def get(self, name: str) -> bytes | None: ...
    def multi(self) -> None: ...
    def set(self, name: str, value: str, ex: int) -> bool: ...
    def incr(self, name: str) -> int: ...
    def decr(self, name: str) -> int: ...
    def expire(self, name: str, time: int) -> bool: ...
    def delete(self, name: str) -> int: ...
    def execute(self, raise_on_error: bool = True) -> list[object]: ...
    def reset(self) -> None: ...


class CounterRedisLike(Protocol):
    """Typed Redis surface the counters consume (single cast crossing point)."""

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int: ...
    def pipeline(self, transaction: bool = True) -> CasPipelineLike: ...


class LuaFairUseCounter:
    """Atomic counter over the Redis Lua interpreter (production path)."""

    def __init__(self, client: CounterRedisLike) -> None:
        self._client = client

    def admit(self, conc_key: str, freq_key: str, limits: CounterLimits) -> int:
        return int(
            self._client.eval(
                ADMISSION_LUA,
                2,
                conc_key,
                freq_key,
                str(limits.cap),
                str(limits.window_seconds),
                str(limits.threshold),
                str(limits.counter_ttl_seconds),
            )
        )

    def release(self, conc_key: str) -> int:
        return int(self._client.eval(RELEASE_LUA, 1, conc_key))

    def release_claim(self, conc_key: str, marker_key: str, marker_ttl: int) -> int:
        return int(self._client.eval(RELEASE_CLAIM_LUA, 2, conc_key, marker_key, str(marker_ttl)))


class _CounterContentionError(RuntimeError):
    """WATCH aborts exhausted the CAS retry bound; admission fails closed."""


class CasFairUseCounter:
    """Atomic-equivalent counter via WATCH/MULTI/EXEC compare-and-swap.

    Mirrors :data:`ADMISSION_LUA` / :data:`RELEASE_LUA` line by line:
    reads happen under WATCH; a concurrent writer aborts the
    transaction; the bounded retry loop re-reads. The frequency counter
    increments on every call (rejections are traffic, exactly like the
    Lua), while the concurrency counter increments only when admission
    is allowed. ``EXPIRE`` fires only when the key was absent before
    this transaction (the Lua ``count == 1`` test), keeping the
    fixed-window semantics identical. The Lua path executes the same
    contract as one atomic EVAL; the CAS equivalent splits the decision
    into one atomic transaction per operation, which is the strongest
    equivalent provable against fakeredis — single-EVAL atomicity under
    real load stays a gate-exit concern.
    """

    def __init__(self, client: CounterRedisLike) -> None:
        self._client = client

    def admit(self, conc_key: str, freq_key: str, limits: CounterLimits) -> int:
        for _ in range(_CAS_RETRIES):
            pipe = self._client.pipeline(transaction=True)
            pipe.watch(conc_key, freq_key)
            try:
                raw_f = pipe.get(freq_key)
                freq = int(raw_f) if raw_f is not None else 0
                raw_c = pipe.get(conc_key)
                conc = int(raw_c) if raw_c is not None else 0
                pipe.multi()
                pipe.incr(freq_key)
                if freq == 0:
                    pipe.expire(freq_key, limits.window_seconds)
                if freq + 1 <= limits.threshold and conc < limits.cap:
                    pipe.incr(conc_key)
                    if conc == 0:
                        pipe.expire(conc_key, limits.counter_ttl_seconds)
                pipe.execute()
                if freq + 1 > limits.threshold:
                    return -(freq + 1)
                if conc >= limits.cap:
                    return -1
                return 1
            except WatchError:
                continue
            finally:
                pipe.reset()
        raise _CounterContentionError("counter contention exceeded retry bound")

    def release(self, conc_key: str) -> int:
        for _ in range(_CAS_RETRIES):
            pipe = self._client.pipeline(transaction=True)
            pipe.watch(conc_key)
            try:
                raw = pipe.get(conc_key)
                conc = int(raw) if raw is not None else 0
                if conc <= 0:
                    return 0
                pipe.multi()
                if conc == 1:
                    pipe.delete(conc_key)
                else:
                    pipe.decr(conc_key)
                pipe.execute()
                return conc - 1
            except WatchError:
                continue
            finally:
                pipe.reset()
        raise _CounterContentionError("counter contention exceeded retry bound")

    def release_claim(self, conc_key: str, marker_key: str, marker_ttl: int) -> int:
        for _ in range(_CAS_RETRIES):
            pipe = self._client.pipeline(transaction=True)
            pipe.watch(conc_key, marker_key)
            try:
                if pipe.get(marker_key) is not None:
                    return -2
                raw = pipe.get(conc_key)
                conc = int(raw) if raw is not None else 0
                pipe.multi()
                pipe.set(marker_key, "1", ex=marker_ttl)
                if conc > 1:
                    pipe.decr(conc_key)
                elif conc == 1:
                    pipe.delete(conc_key)
                pipe.execute()
                return max(0, conc - 1)
            except WatchError:
                continue
            finally:
                pipe.reset()
        raise _CounterContentionError("counter contention exceeded retry bound")


def _build_client(settings: Settings) -> CounterRedisLike:
    client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=False,
        socket_timeout=_SOCKET_TIMEOUT_SECONDS,
        socket_connect_timeout=_SOCKET_CONNECT_TIMEOUT_SECONDS,
    )
    return cast(CounterRedisLike, client)


class FairUsePolicy:
    """Deterministic Redis-shared admission policy (BE-10, :class:`AdmissionPolicy`).

    ``settings`` mirrors the BE-04/BE-05 constructor pattern (the
    default client is built from ``redis_url``); ``client`` is the test
    injection seam, ``options`` the tunables, and ``counter`` the
    atomic counter implementation (defaults to the production Lua
    path).
    """

    def __init__(
        self,
        settings: Settings,
        client: CounterRedisLike | None = None,
        *,
        options: FairUseOptions | None = None,
        counter: FairUseCounter | None = None,
    ) -> None:
        self._client = client if client is not None else _build_client(settings)
        knobs = options if options is not None else FairUseOptions()
        self._validate_options(knobs)
        # The per-origin concurrency cap and the counter TTL default to the
        # runtime Settings axes (F-5), so the enforced cap can never drift
        # from the advertised capabilities contract; the approved R-03 /
        # retention values remain the Settings defaults.
        self._cap = (
            knobs.max_concurrent_per_origin
            if knobs.max_concurrent_per_origin is not None
            else settings.max_concurrent_per_origin
        )
        self._counter_ttl = (
            knobs.counter_ttl_seconds
            if knobs.counter_ttl_seconds is not None
            else settings.retention_seconds
        )
        self._limits = CounterLimits(
            cap=self._cap,
            window_seconds=knobs.window_seconds,
            threshold=knobs.delay_threshold,
            counter_ttl_seconds=self._counter_ttl,
        )
        self._threshold = knobs.delay_threshold
        self._backoff_base = knobs.backoff_base_seconds
        self._backoff_max = knobs.backoff_max_seconds
        self._challenge_after = knobs.challenge_after_delays
        self._reject_after = knobs.reject_after_delays
        self._concurrency_retry_after = knobs.concurrency_retry_after_seconds
        self._counter = counter if counter is not None else LuaFairUseCounter(self._client)

    @staticmethod
    def _validate_options(knobs: FairUseOptions) -> None:
        if knobs.max_concurrent_per_origin is not None and knobs.max_concurrent_per_origin < 1:
            raise ValueError("max_concurrent_per_origin must be >= 1")
        if knobs.window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")
        if knobs.delay_threshold < 1:
            raise ValueError("delay_threshold must be >= 1")
        if knobs.backoff_base_seconds < 1:
            raise ValueError("backoff_base_seconds must be >= 1")
        if knobs.backoff_max_seconds < knobs.backoff_base_seconds:
            raise ValueError("backoff_max_seconds must be >= backoff_base_seconds")
        if knobs.challenge_after_delays < 1:
            raise ValueError("challenge_after_delays must be >= 1")
        if knobs.reject_after_delays <= knobs.challenge_after_delays:
            raise ValueError("reject_after_delays must be > challenge_after_delays")
        if knobs.concurrency_retry_after_seconds < 1:
            raise ValueError("concurrency_retry_after_seconds must be >= 1")
        if knobs.counter_ttl_seconds is not None and knobs.counter_ttl_seconds < 1:
            raise ValueError("counter_ttl_seconds must be >= 1")

    @property
    def max_concurrent_per_origin(self) -> int:
        """The approved per-origin concurrency cap in force."""
        return self._cap

    @property
    def counter_ttl_seconds(self) -> int:
        """The counter TTL safety net in force."""
        return self._counter_ttl

    def evaluate(self, *, origin: str | None, tool: str, queued: int) -> FairUseOutcome:
        """The full four-level decision with BE-08 mapping and retry guidance.

        ``tool`` and ``queued`` are accepted for the BE-05 protocol
        shape; per-tool limits live in BE-08 validation and round-robin
        ordering in the queue, so decisions depend only on the
        per-origin shared counters (deterministic, equal weight).
        """
        del tool, queued
        try:
            result = self._counter.admit(
                self._key(CONCURRENCY_KEY_PREFIX, origin),
                self._key(FREQUENCY_KEY_PREFIX, origin),
                self._limits,
            )
        except Exception as exc:
            logger.error(
                "fair use redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return self._degraded_outcome()
        return self._outcome_from_code(result)

    def _outcome_from_code(self, result: int) -> FairUseOutcome:
        if result == 1:
            return FairUseOutcome(FairUseDecision.ALLOW)
        if result == -1:
            return FairUseOutcome(
                FairUseDecision.CHALLENGE,
                FailureCode.TOO_MANY_CONCURRENT,
                retry_after_seconds=self._concurrency_retry_after,
            )
        if result < -1:
            level = -result - self._threshold
            retry_after = backoff_seconds(level, base=self._backoff_base, maximum=self._backoff_max)
            if level < self._challenge_after:
                return FairUseOutcome(
                    FairUseDecision.DELAY,
                    FailureCode.RATE_LIMITED,
                    retry_after_seconds=retry_after,
                )
            if level < self._reject_after:
                return FairUseOutcome(
                    FairUseDecision.CHALLENGE,
                    FailureCode.RATE_LIMITED,
                    retry_after_seconds=retry_after,
                )
            return FairUseOutcome(FairUseDecision.REJECT, FailureCode.RATE_LIMITED)
        logger.error(
            "fair use unexpected counter code",
            extra={"fields": {"code": result}},
        )
        return self._degraded_outcome()

    def _degraded_outcome(self) -> FairUseOutcome:
        return FairUseOutcome(FairUseDecision.DELAY, FailureCode.RATE_LIMITED, degraded=True)

    def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision:
        """The BE-05 :class:`AdmissionPolicy` seam level for this admission."""
        return self.evaluate(origin=origin, tool=tool, queued=queued).to_admission()

    def release(self, *, origin: str | None) -> None:
        """Free one per-origin concurrency slot; best-effort and never raises.

        A release lost to Redis failure is reclaimed by the counter TTL
        (every key TTLed, R-09); the failure is logged by class name
        only (DEC-175). This plain release carries no per-claim marker
        and is the context-free surface; the job lifecycle uses
        :meth:`release_fingerprint_claim`, whose marker guarantees
        at-most-once semantics.
        """
        conc_key = self._key(CONCURRENCY_KEY_PREFIX, origin)
        try:
            self._counter.release(conc_key)
        except Exception as exc:
            logger.error(
                "fair use redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )

    def release_claim(self, *, origin: str | None, claim: str) -> None:
        """Free the claim's slot by raw origin; at-most-once per *claim*.

        The queue-side lifecycle (rollback after a granted admission,
        cancellation) releases through this surface.
        """
        self.release_fingerprint_claim(fingerprint=fingerprint_origin(origin), claim=claim)

    def release_fingerprint_claim(self, *, fingerprint: str, claim: str) -> None:
        """Free the claim's slot by origin fingerprint; at-most-once per *claim*.

        The per-claim release marker (:data:`RELEASE_MARKER_PREFIX`) makes
        the release idempotent: the worker terminal path, the
        reconciliation recovery path, cancellation, and enqueue rollback
        can all invoke this for the same claim and the counter is
        decremented exactly once. Never raises; a lost release or marker
        is reclaimed by the counter TTL safety net.
        """
        conc_key = f"{CONCURRENCY_KEY_PREFIX}:{fingerprint}"
        marker_key = f"{RELEASE_MARKER_PREFIX}:{claim}"
        try:
            self._counter.release_claim(conc_key, marker_key, self._counter_ttl)
        except Exception as exc:
            logger.error(
                "fair use redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )

    @staticmethod
    def _key(prefix: str, origin: str | None) -> str:
        return f"{prefix}:{fingerprint_origin(origin)}"


__all__ = [
    "ADMISSION_LUA",
    "CONCURRENCY_KEY_PREFIX",
    "FREQUENCY_KEY_PREFIX",
    "RELEASE_CLAIM_LUA",
    "RELEASE_LUA",
    "RELEASE_MARKER_PREFIX",
    "CasFairUseCounter",
    "CasPipelineLike",
    "CounterLimits",
    "CounterRedisLike",
    "FairUseCounter",
    "FairUseDecision",
    "FairUseOptions",
    "FairUseOutcome",
    "FairUsePolicy",
    "LuaFairUseCounter",
    "backoff_seconds",
    "fingerprint_origin",
]
