"""Redis-backed task store domain (BE-04).

The ``queue`` package owns the durable, minimal-metadata Redis task store
and (in BE-05) the Streams-based queue. ``store.py`` is the only module this
package contributes in BE-04; it holds the typed task record the downstream
tasks (BE-05 queue, BE-06 status, BE-07 cleanup, BE-10 fair-use) consume.
"""

from __future__ import annotations

from app.queue.store import (
    CorruptRecordError,
    InvalidRecordError,
    ProhibitedFieldError,
    RedisLike,
    StoreUnavailableError,
    TaskConflictError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)

__all__ = [
    "CorruptRecordError",
    "InvalidRecordError",
    "ProhibitedFieldError",
    "RedisLike",
    "StoreUnavailableError",
    "TaskConflictError",
    "TaskNotFoundError",
    "TaskRecord",
    "TaskStore",
    "TransitionPayload",
]
