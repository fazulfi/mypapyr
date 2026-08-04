"""Redis Streams job queue with fail-closed admission (BE-05).

Admission into the durable worker queue: an idempotent consumer-group
(``jobs`` / ``workers``), bounded ``XADD`` entries carrying only the
DEC-174 opaque task id/tool/route, and the approved R-07 caps — queue
length 2000 and max wait 900 s — enforced before any entry is written.
Length enforcement is ONE server-side atomic unit (F-1): a Lua
check-and-XADD (real Redis) or its WATCH/MULTI/EXEC equivalent (injected
fakeredis client) rejects at the cap with :class:`QueueFullError` instead
of trimming — so a concurrent admission can never evict an entry that was
already durably admitted.

Fair scheduling (R-08): ordinary and retried jobs carry equal weight and
there is no paid lane. The deterministic admission seam is
:class:`AdmissionPolicy` — per-origin round-robin and per-origin
concurrency (4) plug in here. A production-built queue defaults to the
Settings-backed Redis-shared :class:`FairUsePolicy` (F-4): every granted
ALLOW reserves one per-origin concurrency claim that is released exactly
once on rollback, cancellation, or the worker's terminal path. A
test-built queue (injected client) defaults to the pure, deterministic
:class:`AllowAllAdmission` unless a policy is injected. A
worker-degradation probe pauses admission fail-closed: when the probe
reports unhealthy, :meth:`JobQueue.enqueue` raises
:class:`QueueUnavailableError`.

Cancellation (DEC-069): :meth:`JobQueue.cancel` atomically transitions a
queued task to ``cancelled`` through the store's Lua-backed surface and
then purges the still-unclaimed stream entry best-effort, releasing the
entry's reserved concurrency claim exactly once, so a worker neither
executes the job nor, in the common case, even picks it up; a worker
that already picked the entry reconciles against the terminal state and
acknowledges without execution.

Fail-closed error taxonomy (all :class:`QueueError` subclasses):
``QueueUnavailableError`` (Redis failure or degraded worker — retryable),
``QueueFullError`` (approved R-07 queue-length cap — retryable),
``QueueMaxWaitError`` (approved R-07 max-wait cap — retryable, a
:class:`QueueFullError` subclass mapped to
``FailureCode.MAX_WAIT_EXCEEDED``), ``QueueDelayedError`` (policy DELAY —
retryable), ``QueueRejectedError`` (policy REJECT — not retryable).
Store failures propagate unchanged from BE-04 (``TaskConflictError`` for
duplicates, ``StoreUnavailableError`` for Redis loss). A rejected or
failed enqueue rolls back the just-created store record so no phantom
queued task survives, and releases any concurrency claim the admission
had already reserved.

Privacy contract (DEC-175): entries carry opaque task ids, tool/route
strings, and the opaque 64-hex origin fingerprint only; logs carry
exception class names and operation names, never messages, task ids,
origins, or object references.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, cast, runtime_checkable

import redis
from redis.exceptions import RedisError, WatchError

from app.config import Settings
from app.queue.contracts import AdmissionDecision, AdmissionPolicy, AllowAllAdmission
from app.queue.store import (
    LuaRedisLike,
    PipelineLike,
    RedisLike,
    StoreError,
    TaskRecord,
    TaskStore,
)
from app.routers.capabilities import FailureCode
from app.security.fair_use import FairUsePolicy, fingerprint_origin

logger = logging.getLogger(__name__)

# Stream and consumer-group namespaces for the server-job queue.
STREAM_KEY = "jobs"
GROUP_NAME = "workers"

# Entry vocabulary: exactly these minimal fields (DEC-174). ``origin``
# carries only the opaque 64-hex SHA-256 origin fingerprint — never the
# raw origin (DEC-175) — so the worker and the cancel path can release
# the fair-use concurrency claim that admission reserved (F-4).
ENTRY_FIELDS: tuple[str, ...] = ("task_id", "tool", "route", "origin")

# Default socket bounds for the constructed client; a dead Redis must fail
# closed instead of hanging (mirrors the BE-04 store client).
_SOCKET_TIMEOUT_SECONDS = 5.0
_SOCKET_CONNECT_TIMEOUT_SECONDS = 5.0

# Recovery threshold when a worker crashes after claiming: the queue-side
# entry must be idle strictly longer than the maximum possible execution
# timeout before another claim is attempted (redis-reference-audit).
_CLAIM_IDLE_GRACE_SECONDS = 60.0


class QueueError(RuntimeError):
    """Base class for typed queue failures."""

    retryable: bool = False
    failure_code: FailureCode = FailureCode.RATE_LIMITED


class QueueUnavailableError(QueueError):
    """Redis is unreachable, a queue operation failed, or admission is paused.

    The fail-closed posture for Redis loss (R-09) and worker degradation:
    callers receive a typed retryable error instead of a silently dropped
    job. Includes the noeviction OOM case surfaced by the store.
    """

    retryable = True
    failure_code = FailureCode.RATE_LIMITED


class QueueFullError(QueueError):
    """An approved R-07 cap is reached: queue length or max wait exceeded.

    The job is rejected before any entry is written and its store record is
    rolled back. Retryable: the queue may drain.
    """

    retryable = True
    failure_code = FailureCode.QUEUE_FULL


class QueueMaxWaitError(QueueFullError):
    """The approved R-07 max-wait cap was reached (distinct failure code).

    Subclass of :class:`QueueFullError` so retryability and rollback
    behavior are unchanged; the distinct :data:`FailureCode.MAX_WAIT_EXCEEDED`
    makes the BE-08 bridge deterministic.
    """

    retryable = True
    failure_code = FailureCode.MAX_WAIT_EXCEEDED


class QueueDelayedError(QueueError):
    """The admission policy asked to delay (R-08 enforcement level)."""

    retryable = True
    failure_code = FailureCode.RATE_LIMITED


class QueueRejectedError(QueueError):
    """The admission policy rejected the job (R-08 enforcement level)."""

    retryable = False
    failure_code = FailureCode.RATE_LIMITED


@runtime_checkable
class ConcurrencyReleaser(Protocol):
    """At-most-once claim-release surface (F-4).

    :class:`FairUsePolicy` implements it: a granted ALLOW reserves one
    per-origin concurrency slot that the worker (terminal / reconcile /
    abandon) or the queue (cancel / rollback) frees exactly once per
    claim, keyed by the opaque origin fingerprint.
    """

    def release_claim(self, *, origin: str | None, claim: str) -> None: ...
    def release_fingerprint_claim(self, *, fingerprint: str, claim: str) -> None: ...


# One claimed entry as returned by the stream commands.
ClaimedEntry = tuple[bytes, Mapping[bytes, bytes]]

# XAUTOCLAIM result: (next cursor, claimed entries, deleted entry ids).
XAutoClaimResult = tuple[bytes, list[ClaimedEntry], list[bytes]]


class StreamsRedisLike(RedisLike, Protocol):
    """Typed Redis Streams surface the queue and worker consume.

    The single cast crossing point for stream commands: the concrete
    ``redis.Redis`` client (or ``fakeredis.FakeRedis`` in tests) is cast to
    this protocol at construction, because redis-py's own stubs union
    synchronous and asynchronous return types while this module is strictly
    synchronous.
    """

    def xgroup_create(
        self,
        name: str,
        groupname: str,
        id: str = "0",
        mkstream: bool = False,
        entries_read: int | None = None,
    ) -> None: ...

    def xadd(
        self,
        name: str,
        fields: Mapping[str, str],
        id: str = "*",
        maxlen: int | None = None,
        approximate: bool = True,
    ) -> bytes: ...

    def xreadgroup(
        self,
        groupname: str,
        consumername: str,
        streams: Mapping[str, str],
        count: int | None = None,
        block: int | None = None,
    ) -> list[tuple[bytes, list[ClaimedEntry]]]: ...

    def xack(self, name: str, groupname: str, *ids: bytes) -> int: ...

    def xautoclaim(
        self,
        name: str,
        groupname: str,
        consumername: str,
        min_idle_time: int,
        start_id: bytes = b"0-0",
    ) -> XAutoClaimResult: ...

    def xlen(self, name: str) -> int: ...

    def xrange(
        self, name: str, start: str = "-", end: str = "+", count: int | None = None
    ) -> list[ClaimedEntry]: ...

    def xdel(self, name: str, *ids: bytes) -> int: ...


def _build_stream_client(settings: Settings) -> StreamsRedisLike:
    client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=False,
        socket_timeout=_SOCKET_TIMEOUT_SECONDS,
        socket_connect_timeout=_SOCKET_CONNECT_TIMEOUT_SECONDS,
    )
    return cast(StreamsRedisLike, client)


def _entry_id_timestamp_ms(entry_id: bytes) -> int | None:
    """Millisecond part of a stream id (``<ms>-<seq>``), or None if malformed."""
    try:
        ms = int(entry_id.split(b"-", 1)[0])
    except (ValueError, IndexError):
        return None
    return ms


# F-1: bounded admission as ONE server-side atomic unit. The length check
# and the append cannot race, so a concurrent admission can never push the
# stream past the cap and evict a previously admitted entry. Returns 0
# (reject) at the cap and 1 (appended) below it. No MAXLEN is used: the
# atomic check is the bound, and omitting exact trimming makes silent
# eviction structurally impossible even if this guard were ever regressed.
_APPEND_LUA = """
local len = redis.call('XLEN', KEYS[1])
if len >= tonumber(ARGV[1]) then return 0 end
redis.call('XADD', KEYS[1], '*', 'task_id', ARGV[2], 'tool', ARGV[3],
    'route', ARGV[4], 'origin', ARGV[5])
