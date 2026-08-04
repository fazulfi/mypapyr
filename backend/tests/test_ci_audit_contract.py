"""CI supply-chain audit contract tests.

Locks the transitive-audit contract of the ``supplychain-pip-audit`` job in
``.github/workflows/ci.yml``. Regression for a real gap: the audit ran with
``--no-deps`` and ``--disable-pip``, so ``pip-audit`` only checked the
directly pinned lines of ``requirements*.txt`` and never the resolved
dependency tree — which is why a vulnerable transitive ``starlette`` went
undetected before the FastAPI 0.141.1 / Starlette 1.3.1 upgrade.

The contract: the pip-audit invocation must
  * cover both ``requirements.txt`` (runtime) and
    ``requirements-dev.txt`` (dev), and
  * NOT use ``--no-deps`` or ``--disable-pip``, which would skip or disable
    dependency resolution and hide transitive vulnerabilities.
"""

from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CI_WORKFLOW = BACKEND_DIR.parent / ".github" / "workflows" / "ci.yml"


# Indentation-aware YAML reader (no PyYAML dependency).
#
# Deliberately avoids the untyped PyYAML import so the strict mypy contract
# over the test surface is satisfied without ``# type: ignore``, an ``Any``
# cast, or a new runtime dependency. Only the ``jobs.<name>.env.<key>: value``
# subset of YAML is needed — anything else is out of scope. The parser derives
# the indentation of ``env:`` from the indentation of the enclosing ``jobs:``
# mapping so a value is read at its true structural depth, not via a fragile
# global substring match.
#
# Grammar supported: LF endings, two-space indent, no tabs, plain
# ``key: value`` mappings on the read paths. List items and flow sequences
# are skipped (they are not part of the env-value contract surface).


def _line_indent(line: str) -> int:
    stripped = line.lstrip(" ")
    return len(line) - len(stripped)


def _split_mapping(line: str) -> tuple[str, str, int] | None:
    """Return ``(key, value, indent)`` for a ``key: value`` mapping line.

    Returns ``None`` for blank lines, comments, list items, flow values, and
    block scalars. Quoted values are returned with their surrounding quotes
    preserved for the caller to strip.
    """
    stripped = line.lstrip(" ")
    if not stripped or stripped.startswith("#"):
        return None
    if "\t" in line[: len(line) - len(stripped)]:
        return None
    if stripped.startswith("- "):
        return None
    if ":" not in stripped:
        return None
    key, _, value = stripped.partition(":")
    if not key or not all(ch.isalnum() or ch in "-_" for ch in key):
        return None
    return key, value.strip(), _line_indent(line)


def _strip_yaml_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _read_jobs_env(workflow_text: str) -> dict[str, dict[str, str]]:
    """Return ``{job_name: {env_key: env_value}}`` parsed from ``workflow_text``.

    Empty / missing env blocks are represented as ``{}``. Only string-valued
    env entries are surfaced — the contract asserts on string values, and
    any non-string would already be a workflow shape error.

    The parser anchors on the indentation of the top-level ``jobs:`` key.
    Jobs are expected at ``jobs_indent + 2``, ``env:`` at ``jobs_indent + 4``,
    and env keys at ``jobs_indent + 6``. Any ``key:`` line at a depth outside
    these three roles is intentionally ignored — we only need the env
    contract surface, and tracking the full YAML tree would mean either a
    full parser or fragile assumptions about list-item / flow-sequence shapes.
    """
    jobs: dict[str, dict[str, str]] = {}
    jobs_indent: int | None = None
    current_job: str | None = None
    current_env: dict[str, str] | None = None
    expect_env_key = False

    def _finalise_current_job() -> None:
        nonlocal current_job, current_env
        if current_job is not None:
            jobs[current_job] = current_env if current_env is not None else {}
        current_job = None
        current_env = None

    for raw_line in workflow_text.splitlines():
        parsed = _split_mapping(raw_line)
        if parsed is None:
            continue
        key, value, indent = parsed

        if jobs_indent is None:
            if key == "jobs":
                jobs_indent = indent
            continue

        if indent == jobs_indent + 2:
            _finalise_current_job()
            current_job = key
            current_env = {}
            expect_env_key = False
        elif indent == jobs_indent + 4 and current_job is not None and key == "env":
            expect_env_key = True
        elif indent == jobs_indent + 6 and expect_env_key and current_env is not None:
            current_env[key] = _strip_yaml_quotes(value)
        else:
            expect_env_key = False

    _finalise_current_job()
    return jobs


def _workflow_jobs() -> dict[str, dict[str, str]]:
    """Read ``CI_WORKFLOW`` and return its ``jobs`` env map (see ``_read_jobs_env``)."""
    return _read_jobs_env(CI_WORKFLOW.read_text(encoding="utf-8"))


def _pip_audit_invocations(workflow_text: str) -> list[str]:
    """Run steps (not the ``pip install pip-audit`` bootstrap) that invoke the
    audit command itself."""
    return [
        line.strip()
        for line in workflow_text.splitlines()
        if "pip-audit" in line and "pip install" not in line
    ]


def test_ci_pip_audit_audits_transitive_dependencies() -> None:
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    invocations = _pip_audit_invocations(workflow)
    assert invocations, "no pip-audit invocation found in ci.yml"
    for invocation in invocations:
        assert "--no-deps" not in invocation, invocation
        assert "--disable-pip" not in invocation, invocation


def test_ci_pip_audit_covers_runtime_and_dev_requirements() -> None:
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    invocations = "\n".join(_pip_audit_invocations(workflow))
    assert "-r requirements.txt" in invocations
    assert "-r requirements-dev.txt" in invocations


def test_ci_production_compose_dir_is_github_evaluated_path() -> None:
    """Regression for the final blocker: the qa-production-api Compose gate
    used a literal ``$(printf ...)`` shell fragment as ``PAPYR_COMPOSE_DIR``.

    GitHub Actions templates ``env:`` values with the ``${{ }}`` expression
    engine only; a ``$(…)`` fragment is never evaluated, so the Compose gate
    resolved a nonexistent literal directory on a real runner. The value must
    be a path GitHub Actions actually evaluates.
    """
    jobs = _workflow_jobs()
    assert jobs["qa-production-api"]["PAPYR_COMPOSE_DIR"] == "${{ github.workspace }}/deploy"


def test_ci_job_env_values_contain_no_shell_fragment() -> None:
    """No job ``env:`` value may smuggle shell syntax (``$(...)`` or a
    backtick) past the workflow expression engine — it would be set literally
    on the runner and never execute, and it is also how the deploy keyword
    scan was previously dodged."""
    for job_name, env in _workflow_jobs().items():
        for key, value in env.items():
            assert isinstance(value, str), (job_name, key, value)
            assert "$(" not in value, (job_name, key, value)
            assert "`" not in value, (job_name, key, value)


def test_ci_deploy_path_is_literal_not_obfuscated() -> None:
    """The no-CD keyword guard is scoped to commands/run-step semantics, so a
    legitimate workspace path reference to ``deploy`` must be expressed
    literally — never assembled from fragments to dodge the scan."""
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "${{ github.workspace }}/deploy" in workflow
    assert "$(printf" not in workflow
    assert "'de'" not in workflow and '"de"' not in workflow
