"""Scheduled cleanup service: bounded idempotent passes over expired tasks (U-OPS).

Operational activation layer over the BE-07 coordinator for the two-mechanism
retention guarantee (arch 12/13): one bounded, idempotent pass suitable for a
timer or dedicated process — never an unbounded drain, never a request-handler
hook. Each pass:

* discovers expired records through the BE-04 ``list_expired`` seam in
  bounded SCAN pages (``batch_limit``) with hard caps on discovery work
  (``max_pages``) and deletions (``max_records``); SCAN gives no snapshot,
  so a seen-set terminates the drain when pages revisit;
* applies expiry PLUS a grace period: a record becomes eligible only once
  ``expires_at + grace_seconds <= now`` — the arch 9.1 deadline guard plus a
  window against clock skew and deadline-boundary races;
* protects active jobs: records still ``processing`` are deferred and
  counted, never deleted, whatever their expiry says (a queued record past
  its deadline is unclaimable — the store's CAS rejects the claim — so it is
  safe to clean);
* delegates every deletion to the BE-07 coordinator, preserving the safety
  order (R2 objects first, then the record), idempotency, and fail-closed
  error taxonomy;
* records a bounded privacy-safe freshness marker (``ops:cleanup`` hash with
  TTL) after every real pass — success or failure — which the monitor reads;
  dry runs classify without deleting and never write the marker.

Privacy contract (DEC-166, DEC-175): logs and marker carry counts, timing,
and exception class names only; task ids, object keys, and exception messages
never appear. Marker field names stay clear of the DEC-174 prohibited stems.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.queue.store import TaskRecord
from app.tasks.cleanup import (
    CleanupCoordinator,
    CleanupError,
    CleanupOutcome,
)
from app.tasks.state_machine import JobState

logger = logging.getLogger(__name__)

CLEANUP_MARKER_KEY = "ops:cleanup"

DEFAULT_CLEANUP_GRACE_SECONDS = 300
DEFAULT_CLEANUP_BATCH_LIMIT = 100
DEFAULT_CLEANUP_MAX_RECORDS = 500
DEFAULT_CLEANUP_MAX_PAGES = 50
DEFAULT_CLEANUP_MARKER_TTL_SECONDS = 7 * 24 * 3600


class CleanupServiceError(CleanupError):
    """A scheduled pass failed; the marker records it and the cause chains."""


class CleanupMarkerStore(Protocol):
    """Minimal Redis surface for the freshness marker."""

    def hset(self, name: str, mapping: Mapping[str, str]) -> int: ...
    def expire(self, name: str, seconds: int) -> bool: ...
    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]: ...


class CleanupMarkerReader(Protocol):
    """Read-only subset of CleanupMarkerStore (sufficient for monitoring)."""

    def hgetall(self, name: str) -> Mapping[bytes | str, bytes | str]: ...


class CleanupStore(Protocol):
    """Task-store surface the service consumes (BE-04)."""

    def get(self, task_id: str) -> TaskRecord: ...
    def delete(self, task_id: str) -> bool: ...
    def list_expired(self, now: datetime, *, limit: int = 100) -> list[TaskRecord]: ...


class ObjectDeleter(Protocol):
    """R2 delete surface the service consumes (BE-03)."""

    def delete_object(self, key: str) -> bool: ...


@dataclass(frozen=True)
class CleanupServiceReport:
    """Aggregate outcome of one bounded pass: counts and timing only."""

    cleaned: int
    already_clean: int
    deferred_active: int
    deferred_grace: int
    examined: int
    dry_run: bool
    outcome: str
    error: str | None
    started_at: datetime
    completed_at: datetime

    @property
    def elapsed_seconds(self) -> float:
        return (self.completed_at - self.started_at).total_seconds()


def _decode_marker_value(value: bytes | str) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else value


def read_cleanup_marker(marker_store: CleanupMarkerReader) -> Mapping[str, str] | None:
    """Return the decoded ``ops:cleanup`` marker fields, or None when absent."""
    raw = marker_store.hgetall(CLEANUP_MARKER_KEY)
    if not raw:
        return None
    return {_decode_marker_value(key): _decode_marker_value(value) for key, value in raw.items()}


@dataclass(frozen=True)
class _PassCounters:
    cleaned: int
    already_clean: int
    deferred_active: int
    deferred_grace: int
    examined: int
    dry_run: bool
    started_at: datetime


@dataclass(frozen=True)
class CleanupServiceOptions:
    """Operational bounds for one scheduled cleanup pass."""

    grace_seconds: int = DEFAULT_CLEANUP_GRACE_SECONDS
    batch_limit: int = DEFAULT_CLEANUP_BATCH_LIMIT
    max_records: int = DEFAULT_CLEANUP_MAX_RECORDS
    max_pages: int = DEFAULT_CLEANUP_MAX_PAGES
    marker_ttl_seconds: int = DEFAULT_CLEANUP_MARKER_TTL_SECONDS


class CleanupService:
    """Bounded idempotent scheduled cleanup over the BE-07 coordinator."""

    def __init__(
        self,
        store: CleanupStore,
        r2_client: ObjectDeleter,
        *,
        clock: Callable[[], datetime] | None = None,
        marker_store: CleanupMarkerStore | None = None,
        options: CleanupServiceOptions | None = None,
    ) -> None:
        opts = options if options is not None else CleanupServiceOptions()
        if opts.grace_seconds < 0:
            raise ValueError("grace_seconds must be non-negative")
        if opts.batch_limit < 1 or opts.max_records < 1 or opts.max_pages < 1:
            raise ValueError("cleanup bounds must be positive")
        if opts.marker_ttl_seconds < 1:
            raise ValueError("marker_ttl_seconds must be positive")
        self._store = store
        self._clock = clock if clock is not None else (lambda: datetime.now(UTC))
        self._marker_store = marker_store
        self._grace = timedelta(seconds=opts.grace_seconds)
        self._batch_limit = opts.batch_limit
        self._max_records = opts.max_records
        self._max_pages = opts.max_pages
        self._marker_ttl = opts.marker_ttl_seconds
        self._coordinator = CleanupCoordinator(store, r2_client, clock=self._clock)

    def run_once(self, *, dry_run: bool = False) -> CleanupServiceReport:
        """Run one bounded pass; raises :class:`CleanupServiceError` fail-closed."""
        started = self._clock()
        cleaned = 0
        already_clean = 0
        deferred_active = 0
        deferred_grace = 0
        examined = 0
        seen: set[str] = set()
        try:
            for _ in range(self._max_pages):
                now = self._clock()
                page = self._store.list_expired(now, limit=self._batch_limit)
                if not page:
                    break
                fresh = [record for record in page if record.task_id not in seen]
                seen.update(record.task_id for record in page)
                if not fresh:
                    break
                for record in fresh:
                    examined += 1
                    if record.state is JobState.PROCESSING:
                        deferred_active += 1
                        continue
                    if record.expires_at + self._grace > now:
                        deferred_grace += 1
                        continue
                    if dry_run:
                        cleaned += 1
                        continue
                    result = self._coordinator.cleanup_task(record.task_id)
                    if result.outcome is CleanupOutcome.CLEANED:
                        cleaned += 1
                    elif result.outcome is CleanupOutcome.ALREADY_CLEAN:
                        already_clean += 1
                    else:
                        deferred_grace += 1
                    if cleaned + already_clean >= self._max_records:
                        return self._finish_success(
                            _PassCounters(
                                cleaned,
                                already_clean,
                                deferred_active,
                                deferred_grace,
                                examined,
                                dry_run,
                                started,
                            )
                        )
        except Exception as exc:
            self._mark_failure(exc)
            logger.error(
                "cleanup pass failed",
                extra={
                    "fields": {
                        "cleaned": cleaned,
                        "already_clean": already_clean,
                        "deferred_active": deferred_active,
                        "deferred_grace": deferred_grace,
                        "examined": examined,
                        "error": type(exc).__name__,
                    }
                },
            )
            raise CleanupServiceError("cleanup pass failed") from exc
        return self._finish_success(
            _PassCounters(
                cleaned, already_clean, deferred_active, deferred_grace, examined, dry_run, started
            )
        )

    def _finish_success(self, counters: _PassCounters) -> CleanupServiceReport:
        completed = self._clock()
        report = CleanupServiceReport(
            cleaned=counters.cleaned,
            already_clean=counters.already_clean,
            deferred_active=counters.deferred_active,
            deferred_grace=counters.deferred_grace,
            examined=counters.examined,
            dry_run=counters.dry_run,
            outcome="ok",
            error=None,
            started_at=counters.started_at,
            completed_at=completed,
        )
        if not counters.dry_run:
            self._write_marker(
                {
                    "last_outcome": "ok",
                    "last_success_at": completed.isoformat(timespec="seconds"),
                    "last_finished_at": completed.isoformat(timespec="seconds"),
                    "cleaned": str(counters.cleaned),
                    "already_clean": str(counters.already_clean),
                    "deferred_active": str(counters.deferred_active),
                    "deferred_grace": str(counters.deferred_grace),
                    "examined": str(counters.examined),
                }
            )
        logger.info(
            "cleanup pass ok",
            extra={
                "fields": {
                    "cleaned": counters.cleaned,
                    "already_clean": counters.already_clean,
                    "deferred_active": counters.deferred_active,
                    "deferred_grace": counters.deferred_grace,
                    "examined": counters.examined,
                    "dry_run": counters.dry_run,
                    "elapsed_ms": int(report.elapsed_seconds * 1000),
                }
            },
        )
        return report

    def _mark_failure(self, exc: Exception) -> None:
        completed = self._clock()
        self._write_marker(
            {
                "last_outcome": "failed",
                "last_finished_at": completed.isoformat(timespec="seconds"),
                "last_error": type(exc).__name__,
            }
        )

    def _write_marker(self, fields: Mapping[str, str]) -> None:
        if self._marker_store is None:
            return
        try:
            self._marker_store.hset(CLEANUP_MARKER_KEY, dict(fields))
            self._marker_store.expire(CLEANUP_MARKER_KEY, self._marker_ttl)
        except Exception as exc:
            logger.error(
                "cleanup marker write failed",
                extra={"fields": {"error": type(exc).__name__}},
            )