return 1
"""

# Bounded WATCH retries for the CAS append: contention means another
# admission won the slot; the retry re-reads the length fail-closed.
_APPEND_CAS_RETRIES = 4


class StreamsPipelineLike(PipelineLike, Protocol):
    """Watched pipeline surface the CAS append consumes."""

    def xlen(self, name: str) -> int: ...
    def xadd(self, name: str, fields: Mapping[str, str]) -> bytes: ...


class AppendMechanism(Protocol):
    """Atomic check-and-XADD seam (F-1).

    :class:`LuaAppendMechanism` is the production path (one server-side
    ``EVAL``); :class:`CasAppendMechanism` is the WATCH/MULTI/EXEC
    atomic-equivalent provable against fakeredis, which has no EVAL
    support. Both implement the same contract: ``append`` returns True
    only when the entry was added, False when the stream is at the cap —
    and no existing entry is ever trimmed.
    """

    def append(self, key: str, fields: Mapping[str, str], *, maxlen: int) -> bool: ...


class LuaAppendMechanism:
    """F-1 append: one atomic EVAL (production path).

    The script checks the stream length and conditionally XADDs in one
    server-side unit, so no interleaving can push the stream past the cap
    and evict a previously admitted entry. Script codes map to the queue's
    typed errors: 0 -> the cap was reached (:class:`QueueFullError` is
    raised by the caller), 1 -> appended atomically; any other result or a
    Redis failure fails closed with :class:`QueueUnavailableError`.
    """

    def __init__(self, client: LuaRedisLike) -> None:
        self._client = client

    def append(self, key: str, fields: Mapping[str, str], *, maxlen: int) -> bool:
        try:
            result = self._client.eval(
                _APPEND_LUA,
                1,
                key,
                str(maxlen),
                fields["task_id"],
                fields["tool"],
                fields["route"],
                fields["origin"],
            )
        except RedisError as exc:
            logger.error(
                "job queue redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise QueueUnavailableError() from exc
        if isinstance(result, int):
            if result == 1:
                return True
            if result == 0:
                return False
        elif len(result) == 1 and result[0] == 1:
            return True
        elif len(result) == 1 and result[0] == 0:
            return False
        logger.error("job queue atomic append returned an unknown result")
        raise QueueUnavailableError()


class CasAppendMechanism:
    """Atomic-equivalent append via WATCH/MULTI/EXEC (fakeredis-provable).

    Mirrors :data:`_APPEND_LUA` line by line: the length is read under
    WATCH; a concurrent writer aborts the transaction and the bounded
    retry re-reads; the append fires only when the length is below the
    cap. This is the strongest atomic equivalent provable against
    fakeredis, which has no EVAL support (cf.
    ``security.fair_use.CasFairUseCounter``).
    """

    def __init__(self, client: StreamsRedisLike) -> None:
        self._client = client

    def append(self, key: str, fields: Mapping[str, str], *, maxlen: int) -> bool:
        try:
            for _ in range(_APPEND_CAS_RETRIES):
                pipe = cast(StreamsPipelineLike, self._client.pipeline(transaction=True))
                pipe.watch(key)
                try:
                    if pipe.xlen(key) >= maxlen:
                        return False
                    pipe.multi()
                    pipe.xadd(key, fields)
                    pipe.execute()
                    return True
                except WatchError:
                    continue
                finally:
                    pipe.reset()
        except RedisError as exc:
            logger.error(
                "job queue redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise QueueUnavailableError() from exc
        raise QueueUnavailableError()


def _select_append_mechanism(client: StreamsRedisLike, *, injected: bool) -> AppendMechanism:
    """Lua for the production-built client, CAS for injected (fakeredis) clients.

    ``client=None`` in the constructor builds the production client (real
    Redis, EVAL-capable) and selects the Lua path; an injected client is
    the test seam (fakeredis has no EVAL support) and gets the
    WATCH/MULTI/EXEC atomic-equivalent — the store's Lua/CAS duality
    applied to admission.
    """
    if injected:
        return CasAppendMechanism(client)
    return LuaAppendMechanism(cast(LuaRedisLike, client))


@dataclass(frozen=True)
class QueueOptions:
    """Injection knobs for :class:`JobQueue`.

    ``clock`` is the time source for the max-wait check, ``policy`` the
    R-08 admission seam, ``releaser`` the at-most-once claim-release seam
    (F-4; when unset the queue uses the policy itself if it can release),
    and ``readiness`` the worker-degradation probe (False pauses admission
    fail-closed).
    """

    clock: Callable[[], datetime] | None = None
    policy: AdmissionPolicy | None = None
    releaser: ConcurrencyReleaser | None = None
    readiness: Callable[[], bool] | None = None


class JobQueue:
    """Admission and durable enqueue over one Redis Streams consumer group.

    Constructor consumes :class:`app.config.Settings` (BE-01): the default
    client is built from ``redis_url`` with explicit socket timeouts, and
    the approved R-07 caps (``max_queue_length``, ``max_wait_seconds``)
    bound admission. ``client`` is the test injection seam (fakeredis),
    ``store`` the BE-04 task store the queue writes through, and
    ``options`` carries the injectable clock, admission policy, and
    readiness probe.
    """

    def __init__(
        self,
        settings: Settings,
        store: TaskStore,
        client: StreamsRedisLike | None = None,
        *,
        options: QueueOptions | None = None,
        append: AppendMechanism | None = None,
    ) -> None:
        self._settings = settings
        self._store = store
        self._client = client if client is not None else _build_stream_client(settings)
        knobs = options if options is not None else QueueOptions()
        self._clock = knobs.clock if knobs.clock is not None else (lambda: datetime.now(UTC))
        # F-4: a production-built queue (client=None) defaults to the
        # Settings-backed Redis-shared fair-use policy; a test-built queue
        # defaults to the deterministic allow-all (injected clients carry
        # their own policy through QueueOptions).
        self._policy = (
            knobs.policy
            if knobs.policy is not None
            else FairUsePolicy(settings)
            if client is None
            else AllowAllAdmission()
        )
        self._releaser = (
            knobs.releaser
            if knobs.releaser is not None
            else (self._policy if isinstance(self._policy, ConcurrencyReleaser) else None)
        )
        self._readiness = knobs.readiness
        self._group_ready = False
        self._append_impl = (
            append
            if append is not None
            else _select_append_mechanism(self._client, injected=client is not None)
        )

    @property
    def admission_policy(self) -> AdmissionPolicy:
        """The admission policy in force (F-4 introspection seam)."""
        return self._policy

    def enqueue(
        self, record: TaskRecord, *, origin: str | None = None, route: str | None = None
    ) -> TaskRecord:
        """Admit and durably enqueue *record*; returns the normalized record.

        The record is created in the store first (duplicate ids raise
        :class:`TaskConflictError` unchanged), then admitted under the
        approved R-07 caps and the admission policy, then appended to the
        stream as exactly ``task_id``/``tool``/``route``/``origin`` fields
        through the atomic check-and-XADD (F-1): at the cap the append
        rejects with :class:`QueueFullError` instead of trimming. Any
        failure after the store write — a typed queue rejection or an
        unexpected exception from the admission seam — rolls back the
        just-created record and re-raises, so no phantom queued task
        survives. When admission already granted an ALLOW (one concurrency
        claim reserved) and the append then fails, the claim is released
        exactly once (F-4).
        """
        created = self._store.create(record)
        allowed = False
        try:
            allowed = self._admit(created, origin)
            self._append(created, route, origin)
            return created
        except Exception:
            self._rollback(created.task_id)
            if allowed:
                self._release_claim(origin, created.task_id)
            raise

    def stream_length(self) -> int:
        """Current stream length; fails closed on Redis errors."""
        try:
            return self._client.xlen(STREAM_KEY)
        except Exception as exc:
            logger.error(
                "job queue redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise QueueUnavailableError() from exc

    def cancel(self, task_id: str) -> TaskRecord:
        """Atomically cancel a queued task (DEC-069); returns the cancelled record.

        The record transition is one server-side atomic unit through the
        store (:meth:`TaskStore.cancel`): only a queued, not-yet-expired
        record becomes ``cancelled``, so no interleaving can both cancel
        and execute the job. On success the still-unclaimed stream entry
        is purged best-effort and its reserved concurrency claim is
        released exactly once (F-4); when the purge cannot resolve the
        origin fingerprint the release is deferred to the counter TTL
        safety net. Purge failures are logged (class name only) and never
        raise, because the atomic record transition is authoritative and a
        worker that already picked the entry reconciles against the
        terminal state without execution. Store errors propagate
        unchanged: :class:`TaskNotFoundError` (unknown or expired),
        :class:`TaskConflictError` (already processing or terminal —
        cancellation is no longer available), :class:`StoreUnavailableError`.
        """
        cancelled = self._store.cancel(task_id)
        fingerprint = self._purge_entry(task_id)
        if fingerprint is not None:
            self._release_fingerprint(fingerprint, task_id)
        return cancelled

    def _purge_entry(self, task_id: str) -> str | None:
        """Best-effort purge of the cancelled entry; returns its origin
        fingerprint (or None when the entry is not found)."""
        target = task_id.encode("utf-8")
        try:
            entries = self._client.xrange(STREAM_KEY, "-", "+")
        except Exception as exc:
            logger.error(
                "job queue redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return None
        for entry_id, fields in entries:
            if fields.get(b"task_id") == target:
                try:
                    self._client.xdel(STREAM_KEY, entry_id)
                except Exception as exc:
                    logger.error(
                        "job queue redis failure",
                        extra={"fields": {"error": type(exc).__name__}},
                    )
                raw = fields.get(b"origin")
                if raw is None:
                    return None
                try:
                    return raw.decode("utf-8")
                except UnicodeDecodeError as exc:
                    logger.error(
                        "job queue corrupt entry fingerprint",
                        extra={"fields": {"error": type(exc).__name__}},
                    )
                    return None
        return None

    def _release_claim(self, origin: str | None, claim: str) -> None:
        releaser = self._releaser
        if releaser is not None:
            releaser.release_claim(origin=origin, claim=claim)

    def _release_fingerprint(self, fingerprint: str, claim: str) -> None:
        releaser = self._releaser
        if releaser is not None:
            releaser.release_fingerprint_claim(fingerprint=fingerprint, claim=claim)

    def _admit(self, record: TaskRecord, origin: str | None) -> bool:
        """Admit under the caps and the policy; True when an ALLOW was granted.

        A granted ALLOW reserves one per-origin concurrency claim, so the
        caller is responsible for releasing it on rollback (F-4);
        DELAY/REJECT and the cap rejections reserve nothing.
        """
        if self._readiness is not None and not self._readiness():
            raise QueueUnavailableError("admission paused: worker degraded")
        queued = self.stream_length()
        if queued >= self._settings.max_queue_length:
            raise QueueFullError("queue length cap reached")
        oldest = self._oldest_wait_ms()
        if oldest is not None and oldest >= self._settings.max_wait_seconds * 1000:
            raise QueueMaxWaitError("max wait cap reached")
        decision = self._policy.decide(origin=origin, tool=record.tool, queued=queued)
        if decision is AdmissionDecision.DELAY:
            raise QueueDelayedError("admission policy delays this job")
        if decision is AdmissionDecision.REJECT:
            raise QueueRejectedError("admission policy rejects this job")
        return True

    def _oldest_wait_ms(self) -> int | None:
        """Age of the oldest queued entry in ms, or None when the queue is empty."""
        try:
            # Positional range bounds: fakeredis's xrange is positional-only.
            entries = self._client.xrange(STREAM_KEY, "-", "+", count=1)
        except Exception as exc:
            logger.error(
                "job queue redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise QueueUnavailableError() from exc
        if not entries:
            return None
        oldest_ms = _entry_id_timestamp_ms(entries[0][0])
        if oldest_ms is None:
            logger.error("job queue corrupt stream id")
            raise QueueUnavailableError()
        now_ms = int(self._clock().timestamp() * 1000)
        return max(0, now_ms - oldest_ms)

    def _append(self, record: TaskRecord, route: str | None, origin: str | None) -> None:
        self._ensure_group()
        fields: dict[str, str] = {
            "task_id": record.task_id,
            "tool": record.tool,
            "route": route if route is not None else record.tool,
            "origin": fingerprint_origin(origin),
        }
        appended = self._append_impl.append(
            STREAM_KEY, fields, maxlen=self._settings.max_queue_length
        )
        if not appended:
            raise QueueFullError("queue length cap reached")

    def _ensure_group(self) -> None:
        if self._group_ready:
            return
        try:
            self._client.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        except Exception as exc:
            name = type(exc).__name__
            if "BUSYGROUP" in name or "BUSYGROUP" in str(exc):
                self._group_ready = True
                return
            logger.error(
                "job queue redis failure",
                extra={"fields": {"error": name}},
            )
            raise QueueUnavailableError() from exc
        self._group_ready = True

    def _rollback(self, task_id: str) -> None:
        try:
            self._store.delete(task_id)
        except StoreError as exc:
            logger.error(
                "job queue rollback failure",
                extra={"fields": {"error": type(exc).__name__}},
            )


__all__ = [
    "ENTRY_FIELDS",
    "GROUP_NAME",
    "STREAM_KEY",
    "_CLAIM_IDLE_GRACE_SECONDS",
    "AdmissionDecision",
    "AdmissionPolicy",
    "AllowAllAdmission",
    "AppendMechanism",
    "CasAppendMechanism",
    "ClaimedEntry",
    "ConcurrencyReleaser",
    "JobQueue",
    "LuaAppendMechanism",
    "QueueDelayedError",
    "QueueError",
    "QueueFullError",
    "QueueMaxWaitError",
    "QueueRejectedError",
    "QueueUnavailableError",
    "StreamsRedisLike",
    "XAutoClaimResult",
]
