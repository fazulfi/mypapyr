"""U-PINS worker engine pin contract tests (RED until the pins land).

Locks the worker image's five-tool engine dependencies per the Phase-5 U-PINS
contract (BLKR-10, P4-06, P4-07), derived from:

* ``audit-outputs/phase-4/research/external-dependency-guidance.md``
  (Ghostscript 10.07.1 official Artifex source; img2pdf 0.6.3; pypdfium2
  5.12.1; Pillow decompression-bomb safeguard left enabled).
* The real five-tool worker imports: ``image_to_pdf_service`` imports
  ``PIL`` and lazy-imports ``img2pdf``; ``pdf_to_jpg_service`` lazy-imports
  ``pypdfium2``; ``compress_service`` shells out to the Ghostscript binary.
* The official Artifex ``gs10071`` release (published 2026-05-19): the
  ``ghostscript-10.07.1.tar.xz`` SHA256 below was computed from the official
  download and cross-checked against the release's official SHA512SUMS.

RED phase: fails against HEAD (GS 10.05.1 URL/sha, no engine pins in
``requirements.txt``, engines not installed). GREEN once the pins land in
``requirements.txt``/``Dockerfile.worker`` and are installed.

Design notes mirror ``test_dependencies.py``: engine modules are imported via
``importlib`` (img2pdf ships no ``py.typed``, so a static import would break
the strict-mypy gate); the contract under test is runtime importability.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import Any, cast

BACKEND_DIR = Path(__file__).resolve().parent.parent
RUNTIME_REQUIREMENTS = BACKEND_DIR / "requirements.txt"
DOCKERFILE_WORKER = BACKEND_DIR / "Dockerfile.worker"

# Official Artifex gs10071 release data (authoritative). The SHA256 was
# computed from the official ghostscript-10.07.1.tar.xz download and the
# download was cross-verified against the release's official SHA512SUMS.
AUTHORITATIVE_GS_VERSION = "10.07.1"
AUTHORITATIVE_GS_RELEASE_TAG = "gs10071"
AUTHORITATIVE_GS_SHA256 = "1cdb766de8db8f1e589c817f09c5855ea5f65dfc8540e465a69ac14c18416025"
# The GS 10.05.1 checksum pinned at HEAD; must be replaced, never reused.
STALE_GS_10_05_1_SHA256 = "22f2bdca15c28830c9715cddc5c296ea66898bfdab0b604a4e0bcfeb03af6cad"

WORKER_ENGINE_PINS: dict[str, str] = {
    "img2pdf": "0.6.3",
    "Pillow": "12.3.0",
    "pypdfium2": "5.12.1",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_pins(path: Path) -> dict[str, str]:
    """Parse exact ``name==version`` pins (mirrors ``test_dependencies``)."""
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-r", "-e", "--")):
            continue
        name, separator, version = line.partition("==")
        assert separator, f"non-exact pin in {path.name}: {raw!r}"
        assert version and version == version.strip()
        assert " " not in version and "," not in version
        assert all(op not in version for op in ("<", ">", "~", "!"))
        pins[name] = version
    assert pins, f"no pins parsed from {path.name}"
    return pins


def _parse_worker_dockerfile() -> tuple[str | None, str | None, str | None]:
    """Extract GS_VERSION, GS_SHA256, and the release tag from Dockerfile.worker."""
    content = _read_text(DOCKERFILE_WORKER)
    version = re.search(r"ARG\s+GS_VERSION=(\d+\.\d+\.\d+)", content)
    sha = re.search(r"ARG\s+GS_SHA256=([0-9a-f]{64})", content)
    tag = re.search(r"releases/download/(gs\d+)/ghostscript-\$\{GS_VERSION\}\.tar\.xz", content)
    return (
        version.group(1) if version else None,
        sha.group(1) if sha else None,
        tag.group(1) if tag else None,
    )


def _module_attr(module_name: str, attribute: str) -> Any:
    """Runtime-imported attribute access; the single cast crossing point."""
    return getattr(cast(Any, importlib.import_module(module_name)), attribute)


def test_worker_engine_pins_are_exact_in_requirements_txt() -> None:
    """img2pdf, Pillow, pypdfium2 must be exact pins in requirements.txt."""
    pins = _parse_pins(RUNTIME_REQUIREMENTS)
    for package, version in WORKER_ENGINE_PINS.items():
        assert package in pins, f"{package} missing from requirements.txt"
        assert pins[package] == version, f"{package} pinned {pins[package]}, expected {version}"


def test_ghostscript_version_in_dockerfile_worker_matches_official() -> None:
    """Dockerfile.worker must build the official GS 10.07.1 (not stale 10.05.1)."""
    version, _, _ = _parse_worker_dockerfile()
    assert version == AUTHORITATIVE_GS_VERSION, (
        f"Dockerfile.worker GS_VERSION is {version}, expected {AUTHORITATIVE_GS_VERSION}"
    )


def test_ghostscript_release_url_tracks_official_tag() -> None:
    """The tarball URL must track the official gs10071 release tag."""
    _, _, tag = _parse_worker_dockerfile()
    assert tag == AUTHORITATIVE_GS_RELEASE_TAG, (
        f"Dockerfile.worker downloads from release tag {tag!r}, "
        f"expected {AUTHORITATIVE_GS_RELEASE_TAG!r}"
    )


def test_ghostscript_sha256_is_official_and_not_stale() -> None:
    """GS_SHA256 must be the verified official 10.07.1 checksum."""
    _, sha256, _ = _parse_worker_dockerfile()
    assert sha256 is not None, "GS_SHA256 ARG not found in Dockerfile.worker"
    assert re.fullmatch(r"[0-9a-f]{64}", sha256), f"GS_SHA256 is not lowercase hex: {sha256}"
    assert sha256 != STALE_GS_10_05_1_SHA256, (
        "GS_SHA256 is still the stale 10.05.1 artifact checksum"
    )
    assert sha256 == AUTHORITATIVE_GS_SHA256, (
        f"GS_SHA256 {sha256} does not match the official 10.07.1 checksum {AUTHORITATIVE_GS_SHA256}"
    )


def test_worker_engine_import_surfaces() -> None:
    """Engines import with the surfaces the five-tool executors consume.

    Fails in RED (engines not installed); passes once the pinned engines are
    installed. The Pillow decompression-bomb safeguard must remain enabled
    (never ``--pillow-limit-break`` per external-dependency-guidance.md).
    """
    convert = _module_attr("img2pdf", "convert")
    assert callable(convert), "img2pdf.convert is not callable"

    max_pixels = _module_attr("PIL.Image", "MAX_IMAGE_PIXELS")
    assert isinstance(max_pixels, int) and max_pixels > 0, (
        "Pillow decompression-bomb safeguard is disabled (MAX_IMAGE_PIXELS unset)"
    )
    bomb_warning = _module_attr("PIL.Image", "DecompressionBombWarning")
    assert bomb_warning is not None, "Pillow DecompressionBombWarning missing"

    pdf_document = _module_attr("pypdfium2", "PdfDocument")
    assert pdf_document is not None, "pypdfium2.PdfDocument missing (PDFium engine absent)"
    # Engine self-check: the installed pypdfium2 must self-report the pinned
    # version, and the bundled PDFium binary version must be present (the CVE
    # tracking target per external-dependency-guidance.md section 11.3).
    version_info = _module_attr("pypdfium2.version", "PYPDFIUM_INFO")
    assert str(version_info) == WORKER_ENGINE_PINS["pypdfium2"], (
        f"pypdfium2 self-reports {version_info}, expected {WORKER_ENGINE_PINS['pypdfium2']}"
    )
    pdfium_info = _module_attr("pypdfium2.version", "PDFIUM_INFO")
    assert str(pdfium_info), "pypdfium2.version.PDFIUM_INFO (bundled PDFium binary) missing"


def test_dockerfile_preserves_nonroot_tini_health_cmd_contract() -> None:
    """U-PINS must not disturb the U-WORKER hardened image contract."""
    content = _read_text(DOCKERFILE_WORKER)
    assert "USER appuser" in content, "non-root USER appuser contract broken"
    assert 'ENTRYPOINT ["/usr/bin/tini", "--"]' in content, "tini ENTRYPOINT contract broken"
    assert "HEALTHCHECK" in content, "HEALTHCHECK probe contract broken"
    assert 'CMD ["python", "-m", "app.worker"]' in content, "worker CMD contract broken"
