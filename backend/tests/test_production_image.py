"""Production image privacy and engine-contract tests (review-fixes unit).

Locks the ``backend/Dockerfile.production`` contract against two review
blockers and keeps the admission-control-plane posture stable:

* H-1 (security review): the production CMD must disable uvicorn's access
  logger. ``task_id`` is a de-facto capability token (possession of the
  status/download paths mints signed URLs and reveals task metadata), and
  uvicorn's ``access`` logger writes every request line verbatim to stderr,
  bypassing ``app.utils.logging.PrivacyFormatter`` entirely. The regression
  is the ``--no-access-log`` flag on the single uvicorn process.
* B2 (context-mining review): the image contract must accurately declare
  pikepdf (the SEC-02 sanitizer, pinned in ``requirements.txt`` and
  installed by the builder stage) as a sanctioned runtime dependency, while
  still claiming NO tool engines (img2pdf/Pillow/pypdfium2/Ghostscript are
  NOT installed here — they belong to the future worker image).

These are pure file-content contracts (no app imports, no environment
needed), mirroring the ``test_dependencies.py`` pattern of locking deploy
artifacts by reading them from disk.
"""

from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DOCKERFILE = BACKEND_DIR / "Dockerfile.production"

#: The five-tool engine dependencies must never be claimed as installed in
#: the control-plane image; only the SEC-02 sanitizer (pikepdf) is.
TOOL_ENGINES = ("img2pdf", "Pillow", "pypdfium2", "Ghostscript")

_SANCTIONED_MARKER = "sanctioned"


def _cmd_line() -> str:
    """The production ``CMD`` instruction (the column-0 array form).

    The HEALTHCHECK instruction embeds an indented ``CMD [...]``
    continuation; only the column-0 ``CMD`` is the process launcher.
    """
    lines = DOCKERFILE.read_text(encoding="utf-8").splitlines()
    cmd_lines = [line for line in lines if line.startswith("CMD ")]
    assert len(cmd_lines) == 1, f"expected exactly one CMD instruction, found {cmd_lines!r}"
    return cmd_lines[0].strip()


# --- H-1: uvicorn access log must be disabled in production -----------------


def test_production_cmd_disables_access_log() -> None:
    """Regression for H-1: task-id capability tokens never reach access logs.

    The status/download request lines embed ``task_id``; uvicorn's access
    logger emits them verbatim, bypassing the application PrivacyFormatter.
    The production image must therefore run with ``--no-access-log``.
    """
    assert "--no-access-log" in _cmd_line()


def test_production_cmd_is_single_uvicorn_without_reload() -> None:
    """Admission-control-plane posture: one bounded process, no reload."""
    cmd = _cmd_line()
    assert cmd.startswith('CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"')
    assert "--reload" not in cmd
    assert "watchfiles" not in cmd


def test_production_cmd_documents_the_access_log_privacy_rationale() -> None:
    """The image must state WHY the access log is off (capability privacy)."""
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "--no-access-log" in text
    assert "capability" in text.lower() or "access log" in text.lower()


# --- B2: engine contract must be true (pikepdf runtime; no tool engines) ----


def test_production_contract_declares_pikepdf_as_sanctioned_runtime_dependency() -> None:
    """B2: pikepdf (SEC-02 sanitizer) is installed; the contract must say so."""
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "pikepdf" in text
    assert _SANCTIONED_MARKER in text
    assert "runtime" in text


def test_production_contract_never_lists_pikepdf_as_not_installed() -> None:
    """B2: the stale "not installed here" claim must not cover pikepdf."""
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        lowered = line.lower()
        if "not installed" in lowered:
            assert "pikepdf" not in lowered, line


def _contract_bullets(text: str) -> list[str]:
    """The ``#   * `` contract bullets, one string per bullet (lines joined)."""
    bullets: list[str] = []
    for line in text.splitlines():
        if line.startswith("#   * "):
            bullets.append(line)
        elif bullets and line.startswith("#") and not line.startswith("#   * "):
            bullets[-1] += " " + line.lstrip("#").strip()
    return bullets


def test_production_contract_does_not_claim_tool_engines() -> None:
    """The five-tool engines are NOT installed here; every mention says so.

    Each engine is named only to be excluded: the contract bullet naming it
    must carry a non-installation claim, so the image contract can never be
    misread as shipping tool engines in the control-plane image.
    """
    text = DOCKERFILE.read_text(encoding="utf-8")
    for engine in TOOL_ENGINES:
        assert engine in text
    for bullet in _contract_bullets(text):
        if any(engine in bullet for engine in TOOL_ENGINES):
            assert "not installed" in bullet.lower(), bullet


def test_production_builder_installs_runtime_requirements() -> None:
    """Stability guard: the sanctioned deps enter via the pinned file."""
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "COPY --chown=root:root requirements.txt ./" in text
    assert "pip install --no-cache-dir -r requirements.txt" in text
    assert "pikepdf==10.11.0" in (BACKEND_DIR / "requirements.txt").read_text(encoding="utf-8")
