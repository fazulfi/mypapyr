"""Threat classification and fail-closed matrix tests (SEC-01).

Locks the ``app.security.classification`` contract (execution-matrix.md
SEC-01 row; plan:670-679; arch 17): closed safe threat classes with no raw
scanner/provider details (DEC-088, DEC-169), the D5-brief fail-closed
matrix in which anything not classifiable as safe fails closed (DEC-088,
DEC-065), blocking that precedes sanitization and can never be downgraded
into an output, mapping of BE-02 validation outcomes through the BE-08
failure vocabulary into privacy-safe localizable rejections, and the
scanner/sanitizer interface contracts SEC-02 (sanitize.py) and SEC-03
(scanner client, under R-10) implement behind this module — a stub
reporting scanner-unavailable must exercise the fail-closed path (DEC-171).

Rejection message keys are locked to the existing envelope vocabulary
(``app/errors.py``) by comparing live against ``spec_for_status``; no
filename, content, object-key, credential, or engine detail may appear in
any verdict, rejection, or log-reachable string.
"""

from __future__ import annotations

import pytest

from app.errors import ErrorCategory, spec_for_status
from app.routers.capabilities import FailureCode, failure_code_for, failure_code_meta
from app.security.classification import (
    MESSAGE_KEY_FORBIDDEN,
    MESSAGE_KEY_INTERNAL_ERROR,
    MESSAGE_KEY_RATE_LIMITED,
    SanitizationCategory,
    SanitizationVerdict,
    Sanitizer,
    SanitizerStatus,
    ScannerStatus,
    ScannerVerdict,
    SecurityDecision,
    ThreatClass,
    ThreatCode,
    ThreatRejection,
    ThreatScanner,
    ThreatVerdict,
    block_rejection,
    classify_payload,
    rejection_for,
    threat_code_for,
    threat_code_meta,
    verdict_rejection,
)
from app.security.validation import ValidationFailure

# --- envelope vocabulary lock: every key SEC-01 emits must already exist ---

_ENVELOPE_MESSAGE_KEYS: frozenset[str] = frozenset(
    {
        *{spec_for_status(status).message_key for status in range(400, 600)},
        "error.invalidRequest",  # RequestValidationError handler key (errors.py)
        "error.processingFailed",  # schema-layer closed vocabulary (schemas/job.py)
    }
)

_THREAT_CODE_META_EXPECTED: dict[ThreatCode, tuple[str, bool]] = {
    ThreatCode.THREAT_BLOCKED: (MESSAGE_KEY_FORBIDDEN, False),
    ThreatCode.INDETERMINATE: (MESSAGE_KEY_INTERNAL_ERROR, False),
    ThreatCode.SCANNER_UNAVAILABLE: (MESSAGE_KEY_RATE_LIMITED, True),
    ThreatCode.SANITIZATION_UNAVAILABLE: (MESSAGE_KEY_RATE_LIMITED, True),
}


# --- stub scanner / sanitizer (interface stand-ins, no engine reach) ---


class _StubScanner:
    """Minimal ``ThreatScanner`` stand-in reporting a fixed verdict."""

    def __init__(self, verdict: ScannerVerdict) -> None:
        self._verdict = verdict
        self.calls: list[bytes] = []

    def scan(self, data: bytes) -> ScannerVerdict:
        self.calls.append(data)
        return self._verdict


class _StubSanitizer:
    """Minimal ``Sanitizer`` stand-in reporting a fixed verdict."""

    def __init__(self, verdict: SanitizationVerdict) -> None:
        self._verdict = verdict
        self.calls: list[bytes] = []

    def sanitize(self, data: bytes) -> SanitizationVerdict:
        self.calls.append(data)
        return self._verdict


# --- threat classes and codes ---


def test_threat_classes_are_closed_safe_categories() -> None:
    assert {member.value for member in ThreatClass} == {
        "malicious",
        "active_content",
        "indeterminate",
        "scanner_unavailable",
        "sanitization_unavailable",
    }
    for member in ThreatClass:
        # Safe closed category names only: no provider names, signatures,
        # paths, or punctuation that could smuggle engine internals.
        assert member.value.islower()
        assert member.value.replace("_", "").isalnum()


