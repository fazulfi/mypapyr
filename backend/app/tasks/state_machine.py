"""Pure job-state transition rules for server tasks.

This module contains no persistence, Redis, queue, worker, or cleanup logic.
State vocabulary and transition rules follow the public architecture contract.

Expiry decision (wording-conflict resolution): ``expired`` is deliberately
NOT a member of ``JobState``. Expiry is not a state: the artifact lifecycle
is driven by the absolute retention deadline. Expiration is modeled as a separate lifecycle outcome
(``LifecycleOutcome.EXPIRED``) so the ``done -> expired`` and
``failed -> expired`` transitions stay expressible
without polluting the active public state vocabulary. Expired records are
no longer queryable as active tasks; the status contract returns a distinct
not-found response for them.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Final


class JobState(StrEnum):
    """Active public server task states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobEvent(StrEnum):
    """Events that drive transitions.

    ``ENGINE_ERROR``, ``TIMEOUT`` and ``SAFETY_SHUTDOWN`` are distinct events
    because failure reasons are explicitly modeled (the
    failure causes are system-controlled and distinct from user cancellation).
    """

    WORKER_CLAIMED = "worker_claimed"
    RESULT_UPLOADED = "result_uploaded"
    ENGINE_ERROR = "engine_error"
    TIMEOUT = "timeout"
    SAFETY_SHUTDOWN = "safety_shutdown"
    USER_CANCELLED = "user_cancelled"
    DEADLINE_REACHED = "deadline_reached"


class LifecycleOutcome(StrEnum):
    """Non-state lifecycle outcomes driven by the absolute retention deadline.

    Expiry is not a state. Keeping it here lets the transition table express
    ``done/failed -> expired`` without extending the active public
    ``JobState`` vocabulary.
    """

    EXPIRED = "expired"


type TransitionTarget = JobState | LifecycleOutcome

# Terminal active states: no transition to another ``JobState`` exists.
# ``done`` and ``failed`` additionally yield ``LifecycleOutcome.EXPIRED`` on
# ``DEADLINE_REACHED``; ``cancelled`` is fully terminal.
TERMINAL_STATES: Final[frozenset[JobState]] = frozenset(
    {JobState.DONE, JobState.FAILED, JobState.CANCELLED}
)

# Deterministic, exhaustive contract table. Every (state, event) pair not
# listed here is guarded: the
# transition is not permitted and ``transition`` returns ``None``. User
# cancellation is only expressible from ``queued``; atomicity with worker
# pickup requires an atomic queue operation and remains outside this module.
TRANSITIONS: Final[Mapping[tuple[JobState, JobEvent], TransitionTarget]] = {
    (JobState.QUEUED, JobEvent.WORKER_CLAIMED): JobState.PROCESSING,
    (JobState.QUEUED, JobEvent.USER_CANCELLED): JobState.CANCELLED,
    (JobState.PROCESSING, JobEvent.RESULT_UPLOADED): JobState.DONE,
    (JobState.PROCESSING, JobEvent.ENGINE_ERROR): JobState.FAILED,
    (JobState.PROCESSING, JobEvent.TIMEOUT): JobState.FAILED,
    (JobState.PROCESSING, JobEvent.SAFETY_SHUTDOWN): JobState.FAILED,
    (JobState.DONE, JobEvent.DEADLINE_REACHED): LifecycleOutcome.EXPIRED,
    (JobState.FAILED, JobEvent.DEADLINE_REACHED): LifecycleOutcome.EXPIRED,
}


def transition(state: JobState, event: JobEvent) -> TransitionTarget | None:
    """Return the deterministic target of ``event`` applied to ``state``.

    A guarded (not permitted) pair returns ``None``; the function is total
    over every (state, event) pair and never invents a state.
    """
    if not isinstance(state, JobState):
        raise TypeError(f"state must be a JobState member, got {type(state).__name__}")
    if not isinstance(event, JobEvent):
        raise TypeError(f"event must be a JobEvent member, got {type(event).__name__}")
    return TRANSITIONS.get((state, event))
