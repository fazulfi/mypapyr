"""Threat classification and fail-closed matrix (SEC-01).

Owned by SEC-01 (execution-matrix.md); consumed by TL-02..TL-04 (fail-closed
tests), SEC-02 (sanitize.py implements the :class:`Sanitizer` interface
behind this module) and SEC-03 (the concrete scanner client lands under
R-10). Implements the D5-brief threat-classification and fail-closed
matrix: anything not classifiable as safe fails closed (DEC-088, DEC-065,
DEC-171); a failed or stale scanner must never silently accept files;
blocking precedes sanitization and sanitization never downgrades a blocked
file into an output.

Threat classes are closed safe categories (:class:`ThreatClass`) with no
raw scanner/provider details, filenames, content, object keys, or
credentials (DEC-175, DEC-169). Rejections (:class:`ThreatRejection`) carry
only a closed category, a stable machine-readable code, and a message key
from the existing envelope vocabulary (``app/errors.py``) so the
presentation layer localizes them; the module defines no new message keys.
BE-02 validation outcomes map through the BE-08 failure vocabulary
(``app.routers.capabilities``: :func:`failure_code_for`) — the approved
vocabulary is the single source of truth, reused here, never duplicated.

The scanner and sanitizer interface contracts are the minimal protocols
SEC-02/SEC-03 implement: verdict objects carry closed status values only,
so a stub reporting scanner-unavailable exercises the fail-closed path
without any engine reach. This module performs no scanning, sanitization,
or I/O of any kind.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Protocol, runtime_checkable

from app.errors import ErrorCategory
from app.routers.capabilities import FailureCode, failure_code_for, failure_code_meta
from app.security.validation import ValidationFailure

__all__ = [
    "MESSAGE_KEY_FORBIDDEN",
    "MESSAGE_KEY_INTERNAL_ERROR",
    "MESSAGE_KEY_RATE_LIMITED",
    "SanitizationCategory",
    "SanitizationVerdict",
    "Sanitizer",
    "SanitizerStatus",
    "ScannerStatus",
    "ScannerVerdict",
    "SecurityDecision",
    "ThreatClass",
    "ThreatCode",
    "ThreatCodeMeta",
    "ThreatRejection",
    "ThreatScanner",
    "ThreatVerdict",
    "block_rejection",
    "classify_payload",
    "rejection_for",
    "threat_code_for",
    "threat_code_meta",
    "verdict_rejection",
]

# Message keys reused from the existing envelope vocabulary (app/errors.py);
# the presentation layer resolves them (errors.py docstring). No new keys
# are introduced: the values equal ``spec_for_status`` output verbatim.
MESSAGE_KEY_FORBIDDEN: Final[str] = "error.forbidden"
MESSAGE_KEY_INTERNAL_ERROR: Final[str] = "error.internalError"
MESSAGE_KEY_RATE_LIMITED: Final[str] = "error.rateLimited"


class ThreatClass(StrEnum):
    """Closed safe threat categories (D5 brief; DEC-088, DEC-169).

    Values are the stable machine-readable categories and never carry
    provider names, signatures, paths, or payload details.
    """

    MALICIOUS = "malicious"
    ACTIVE_CONTENT = "active_content"
    INDETERMINATE = "indeterminate"
    SCANNER_UNAVAILABLE = "scanner_unavailable"
    SANITIZATION_UNAVAILABLE = "sanitization_unavailable"


class ThreatCode(StrEnum):
    """Closed stable machine-readable threat codes (SEC-01-owned).

    The envelope vocabulary for blocked and fail-closed outcomes
    (``threat_blocked`` follows the c2 brief precedent); validation-mapped
    outcomes reuse the BE-08 :class:`FailureCode` vocabulary instead.
    """

    THREAT_BLOCKED = "threat_blocked"
    INDETERMINATE = "indeterminate"
    SCANNER_UNAVAILABLE = "scanner_unavailable"
    SANITIZATION_UNAVAILABLE = "sanitization_unavailable"


@dataclass(frozen=True)
class ThreatCodeMeta:
    """Stable metadata for a :class:`ThreatCode` (message key + retryability)."""

    message_key: str
    retryable: bool


_THREAT_CODE_META: Final[Mapping[ThreatCode, ThreatCodeMeta]] = {
    ThreatCode.THREAT_BLOCKED: ThreatCodeMeta(message_key=MESSAGE_KEY_FORBIDDEN, retryable=False),
    ThreatCode.INDETERMINATE: ThreatCodeMeta(
        message_key=MESSAGE_KEY_INTERNAL_ERROR, retryable=False
    ),
    ThreatCode.SCANNER_UNAVAILABLE: ThreatCodeMeta(
        message_key=MESSAGE_KEY_RATE_LIMITED, retryable=True
    ),
    ThreatCode.SANITIZATION_UNAVAILABLE: ThreatCodeMeta(
        message_key=MESSAGE_KEY_RATE_LIMITED, retryable=True
    ),
}

_THREAT_CODE_BY_CLASS: Final[Mapping[ThreatClass, ThreatCode]] = {
    ThreatClass.MALICIOUS: ThreatCode.THREAT_BLOCKED,
    ThreatClass.ACTIVE_CONTENT: ThreatCode.THREAT_BLOCKED,
    ThreatClass.INDETERMINATE: ThreatCode.INDETERMINATE,
    ThreatClass.SCANNER_UNAVAILABLE: ThreatCode.SCANNER_UNAVAILABLE,
    ThreatClass.SANITIZATION_UNAVAILABLE: ThreatCode.SANITIZATION_UNAVAILABLE,
}


def threat_code_meta(code: ThreatCode) -> ThreatCodeMeta:
    """Stable metadata for *code*; unknown codes fail closed.

    The ``isinstance`` guard mirrors ``failure_code_meta`` (BE-08):
    ``StrEnum`` members compare equal to their string value, so a plain
    string would otherwise pass the lookup.
    """
    if not isinstance(code, ThreatCode):
        raise ValueError(f"unknown threat code: {code!r}")
    return _THREAT_CODE_META[code]


def threat_code_for(threat_class: ThreatClass) -> ThreatCode:
    """The stable envelope code for a :class:`ThreatClass`."""
    if not isinstance(threat_class, ThreatClass):
        raise ValueError(f"unknown threat class: {threat_class!r}")
    return _THREAT_CODE_BY_CLASS[threat_class]


class ScannerStatus(StrEnum):
    """Closed scanner outcome values (no provider details, DEC-171)."""

    CLEAN = "clean"
    MALICIOUS = "malicious"
    UNAVAILABLE = "unavailable"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class ScannerVerdict:
    """Typed scanner outcome; the only field is the closed status value."""

    status: ScannerStatus


@runtime_checkable
class ThreatScanner(Protocol):
    """Scanner interface contract (SEC-03 implements under R-10; TL-03 consumes).

    ``scan`` must return a :class:`ScannerVerdict` and must never raise
    with payload details; unavailable and indeterminate outcomes are
    reported through the verdict so the fail-closed matrix can reject
    instead of silently accepting (DEC-171).
    """

    def scan(self, data: bytes) -> ScannerVerdict: ...


class SanitizationCategory(StrEnum):
    """Closed safe active-content categories (DEC-090/DEC-091).

    SEC-02 reports these after a sanitization pass; the names carry no
    payload details.
    """

    JAVASCRIPT = "javascript"
    EMBEDDED_ATTACHMENT = "embedded_attachment"
    LAUNCH_ACTION = "launch_action"
    EXTERNAL_ACTION = "external_action"


class SanitizerStatus(StrEnum):
    """Closed sanitization outcome values (DEC-171)."""

    CLEAN = "clean"
    SANITIZED = "sanitized"
    REFUSED = "refused"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class SanitizationVerdict:
    """Typed sanitization outcome: closed status plus closed category names.

    ``REFUSED`` means active content exceeded the sanitizable scope; the
    fail-closed matrix blocks such files (they are never downgraded into
    outputs).
    """

    status: SanitizerStatus
    categories: tuple[SanitizationCategory, ...] = ()


@runtime_checkable
class Sanitizer(Protocol):
    """Sanitization interface contract (SEC-02 implements; TL-04 consumes).

    ``sanitize`` must return a :class:`SanitizationVerdict`; refusal and
    unavailability must be reported through the verdict (fail closed),
    never raised with payload details.
    """

    def sanitize(self, data: bytes) -> SanitizationVerdict: ...


class SecurityDecision(StrEnum):
    """Closed decision outcomes of the fail-closed matrix (D5 brief)."""

    ALLOW = "allow"
    BLOCK = "block"
    REJECT = "reject"


@dataclass(frozen=True)
class ThreatVerdict:
    """Result of the fail-closed classification matrix.

    ``ALLOW`` carries no rejection fields; ``BLOCK`` carries
    ``threat_class``; ``REJECT`` carries the BE-02 ``failure``. Message
    keys always come from the existing envelope vocabulary.
    """

    decision: SecurityDecision
    message_key: str | None = None
    retryable: bool = False
    threat_class: ThreatClass | None = None
    failure: ValidationFailure | None = None


class ThreatRejection(Exception):
    """Fail-closed rejection carrying only safe closed-category fields.

    Exactly one of ``failure`` (BE-02 outcome) or ``threat_class`` is set;
    ``code`` is the BE-08 :class:`FailureCode` for validation outcomes or
    the SEC-01 :class:`ThreatCode` for threat blocks. ``str()`` yields the
    bare category value; filenames, contents, passwords, and engine
    details never reach the exception (DEC-175).
    """

    failure: ValidationFailure | None
    threat_class: ThreatClass | None
    code: FailureCode | ThreatCode
    category: ErrorCategory
    message_key: str
    retryable: bool

    def __init__(
        self,
        *,
        failure: ValidationFailure | None = None,
        threat_class: ThreatClass | None = None,
        message_key: str,
        retryable: bool = False,
    ) -> None:
        if (failure is None) == (threat_class is None):
            raise ValueError("exactly one of failure/threat_class must be set")
        if failure is not None:
            super().__init__(failure.value)
            self.failure = failure
            self.threat_class = None
            self.code = failure_code_for(failure)
            self.category = ErrorCategory.VALIDATION
        else:
            assert threat_class is not None
            super().__init__(threat_class.value)
            self.failure = None
            self.threat_class = threat_class
            self.code = threat_code_for(threat_class)
            self.category = ErrorCategory.THREAT
        self.message_key = message_key
        self.retryable = retryable


def rejection_for(failure: ValidationFailure) -> ThreatRejection:
    """Map a BE-02 validation outcome to a safe localizable rejection.

    The code comes from the BE-08 failure vocabulary
    (:func:`failure_code_for`) and the message key/retryability from its
    stable metadata — the approved vocabulary is reused, never duplicated.
    """
    if not isinstance(failure, ValidationFailure):
        raise ValueError(f"unknown validation failure: {failure!r}")
    code = failure_code_for(failure)
    meta = failure_code_meta(code)
    return ThreatRejection(
        failure=failure,
        message_key=meta.message_key,
        retryable=meta.retryable,
    )


def block_rejection(threat_class: ThreatClass) -> ThreatRejection:
    """A fail-closed block rejection for *threat_class*."""
    if not isinstance(threat_class, ThreatClass):
        raise ValueError(f"unknown threat class: {threat_class!r}")
    meta = threat_code_meta(threat_code_for(threat_class))
    return ThreatRejection(
        threat_class=threat_class,
        message_key=meta.message_key,
        retryable=meta.retryable,
    )


def _blocked(threat_class: ThreatClass) -> ThreatVerdict:
    meta = threat_code_meta(threat_code_for(threat_class))
    return ThreatVerdict(
        decision=SecurityDecision.BLOCK,
        message_key=meta.message_key,
        retryable=meta.retryable,
        threat_class=threat_class,
    )


def _scan_block(scanner_verdict: ScannerVerdict | None) -> ThreatVerdict | None:
    """Blocking verdict when scanning is required and not clean, else ``None``.

    ``None`` here means "no verdict was produced" and fails closed as
    scanner-unavailable — a missing result must never silently accept.
    """
    if scanner_verdict is None or scanner_verdict.status is ScannerStatus.UNAVAILABLE:
        return _blocked(ThreatClass.SCANNER_UNAVAILABLE)
    if scanner_verdict.status is ScannerStatus.MALICIOUS:
        return _blocked(ThreatClass.MALICIOUS)
    if scanner_verdict.status is ScannerStatus.INDETERMINATE:
        return _blocked(ThreatClass.INDETERMINATE)
    return None


def _sanitize_block(sanitizer_verdict: SanitizationVerdict | None) -> ThreatVerdict | None:
    """Blocking verdict when sanitization is required and not clean, else ``None``.

    A refusal means active content exceeded the sanitizable scope; the
    file is blocked and never downgraded into an output.
    """
    if sanitizer_verdict is None or sanitizer_verdict.status is SanitizerStatus.UNAVAILABLE:
        return _blocked(ThreatClass.SANITIZATION_UNAVAILABLE)
    if sanitizer_verdict.status is SanitizerStatus.REFUSED:
        return _blocked(ThreatClass.ACTIVE_CONTENT)
    return None


def classify_payload(
    *,
    validation_failure: ValidationFailure | None = None,
    scanning_required: bool,
    scanner_verdict: ScannerVerdict | None = None,
    sanitization_required: bool = False,
    sanitizer_verdict: SanitizationVerdict | None = None,
) -> ThreatVerdict:
    """The fail-closed classification matrix (D5 brief).

    Order matters: a validation outcome rejects before any scanner or
    sanitizer consideration (isolated inspection only), a scanner verdict
    blocks before sanitization is considered, and anything whose
    classification cannot be established as safe fails closed.
    """
    if validation_failure is not None:
        rejection = rejection_for(validation_failure)
        return ThreatVerdict(
            decision=SecurityDecision.REJECT,
            message_key=rejection.message_key,
            retryable=rejection.retryable,
            failure=validation_failure,
        )
    if scanning_required:
        blocked = _scan_block(scanner_verdict)
        if blocked is not None:
            return blocked
    if sanitization_required:
        blocked = _sanitize_block(sanitizer_verdict)
        if blocked is not None:
            return blocked
    return ThreatVerdict(decision=SecurityDecision.ALLOW)


def verdict_rejection(verdict: ThreatVerdict) -> ThreatRejection | None:
    """The safe rejection for a non-``ALLOW`` verdict, else ``None``."""
    if verdict.decision is SecurityDecision.ALLOW:
        return None
    if verdict.threat_class is not None:
        return block_rejection(verdict.threat_class)
    if verdict.failure is not None:
        return rejection_for(verdict.failure)
    raise ValueError("non-ALLOW verdict without threat_class or failure")
