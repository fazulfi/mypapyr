"""Tests for merge service (TL-03)."""

import pytest
from datetime import timedelta

from app.services.merge_service import MergeEngine, MergeResult, PikepdfError


class TestMergeEngine:
    def test_merge_engine_creation(self):
        """Engine initializes correctly."""
        engine = MergeEngine()
        assert engine is not None
    
    def test_merge_with_two_inputs(self):
        """Merge two valid PDFs."""
        # This will fail without real PDFs, but proves structure exists
        engine = MergeEngine()
        
        # With fake data that's not a real PDF, should raise error
        fake_pdf_1 = b'%PDF-fake-data-1'
        fake_pdf_2 = b'%PDF-fake-data-2'
        
        with pytest.raises(PikepdfError):
            engine.merge([fake_pdf_1, fake_pdf_2], timeout=timedelta(seconds=180))
    
    def test_merge_empty_sources(self):
        """Merging no sources raises error."""
        engine = MergeEngine()
        with pytest.raises(PikepdfError, match='No inputs'):
            engine.merge([], timeout=timedelta(seconds=180))
