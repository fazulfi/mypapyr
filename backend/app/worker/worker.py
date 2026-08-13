"""One-job worker substrate over the Redis Streams queue (BE-05).

The worker claims exactly one job at a time per instance (DEC-189): an
``XREADGROUP ... >`` read without ``NOACK`` keeps every delivery in the
PEL, and the PEL entry is released only after the BE-04 task store durably
records a terminal state (done/failed/cancelled) — never before. Terminal
release is ``XDEL`` then ``XACK``: the stream entry is removed first (one
command that clears it from both the stream and the PEL, so completed
jobs stop consuming the R-07 max-length/max-wait admission capacity) and
the acknowledgment fires second, strictly after the terminal store write.
Either failure degrades the worker and leaves the entry pending for
recovery — never acknowledged-but-retained, so a completed job can never
permanently occupy a queue slot. Execution runs through an injectable
:class:`JobExecutor` under an explicit per-job timeout
(:class:`ExecutionTimeoutPolicy`; per-tool overrides enter through the
same seam), and an injectable :class:`JobRunner` applies the wall-clock
bound (default: a daemon thread so a timed-out executor can never hang the
process).

Stale-claim recovery is a cursor-aware :class:`XAUTOCLAIM` loop with the
claim idle threshold strictly above the maximum execution timeout:
reclaimed entries are (a) re-executed when the store record is still
``queued`` (crash before the claim transition), (b) deleted and
acknowledged without re-execution when the record is already terminal
(crash between terminal store update and the PEL release), (c) failed as
``timeout`` without re-execution when the record is stale ``processing``
(crash mid-execution — at-most-once), and (d) dropped when the entry was
deleted/trimmed while pending. ``0-0`` terminates the loop; deleted-entry
ids are never executed.

Fail-closed behavior: any Redis or store unavailability raises
:class:`WorkerUnavailableError` and degrades the worker (``healthy`` is
False), which pauses queue admission through the readiness probe. Logs
carry exception class names and operation names only (DEC-175).

Fair use (F-4): a worker that picked up an entry releases the per-origin
concurrency claim its admission reserved exactly once — on terminal
completion/failure/timeout, on reconciliation of a terminal or
stale-processing record, and on abandon (record deleted). No raw origin
appears in entries or logs; release rides on the opaque origin
fingerprint plus a per-claim at-most-once marker.
"""

from __future__ import annotations

import logging
import multiprocessing
import os
import pickle
import signal
import threading
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from multiprocessing.connection import _ConnectionBase
from multiprocessing.context import SpawnContext
from multiprocessing.process import BaseProcess
from typing import Any, Protocol