def test_threat_codes_are_closed_and_stable() -> None:
    assert {member.value for member in ThreatCode} == {
        "threat_blocked",
        "indeterminate",
        "scanner_unavailable",
        "sanitization_unavailable",
    }


def test_every_threat_code_has_stable_envelope_metadata() -> None:
    assert set(_THREAT_CODE_META_EXPECTED) == set(ThreatCode)
    for code, (message_key, retryable) in _THREAT_CODE_META_EXPECTED.items():
        meta = threat_code_meta(code)
        assert meta.message_key == message_key
        assert meta.retryable is retryable
        assert meta.message_key in _ENVELOPE_MESSAGE_KEYS


def test_threat_code_meta_rejects_non_enum_values() -> None:
    with pytest.raises(ValueError):
        threat_code_meta("threat_blocked")  # type: ignore[arg-type]


def test_every_threat_class_maps_to_a_threat_code() -> None:
    assert set(threat_code_for(member) for member in ThreatClass) <= set(ThreatCode)
    assert threat_code_for(ThreatClass.MALICIOUS) is ThreatCode.THREAT_BLOCKED
    assert threat_code_for(ThreatClass.ACTIVE_CONTENT) is ThreatCode.THREAT_BLOCKED
    assert threat_code_for(ThreatClass.INDETERMINATE) is ThreatCode.INDETERMINATE
    assert threat_code_for(ThreatClass.SCANNER_UNAVAILABLE) is ThreatCode.SCANNER_UNAVAILABLE
    assert (
        threat_code_for(ThreatClass.SANITIZATION_UNAVAILABLE) is ThreatCode.SANITIZATION_UNAVAILABLE
    )


def test_threat_code_for_rejects_non_enum_values() -> None:
    with pytest.raises(ValueError):
        threat_code_for("malicious")  # type: ignore[arg-type]


# --- BE-02 outcome -> BE-08 vocabulary -> safe localizable rejection ---


@pytest.mark.parametrize("failure", list(ValidationFailure))
def test_rejection_for_maps_validation_failure_to_be08_vocabulary(
    failure: ValidationFailure,
) -> None:
    rejection = rejection_for(failure)
    code = failure_code_for(failure)
    assert rejection.failure is failure
    assert rejection.threat_class is None
    assert rejection.code is code
    assert isinstance(rejection.code, FailureCode)
    assert rejection.category is ErrorCategory.VALIDATION
    assert rejection.message_key == failure_code_meta(code).message_key
    assert rejection.message_key in _ENVELOPE_MESSAGE_KEYS
    assert rejection.retryable is failure_code_meta(code).retryable


def test_rejection_for_rejects_non_failure_values() -> None:
    with pytest.raises(ValueError):
        rejection_for("empty")  # type: ignore[arg-type]


# --- threat block rejections ---


@pytest.mark.parametrize("threat_class", list(ThreatClass))
def test_block_rejection_carries_only_safe_closed_fields(threat_class: ThreatClass) -> None:
    rejection = block_rejection(threat_class)
    assert rejection.threat_class is threat_class
    assert rejection.failure is None
    assert rejection.code is threat_code_for(threat_class)
    assert isinstance(rejection.code, ThreatCode)
    assert rejection.category is ErrorCategory.THREAT
    meta = threat_code_meta(threat_code_for(threat_class))
    assert rejection.message_key == meta.message_key
    assert rejection.message_key in _ENVELOPE_MESSAGE_KEYS
    assert rejection.retryable is meta.retryable


def test_block_rejection_rejects_non_enum_values() -> None:
    with pytest.raises(ValueError):
        block_rejection("malicious")  # type: ignore[arg-type]


def test_rejection_str_is_the_bare_safe_category() -> None:
    assert str(rejection_for(ValidationFailure.EMPTY)) == "empty"
    assert str(block_rejection(ThreatClass.MALICIOUS)) == "malicious"
    assert str(block_rejection(ThreatClass.SCANNER_UNAVAILABLE)) == "scanner_unavailable"


# --- fail-closed matrix ---


