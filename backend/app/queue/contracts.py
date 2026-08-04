"""BE-05 admission seam types (shared by queue and fair use).

The admission decision levels, the deterministic :class:`AdmissionPolicy`
protocol, and the test-built always-allow default live here so the queue
(which defaults production admission to the Settings-backed fair-use
policy) and ``security.fair_use`` (which consumes the seam) can both
import them without a module cycle. ``app.queue.queue`` re-exports every
name for backward compatibility.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol


class AdmissionDecision(StrEnum):
    """R-08 enforcement levels expressible at admission."""

    ALLOW = "allow"
    DELAY = "delay"
    REJECT = "reject"


class AdmissionPolicy(Protocol):
    """Deterministic admission seam (R-08).

    BE-10 supplies the Redis-shared per-origin implementation; the
    protocol is the contract it plugs into. ``queued`` is the observed
    stream length at admission time.
    """

    def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision: ...


class AllowAllAdmission:
    """Deterministic always-allow policy for test-built queues.

    Ordinary and retried jobs have equal weight and no paid class exists
    (DEC-134/DEC-137). A production-built queue (``client=None``) instead
    defaults to the Settings-backed :class:`FairUsePolicy` (F-4), so the
    shipped admission posture is never allow-all.
    """

    def decide(self, *, origin: str | None, tool: str, queued: int) -> AdmissionDecision:
        del origin, tool, queued
        return AdmissionDecision.ALLOW


__all__ = ["AdmissionDecision", "AdmissionPolicy", "AllowAllAdmission"]
