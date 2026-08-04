"""Cleanup coordinator for the temporary-object lifecycle (BE-07).

Application-side deletion half of the two-mechanism retention guarantee
(arch 12/13): delete every R2 object referenced by a task record **at**
the absolute deadline (``expires_at``), then remove the Redis record.
Deletion is idempotent (already-gone records count as clean, missing
objects count as success via BE-03's ``NoSuchKey`` semantics),
observable with counts and timing only (DEC-166), and recoverable after
restarts: a sweep that crashes mid-batch is re-runnable because every
step is safe to repeat, and a record whose objects failed to delete is
preserved (its TTL still expires it, and the R2 lifecycle rule remains
the independent backup — arch 13: either mechanism alone is
insufficient).

Ordering is the safety invariant: objects are deleted **before** the
record. Deleting the record first would orphan objects with no recovery
path other than the lifecycle rule; deleting objects first means a
record-deletion failure leaves only a stale record that dies by TTL.

Privacy contract (DEC-166, DEC-175): telemetry carries counts, timing,
and exception class names only. Task ids, object keys, bucket names, and
exception messages never reach logs — messages are fixed strings and
structured fields hold counts only.

Candidate discovery is wired to the BE-04 ``TaskStore.list_expired``
seam: ``run_expired`` drains the expired keyspace in bounded SCAN-based
pages — no snapshot, pages may revisit keys already cleaned, so progress
comes from deletion alone and the drain terminates on an empty page.
``run(task_ids)`` keeps the direct candidate-id API for callers that
already know their candidates. Restart recovery is inherent: the
keyspace is the only state, so a crashed drain simply re-discovers the
survivors.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NoReturn, Protocol

from app.queue.store import StoreError, TaskNotFoundError, TaskRecord

logger = logging.getLogger(__name__)


class CleanupOutcome(StrEnum):
    """Per-task disposition of a cleanup pass."""

    CLEANED = "cleaned"
    ALREADY_CLEAN = "already_clean"
    SKIPPED = "skipped"


class CleanupError(RuntimeError):
    """Base class for cleanup lifecycle failures."""


class CleanupUnavailableError(CleanupError):
    """Store or object-store degradation prevented cleanup (fail closed).

    Raised with the chained underlying error; the message carries counts
    only, never task ids or object references.
    """


@dataclass(frozen=True)
class TaskCleanupResult:
    """Typed outcome of cleaning a single task."""

    outcome: CleanupOutcome


@dataclass(frozen=True)
class CleanupRun:
    """Aggregate result of one sweep: counts and timing only (DEC-166)."""

    cleaned: int
    already_clean: int
    skipped: int
    started_at: datetime
    completed_at: datetime

    @property
    def elapsed_seconds(self) -> float:
        return (self.completed_at - self.started_at).total_seconds()


class CleanupStore(Protocol):
    """Minimal task-store surface the coordinator consumes (BE-04).

    ``list_expired`` is the discovery seam for the canonical deadline
    sweep: bounded SCAN-based pages of records whose persisted
    ``expires_at`` has passed but whose keys Redis has not yet reaped.
    """

    def get(self, task_id: str) -> TaskRecord: ...
    def delete(self, task_id: str) -> bool: ...
    def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]: ...


class ObjectDeleter(Protocol):
    """Minimal R2 delete surface the coordinator consumes (BE-03).

    ``delete_object`` is idempotent: a missing object counts as success,
    and any other service failure propagates so the coordinator can fail
    closed.
    """

    def delete_object(self, key: str) -> bool: ...


class CleanupCoordinator:
    """Deletes expired tasks' R2 objects and records, idempotently.

    Consumes BE-04's typed store and BE-03's R2 client through narrow
    protocols (the concrete ``TaskStore``/``R2Client`` satisfy them
    structurally). ``clock`` is the injectable time source; the deadline
    comparison ``expires_at <= now`` is the coordinator's own guard, so a
    caller can never trigger early deletion of a live job's objects
    (arch 9.1).
    """

    def __init__(
        self,
        store: CleanupStore,
        r2_client: ObjectDeleter,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = store
        self._r2 = r2_client
        self._clock = clock if clock is not None else (lambda: datetime.now(UTC))

    def cleanup_task(self, task_id: str) -> TaskCleanupResult:
        """Delete *task_id*'s expired objects and record.

        An already-removed record counts as :attr:`CleanupOutcome.
        ALREADY_CLEAN` without touching the object store (idempotent). A
        record whose deadline has not arrived is skipped, objects intact.
        Any store read failure or object deletion failure raises
        :class:`CleanupUnavailableError` with the record preserved.
        """
        now = self._clock()
        try:
            record = self._store.get(task_id)
        except TaskNotFoundError:
            return TaskCleanupResult(CleanupOutcome.ALREADY_CLEAN)
        except StoreError as exc:
            raise CleanupUnavailableError("cleanup could not read the task record") from exc
        if record.expires_at > now:
            return TaskCleanupResult(CleanupOutcome.SKIPPED)
        for key in record.objects:
            try:
                self._r2.delete_object(key)
            except Exception as exc:
                # R2Client propagates botocore ClientError (untyped,
                # importlib crossing point in r2.py); the typed contract
                # is "any non-NoSuchKey failure surfaces". Failing closed
                # on the record keeps it retryable by the next sweep.
                raise CleanupUnavailableError(
                    "cleanup could not delete a temporary object"
                ) from exc
        try:
            self._store.delete(task_id)
        except StoreError as exc:
            # Objects are already gone; the stale record dies by TTL.
            raise CleanupUnavailableError("cleanup could not remove the task record") from exc
        return TaskCleanupResult(CleanupOutcome.CLEANED)

    def run(self, task_ids: Iterable[str]) -> CleanupRun:
        """Sweep *task_ids*, aggregating counts and timing (DEC-166).

        Fails fast: the first per-task degradation aborts the sweep and
        raises :class:`CleanupUnavailableError` (chained), so the
        scheduler retries and the remaining candidates are never half-
        processed. The error log carries counts and the exception class
        name only.
        """
        started = self._clock()
        cleaned = 0
        already_clean = 0
        skipped = 0
        try:
            for task_id in task_ids:
                cleaned, already_clean, skipped = self._count_result(
                    self.cleanup_task(task_id), cleaned, already_clean, skipped
                )
        except CleanupError as exc:
            self._abort_run(cleaned, already_clean, skipped, exc)
        return self._finish_run(started, cleaned, already_clean, skipped)

    def run_expired(self, *, limit: int = 100) -> CleanupRun:
        """Drain expired records with bounded discovery passes.

        Repeatedly asks the store for up to *limit* expired records
        (SCAN-based pages; no snapshot — a page may revisit keys that
        earlier passes already cleaned) and cleans each one. Every
        returned record is deleted by the pass or already gone, so the
        expired keyspace strictly shrinks and the drain terminates on an
        empty page; progress never depends on page disjointness. A store
        discovery failure aborts fail-closed (chained); per-task
        degradation aborts like :meth:`run`. Restart recovery is
        inherent: the keyspace is the only state, so a crashed drain
        re-discovers the survivors.
        """
        started = self._clock()
        cleaned = 0
        already_clean = 0
        skipped = 0
        try:
            while True:
                page = self._store.list_expired(self._clock(), limit=limit)
                if not page:
                    break
                for record in page:
                    cleaned, already_clean, skipped = self._count_result(
                        self.cleanup_task(record.task_id), cleaned, already_clean, skipped
                    )
        except StoreError as exc:
            logger.error(
                "cleanup run failed",
                extra={
                    "fields": {
                        "cleaned": cleaned,
                        "already_clean": already_clean,
                        "skipped": skipped,
                        "error": type(exc).__name__,
                    }
                },
            )
            raise CleanupUnavailableError("cleanup could not discover expired records") from exc
        except CleanupError as exc:
            self._abort_run(cleaned, already_clean, skipped, exc)
        return self._finish_run(started, cleaned, already_clean, skipped)

    @staticmethod
    def _count_result(
        result: TaskCleanupResult, cleaned: int, already_clean: int, skipped: int
    ) -> tuple[int, int, int]:
        if result.outcome is CleanupOutcome.CLEANED:
            return cleaned + 1, already_clean, skipped
        if result.outcome is CleanupOutcome.ALREADY_CLEAN:
            return cleaned, already_clean + 1, skipped
        return cleaned, already_clean, skipped + 1

    def _finish_run(
        self, started: datetime, cleaned: int, already_clean: int, skipped: int
    ) -> CleanupRun:
        completed = self._clock()
        run = CleanupRun(
            cleaned=cleaned,
            already_clean=already_clean,
            skipped=skipped,
            started_at=started,
            completed_at=completed,
        )
        logger.info(
            "cleanup run ok",
            extra={
                "fields": {
                    "cleaned": cleaned,
                    "already_clean": already_clean,
                    "skipped": skipped,
                    "elapsed_ms": int(run.elapsed_seconds * 1000),
                }
            },
        )
        return run

    def _abort_run(
        self, cleaned: int, already_clean: int, skipped: int, exc: CleanupError
    ) -> NoReturn:
        processed = cleaned + already_clean + skipped + 1
        logger.error(
            "cleanup run failed",
            extra={
                "fields": {
                    "cleaned": cleaned,
                    "already_clean": already_clean,
                    "skipped": skipped,
                    "error": type(exc).__name__,
                }
            },
        )
        raise CleanupUnavailableError(
            f"cleanup aborted: 1 of {processed} candidate(s) failed"
        ) from exc
