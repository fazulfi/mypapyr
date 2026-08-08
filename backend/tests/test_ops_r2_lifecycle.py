"""Contract tests for the R2 lifecycle policy gate (U-R2; ARC-06, PE-03).

The deploy-owned declaration ``deploy/r2-lifecycle.json`` is the artifact an
operator applies to the bucket at deploy time (wrangler ``r2 bucket
lifecycle set``); the approved contract itself lives in code so a drifted,
truncated, or secret-bearing artifact FAILS a deterministic gate instead of
being applied silently:

* the exact two approved rules (tmp/ expiration safety net at the R2
  one-day minimum, incomplete-multipart abort at one day) are present,
  enabled, and unmodified — any other rule id, count, prefix, day value,
  or status is drift;
* the artifact carries no account identifiers, tokens, or key material
  (R2 lifecycle request bodies never do; their presence is a leak);
* the gate is R2-native: day-granularity expiration only, never S3-only
  constructs that R2 rejects.

Application to the live bucket remains a manual, deploy-time operator
action (documented by the apply contract the module renders); this gate
never touches the network and never mutates anything.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from app.ops.r2_lifecycle import (
    EXPECTED_LIFECYCLE,
    LifecycleDriftError,
    LifecyclePolicyAbsent,
    LifecyclePolicyMalformed,
    LifecycleSecretError,
    compare_lifecycle,
    load_lifecycle_file,
    render_apply_contract,
    verify_lifecycle_file,
)

CANONICAL_PATH = Path(__file__).resolve().parents[2] / "deploy" / "r2-lifecycle.json"

_TMP_RULE_ID = "papyr-tmp-objects-expire-r2-minimum-1-day-safety-net"
_MULTIPART_RULE_ID = "papyr-abort-incomplete-multipart-r2-minimum-1-day"


def _canonical() -> dict[str, Any]:
    return copy.deepcopy(json.loads(CANONICAL_PATH.read_text(encoding="utf-8")))


# --- contract shape -----------------------------------------------------------


def test_expected_contract_is_r2_native_two_rule_safety_net() -> None:
    rules = EXPECTED_LIFECYCLE["Rules"]
    assert len(rules) == 2
    by_id = {rule["ID"]: rule for rule in rules}
    assert set(by_id) == {_TMP_RULE_ID, _MULTIPART_RULE_ID}
    tmp_rule = by_id[_TMP_RULE_ID]
    assert tmp_rule["Status"] == "Enabled"
    assert tmp_rule["Filter"] == {"Prefix": "tmp/"}
    # R2 enforces whole-day granularity with a one-day minimum; the approved
    # safety net sits exactly at that minimum (the 3600 s ceiling is
    # application cleanup, never the lifecycle rule).
    assert tmp_rule["Expiration"] == {"Days": 1}
    multipart_rule = by_id[_MULTIPART_RULE_ID]
    assert multipart_rule["Status"] == "Enabled"
    assert multipart_rule["AbortIncompleteMultipartUpload"] == {"DaysAfterInitiation": 1}


def test_expected_contract_carries_no_s3_only_constructs() -> None:
    serialized = json.dumps(EXPECTED_LIFECYCLE)
    for s3_only in (
        "NoncurrentVersionExpiration",
        "Transitions",
        "StorageClass",
        "GLACIER",
        "DEEP_ARCHIVE",
        "Intelligent-Tiering",
    ):
        assert s3_only not in serialized


def test_expected_contract_carries_no_secrets_or_account_identifiers() -> None:
    serialized = json.dumps(EXPECTED_LIFECYCLE).lower()
    for marker in ("secret", "token", "password", "access_key", "account", "akia"):
        assert marker not in serialized


# --- drift detection ----------------------------------------------------------


def test_compare_clean_document_reports_no_findings() -> None:
    assert compare_lifecycle(_canonical()) == []


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda doc: doc["Rules"].pop(), id="missing-rule"),
        pytest.param(
            lambda doc: doc["Rules"].append({"ID": "rogue", "Status": "Enabled"}),
            id="unexpected-rule",
        ),
        pytest.param(
            lambda doc: doc["Rules"][0].update({"Status": "Disabled"}),
            id="tmp-rule-disabled",
        ),
        pytest.param(
            lambda doc: doc["Rules"][0]["Filter"].update({"Prefix": ""}),
            id="prefix-blanked",
        ),
        pytest.param(
            lambda doc: doc["Rules"][0]["Filter"].update({"Prefix": "uploads/"}),
            id="prefix-drifted",
        ),
        pytest.param(
            lambda doc: doc["Rules"][0]["Expiration"].update({"Days": 7}),
            id="expiration-days-drifted",
        ),
        pytest.param(
            lambda doc: doc["Rules"][0].update({"ID": "renamed-rule"}),
            id="rule-id-renamed",
        ),
        pytest.param(
            lambda doc: doc["Rules"][1]["AbortIncompleteMultipartUpload"].update(
                {"DaysAfterInitiation": 3}
            ),
            id="multipart-days-drifted",
        ),
        pytest.param(lambda doc: doc.pop("Rules"), id="rules-key-absent"),
        pytest.param(
            lambda doc: doc["Rules"][0]["Expiration"].pop("Days"),
            id="expiration-days-absent",
        ),
    ],
)
def test_compare_reports_drift_for_every_mutation(
    mutate: Callable[[dict[str, Any]], object],
) -> None:
    drifted = _canonical()
    mutate(drifted)
    findings = compare_lifecycle(drifted)
    assert findings, "mutation was not detected as drift"
    for finding in findings:
        assert finding["kind"] in {
            "missing_rule",
            "unexpected_rule",
            "missing_field",
            "value_mismatch",
        }
        assert isinstance(finding["path"], str) and finding["path"]


def test_drift_findings_are_deterministic() -> None:
    drifted = _canonical()
    drifted["Rules"][0]["Expiration"]["Days"] = 7
    assert compare_lifecycle(drifted) == compare_lifecycle(drifted)


def test_verify_raises_drift_error_with_findings(tmp_path: Path) -> None:
    drifted = _canonical()
    drifted["Rules"][0]["Status"] = "Disabled"
    path = tmp_path / "drifted.json"
    path.write_text(json.dumps(drifted), encoding="utf-8")
    with pytest.raises(LifecycleDriftError) as excinfo:
        verify_lifecycle_file(path)
    assert excinfo.value.findings
    assert all(isinstance(finding["path"], str) for finding in excinfo.value.findings)


def test_verify_accepts_the_canonical_deploy_artifact() -> None:
    # The committed deploy artifact must always satisfy the gate it ships with.
    verify_lifecycle_file(CANONICAL_PATH)


# --- absence / malformed handling ----------------------------------------------


def test_load_missing_file_raises_absent(tmp_path: Path) -> None:
    with pytest.raises(LifecyclePolicyAbsent):
        load_lifecycle_file(tmp_path / "no-such-file.json")


def test_verify_missing_file_raises_absent(tmp_path: Path) -> None:
    with pytest.raises(LifecyclePolicyAbsent):
        verify_lifecycle_file(tmp_path / "no-such-file.json")


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("{not json", id="invalid-json"),
        pytest.param("[1, 2, 3]", id="not-an-object"),
        pytest.param('"lifecycle"', id="bare-string"),
    ],
)
def test_load_malformed_document_raises_malformed(tmp_path: Path, content: str) -> None:
    path = tmp_path / "malformed.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(LifecyclePolicyMalformed):
        load_lifecycle_file(path)


# --- secret material guard -----------------------------------------------------


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("AccountId", id="account-id"),
        pytest.param("SecretToken", id="secret-token"),
        pytest.param("AccessKeyId", id="access-key"),
        pytest.param("Password", id="password"),
    ],
)
def test_verify_rejects_secret_or_identity_material(tmp_path: Path, field_name: str) -> None:
    leaked = _canonical()
    leaked[field_name] = "sensitive-material"
    path = tmp_path / "leaked.json"
    path.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(LifecycleSecretError):
        verify_lifecycle_file(path)


def test_secret_guard_inspects_nested_rule_fields(tmp_path: Path) -> None:
    leaked = _canonical()
    leaked["Rules"][0]["Credentials"] = {"Token": "abc"}
    path = tmp_path / "nested-leak.json"
    path.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(LifecycleSecretError):
        verify_lifecycle_file(path)


def test_secret_error_message_never_echoes_the_secret(tmp_path: Path) -> None:
    leaked = _canonical()
    leaked["SecretToken"] = "super-secret-value-123"
    path = tmp_path / "leaked.json"
    path.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(LifecycleSecretError) as excinfo:
        verify_lifecycle_file(path)
    assert "super-secret-value-123" not in str(excinfo.value)


# --- apply contract (documentation, never execution) ----------------------------


def test_apply_contract_documents_wrangler_invocation_without_identifiers() -> None:
    lines = render_apply_contract()
    joined = "\n".join(lines)
    assert any("wrangler" in line for line in lines)
    assert any("lifecycle" in line for line in lines)
    assert "r2-lifecycle.json" in joined
    # The contract is account-agnostic: the bucket name is a placeholder the
    # operator substitutes out-of-band; no concrete account or bucket id ships.
    for marker in ("secret", "token", "password"):
        assert marker not in joined.lower()


def test_apply_contract_names_the_canonical_artifact_only(tmp_path: Path) -> None:
    # The gate's own CLI contract: verify any artifact without applying it.
    lines = render_apply_contract()
    assert any("check" in line.lower() for line in lines)