from app.config import Settings
from app.queue.queue import (
    _CLAIM_IDLE_GRACE_SECONDS,
    GROUP_NAME,
    STREAM_KEY,
    ClaimedEntry,
    ConcurrencyReleaser,
    StreamsRedisLike,
    XAutoClaimResult,
    _build_stream_client,
)
from app.queue.store import (
    StoreError,
    StoreUnavailableError,
    TaskConflictError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import ErrorSummary, Progress, ResultSummary
from app.security.fair_use import FairUsePolicy
from app.tasks.state_machine import JobEvent, JobState

logger = logging.getLogger(__name__)

# Consumer name namespace: one named consumer per worker instance so a
# restarted worker resumes its own pending entries deterministically.
DEFAULT_CONSUMER_NAME = "worker"

# Safe, deterministic failure summaries (no engine internals; DEC-033).
TIMEOUT_ERROR = ErrorSummary(
    code="timeout", category="engine", retryable=True, message_key="error.jobTimeout"
)
ENGINE_ERROR_FALLBACK = ErrorSummary(
    code="engine_error", category="engine", retryable=False, message_key="error.engineError"
)

# Terminal states the worker may acknowledge without re-execution.
_TERMINAL_STATES: frozenset[JobState] = frozenset(
    {JobState.DONE, JobState.FAILED, JobState.CANCELLED}
)

# Entry field vocabulary the worker accepts: the queue's four fields, with
# ``origin`` carrying only the opaque 64-hex fingerprint (F-4). Entries
# predating the fingerprint field (three fields) decode with
# ``origin_fingerprint=None`` and are processed without a claim release.
_ENTRY_FIELDS: frozenset[str] = frozenset({"task_id", "tool", "route", "origin"})
_REQUIRED_ENTRY_FIELDS: frozenset[str] = frozenset({"task_id", "tool", "route"})
_HEX_DIGITS: frozenset[str] = frozenset("0123456789abcdef")
_FINGERPRINT_LENGTH = 64

# Bounded XAUTOCLAIM pass count; each pass pages through the PEL with the
# server default page size and terminates at cursor ``0-0``.
_RECOVERY_MAX_PASSES = 100

_TERMINAL_RETRY_MAX_ATTEMPTS = 6
_TERMINAL_RETRY_BASE_DELAY_SECONDS = 0.25
_TERMINAL_RETRY_MAX_DELAY_SECONDS = 2.0


class WorkerError(RuntimeError):
    """Base class for typed worker failures."""


class WorkerUnavailableError(WorkerError):
    """Redis or the task store is unavailable; the worker is degraded.

    Fail-closed: the worker pauses (``healthy`` False) so admission is
    rejected until a successful pass clears the degradation.
    """


class ExecutionKind(StrEnum):
    """Outcome of a job execution, as reported by the executor."""

    SUCCESS = "success"
    FAILURE = "failure"


@dataclass(frozen=True)
class ExecutionOutcome:
    """Executor result: a result summary on success, an error on failure.

    ``objects`` carries the published output object keys on a successful
    outcome; the worker maps a success without ``objects`` to a safe
    engine error instead of publishing a done record with no outputs.
    """

    kind: ExecutionKind
    result: ResultSummary | None = None
    error: ErrorSummary | None = None
    objects: tuple[str, ...] | None = None


_FAILED_CRASH_OUTCOME = ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)


@dataclass(frozen=True)
class ClaimedJob:
    """Minimal job context handed to executors (DEC-174: no document data)."""

    task_id: str
    tool: str
    route: str
    entry_id: bytes
    origin_fingerprint: str | None = None


ProgressReporter = Callable[[Progress], None]


class JobExecutor(Protocol):
    """Typed execution seam; tool handlers (TL) implement this.

    ``report`` forwards measurable progress to the task store
    (``expected_state`` processing); returning
    :class:`ExecutionOutcome` with a result/error pair. Raising or
    violating the outcome contract fails the job closed with a safe
    engine error.
    """

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome: ...


class JobRunner(Protocol):
    """Applies the per-job wall-clock timeout to an executor call.

    Returns the outcome, or ``None`` when the timeout elapsed first.
    """

    def run(
        self, job: ClaimedJob, report: ProgressReporter, timeout: timedelta
    ) -> ExecutionOutcome | None: ...


class _ChildProgressReporter:
    def __init__(self, conn: _ConnectionBase[Any, Any]) -> None:
        self._conn = conn

    def __call__(self, progress: Progress) -> None:
        if not isinstance(progress, Progress):
            raise TypeError("child progress must be Progress")
        self._conn.send(("progress", progress))


def _send_child_failure(conn: _ConnectionBase[Any, Any], error_name: str) -> None:
    with suppress(Exception):
        conn.send(("error", error_name))


def _child_target(executor: JobExecutor, job: ClaimedJob, conn: _ConnectionBase[Any, Any]) -> None:
    try:
        setsid = getattr(os, "setsid", None)
        if setsid is not None:
            setsid()
        outcome = executor.execute(job, _ChildProgressReporter(conn))
        if not isinstance(outcome, ExecutionOutcome):
            _send_child_failure(conn, "InvalidExecutionOutcome")
        else:
            conn.send(("outcome", outcome))
    except Exception as exc:
        _send_child_failure(conn, type(exc).__name__)
    finally:
        conn.close()


