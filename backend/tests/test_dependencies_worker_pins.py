"""RED tests for worker engine dependency pins (U-PINS).

Locks the worker image's runtime engines as per Phase-5 U-PINS contract:

* Ghostscript 10.07.1 from Artifex (official source tarball) with exact SHA256
* img2pdf==0.6.3 (LGPLv3, latest as of 2025-11-05)
* Pillow (decompression-bomb safeguard enabled; exact pin resolved via pip-audit)
* pypdfium2==5.12.1 (bundled PDFium binary, BSD/Apache dual license)

RED phase: these tests MUST fail against the current state (GS 10.05.1, no
img2pdf/pillow/pypdfium2 pins in requirements.txt, Dockerfile.worker still
cites 10.05.1), and PASS only after pins are added and verified in CI/evidence.

Evidence paths (gitignored): audit-outputs/phase-5/tdd/U-PINS-red.md, green.md
"""

from __future__ import annotations

import re
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
RUNTIME_REQUIREMENTS = BACKEND_DIR / "requirements.txt"
DOCKERFILE_WORKER = BACKEND_DIR / "Dockerfile.worker"

# Official Artifex release data (authoritative, from ghostscript.com/releases)
# Ghostscript 10.07.1 was released 2026-05-19
AUTHORITATIVE_GS_VERSION = "10.07.1"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_worker_dockerfile() -> tuple[str | None, str | None]:
    """Extract GS_VERSION ARG and its associated SHA256 from Dockerfile.worker."""
    content = _read_text(DOCKERFILE_WORKER)
    gs_version_match = re.search(r'ARG\s+GS_VERSION=(\d+\.\d+\.\d+)', content)
    gs_sha_match = re.search(r'ARG\s+GS_SHA256=([0-9a-f]{64})', content)
    return gs_version_match.group(1) if gs_version_match else None, gs_sha_match.group(1) if gs_sha_match else None


def test_worker_engine_pins_are_exact_in_requirements_txt() -> None:
    """RED: img2pdf, Pillow, pypdfium2 must appear as exact pins in requirements.txt.

    This test fails until pins are added in the GREEN phase.
    """
    content = _read_text(RUNTIME_REQUIREMENTS)
    assert "img2pdf==0.6.3" in content, "img2pdf==0.6.3 not pinned in requirements.txt"
    # Pillow exact pin must exist (version TBD based on guidance + pip-audit)
    assert re.search(r"Pillow==\d+\.\d+\.\d+", content), "Pillow not pinned as exact version in requirements.txt"
    assert "pypdfium2==5.12.1" in content, "pypdfium2==5.12.1 not pinned in requirements.txt"


def test_ghostscript_version_in_dockerfile_worker_matches_official() -> None:
    """RED: Dockerfile.worker must declare GS_VERSION 10.07.1.

    Current baseline (before GREEN): Ghostscript 10.05.1. This test FAILS until
    updated to 10.07.1 per authoritative external-dependency-guidance.md.
    """
    version, _ = _parse_worker_dockerfile()
    assert version == AUTHORITATIVE_GS_VERSION, f"Dockerfile.worker GS_VERSION is {version}, expected {AUTHORITATIVE_GS_VERSION}"


def test_ghostscript_sha256_is_64_hex_and_not_stale() -> None:
    """RED: Dockerfile.worker must declare a 64-char hex SHA256 != stale 10.05.1 value.

    This enforces artifact reproducibility. The actual checksum will be fetched
    from Artifex at implementation time and verified against the downloadable tarball.
    """
    _, sha256 = _parse_worker_dockerfile()
    assert sha256 is not None, "GS_SHA256 ARG not found in Dockerfile.worker"
    assert len(sha256) == 64, f"GS_SHA256 must be exactly 64 hex chars, got {len(sha256)}: {sha256}"
    assert re.match(r"^[0-9a-f]{64}$", sha256), f"GS_SHA256 is not valid lowercase hex: {sha256}"
    stale_sha = "22f2bdca15c28830c9715cddc5c296ea66898bfdab0b604a4e0bcfeb03af6cad"
    assert sha256 != stale_sha, "GS_SHA256 appears to be the stale 10.05.1 artifact; update to 10.07.1 official checksum"


def test_import_surfaces_exist_for_worker_engines() -> None:
    """RED: Verify img2pdf, PIL, pypdfium2 can be imported.

    These imports MUST fail in the RED phase (packages not yet installed).
    They must pass after GREEN pins land in requirements.txt and the worker
    image context.
    """
    try:
        import img2pdf  # noqa: F401
    except ImportError as exc:
        raise AssertionError("img2pdf not importable; add img2pdf==0.6.3 to requirements.txt") from exc

    try:
        import PIL  # noqa: F401
    except ImportError as exc:
        raise AssertionError("PIL not importable; add Pillow to requirements.txt with exact pin") from exc

    try:
        import pypdfium2  # noqa: F401
    except ImportError as exc:
        raise AssertionError("pypdfium2 not importable; add pypdfium2==5.12.1 to requirements.txt") from exc
