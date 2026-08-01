"""Contract tests for the pure job-state transition module.

The public architecture specification defines the state vocabulary and
transition behavior verified here.

The full 5 x 7 = 35 (state, event) product is covered exactly once: every
pair is either a valid transition (``VALID_TRANSITIONS``) or a guarded pair
(``GUARDED_PAIRS``), and the union test locks that coverage so the contract
cannot grow or shrink without failing.
"""

from __future__ import annotations

from typing import Final, cast

import pytest

from app.tasks.state_machine import (
    TERMINAL_STATES,
    TRANSITIONS,
    JobEvent,
    JobState,
    LifecycleOutcome,
    TransitionTarget,
    transition,
)

# --- Public vocabulary ------------------------------------------------------

# Active public server task states (CR 2.1, lines 72-84; ARCH 13.1, line 145).
ACTIVE_STATE_VALUES: Final[tuple[str, ...]] = (
    "queued",
    "processing",
    "done",
    "failed",
    "cancelled",
)


def test_active_state_vocabulary_is_exact_closed_set() -> None:
    assert [state.value for state in JobState] == list(ACTIVE_STATE_VALUES)
    assert len(JobState) == 5


def test_expired_is_not_an_active_state() -> None:
    # Expiry is not a state (CR 2.1 line 84; ARCH 13.1 line 157): it is a
    # separate lifecycle outcome, never a member of the active JobState enum.
    assert "expired" not in {state.value for state in JobState}
    assert LifecycleOutcome.EXPIRED.value == "expired"


def test_terminal_states_are_done_failed_cancelled() -> None:
    assert frozenset({JobState.DONE, JobState.FAILED, JobState.CANCELLED}) == (TERMINAL_STATES)


# --- Transition table -------------------------------------------------------

VALID_TRANSITIONS: Final[tuple[tuple[JobState, JobEvent, JobState | LifecycleOutcome], ...]] = (
    (JobState.QUEUED, JobEvent.WORKER_CLAIMED, JobState.PROCESSING),
    (JobState.QUEUED, JobEvent.USER_CANCELLED, JobState.CANCELLED),
    (JobState.PROCESSING, JobEvent.RESULT_UPLOADED, JobState.DONE),
    (JobState.PROCESSING, JobEvent.ENGINE_ERROR, JobState.FAILED),
    (JobState.PROCESSING, JobEvent.TIMEOUT, JobState.FAILED),
    (JobState.PROCESSING, JobEvent.SAFETY_SHUTDOWN, JobState.FAILED),
    # Deadline expiry is a lifecycle outcome, not an active state (ARCH 13.1
    # lines 151-157; CR 2.2 lines 97-98).
    (JobState.DONE, JobEvent.DEADLINE_REACHED, LifecycleOutcome.EXPIRED),
    (JobState.FAILED, JobEvent.DEADLINE_REACHED, LifecycleOutcome.EXPIRED),
)

GUARDED_PAIRS: Final[tuple[tuple[JobState, JobEvent], ...]] = (
    # queued: only worker claim and user cancellation are permitted.
    (JobState.QUEUED, JobEvent.RESULT_UPLOADED),
    (JobState.QUEUED, JobEvent.ENGINE_ERROR),
    (JobState.QUEUED, JobEvent.TIMEOUT),
    (JobState.QUEUED, JobEvent.SAFETY_SHUTDOWN),
    (JobState.QUEUED, JobEvent.DEADLINE_REACHED),
    # processing: only result upload and the three failure events; a claimed
    # job can no longer be cancelled (ARCH 13.1 line 183).
    (JobState.PROCESSING, JobEvent.WORKER_CLAIMED),
    (JobState.PROCESSING, JobEvent.USER_CANCELLED),
    (JobState.PROCESSING, JobEvent.DEADLINE_REACHED),
    # done: terminal active state; only deadline-reached expiry applies.
    (JobState.DONE, JobEvent.WORKER_CLAIMED),
    (JobState.DONE, JobEvent.RESULT_UPLOADED),
    (JobState.DONE, JobEvent.ENGINE_ERROR),
    (JobState.DONE, JobEvent.TIMEOUT),
    (JobState.DONE, JobEvent.SAFETY_SHUTDOWN),
    (JobState.DONE, JobEvent.USER_CANCELLED),
    # failed: terminal active state; only deadline-reached expiry applies.
    (JobState.FAILED, JobEvent.WORKER_CLAIMED),
    (JobState.FAILED, JobEvent.RESULT_UPLOADED),
    (JobState.FAILED, JobEvent.ENGINE_ERROR),
    (JobState.FAILED, JobEvent.TIMEOUT),
    (JobState.FAILED, JobEvent.SAFETY_SHUTDOWN),
    (JobState.FAILED, JobEvent.USER_CANCELLED),
    # cancelled: terminal; every event is guarded (ARCH 13.1 line 154).
    (JobState.CANCELLED, JobEvent.WORKER_CLAIMED),
    (JobState.CANCELLED, JobEvent.RESULT_UPLOADED),
    (JobState.CANCELLED, JobEvent.ENGINE_ERROR),
    (JobState.CANCELLED, JobEvent.TIMEOUT),
    (JobState.CANCELLED, JobEvent.SAFETY_SHUTDOWN),
    (JobState.CANCELLED, JobEvent.USER_CANCELLED),
    (JobState.CANCELLED, JobEvent.DEADLINE_REACHED),
)


