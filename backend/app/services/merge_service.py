"""Merge PDF tool service: pikepdf merge engine.

Owned by TL-03 (execution-matrix.md). The :class:`MergeEngine` merges
multiple sanitized PDFs in user-specified order with deterministic page
order. The worker executes merge jobs through the generic :class:`JobExecutor`
seam; this module owns only the engine (the executor was folded into the
worker protocol surface in the T-series redo).

Privacy contract: logs carry operation names and exception class names only.
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import pikepdf

logger = logging.getLogger(__name__)


class PikepdfError(Exception):
    """Normalized error for pikepdf-level merge failures."""


@dataclass(frozen=True)
class MergeResult:
    """Result of a merge operation."""

    total_pages: int
    total_bytes: int


class MergeEngine:
    """Pikepdf-based merge engine."""

    def merge(self, sources: list[bytes], *, timeout: timedelta) -> MergeResult:
        """Merge multiple PDFs into one, deterministic page order.

        Args:
            sources: List of sanitized PDF bytes (must have same MIME type)
            timeout: Maximum execution time

        Returns:
            MergeResult with total_pages and total_bytes
        """
        try:
            with tempfile.TemporaryDirectory(prefix="papyr-merge-") as tmpdir:
                # Write all inputs to temp files
                input_paths = []
                for i, data in enumerate(sources):
                    path = Path(tmpdir) / f"input_{i}.pdf"
                    path.write_bytes(data)
                    input_paths.append(path)

                # Open all PDFs with pikepdf
                pdfs = [pikepdf.open(str(p)) for p in input_paths]

                if not pdfs:
                    raise PikepdfError("No inputs")

                # Merge pages in order (user order preserved)
                merged = pikepdf.new()
                for pdf in pdfs:
                    merged.pages.extend(pdf.pages)
                    pdf.close()

                # Write output
                output_path = Path(tmpdir) / "output.pdf"
                merged.save(str(output_path))
                merged.close()

                # Count total pages
                total_pages = len(merged.pages)
                output_size = output_path.stat().st_size
        except PikepdfError:
            raise
        except Exception as exc:
            # pikepdf surfaces low-level failures as pikepdf._core.PdfError and
            # corrupt/invalid inputs raise opaque exceptions. Normalize to the
            # domain error so callers (worker/APIs) can map it deterministically.
            if type(exc).__module__.startswith("pikepdf"):
                raise PikepdfError(f"PDF processing failed: {exc}") from exc
            raise

        return MergeResult(total_pages=total_pages, total_bytes=output_size)
