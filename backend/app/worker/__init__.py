"""One-job worker substrate (BE-05).

The ``worker`` package owns the bounded processing loop over the BE-05
Redis Streams queue: one in-flight job per worker instance, explicit
per-job timeouts, XAUTOCLAIM stale-claim recovery, and XACK only after
the BE-04 task store records a terminal state. Tool handlers (TL) plug
into :class:`app.worker.worker.JobExecutor`; status consumers (BE-06)
consume the worker's ``healthy``/``in_flight`` posture and the queue's
typed errors.
"""

from __future__ import annotations

from app.worker.worker import (
    DEFAULT_CONSUMER_NAME,
    ENGINE_ERROR_FALLBACK,
    TIMEOUT_ERROR,
    ClaimedJob,
    DaemonThreadJobRunner,
    DefaultTimeoutPolicy,
    ExecutionKind,
    ExecutionOutcome,
    ExecutionTimeoutPolicy,
    JobExecutor,
    JobRunner,
    JobWorker,
    ProgressReporter,
    SubprocessJobRunner,
    WorkerError,
    WorkerUnavailableError,
)

__all__ = [
    "DEFAULT_CONSUMER_NAME",
    "ENGINE_ERROR_FALLBACK",
    "TIMEOUT_ERROR",
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
    "WorkerError",
    "WorkerUnavailableError",
]
