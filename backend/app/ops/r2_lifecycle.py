"""Cloudflare R2 lifecycle policy contract and drift verification (U-R2; ARC-06, PE-03).

``deploy/r2-lifecycle.json`` is the deploy-owned artifact an operator applies
to the bucket (wrangler ``r2 bucket lifecycle set``); the approved contract
itself lives HERE in code, so a drifted, truncated, or secret-bearing
artifact fails a deterministic gate instead of being applied silently:

* exactly the two approved rules — the ``tmp/`` expiration safety net at the
  R2 one-day minimum and the incomplete-multipart abort at one day — present,
  enabled, and unmodified; any other rule id, count, prefix, day value, or
  status is drift (R2 enforces whole-day granularity with a one-day minimum;
  the 3600 s retention ceiling is application cleanup, never this rule);
* no account identifiers, tokens, keys, or passwords anywhere in the
  artifact — R2 lifecycle bodies never carry them, so their presence is a
  leak the gate rejects without echoing the material;
* R2-native shape only: no S3-only constructs (versioning transitions,
  storage classes) that R2 does not accept.

The gate never touches the network and never mutates anything; applying the
lifecycle to the live bucket stays a manual deploy-time operator action
documented by :func:`render_apply_contract`.

CLI contract (``python -m app.ops.r2_lifecycle`` / scripts/check-r2-lifecycle.sh):
``--check PATH`` verifies an artifact and prints a JSON report; exit 0 match,
exit 1 drift or secret material, exit 2 absent/malformed artifact.
``--print-apply-contract`` prints the documented apply instructions.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TypedDict

_EXPECTED_TMP_RULE_ID = "papyr-tmp-objects-expire-r2-minimum-1-day-safety-net"
_EXPECTED_MULTIPART_RULE_ID = "papyr-abort-incomplete-multipart-r2-minimum-1-day"
_MAX_LIFECYCLE_CHECK_ARGS = 2  # len(args) must equal 2 for --check


class _LifecycleDocument(TypedDict):
    RetentionContract: dict[str, object]
    Rules: list[dict[str, object]]


EXPECTED_LIFECYCLE: _LifecycleDocument = {
    "RetentionContract": {
        "HardMaximumSeconds": 3600,
        "Enforcement": "application-cleanup",
        "LifecycleSafetyNet": "r2-minimum-one-day-expiration",
    },
    "Rules": [
        {
            "ID": _EXPECTED_TMP_RULE_ID,
            "Status": "Enabled",
            "Filter": {"Prefix": "tmp/"},
            "Expiration": {"Days": 1},
        },
        {
            "ID": _EXPECTED_MULTIPART_RULE_ID,
            "Status": "Enabled",
            "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1},
        },
    ],
}

_SECRET_KEY_MARKERS: tuple[str, ...] = (
    "secret",
    "token",
    "password",
    "passwd",
    "accesskey",
    "account",
    "akia",
    "privatekey",
    "credential",
)


class LifecycleError(RuntimeError):
    """Base class for lifecycle gate failures."""


class LifecyclePolicyAbsent(LifecycleError):
    """The lifecycle artifact is missing or unreadable."""


class LifecyclePolicyMalformed(LifecycleError):
    """The lifecycle artifact is not a JSON object."""


class LifecycleDriftError(LifecycleError):
    """The lifecycle artifact deviates from the approved contract."""

    def __init__(self, findings: Sequence[Mapping[str, object]]) -> None:
        self.findings = [dict(finding) for finding in findings]
        super().__init__(f"lifecycle drift detected: {len(self.findings)} finding(s)")


class LifecycleSecretError(LifecycleError):
    """The lifecycle artifact carries secret or identity material."""


def _normalize_key(name: str) -> str:
    lowered = name.lower()
    for separator in ("_", "-", " ", "."):
        lowered = lowered.replace(separator, "")
    return lowered


def _scan_for_secrets(value: object, path: str) -> list[str]:
    if isinstance(value, Mapping):
        hits: list[str] = []
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if isinstance(key, str) and any(
                marker in _normalize_key(key) for marker in _SECRET_KEY_MARKERS
            ):
                hits.append(child_path)
            hits.extend(_scan_for_secrets(child, child_path))
        return hits
    if isinstance(value, list):
        hits = []
        for index, child in enumerate(value):
            hits.extend(_scan_for_secrets(child, f"{path}[{index}]"))
        return hits
    return []


def _compare_values(expected: object, actual: object, path: str) -> list[dict[str, object]]:
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        findings: list[dict[str, object]] = []
        for key in expected:
            child_path = f"{path}.{key}" if path else str(key)
            if key not in actual:
                msg_kind = "missing_field"
                findings.append(
                    {
                        "kind": msg_kind,
                        "path": child_path,
                        "expected": expected[key],
                        "actual": None,
                    }
                )
            else:
                findings.extend(_compare_values(expected[key], actual[key], child_path))
        for key in actual:
            if key not in expected:
                child_path = f"{path}.{key}" if path else str(key)
                msg_kind = "unexpected_field"
                findings.append(
                    {
                        "kind": msg_kind,
                        "path": child_path,
                        "expected": None,
                        "actual": actual[key],
                    }
                )
        return findings
    if expected != actual:
        msg_mismatch = "value_mismatch"
        return [{"kind": msg_mismatch, "path": path, "expected": expected, "actual": actual}]
    return []


def _compare_rules(
    expected_rules: Sequence[Mapping[str, object]], actual_rules: object
) -> list[dict[str, object]]:
    if not isinstance(actual_rules, list):
        exp_type = "a list of rules"
        return [
            {
                "kind": "value_mismatch",
                "path": "Rules",
                "expected": exp_type,
                "actual": type(actual_rules).__name__,
            }
        ]
    findings: list[dict[str, object]] = []
    expected_by_id = {rule.get("ID"): rule for rule in expected_rules}
    actual_by_id: dict[object, Mapping[str, object]] = {}
    for index, rule in enumerate(actual_rules):
        if not isinstance(rule, Mapping):
            # Nested if statement must be indented
            msg_obj = "an object"
            findings.append(
                {
                    "kind": "value_mismatch",
                    "path": f"Rules[{index}]",
                    "expected": msg_obj,
                    "actual": type(rule).__name__,
                }
            )
            continue
        rule_id = rule.get("ID")
        if rule_id in actual_by_id:
            msg_dup = f"duplicate ID {rule_id!r}"
            findings.append(
                {
                    "kind": "unexpected_rule",
                    "path": f"Rules[{index}]",
                    "expected": None,
                    "actual": msg_dup,
                }
            )
            continue
        actual_by_id[rule_id] = rule
    for rule_id, exp_rule in expected_by_id.items():
        if rule_id not in actual_by_id:
            findings.append(
                {
                    "kind": "missing_rule",
                    "path": f"Rules[ID={rule_id!r}]",
                    "expected": exp_rule,
                    "actual": None,
                }
            )
            continue
        findings.extend(_compare_values(exp_rule, actual_by_id[rule_id], f"Rules[ID={rule_id!r}]"))
    for rule_id, act_rule in actual_by_id.items():
        if rule_id not in expected_by_id:
            findings.append(
                {
                    "kind": "unexpected_rule",
                    "path": f"Rules[ID={rule_id!r}]",
                    "expected": None,
                    "actual": act_rule,
                }
            )
    return findings


def compare_lifecycle(actual: Mapping[str, object]) -> list[dict[str, object]]:
    """Return structured drift findings; empty when *actual* matches exactly."""
    findings: list[dict[str, object]] = []
    expected_top = {key: value for key, value in EXPECTED_LIFECYCLE.items() if key != "Rules"}
    actual_top = {key: value for key, value in actual.items() if key != "Rules"}
    findings.extend(_compare_values(expected_top, actual_top, ""))
    expected_rules = EXPECTED_LIFECYCLE["Rules"]
    actual_rules = actual.get("Rules")
    if actual_rules is None:
        findings.append(
            {
                "kind": "missing_field",
                "path": "Rules",
                "expected": expected_rules,
                "actual": None,
            }
        )
    else:
        findings.extend(_compare_rules(expected_rules, actual_rules))
    return findings


def load_lifecycle_file(path: str | Path) -> Mapping[str, object]:
    """Load *path* as a JSON object; absent/unreadable or non-object raises."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise LifecyclePolicyAbsent(
            f"lifecycle artifact absent or unreadable: {type(exc).__name__}"
        ) from exc
    try:
        parsed = json.loads(raw)
    except ValueError as exc:
        raise LifecyclePolicyMalformed("lifecycle artifact is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise LifecyclePolicyMalformed("lifecycle artifact must be a JSON object")
    return parsed


def verify_lifecycle_file(path: str | Path) -> None:
    """Verify *path* against the approved contract; raises on any violation."""
    document = load_lifecycle_file(path)
    secret_paths = _scan_for_secrets(document, "")
    if secret_paths:
        raise LifecycleSecretError(
            f"lifecycle artifact carries secret or identity material at {len(secret_paths)} path(s)"
        )
    findings = compare_lifecycle(document)
    if findings:
        raise LifecycleDriftError(findings)


def render_apply_contract() -> tuple[str, ...]:
    """Documented deploy-time apply contract; account/bucket-agnostic by design."""
    return (
        "# Papyr R2 lifecycle apply contract (U-R2)",
        "# Application is a MANUAL deploy-time operator action; this repository",
        "# never applies lifecycle rules and never embeds account identifiers.",
        "",
        "# 1. Check the canonical artifact against the approved contract:",
        "python -m app.ops.r2_lifecycle --check deploy/r2-lifecycle.json",
        "",
        "# 2. Apply with wrangler (substitute <BUCKET_NAME> out-of-band):",
        "wrangler r2 bucket lifecycle set <BUCKET_NAME> --file deploy/r2-lifecycle.json",
        "",
        "# Alternative (S3-compatible API, R2-native semantics):",
        "#   PUT /?lifecycle on the bucket endpoint with the artifact as body.",
        "",
        "# Exit codes of --check: 0 match, 1 drift or prohibited material, "
        + "2 absent/malformed.",
        "# R2 constraints honored: whole-day granularity, Expiration.Days minimum 1,",
        "# AbortIncompleteMultipartUpload.DaysAfterInitiation minimum 1, no S3-only",
        "# constructs (versioning transitions, storage classes).",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--print-apply-contract":
        print("\n".join(render_apply_contract()))
        return 0
    if len(args) != _MAX_LIFECYCLE_CHECK_ARGS or args[0] != "--check":
        print(
            "usage: python -m app.ops.r2_lifecycle --check PATH | --print-apply-contract",
            file=sys.stderr,
        )
        return 2
    try:
        verify_lifecycle_file(args[1])
    except (LifecyclePolicyAbsent, LifecyclePolicyMalformed) as exc:
        status = "absent" if isinstance(exc, LifecyclePolicyAbsent) else "malformed"
        print(json.dumps({"status": status, "error": str(exc)}))
        return 2
    except LifecycleSecretError as exc:
        print(json.dumps({"status": "secret_material", "error": str(exc)}))
        return 1
    except LifecycleDriftError as exc:
        print(json.dumps({"status": "drift", "findings": exc.findings}, default=str))
        return 1
    print(json.dumps({"status": "match"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
