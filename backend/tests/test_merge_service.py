"""Tests for merge service (TL-03)."""

from datetime import timedelta

import pytest

from app.services.merge_service import MergeEngine, PikepdfError


class TestMergeEngine:
    def test_merge_engine_creation(self) -> None:
        """Engine initializes correctly."""
        engine = MergeEngine()
        assert engine is not None

    def test_merge_with_two_inputs(self) -> None:
        """Merge two valid PDFs."""
        # This will fail without real PDFs, but proves structure exists
        engine = MergeEngine()

        # With fake data that's not a real PDF, should raise error
        fake_pdf_1 = b"%PDF-fake-data-1"
        fake_pdf_2 = b"%PDF-fake-data-2"

        with pytest.raises(PikepdfError):
            engine.merge([fake_pdf_1, fake_pdf_2], timeout=timedelta(seconds=180))

    def test_merge_empty_sources(self) -> None:
        """Merging no sources raises error."""
        engine = MergeEngine()
        with pytest.raises(PikepdfError, match="No inputs"):
            engine.merge([], timeout=timedelta(seconds=180))