def _signal_group(pid: int | None, sig: int) -> None:
    if pid is None or os.name == "nt":
        return
    killpg = getattr(os, "killpg", None)
    if killpg is None:
        return
    with suppress(ProcessLookupError, PermissionError, OSError):
        killpg(pid, sig)


class DaemonThreadJobRunner:
    """Default runner for test-built workers: one daemon thread per job.

    A timed-out executor thread keeps running in the background (daemon, so
    process exit is never blocked) while the worker fails the job as
    ``timeout``. Production-built workers default to
    :class:`SubprocessJobRunner`, which hard-kills a timed-out execution.
    """

    def __init__(self, executor: JobExecutor) -> None:
        self._executor = executor

    def run(
        self, job: ClaimedJob, report: ProgressReporter, timeout: timedelta
    ) -> ExecutionOutcome | None:
        box: dict[str, object] = {}

        def target() -> None:
            try:
                box["outcome"] = self._executor.execute(job, report)
            except BaseException as exc:
                box["error"] = exc

        thread = threading.Thread(target=target, name="papyr-job", daemon=True)
        thread.start()
        thread.join(timeout=timeout.total_seconds())
        if thread.is_alive():
            return None
        if "error" in box:
            error = box["error"]
            if isinstance(error, BaseException):
                raise error
        outcome = box.get("outcome")
        return outcome if isinstance(outcome, ExecutionOutcome) else None


_TERMINATE_GRACE_SECONDS = 1.0
_KILL_GRACE_SECONDS = 2.0
_SIGKILL = getattr(signal, "SIGKILL", 9)


class SubprocessJobRunner:
    """Runs the executor in a spawn subprocess so a timeout can hard-kill it.

    The child runs :func:`_child_target` in a fresh interpreter with its own
    POSIX process group, so a timed-out execution including subprocess
    grandchildren (Ghostscript) is terminated, given a bounded grace, killed,
    and reaped before ``run()`` returns. Only type-level progress and an
    ``ExecutionOutcome`` (or a safe exception class name) cross the pipe.
    """

    def __init__(
        self,
        executor: JobExecutor,
        *,
        context: SpawnContext | None = None,
        terminate_grace: timedelta = timedelta(seconds=_TERMINATE_GRACE_SECONDS),
        kill_grace: timedelta = timedelta(seconds=_KILL_GRACE_SECONDS),
    ) -> None:
        if terminate_grace <= timedelta(0):
            raise WorkerError("subprocess runner terminate_grace must be positive")
        if kill_grace <= timedelta(0):
            raise WorkerError("subprocess runner kill_grace must be positive")
        self._executor = executor
        self._ctx = context if context is not None else multiprocessing.get_context("spawn")
        self._terminate_grace = terminate_grace.total_seconds()
        self._kill_grace = kill_grace.total_seconds()
        try:
            pickle.dumps(executor)
        except Exception as exc:
            raise WorkerError("subprocess runner requires a picklable executor") from exc
        self._active: BaseProcess | None = None

    def run(
        self, job: ClaimedJob, report: ProgressReporter, timeout: timedelta
    ) -> ExecutionOutcome | None:
        parent_conn, child_conn = self._ctx.Pipe(duplex=False)
        process = self._ctx.Process(target=_child_target, args=(self._executor, job, child_conn))
        try:
            process.start()
        except Exception:
            parent_conn.close()
            raise
        finally:
            child_conn.close()
        self._active = process
        try:
            return self._drive(parent_conn, process, report, timeout)
        finally:
            try:
                parent_conn.close()
            finally:
                self._reap(process)
                self._active = None

    def close(self) -> None:
        process = self._active
        self._active = None
        if process is None or process.pid is None:
            return
        _signal_group(process.pid, _SIGKILL)
        with suppress(ProcessLookupError, OSError):
            process.kill()
        process.join()
        with suppress(ValueError, OSError):
            process.close()

    def _drive(
        self,
        conn: _ConnectionBase[Any, Any],
        process: BaseProcess,
        report: ProgressReporter,
        timeout: timedelta,
    ) -> ExecutionOutcome | None:
        deadline = time.monotonic() + timeout.total_seconds()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._terminate(process)
                return None
            try:
                ready = conn.poll(remaining)
            except (OSError, ValueError):
                return _FAILED_CRASH_OUTCOME
            if not ready:
                continue
            try:
                message = conn.recv()
            except (EOFError, OSError):
                return _FAILED_CRASH_OUTCOME
            kind = message[0]
            if kind == "progress":
                report(message[1])
                continue
            if kind == "error":
                return _FAILED_CRASH_OUTCOME
            if kind == "outcome":
                outcome = message[1]
                return outcome if isinstance(outcome, ExecutionOutcome) else _FAILED_CRASH_OUTCOME
            return _FAILED_CRASH_OUTCOME

    def _terminate(self, process: BaseProcess) -> None:
        pid = process.pid
        _signal_group(pid, signal.SIGTERM)
        with suppress(ProcessLookupError, OSError):
            process.terminate()
        process.join(self._terminate_grace)
        if process.is_alive():
            _signal_group(pid, _SIGKILL)
            with suppress(ProcessLookupError, OSError):
                process.kill()
            process.join()

    def _reap(self, process: BaseProcess) -> None:
        process.join(self._kill_grace)
        if process.is_alive():
            _signal_group(process.pid, _SIGKILL)
            with suppress(ProcessLookupError, OSError):
                process.kill()
            process.join()
        with suppress(ValueError, OSError):
            process.close()