def test_classify_validation_failure_rejects_without_scanner_reach() -> None:
    scanner = _StubScanner(ScannerVerdict(status=ScannerStatus.MALICIOUS))
    verdict = classify_payload(
        validation_failure=ValidationFailure.CORRUPT,
        scanning_required=True,
        scanner_verdict=scanner.scan(b"payload"),
    )
    assert verdict.decision is SecurityDecision.REJECT
    assert verdict.failure is ValidationFailure.CORRUPT
    assert verdict.threat_class is None
    assert verdict.message_key == rejection_for(ValidationFailure.CORRUPT).message_key
    # A validation outcome wins before any scanner consideration: the
    # verdict is derived from isolated inspection only (no engine reach).
    assert verdict.message_key in _ENVELOPE_MESSAGE_KEYS


def test_classify_scanner_unavailable_fails_closed() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.UNAVAILABLE),
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.SCANNER_UNAVAILABLE
    assert verdict.message_key == MESSAGE_KEY_RATE_LIMITED
    assert verdict.retryable is True
    assert verdict.message_key in _ENVELOPE_MESSAGE_KEYS


def test_classify_scanning_required_without_verdict_fails_closed() -> None:
    verdict = classify_payload(scanning_required=True)
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.SCANNER_UNAVAILABLE


def test_classify_scanner_malicious_blocks() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.MALICIOUS),
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.MALICIOUS
    assert verdict.message_key == MESSAGE_KEY_FORBIDDEN
    assert verdict.retryable is False


def test_classify_scanner_indeterminate_fails_closed() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.INDETERMINATE),
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.INDETERMINATE
    assert verdict.message_key == MESSAGE_KEY_INTERNAL_ERROR


def test_classify_clean_scanner_allows_when_no_sanitization_required() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.CLEAN),
    )
    assert verdict.decision is SecurityDecision.ALLOW
    assert verdict.threat_class is None
    assert verdict.failure is None
    assert verdict.message_key is None


def test_classify_no_scanning_required_allows() -> None:
    verdict = classify_payload(scanning_required=False)
    assert verdict.decision is SecurityDecision.ALLOW


def test_classify_sanitizer_unavailable_fails_closed() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.CLEAN),
        sanitization_required=True,
        sanitizer_verdict=SanitizationVerdict(status=SanitizerStatus.UNAVAILABLE),
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.SANITIZATION_UNAVAILABLE
    assert verdict.retryable is True


def test_classify_sanitizer_refusal_blocks_active_content() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.CLEAN),
        sanitization_required=True,
        sanitizer_verdict=SanitizationVerdict(status=SanitizerStatus.REFUSED),
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.ACTIVE_CONTENT
    assert verdict.message_key == MESSAGE_KEY_FORBIDDEN
    assert verdict.retryable is False


def test_classify_sanitization_required_without_verdict_fails_closed() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.CLEAN),
        sanitization_required=True,
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.SANITIZATION_UNAVAILABLE


def test_classify_sanitized_output_allows() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.CLEAN),
        sanitization_required=True,
        sanitizer_verdict=SanitizationVerdict(
            status=SanitizerStatus.SANITIZED,
            categories=(SanitizationCategory.JAVASCRIPT,),
        ),
    )
    assert verdict.decision is SecurityDecision.ALLOW


def test_blocking_precedes_sanitization_and_never_downgrades() -> None:
    # A scanner-flagged file must be blocked even when the sanitizer would
    # report a successful pass: sanitization never downgrades a blocked
    # file into an output (D5 fail-closed matrix).
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.MALICIOUS),
        sanitization_required=True,
        sanitizer_verdict=SanitizationVerdict(status=SanitizerStatus.SANITIZED),
    )
    assert verdict.decision is SecurityDecision.BLOCK
    assert verdict.threat_class is ThreatClass.MALICIOUS


# --- verdict -> rejection conversion ---


def test_verdict_rejection_allows_none_for_allow() -> None:
    verdict = classify_payload(scanning_required=False)
    assert verdict_rejection(verdict) is None


def test_verdict_rejection_converts_block_verdict() -> None:
    verdict = classify_payload(
        scanning_required=True,
        scanner_verdict=ScannerVerdict(status=ScannerStatus.UNAVAILABLE),
    )
    rejection = verdict_rejection(verdict)
    assert rejection is not None
    assert rejection.threat_class is ThreatClass.SCANNER_UNAVAILABLE
    assert rejection.code is ThreatCode.SCANNER_UNAVAILABLE
    assert rejection.category is ErrorCategory.THREAT
    assert rejection.message_key == MESSAGE_KEY_RATE_LIMITED
    assert rejection.retryable is True


