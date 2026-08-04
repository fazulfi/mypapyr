"""Redis-backed minimal task store (BE-04).

Durable coordination for server jobs: one Redis hash per task under the
``task:<opaque-id>`` keyspace, holding only DEC-174 minimal metadata —
opaque task id, state, timing, expiry, route/tool, progress/result/error
summaries, and non-sensitive temporary object references. Every write sets
the key TTL to the remaining artifact lifetime (never later than the
R-09-approved retention), and the ``noeviction`` posture is honored by
failing closed on every Redis write error — an OOM write is never silently
dropped.

State transitions consume ``app.tasks.state_machine`` unchanged: only
transitions the pure table permits are persisted, and each conditional
state change is a WATCH/MULTI/EXEC compare-and-swap (redis-py 8.x raises
``WatchError`` from ``Pipeline.execute`` on abort), so a stale
``expected_state``/``expected_updated_at`` or a concurrent writer surfaces
as :class:`TaskConflictError` and never half-applies. Expiry is not a
state: ``DEADLINE_REACHED`` is a lifecycle outcome handled by TTL deletion,
not a persisted transition.

User cancellation (DEC-069) has its own public surface,
:meth:`TaskStore.cancel`, whose queued-to-cancelled transition runs as one
server-side atomic unit: the production path is a Lua ``EVAL``
(:class:`LuaCancelMechanism`), and :class:`CasCancelMechanism` is the
WATCH/MULTI/EXEC atomic-equivalent provable against fakeredis (which has
no EVAL support), mirroring the ``security.fair_use`` Lua/CAS precedent.
Either way the state check and the terminal write are atomic, so no
interleaving can both cancel a job and let a worker execute it.

Privacy contract (DEC-174, DEC-175): prohibited field names — filenames,
passwords, signed URLs, content/bytes, previews, tokens, authorization and
cookie material — are structurally excluded by the typed record model and
rejected by a serialization-time scan, including nested and case variants.
Logs carry only exception class names and operation names, never messages,
task ids, or object references.

Fail-closed error taxonomy (all :class:`StoreError` subclasses):
``StoreUnavailableError`` (Redis unreachable or write/read/TTL failure,
including OOM under noeviction), ``TaskNotFoundError`` (unknown or expired
id; the store cannot distinguish the two — Redis removes expired keys),
``TaskConflictError`` (CAS abort, stale expectation, or a guarded
transition), ``InvalidRecordError`` (record/payload violates the store
contract), ``CorruptRecordError`` (stored bytes unreadable), and
``ProhibitedFieldError`` (DEC-174 violation).
"""

from __future__ import annotations

import json
import logging
import math
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol, cast

import redis
from pydantic import ValidationError
from redis.exceptions import RedisError, WatchError

from app.config import Settings
from app.schemas.job import ErrorSummary, Progress, ResultSummary
from app.tasks.state_machine import JobEvent, JobState, transition

logger = logging.getLogger(__name__)

# Keyspace prefix for task records; the suffix is the opaque task id.
TASK_KEY_PREFIX = "task"
# SCAN pattern matching only task records; enumeration never uses KEYS.
TASK_SCAN_PATTERN = f"{TASK_KEY_PREFIX}:*"
# Default socket bounds for the constructed client; the audit recommends
# explicit timeouts so a dead Redis fails closed instead of hanging.
_SOCKET_TIMEOUT_SECONDS = 5.0
_SOCKET_CONNECT_TIMEOUT_SECONDS = 5.0

# DEC-174: normalized field-name stems that must never be persisted.
# Substring matching after normalization (lowercase, separators stripped)
# catches compound and case variants; false positives fail closed.
_PROHIBITED_STEMS: tuple[str, ...] = (
    "filename",
    "name",
    "password",
    "passwd",
    "secret",
    "token",
    "signedurl",
    "url",
    "content",
    "bytes",
    "preview",
    "authorization",
    "auth",
    "cookie",
    "accesskey",
    "key",
)