class ExecutionTimeoutPolicy(Protocol):
    """Per-tool execution timeout seam (R-07).

    The substrate default applies ``Settings.default_timeout_seconds``
    (approved 180 s) to every route; the approved per-tool overrides
    (e.g. PDF-to-JPG 300 s) enter through implementations of this
    protocol, and ``max_timeout`` bounds the stale-claim idle threshold.
    """

    def timeout_for(self, tool: str) -> timedelta: ...
    def max_timeout(self) -> timedelta: ...


class DefaultTimeoutPolicy:
    """Uniform timeout policy from the approved default setting."""

    def __init__(self, default: timedelta) -> None:
        self._default = default

    def timeout_for(self, tool: str) -> timedelta:
        del tool
        return self._default

    def max_timeout(self) -> timedelta:
        return self._default


class ToolTimeoutPolicy:
    """Approved per-tool execution timeout (R-07, I2).

    Reads the closed :data:`TOOL_LIMITS` registry so the worker's outer
    wall-clock timeout matches the per-tool cap the capabilities endpoint
    advertises (e.g. PDF-to-JPG 300 s) instead of a flat default. The
    stale-claim idle threshold uses ``max_timeout()`` — the ceiling across
    tools — so a still-running job is never reconciled as stale and
    re-executed (double-execution hazard).
    """

    def timeout_for(self, tool: str) -> timedelta:
        try:
            limit = TOOL_LIMITS[ToolId(tool)]
        except (KeyError, ValueError):
            # Unknown routes fail closed on the conservative default rather
            # than granting an unbounded or flat 180 s window.
            return timedelta(seconds=180)
        return timedelta(seconds=limit.max_execution_seconds)

    def max_timeout(self) -> timedelta:
        ceiling = max(
            (limit.max_execution_seconds for limit in TOOL_LIMITS.values()),
            default=180,
        )
        return timedelta(seconds=ceiling)


class TerminalRetryPolicy(Protocol):
    """Bounded retry/backoff seam for terminal store writes (F-3).

    ``wait_before_retry(attempt)`` is invoked after each failed terminal
    ``transition_state`` that raised :class:`StoreUnavailableError`;
    ``attempt`` is 1-based. It returns True to retry (blocking however the
    policy sees fit) or False once the bound is exhausted, in which case the
    worker fails closed, degrades, and leaves the entry in the PEL
    unacknowledged.
    """

    def wait_before_retry(self, attempt: int) -> bool: ...