def test_verdict_rejection_converts_reject_verdict() -> None:
    verdict = classify_payload(
        validation_failure=ValidationFailure.SIZE_EXCEEDED, scanning_required=True
    )
    rejection = verdict_rejection(verdict)
    assert rejection is not None
    assert rejection.failure is ValidationFailure.SIZE_EXCEEDED
    assert rejection.code is failure_code_for(ValidationFailure.SIZE_EXCEEDED)
    assert rejection.category is ErrorCategory.VALIDATION


def test_verdict_rejection_rejects_malformed_verdict() -> None:
    with pytest.raises(ValueError):
        verdict_rejection(ThreatVerdict(decision=SecurityDecision.BLOCK))


# --- scanner and sanitizer interface contracts (SEC-02 / SEC-03 implement) ---


def test_scanner_protocol_is_runtime_checkable() -> None:
    stub = _StubScanner(ScannerVerdict(status=ScannerStatus.CLEAN))
    assert isinstance(stub, ThreatScanner)


def test_scanner_protocol_rejects_objects_without_scan() -> None:
    class _NotAScanner:
        pass

    assert not isinstance(_NotAScanner(), ThreatScanner)


def test_scanner_verdict_carries_no_content_or_provider_details() -> None:
    verdict = ScannerVerdict(status=ScannerStatus.MALICIOUS)
    assert verdict.__dict__ == {"status": ScannerStatus.MALICIOUS}
    assert "malicious" in str(verdict)
    # No signature name, no path, no object key can ever appear: the only
    # field is the closed status value.
    assert "signature" not in str(verdict).lower()


def test_sanitizer_protocol_is_runtime_checkable() -> None:
    stub = _StubSanitizer(SanitizationVerdict(status=SanitizerStatus.SANITIZED))
    assert isinstance(stub, Sanitizer)


def test_sanitizer_protocol_rejects_objects_without_sanitize() -> None:
    class _NotASanitizer:
        pass

    assert not isinstance(_NotASanitizer(), Sanitizer)


def test_sanitization_categories_are_closed_safe_names() -> None:
    assert {member.value for member in SanitizationCategory} == {
        "javascript",
        "embedded_attachment",
        "launch_action",
        "external_action",
    }
    for member in SanitizationCategory:
        assert member.value.replace("_", "").isalnum()


def test_sanitization_verdict_carries_only_closed_category_names() -> None:
    verdict = SanitizationVerdict(
        status=SanitizerStatus.SANITIZED,
        categories=(SanitizationCategory.LAUNCH_ACTION, SanitizationCategory.JAVASCRIPT),
    )
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (
        SanitizationCategory.LAUNCH_ACTION,
        SanitizationCategory.JAVASCRIPT,
    )
    # Category reporting stays accurate without payload details (DEC-090).
    assert "action" in str(verdict)
    assert "javascript" in str(verdict)


# --- privacy: no payload content reaches any verdict or rejection string ---


def test_verdict_and_rejection_strings_never_expose_payload() -> None:
    hostile = b"%PDF-1.7\x00\xff\xfe" + b"password=supersecret\x00" + b"\xff" * 16
    scanner = _StubScanner(ScannerVerdict(status=ScannerStatus.CLEAN))
    verdict = classify_payload(scanning_required=True, scanner_verdict=scanner.scan(hostile))
    rejection = verdict_rejection(verdict)
    rendered = f"{verdict!r} {rejection!r} {verdict} {rejection}"
    for token in (b"supersecret", b"%PDF", b"\xff"):
        assert token.decode("latin1", errors="ignore") not in rendered


def test_threat_rejection_requires_exactly_one_of_failure_or_class() -> None:
    with pytest.raises(ValueError):
        ThreatRejection(message_key=MESSAGE_KEY_FORBIDDEN)
    with pytest.raises(ValueError):
        ThreatRejection(
            failure=ValidationFailure.EMPTY,
            threat_class=ThreatClass.MALICIOUS,
            message_key=MESSAGE_KEY_FORBIDDEN,
        )