_REQUIRED_HASH_FIELDS: frozenset[str] = frozenset(
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

# Events that end the job's active execution and stamp ``completed_at``.
# User cancellation is deliberately absent: a cancelled job was never
# completed, and ``updated_at`` carries its terminal timestamp.
_COMPLETING_EVENTS: frozenset[JobEvent] = frozenset(
    {
        JobEvent.RESULT_UPLOADED,
        JobEvent.ENGINE_ERROR,
        JobEvent.TIMEOUT,
        JobEvent.SAFETY_SHUTDOWN,
    }
)

# Terminal target states that carry their respective summary payload.
_TERMINAL_PAYLOAD_STATES: Mapping[JobState, str] = {
    JobState.DONE: "result",
    JobState.FAILED: "error",
}


class StoreError(RuntimeError):
    """Base class for typed task-store failures."""


class StoreUnavailableError(StoreError):
    """Redis is unreachable or a read/write/TTL operation failed.

    Includes ``noeviction`` OOM write failures: they are never silently
    dropped and surface here so admission fails closed.
    """


class TaskNotFoundError(StoreError):
    """The task id is unknown or its record already expired.

    Redis removes expired keys, so the store cannot distinguish an unknown
    id from an expired one; the status API derives the distinct not-found
    responses from the record's expiry semantics (arch 13.5).
    """


class TaskConflictError(StoreError):
    """Atomic conditional change refused.

    Raised when the record's state or ``updated_at`` no longer matches the
    caller's expectation (optimistic conflict, including a concurrent
    WATCH abort), or when the state machine does not permit the requested
    transition for the current state.
    """


class InvalidRecordError(StoreError):
    """The record or payload violates the store contract."""


class CorruptRecordError(StoreError):
    """Stored bytes cannot be decoded into a valid task record."""


class ProhibitedFieldError(StoreError):
    """A DEC-174 prohibited field was found where a task record is written."""


@dataclass(frozen=True)
class TaskRecord:
    """Minimal persisted task record (DEC-174).

    ``task_id`` is opaque and high-entropy. ``objects`` holds only
    non-sensitive temporary object references (opaque R2 keys); every other
    field is metadata. ``progress``/``result``/``error`` reuse the schemas'
    extra-``forbid`` models, so nested prohibited fields are structurally
    impossible.
    """

    task_id: str
    state: JobState
    tool: str
    created_at: datetime
    accepted_at: datetime
    updated_at: datetime
    expires_at: datetime
    queued_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    progress: Progress | None = None
    result: ResultSummary | None = None
    error: ErrorSummary | None = None
    objects: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransitionPayload:
    """Optional summaries attached to terminal transitions.

    ``result`` belongs on transitions to ``done``; ``error`` on transitions
    to ``failed``. The store enforces the pairing (mirroring the schemas'
    ``TaskStatus`` validator); both must be omitted on other transitions.
    """

    result: ResultSummary | None = None
    error: ErrorSummary | None = None


class PipelineLike(Protocol):
    """Watched pipeline surface the store consumes."""

    def watch(self, name: str) -> None: ...
    def hgetall(self, name: str) -> dict[bytes, bytes]: ...
    def multi(self) -> None: ...
    def hset(self, name: str, mapping: Mapping[str, str]) -> int: ...
    def hdel(self, name: str, *fields: str) -> int: ...
    def expire(self, name: str, time: int) -> bool: ...
    def execute(self, raise_on_error: bool = True) -> list[object]: ...
    def reset(self) -> None: ...


class RedisLike(Protocol):
    """Typed Redis surface the store consumes (single cast crossing point).

    The concrete ``redis.Redis`` client (or ``fakeredis.FakeRedis`` in
    tests) is cast to this protocol at construction; redis-py's own stubs
    union sync/async return types, while this module is strictly
    synchronous.
    """

    def hgetall(self, name: str) -> dict[bytes, bytes]: ...
    def pipeline(self, transaction: bool = True) -> PipelineLike: ...
    def ttl(self, name: str) -> int: ...
    def delete(self, name: str) -> int: ...
    def scan_iter(self, match: str | None = None, count: int = 100) -> Iterator[bytes]: ...
    def ping(self) -> bool: ...
    def close(self) -> None: ...


class LuaRedisLike(Protocol):
    """Typed EVAL surface for the Lua cancellation path (DEC-069).

    Stateless ``EVAL`` exactly like ``security.fair_use.CounterRedisLike``
    (no script-cache dependency); the concrete ``redis.Redis`` client is
    cast to this protocol at the store's construction. ``redis-py``
    decodes a script's ``return <int>`` as a scalar RESP integer and a
    returned table as a list, so the reply is typed as either.
    """

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> list[bytes | int] | int: ...


# DEC-069: queued-to-cancelled atomic transition. One server-side EVAL
# makes the existence/state/expiry checks and the terminal write a single
# atomic unit, so no interleaving can both cancel a job and let a worker
# execute it. Returns the full hash field set on success; a single-element
# code list on failure: {1} absent or logically expired, {2} exists but is
# not queued (cancellation is no longer available), {3} corrupt (missing
# ``state``/``expires_at`` fields).
_CANCEL_NOT_FOUND = 1
_CANCEL_CONFLICT = 2
_CANCEL_CORRUPT = 3
_CANCEL_LUA = """
local key = KEYS[1]
local now = ARGV[1]
local raw = redis.call('HGETALL', key)
if #raw == 0 then
  return {1}
end
local state = ''
local expires_at = ''
for i = 1, #raw, 2 do
  if raw[i] == 'state' then state = raw[i + 1] end
  if raw[i] == 'expires_at' then expires_at = raw[i + 1] end
end
if state == '' or expires_at == '' then
  return {3}
end
if state ~= 'queued' then
  return {2}
end
-- Both strings come from store._fmt_datetime: ISO-8601 UTC with a fixed
-- format and a fixed +00:00 offset, so lexicographic order is
-- chronological. The key keeps its existing TTL; cancellation never
-- extends the retention deadline.
if expires_at <= now then
  return {1}
end
redis.call('HSET', key, 'state', 'cancelled', 'updated_at', now)
return redis.call('HGETALL', key)
"""


class CancelMechanism(Protocol):
    """Atomic queued-to-cancelled transition seam (DEC-069).

    :class:`LuaCancelMechanism` is the production path (one server-side
    ``EVAL``); :class:`CasCancelMechanism` is the WATCH/MULTI/EXEC
    atomic-equivalent provable against fakeredis, which has no EVAL
    support. Both implement the same contract: the record must exist,
    not be logically expired, and be ``queued``; the terminal write then
    persists ``cancelled`` with ``updated_at`` stamped.
    """

    def cancel(self, task_id: str, *, now: datetime) -> TaskRecord: ...


def _task_key(task_id: str) -> str:
    return f"{TASK_KEY_PREFIX}:{task_id}"


def _normalize_key(key: str) -> str:
    lowered = key.lower()
    for separator in ("_", "-", " "):
        lowered = lowered.replace(separator, "")
    return lowered


def _scan_prohibited_fields(fields: Mapping[str, str]) -> None:
    for key in fields:
        if any(stem in _normalize_key(key) for stem in _PROHIBITED_STEMS):
            raise ProhibitedFieldError(f"prohibited field {key!r} cannot be persisted")


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise InvalidRecordError("datetimes must be timezone-aware UTC")


def _fmt_datetime(value: datetime) -> str:
    _require_utc(value)
    return value.isoformat(timespec="microseconds")


def _parse_datetime(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("stored datetime is not UTC")
    return parsed


def _optional_datetime(fields: Mapping[str, str], name: str) -> datetime | None:
    raw = fields.get(name)
    return None if raw is None else _parse_datetime(raw)


def _optional_progress(fields: Mapping[str, str]) -> Progress | None:
    raw = fields.get("progress")
    if raw is None:
        return None
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("progress must be a JSON object")
    return Progress.model_validate(payload)


def _optional_result(fields: Mapping[str, str]) -> ResultSummary | None:
    raw = fields.get("result")
    if raw is None:
        return None
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("result must be a JSON object")
    return ResultSummary.model_validate(payload)


def _optional_error(fields: Mapping[str, str]) -> ErrorSummary | None:
    raw = fields.get("error")
    if raw is None:
        return None
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("error must be a JSON object")
    return ErrorSummary.model_validate(payload)


def _optional_objects(fields: Mapping[str, str]) -> tuple[str, ...]:
    raw = fields.get("objects")
    if raw is None:
        return ()
    payload = json.loads(raw)
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("objects must be a JSON array of strings")
    return tuple(payload)


def _ttl_seconds(now: datetime, expires_at: datetime, max_ttl: int) -> int:
    remaining = math.floor((expires_at - now).total_seconds())
    if remaining <= 0:
        raise InvalidRecordError("expiry is not strictly in the future")
    if remaining > max_ttl:
        raise InvalidRecordError("expiry exceeds the retention bound")
    return remaining


def _serialize(record: TaskRecord) -> dict[str, str]:
    try:
        fields: dict[str, str] = {
            "task_id": record.task_id,
            "state": record.state.value,
            "tool": record.tool,
            "created_at": _fmt_datetime(record.created_at),
            "accepted_at": _fmt_datetime(record.accepted_at),
            "updated_at": _fmt_datetime(record.updated_at),
            "expires_at": _fmt_datetime(record.expires_at),
        }
        if record.queued_at is not None:
            fields["queued_at"] = _fmt_datetime(record.queued_at)
        if record.started_at is not None:
            fields["started_at"] = _fmt_datetime(record.started_at)
        if record.completed_at is not None:
            fields["completed_at"] = _fmt_datetime(record.completed_at)
        if record.progress is not None:
            fields["progress"] = json.dumps(
                record.progress.model_dump(), sort_keys=True, separators=(",", ":")
            )
        if record.result is not None:
            fields["result"] = json.dumps(
                record.result.model_dump(), sort_keys=True, separators=(",", ":")
            )
        if record.error is not None:
            fields["error"] = json.dumps(
                record.error.model_dump(), sort_keys=True, separators=(",", ":")
            )
        if record.objects:
            fields["objects"] = json.dumps(list(record.objects), separators=(",", ":"))
        _scan_prohibited_fields(fields)
        return fields
    except (TypeError, ValueError) as exc:
        if isinstance(exc, InvalidRecordError):
            raise
        raise InvalidRecordError("record could not be serialized") from exc


def _deserialize(task_id: str, raw: Mapping[bytes, bytes]) -> TaskRecord:
    try:
        fields = {_utf8(key): _utf8(value) for key, value in raw.items()}
    except UnicodeDecodeError as exc:
        raise CorruptRecordError("record contains non-UTF-8 data") from exc
    _scan_prohibited_fields(fields)
    missing = [name for name in _REQUIRED_HASH_FIELDS if name not in fields]
    if missing:
        raise CorruptRecordError(f"record missing required fields: {','.join(missing)}")
    if fields["task_id"] != task_id:
        raise CorruptRecordError("record task_id does not match its key")
    try:
        state = JobState(fields["state"])
    except ValueError as exc:
        raise CorruptRecordError("record has an unknown state") from exc
    try:
        return TaskRecord(
            task_id=task_id,
            state=state,
            tool=fields["tool"],
            created_at=_parse_datetime(fields["created_at"]),
            accepted_at=_parse_datetime(fields["accepted_at"]),
            updated_at=_parse_datetime(fields["updated_at"]),
            expires_at=_parse_datetime(fields["expires_at"]),
            queued_at=_optional_datetime(fields, "queued_at"),
            started_at=_optional_datetime(fields, "started_at"),
            completed_at=_optional_datetime(fields, "completed_at"),
            progress=_optional_progress(fields),
            result=_optional_result(fields),
            error=_optional_error(fields),
            objects=_optional_objects(fields),
        )
    except (ValueError, TypeError, ValidationError, json.JSONDecodeError) as exc:
        raise CorruptRecordError("stored record payload is corrupt") from exc


def _utf8(value: bytes) -> str:
    return value.decode("utf-8", errors="strict")


def _validate_new_record(record: TaskRecord, now: datetime, max_ttl: int) -> TaskRecord:
    if not record.task_id:
        raise InvalidRecordError("task_id must be non-empty")
    if record.state is not JobState.QUEUED:
        raise InvalidRecordError("records can only be created in the queued state")
    _require_utc(record.created_at)
    _require_utc(record.accepted_at)
    _require_utc(record.updated_at)
    _require_utc(record.expires_at)
    if record.queued_at is not None:
        _require_utc(record.queued_at)
    if record.started_at is not None or record.completed_at is not None:
        raise InvalidRecordError("created records cannot carry started or completed timestamps")
    if record.result is not None or record.error is not None:
        raise InvalidRecordError("created records cannot carry result or error summaries")
    if not record.created_at <= record.accepted_at <= record.expires_at:
        raise InvalidRecordError("created_at <= accepted_at <= expires_at is required")
    if not record.created_at <= record.updated_at <= record.expires_at:
        raise InvalidRecordError("created_at <= updated_at <= expires_at is required")
    if (
        record.queued_at is not None
        and not record.created_at <= record.queued_at <= record.expires_at
    ):
        raise InvalidRecordError("queued_at must fall within the record lifetime")
    _ttl_seconds(now, record.expires_at, max_ttl)
    return TaskRecord(
        task_id=record.task_id,
        state=record.state,
        tool=record.tool,
        created_at=record.created_at,
        accepted_at=record.accepted_at,
        updated_at=record.updated_at,
        expires_at=record.expires_at,
        queued_at=record.queued_at if record.queued_at is not None else record.created_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        progress=record.progress,
        result=record.result,
        error=record.error,
        objects=record.objects,
    )


def _validate_transition_payload(event: JobEvent, payload: TransitionPayload | None) -> None:
    result = payload.result if payload is not None else None
    error = payload.error if payload is not None else None
    if event is JobEvent.RESULT_UPLOADED:
        if result is None:
            raise InvalidRecordError("result is required when the target state is done")
        if error is not None:
            raise InvalidRecordError("error is only allowed when the target state is failed")
        return
    if event in (JobEvent.ENGINE_ERROR, JobEvent.TIMEOUT, JobEvent.SAFETY_SHUTDOWN):
        if error is None:
            raise InvalidRecordError("error is required when the target state is failed")
        if result is not None:
            raise InvalidRecordError("result is only allowed when the target state is done")
        return
    if result is not None or error is not None:
        raise InvalidRecordError("result and error are only allowed on terminal transitions")


def _build_client(settings: Settings) -> RedisLike:
    client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=False,
        socket_timeout=_SOCKET_TIMEOUT_SECONDS,
        socket_connect_timeout=_SOCKET_CONNECT_TIMEOUT_SECONDS,
    )
    return cast(RedisLike, client)


class LuaCancelMechanism:
    """DEC-069 cancel: one atomic EVAL (production path).

    The script checks existence, logical expiry, and the ``queued`` state
    and writes ``cancelled``/``updated_at`` in one server-side unit, so
    no interleaving can both cancel and execute the job. Script codes map
    to the store's typed errors: {1} -> :class:`TaskNotFoundError`, {2}
    -> :class:`TaskConflictError`, {3} -> :class:`CorruptRecordError`.
    """

    def __init__(self, client: LuaRedisLike) -> None:
        self._client = client

    def cancel(self, task_id: str, *, now: datetime) -> TaskRecord:
        key = _task_key(task_id)
        try:
            result = cast(
                list[bytes | int],
                self._client.eval(_CANCEL_LUA, 1, key, _fmt_datetime(now)),
            )
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc
        if len(result) == 1:
            code = result[0]
            if code == _CANCEL_NOT_FOUND:
                raise TaskNotFoundError()
            if code == _CANCEL_CONFLICT:
                raise TaskConflictError("task is not queued; cancellation is no longer available")
            if code != _CANCEL_CORRUPT:
                raise CorruptRecordError("cancellation script returned an unknown code")
            raise CorruptRecordError("task record is corrupt")
        fields: dict[bytes, bytes] = {}
        for index in range(0, len(result) - 1, 2):
            fields[cast(bytes, result[index])] = cast(bytes, result[index + 1])
        return _deserialize(task_id, fields)


class CasCancelMechanism:
    """Atomic-equivalent cancel via WATCH/MULTI/EXEC (fakeredis-provable).

    Mirrors :data:`_CANCEL_LUA` line by line: the record must exist, not
    be logically expired, and be ``queued``; the terminal write then
    persists ``cancelled`` with ``updated_at`` stamped and the TTL
    refreshed. The whole decision-plus-write is one WATCH/MULTI/EXEC
    transaction — the strongest atomic equivalent provable against
    fakeredis, which has no EVAL support (cf.
    ``security.fair_use.CasFairUseCounter``).
    """

    def __init__(self, client: RedisLike, max_ttl_seconds: int) -> None:
        self._client = client
        self._max_ttl_seconds = max_ttl_seconds

    def cancel(self, task_id: str, *, now: datetime) -> TaskRecord:
        key = _task_key(task_id)
        try:
            pipe = self._client.pipeline(transaction=True)
            try:
                pipe.watch(key)
                raw = pipe.hgetall(key)
                if not raw:
                    raise TaskNotFoundError()
                record = _deserialize(task_id, raw)
                if record.expires_at <= now:
                    raise TaskNotFoundError()
                if record.state is not JobState.QUEUED:
                    raise TaskConflictError(
                        "task is not queued; cancellation is no longer available"
                    )
                updated = TaskRecord(
                    task_id=record.task_id,
                    state=JobState.CANCELLED,
                    tool=record.tool,
                    created_at=record.created_at,
                    accepted_at=record.accepted_at,
                    updated_at=now,
                    expires_at=record.expires_at,
                    queued_at=record.queued_at,
                    started_at=record.started_at,
                    completed_at=record.completed_at,
                    progress=record.progress,
                    result=record.result,
                    error=record.error,
                    objects=record.objects,
                )
                pipe.multi()
                pipe.hset(key, mapping=_serialize(updated))
                pipe.expire(key, _ttl_seconds(now, updated.expires_at, self._max_ttl_seconds))
                pipe.execute()
                return updated
            finally:
                pipe.reset()
        except WatchError as exc:
            raise TaskConflictError("task changed concurrently; reload and retry") from exc
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc


class TaskStore:
    """Typed minimal task store over Redis hashes with TTL and atomic CAS.

    Constructor consumes :class:`app.config.Settings` (BE-01): the default
    client is built from ``redis_url`` with explicit socket timeouts, and
    ``retention_seconds`` bounds every record TTL. ``client`` is the test
    injection seam (fakeredis); ``clock`` the injectable time source.
    """

    def __init__(
        self,
        settings: Settings,
        client: RedisLike | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
        cancel: CancelMechanism | None = None,
    ) -> None:
        self._settings = settings
        self._client = client if client is not None else _build_client(settings)
        self._max_ttl_seconds = settings.retention_seconds
        self._clock = clock if clock is not None else (lambda: datetime.now(UTC))
        self._cancel_impl = (
            cancel if cancel is not None else LuaCancelMechanism(cast(LuaRedisLike, self._client))
        )

    def cancel(self, task_id: str) -> TaskRecord:
        """Atomically cancel a queued task (DEC-069); returns the cancelled record.

        The queued-to-cancelled transition runs as one server-side atomic
        unit (default: Lua EVAL; tests inject the CAS equivalent), so no
        interleaving can both cancel the job and let a worker execute it:
        a worker that already picked up the entry loses its claim CAS and
        reconciles against the terminal state without execution. Raises
        :class:`TaskNotFoundError` (unknown or logically expired),
        :class:`TaskConflictError` (not queued — cancellation is no
        longer available), :class:`CorruptRecordError` (undecodable
        record), or :class:`StoreUnavailableError`.
        """
        if not task_id:
            raise InvalidRecordError("task_id must be non-empty")
        return self._cancel_impl.cancel(task_id, now=self._clock())

    def create(self, record: TaskRecord) -> TaskRecord:
        """Persist *record* atomically with TTL = remaining artifact lifetime.

        The id must be absent (duplicate ids raise :class:`TaskConflictError`)
        and the record must be ``queued`` with UTC timestamps ordered
        ``created <= accepted/updated <= expires``, an expiry strictly in
        the future and within retention. The state/payload pairing invariant
        holds at construction: result/error summaries belong only on
        terminal transitions and are rejected here (progress may be set).
        Returns the normalized record (``queued_at`` defaults to
        ``created_at``).
        """
        now = self._clock()
        normalized = _validate_new_record(record, now, self._max_ttl_seconds)
        key = _task_key(record.task_id)
        try:
            pipe = self._client.pipeline(transaction=True)
            try:
                pipe.watch(key)
                if pipe.hgetall(key):
                    raise TaskConflictError("task id already exists")
                pipe.multi()
                pipe.hset(key, mapping=_serialize(normalized))
                pipe.expire(key, _ttl_seconds(now, normalized.expires_at, self._max_ttl_seconds))
                pipe.execute()
                return normalized
            finally:
                pipe.reset()
        except WatchError as exc:
            raise TaskConflictError("task created concurrently; reload and retry") from exc
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc

    def close(self) -> None:
        """Release the store's Redis connection pool (idempotent).

        Called by the application lifespan on shutdown so the API process
        exits cleanly without dangling pooled connections; the pool is
        re-created lazily if the store is used again.
        """
        self._client.close()

    def get(self, task_id: str) -> TaskRecord:
        """Return the record for *task_id*; unknown or expired ids fail closed."""
        if not task_id:
            raise InvalidRecordError("task_id must be non-empty")
        try:
            raw = self._client.hgetall(_task_key(task_id))
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc
        if not raw:
            raise TaskNotFoundError()
        return _deserialize(task_id, raw)

    def ping(self) -> None:
        """Probe Redis connectivity on the store's own client.

        Returns ``None`` when the store can reach Redis; raises
        :class:`StoreUnavailableError` (with only the exception class name
        logged) when it cannot. The readiness surface uses this probe so
        ``/health/ready`` reports exactly what the status/download routers
        will experience.
        """
        try:
            self._client.ping()
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc

    def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]:
        """Return up to *limit* records whose deadline has passed (BE-07 seam).

        Scans the ``task:*`` keyspace with SCAN (never KEYS) and compares
        each record's persisted ``expires_at`` against *now* — the
        authoritative filter, never Redis TTL — so records are discoverable
        between their deadline and the moment Redis reaps the key. Keys
        removed between the scan and the read are skipped, never raised;
        corrupt or tampered records fail closed with
        :class:`CorruptRecordError` and Redis failures map to
        :class:`StoreUnavailableError`, exactly like :meth:`get`. Callers
        loop with fresh pages until an empty list.
        """
        _require_utc(now)
        if limit < 1:
            raise InvalidRecordError("limit must be positive")
        try:
            results: list[TaskRecord] = []
            for raw_key in self._client.scan_iter(match=TASK_SCAN_PATTERN, count=limit):
                if len(results) >= limit:
                    break
                try:
                    key = _utf8(raw_key)
                except UnicodeDecodeError as exc:
                    raise CorruptRecordError("task key is not UTF-8") from exc
                raw = self._client.hgetall(key)
                if not raw:
                    continue
                record = _deserialize(key[len(TASK_KEY_PREFIX) + 1 :], raw)
                if record.expires_at <= now:
                    results.append(record)
            return results
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc

    def transition_state(
        self,
        task_id: str,
        event: JobEvent,
        *,
        expected_state: JobState,
        payload: TransitionPayload | None = None,
    ) -> TaskRecord:
        """Atomically apply *event* under compare-and-swap.

        ``expected_state`` must match the persisted record; a concurrent
        writer or stale expectation raises :class:`TaskConflictError`
        without any partial write. ``payload`` carries the result/error
        summaries for terminal transitions (``done``/``failed``); the store
        enforces the pairing. Only transitions permitted by
        ``app.tasks.state_machine`` are persisted; the state machine's
        timing rules stamp ``started_at`` (worker claim) and
        ``completed_at`` (result and failure events). Returns the updated
        record.
        """
        _validate_transition_payload(event, payload)
        result = payload.result if payload is not None else None
        error = payload.error if payload is not None else None

        def build(record: TaskRecord, now: datetime) -> TaskRecord:
            target = transition(record.state, event)
            if target is None:
                raise TaskConflictError("transition is not permitted for the current task state")
            if not isinstance(target, JobState):
                # Legal for done/failed, but expiry is a lifecycle outcome:
                # the record dies by TTL deletion, never by a persisted
                # transition (state_machine: ``expired`` is not a state).
                raise InvalidRecordError(
                    "deadline expiry is a lifecycle outcome, not a persisted transition"
                )
            started_at = now if event is JobEvent.WORKER_CLAIMED else record.started_at
            completed_at = now if event in _COMPLETING_EVENTS else record.completed_at
            return TaskRecord(
                task_id=record.task_id,
                state=target,
                tool=record.tool,
                created_at=record.created_at,
                accepted_at=record.accepted_at,
                updated_at=now,
                expires_at=record.expires_at,
                queued_at=record.queued_at,
                started_at=started_at,
                completed_at=completed_at,
                progress=record.progress,
                result=result,
                error=error,
                objects=record.objects,
            )

        return self._mutate(task_id, expected_state, None, build)

    def update_progress(
        self,
        task_id: str,
        progress: Progress | None,
        *,
        expected_state: JobState,
        expected_updated_at: datetime | None = None,
    ) -> TaskRecord:
        """Set or clear (``None``) the measurable progress under compare-and-swap.

        ``expected_state``/``expected_updated_at`` guard against stale
        writers exactly like :meth:`transition_state`; ``updated_at`` is
        advanced.
        """

        def build(record: TaskRecord, now: datetime) -> TaskRecord:
            return TaskRecord(
                task_id=record.task_id,
                state=record.state,
                tool=record.tool,
                created_at=record.created_at,
                accepted_at=record.accepted_at,
                updated_at=now,
                expires_at=record.expires_at,
                queued_at=record.queued_at,
                started_at=record.started_at,
                completed_at=record.completed_at,
                progress=progress,
                result=record.result,
                error=record.error,
                objects=record.objects,
            )

        return self._mutate(task_id, expected_state, expected_updated_at, build)

    def delete(self, task_id: str) -> bool:
        """Remove the record; idempotent. Returns whether a record existed.

        R2-style idempotent delete (cf. BE-03 ``delete_object``): a missing
        record returns ``False`` without raising, so cleanup retries and
        double-cancellations are safe. Counts make BE-07 deletion
        observability possible.
        """
        if not task_id:
            raise InvalidRecordError("task_id must be non-empty")
        try:
            return self._client.delete(_task_key(task_id)) > 0
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc

    def ttl_seconds(self, task_id: str) -> int:
        """Remaining TTL in whole seconds; fails closed on invariant breaks.

        A missing record raises :class:`TaskNotFoundError`; a record whose
        key lost its TTL violates the every-key-TTL contract and raises
        :class:`CorruptRecordError`. BE-07 uses this to schedule cleanup
        before the deadline.
        """
        if not task_id:
            raise InvalidRecordError("task_id must be non-empty")
        try:
            ttl = self._client.ttl(_task_key(task_id))
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc
        if ttl < 0:
            if ttl == -1:
                raise CorruptRecordError("record key has no TTL")
            raise TaskNotFoundError()
        return ttl

    def _mutate(
        self,
        task_id: str,
        expected_state: JobState,
        expected_updated_at: datetime | None,
        build: Callable[[TaskRecord, datetime], TaskRecord],
    ) -> TaskRecord:
        """WATCH/MULTI/EXEC compare-and-swap shared by stateful mutations."""
        if not task_id:
            raise InvalidRecordError("task_id must be non-empty")
        key = _task_key(task_id)
        try:
            pipe = self._client.pipeline(transaction=True)
            try:
                pipe.watch(key)
                raw = pipe.hgetall(key)
                if not raw:
                    raise TaskNotFoundError()
                record = _deserialize(task_id, raw)
                now = self._clock()
                if record.expires_at <= now:
                    raise TaskNotFoundError()
                if record.state is not expected_state:
                    raise TaskConflictError("task state changed concurrently; reload and retry")
                if expected_updated_at is not None and record.updated_at != expected_updated_at:
                    raise TaskConflictError("task updated concurrently; reload and retry")
                updated = build(record, now)
                serialized = _serialize(updated)
                removed = [_utf8(name) for name in raw if _utf8(name) not in serialized]
                pipe.multi()
                pipe.hset(key, mapping=serialized)
                if removed:
                    pipe.hdel(key, *removed)
                pipe.expire(key, _ttl_seconds(now, updated.expires_at, self._max_ttl_seconds))
                pipe.execute()
                return updated
            finally:
                pipe.reset()
        except WatchError as exc:
            raise TaskConflictError("task changed concurrently; reload and retry") from exc
        except RedisError as exc:
            logger.error(
                "task store redis failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise StoreUnavailableError() from exc