class BoundedBackoffTerminalRetryPolicy:
    """Deterministic bounded backoff for terminal persistence.

    Up to ``max_attempts`` total attempts (first plus retries); before each
    retry it sleeps ``base_delay * 2 ** (attempt - 1)`` seconds, capped at
    ``max_delay``. ``sleep`` is the injectable seam — tests substitute a
    no-op recorder so retries stay deterministic and fast.
    """

    def __init__(
        self,
        *,
        max_attempts: int = _TERMINAL_RETRY_MAX_ATTEMPTS,
        base_delay: float = _TERMINAL_RETRY_BASE_DELAY_SECONDS,
        max_delay: float = _TERMINAL_RETRY_MAX_DELAY_SECONDS,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise WorkerError("terminal retry max_attempts must be positive")
        self._max_attempts = max_attempts
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._sleep = sleep

    def wait_before_retry(self, attempt: int) -> bool:
        if attempt >= self._max_attempts:
            return False
        delay = min(self._base_delay * (2 ** (attempt - 1)), self._max_delay)
        self._sleep(delay)
        return True


def _decode_entry(fields: dict[bytes, bytes]) -> tuple[str, str, str, str | None] | None:
    """Decode an entry into (task_id, tool, route, origin_fingerprint).

    ``origin_fingerprint`` is None for entries without the field or when
    it is not a well-formed 64-hex fingerprint; None disables the claim
    release (F-4). Returns None when the entry is malformed.
    """
    try:
        decoded = {key.decode("utf-8"): value.decode("utf-8") for key, value in fields.items()}
    except UnicodeDecodeError:
        return None
    if _REQUIRED_ENTRY_FIELDS - set(decoded):
        return None
    if set(decoded) - _ENTRY_FIELDS:
        return None
    task_id, tool, route = decoded["task_id"], decoded["tool"], decoded["route"]
    if not task_id or not tool or not route:
        return None
    origin = decoded.get("origin")
    if origin is not None and not _is_fingerprint(origin):
        return None
    return task_id, tool, route, origin


def _is_fingerprint(value: str) -> bool:
    """True for a well-formed opaque SHA-256 hex fingerprint."""
    return len(value) == _FINGERPRINT_LENGTH and all(char in _HEX_DIGITS for char in value)


@dataclass(frozen=True)
class WorkerOptions:
    """Injection knobs for :class:`JobWorker`.

    ``consumer_name`` names this worker's PEL consumer (a restarted worker
    resumes its own pending entries), ``clock`` is the time source for
    stale-record recovery, ``runner`` the timeout seam, ``timeout_policy``
    the per-tool timeout seam, ``terminal_retry`` the bounded retry seam
    for terminal store persistence, ``releaser`` the at-most-once
    concurrency-claim release seam (F-4; defaults to a Settings-backed
    fair-use policy on production-built workers), and ``claim_min_idle``
    the stale-claim idle threshold (defaults to ``max_timeout + 60 s``).
    """

    consumer_name: str = DEFAULT_CONSUMER_NAME
    clock: Callable[[], datetime] | None = None
    runner: JobRunner | None = None
    timeout_policy: ExecutionTimeoutPolicy | None = None
    terminal_retry: TerminalRetryPolicy | None = None
    releaser: ConcurrencyReleaser | None = None
    claim_min_idle: timedelta | None = None


class JobWorker:
    """One in-flight job per instance over the Streams consumer group.

    Constructor consumes :class:`app.config.Settings` (BE-01) and the
    BE-04 :class:`TaskStore`. ``client`` is the test injection seam
    (fakeredis), ``executor`` the typed job seam, and ``options`` carries
    the injectable consumer name, clock, runner, timeout policy, and claim
    idle threshold.
    """

    def __init__(
        self,
        settings: Settings,
        store: TaskStore,
        client: StreamsRedisLike | None = None,
        *,
        executor: JobExecutor,
        options: WorkerOptions | None = None,
    ) -> None:
        self._settings = settings
        self._store = store
        self._client = client if client is not None else _build_stream_client(settings)
        knobs = options if options is not None else WorkerOptions()
        self._consumer_name = knobs.consumer_name
        self._clock = knobs.clock if knobs.clock is not None else (lambda: datetime.now(UTC))
        self._executor = executor
        self._runner = (
            knobs.runner
            if knobs.runner is not None
            else SubprocessJobRunner(executor)
            if client is None
            else DaemonThreadJobRunner(executor)
        )
        self._policy = (
            knobs.timeout_policy if knobs.timeout_policy is not None else ToolTimeoutPolicy()
        )
        self._terminal_retry = (
            knobs.terminal_retry
            if knobs.terminal_retry is not None
            else BoundedBackoffTerminalRetryPolicy()
        )
        # F-4: a production-built worker (client=None) releases the
        # fair-use concurrency claim its admissions reserved through a
        # Settings-backed shared policy; a test-built worker releases only
        # through an explicitly injected releaser.
        self._releaser = (
            knobs.releaser
            if knobs.releaser is not None
            else FairUsePolicy(settings)
            if client is None
            else None
        )
        self._claim_min_idle = (
            knobs.claim_min_idle
            if knobs.claim_min_idle is not None
            else self._policy.max_timeout() + timedelta(seconds=_CLAIM_IDLE_GRACE_SECONDS)
        )
        if self._claim_min_idle <= self._policy.max_timeout():
            raise WorkerError("claim_min_idle must be strictly above the max execution timeout")
        self._in_flight = False
        self._healthy = True
        self._closed = False
        self._group_ready = False

    @property
    def claim_min_idle(self) -> timedelta:
        """Stale-claim idle threshold, strictly above the execution timeout."""
        return self._claim_min_idle

    @property
    def in_flight(self) -> bool:
        """True while one job is claimed and being executed."""
        return self._in_flight

    @property
    def healthy(self) -> bool:
        """False while degraded by Redis/store unavailability (fail-closed)."""
        return self._healthy

    def run_once(self) -> bool:
        """Claim and run at most one job; True when work was performed.

        New deliveries (``XREADGROUP ... >``, no NOACK) are read first;
        when none, a cursor-aware :class:`XAUTOCLAIM` recovery pass runs.
        While a job is in flight the call returns False immediately — one
        active job per worker instance (DEC-189). Redis or store
        unavailability raises :class:`WorkerUnavailableError` and degrades
        the worker.
        """
        if self._closed:
            raise WorkerError("worker is closed")
        if self._in_flight:
            return False
        try:
            entry = self._read_new()
            if entry is not None:
                self._handle_entry(entry[0], entry[1])
                return True
            return self._recover()
        except WorkerUnavailableError:
            raise
        except Exception as exc:
            logger.error(
                "worker failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            self._healthy = False
            raise WorkerUnavailableError() from exc

    def close(self) -> None:
        """Stop the worker and defensively close a lifecycle-aware runner."""
        self._closed = True
        close = getattr(self._runner, "close", None)
        if callable(close):
            close()

    def _read_new(self) -> tuple[bytes, dict[bytes, bytes]] | None:
        self._ensure_group()
        result = self._client.xreadgroup(
            GROUP_NAME, self._consumer_name, {STREAM_KEY: ">"}, count=1
        )
        if not result:
            self._healthy = True
            return None
        entries = result[0][1]
        if not entries:
            self._healthy = True
            return None
        entry_id, fields = entries[0]
        return entry_id, dict(fields)

    def _recover(self) -> bool:
        cursor = b"0-0"
        handled = False
        for _ in range(_RECOVERY_MAX_PASSES):
            claimed = self._client.xautoclaim(
                STREAM_KEY,
                GROUP_NAME,
                self._consumer_name,
                int(self._claim_min_idle.total_seconds() * 1000),
                start_id=cursor,
            )
            next_cursor, entries, deleted = self._split_claim(claimed)
            if deleted:
                logger.info(
                    "worker dropped deleted pending entries",
                    extra={"fields": {"count": len(deleted)}},
                )
                handled = True
            for entry_id, fields in entries:
                self._handle_entry(entry_id, dict(fields))
                handled = True
            if not entries and not deleted:
                break
            if next_cursor == b"0-0":
                break
            if next_cursor == cursor:
                break
            cursor = next_cursor
        self._healthy = True
        return handled

    def _split_claim(
        self, claimed: XAutoClaimResult
    ) -> tuple[bytes, list[ClaimedEntry], list[bytes]]:
        next_cursor = claimed[0] if isinstance(claimed[0], bytes) else b"0-0"
        entries = claimed[1]
        deleted = claimed[2]
        return next_cursor, entries, deleted

    def _handle_entry(self, entry_id: bytes, fields: dict[bytes, bytes]) -> None:
        decoded = _decode_entry(fields)
        if decoded is None:
            logger.error("worker malformed queue entry")
            self._xdel(entry_id)
            self._xack(entry_id)
            return
        task_id, tool, route, origin_fingerprint = decoded
        try:
            record = self._store.transition_state(
                task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
            )
        except TaskNotFoundError:
            self._xdel(entry_id)
            self._xack(entry_id)
            self._release_fingerprint(origin_fingerprint, task_id)
            return
        except TaskConflictError:
            self._reconcile(entry_id, task_id, route, origin_fingerprint)
            return
        claimed = ClaimedJob(
            task_id=task_id,
            tool=tool,
            route=route,
            entry_id=entry_id,
            origin_fingerprint=origin_fingerprint,
        )
        self._run_claimed(claimed, record)

    def _reconcile(
        self, entry_id: bytes, task_id: str, route: str, origin_fingerprint: str | None
    ) -> None:
        """Resolve a claim conflict from the store's authoritative state.

        Terminal outcomes free the reserved concurrency claim exactly once
        (F-4); the per-claim release marker makes a repeat release by a
        later recovery pass a no-op.
        """
        try:
            record = self._store.get(task_id)
        except TaskNotFoundError:
            self._xdel(entry_id)
            self._xack(entry_id)
            self._release_fingerprint(origin_fingerprint, task_id)
            return
        if record.state in _TERMINAL_STATES:
            self._xdel(entry_id)
            self._xack(entry_id)
            self._release_fingerprint(origin_fingerprint, task_id)
            return
        if record.state is JobState.PROCESSING and self._is_stale(record, route):
            try:
                self._store.transition_state(
                    task_id,
                    JobEvent.TIMEOUT,
                    expected_state=JobState.PROCESSING,
                    payload=TransitionPayload(error=TIMEOUT_ERROR),
                )
            except TaskNotFoundError:
                self._xdel(entry_id)
                self._xack(entry_id)
                self._release_fingerprint(origin_fingerprint, task_id)
                return
            except TaskConflictError:
                return
            self._xdel(entry_id)
            self._xack(entry_id)
            self._release_fingerprint(origin_fingerprint, task_id)

    def _release_fingerprint(self, fingerprint: str | None, claim: str) -> None:
        """Release one concurrency claim by fingerprint; at-most-once (F-4)."""
        releaser = self._releaser
        if releaser is None or fingerprint is None:
            return
        releaser.release_fingerprint_claim(fingerprint=fingerprint, claim=claim)

    def _is_stale(self, record: TaskRecord, route: str) -> bool:
        if record.started_at is None:
            return False
        return record.started_at + self._policy.timeout_for(route) <= self._clock()

    def _run_claimed(self, job: ClaimedJob, record: TaskRecord) -> None:
        self._in_flight = True
        try:
            outcome = self._execute(job)
            terminal = self._terminal_transition(job, record, outcome)
            if terminal is not None:
                self._release_fingerprint(job.origin_fingerprint, job.task_id)
                self._xdel(job.entry_id)
                self._xack(job.entry_id)
        finally:
            self._in_flight = False

    def _execute(self, job: ClaimedJob) -> ExecutionOutcome | None:
        def report(progress: Progress) -> None:
            try:
                self._store.update_progress(
                    job.task_id, progress, expected_state=JobState.PROCESSING
                )
            except StoreError as exc:
                logger.error(
                    "worker progress failure",
                    extra={"fields": {"error": type(exc).__name__}},
                )

        try:
            return self._runner.run(job, report, self._policy.timeout_for(job.route))
        except Exception as exc:
            logger.error(
                "worker execution failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

    def _terminal_transition(
        self, job: ClaimedJob, record: TaskRecord, outcome: ExecutionOutcome | None
    ) -> TaskRecord | None:
        if outcome is None:
            event, payload = JobEvent.TIMEOUT, TransitionPayload(error=TIMEOUT_ERROR)
        elif (
            outcome.kind is ExecutionKind.SUCCESS
            and outcome.result is not None
            and outcome.objects is not None
        ):
            event, payload = (
                JobEvent.RESULT_UPLOADED,
                TransitionPayload(result=outcome.result, objects=outcome.objects),
            )
        else:
            error = outcome.error if outcome.kind is ExecutionKind.FAILURE else None
            event, payload = (
                JobEvent.ENGINE_ERROR,
                TransitionPayload(error=error if error is not None else ENGINE_ERROR_FALLBACK),
            )
        attempt = 0
        while True:
            try:
                return self._store.transition_state(
                    job.task_id, event, expected_state=record.state, payload=payload
                )
            except StoreUnavailableError as exc:
                # F-3: a transient store outage must never convert a computed
                # result into a timeout. Retry (bounded backoff) before the
                # entry is acknowledged; only exhaustion fails closed, leaving
                # the entry in the PEL unacked for later recovery.
                attempt += 1
                error_name = type(exc).__name__
                if not self._terminal_retry.wait_before_retry(attempt):
                    logger.error(
                        "worker terminal persistence exhausted",
                        extra={"fields": {"attempts": attempt, "error": error_name}},
                    )
                    raise
                logger.warning(
                    "worker terminal persistence retry",
                    extra={"fields": {"attempt": attempt, "error": error_name}},
                )
            except TaskNotFoundError:
                self._xdel(job.entry_id)
                self._release_fingerprint(job.origin_fingerprint, job.task_id)
                return None
            except TaskConflictError:
                self._reconcile(job.entry_id, job.task_id, job.route, job.origin_fingerprint)
                return None

    def _xack(self, entry_id: bytes) -> None:
        try:
            self._client.xack(STREAM_KEY, GROUP_NAME, entry_id)
        except Exception as exc:
            logger.error(
                "worker ack failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            self._healthy = False
            raise WorkerUnavailableError() from exc

    def _xdel(self, entry_id: bytes) -> None:
        try:
            self._client.xdel(STREAM_KEY, entry_id)
        except Exception as exc:
            logger.error(
                "worker delete failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            self._healthy = False
            raise WorkerUnavailableError() from exc

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
                "worker redis failure",
                extra={"fields": {"error": name}},
            )
            self._healthy = False
            raise WorkerUnavailableError() from exc
        self._group_ready = True


__all__ = [
    "DEFAULT_CONSUMER_NAME",
    "ENGINE_ERROR_FALLBACK",
    "TIMEOUT_ERROR",
    "BoundedBackoffTerminalRetryPolicy",
    "ClaimedJob",
    "DaemonThreadJobRunner",
    "DefaultTimeoutPolicy",
    "ExecutionKind",
    "ExecutionOutcome",
    "ExecutionTimeoutPolicy",
    "JobExecutor",
    "JobRunner",
    "JobWorker",
    "ProgressReporter",
    "SubprocessJobRunner",
    "TerminalRetryPolicy",
    "WorkerError",
    "WorkerOptions",
    "WorkerUnavailableError",
]