@pytest.mark.parametrize(
    ("state", "event", "expected"),
    VALID_TRANSITIONS,
    ids=[f"{s.value}--{e.value}->{t.value}" for s, e, t in VALID_TRANSITIONS],
)
def test_valid_transition(
    state: JobState, event: JobEvent, expected: JobState | LifecycleOutcome
) -> None:
    assert transition(state, event) is expected


@pytest.mark.parametrize(
    ("state", "event"),
    GUARDED_PAIRS,
    ids=[f"{s.value}--{e.value}" for s, e in GUARDED_PAIRS],
)
def test_guarded_transition_returns_none(state: JobState, event: JobEvent) -> None:
    # A guarded (invalid) pair is rejected deterministically: the contract
    # returns None instead of raising or inventing a state.
    assert transition(state, event) is None


def test_transition_table_matches_contract_exactly() -> None:
    # The table must contain exactly the eight contract transitions: no more,
    # no fewer. Any drift fails this test.
    assert len(TRANSITIONS) == len(VALID_TRANSITIONS)
    assert set(TRANSITIONS) == {(s, e) for s, e, _ in VALID_TRANSITIONS}


def test_every_state_event_pair_is_covered_exactly_once() -> None:
    # Exhaustiveness proof: the union of valid and guarded pairs is the full
    # 5 x 7 = 35 product, with no overlaps and no orphans.
    all_pairs = {(s, e) for s, e, _ in VALID_TRANSITIONS} | set(GUARDED_PAIRS)
    assert all_pairs == {(s, e) for s in JobState for e in JobEvent}
    assert len(VALID_TRANSITIONS) + len(GUARDED_PAIRS) == len(all_pairs) == 35


def test_transition_is_deterministic() -> None:
    for state, event, expected in VALID_TRANSITIONS:
        assert transition(state, event) is expected
        assert transition(state, event) is expected  # repeated call, same result


def test_expiry_result_is_outcome_not_active_state() -> None:
    for state in (JobState.DONE, JobState.FAILED):
        result = transition(state, JobEvent.DEADLINE_REACHED)
        assert result is LifecycleOutcome.EXPIRED
        assert not isinstance(result, JobState)


def test_terminal_states_never_transition_to_an_active_state() -> None:
    for state in TERMINAL_STATES:
        for event in JobEvent:
            result = transition(state, event)
            assert result is None or isinstance(result, LifecycleOutcome)


# --- Input guards -----------------------------------------------------------


def _transition_with_foreign(state: object, event: object) -> TransitionTarget | None:
    """Cross the typed boundary to exercise the runtime TypeError guards.

    The static signature only accepts ``JobState``/``JobEvent``; the foreign
    values below are deliberately cast because the runtime guards themselves
    are under test. Single justified crossing point: no ``Any``, no ignores.
    """
    return transition(cast(JobState, state), cast(JobEvent, event))


@pytest.mark.parametrize("bad_state", ["queued", "processing", 1, None, object()])
def test_non_jobstate_input_raises_type_error(bad_state: object) -> None:
    with pytest.raises(TypeError):
        _transition_with_foreign(bad_state, JobEvent.WORKER_CLAIMED)


@pytest.mark.parametrize("bad_event", ["worker_claimed", "done", 1, None, object()])
def test_non_jobevent_input_raises_type_error(bad_event: object) -> None:
    with pytest.raises(TypeError):
        _transition_with_foreign(JobState.QUEUED, bad_event)
