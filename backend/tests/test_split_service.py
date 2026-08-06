"""Split service engine tests (TL-04).

Tests the SplitEngine page extraction logic.
"""

from __future__ import annotations

from app.services.split_service import SplitEngine


def test_split_engine_creation():
    engine = SplitEngine()
    assert engine is not None


def test_parse_range_spec_simple():
    engine = SplitEngine()
    ranges = engine._parse_range_spec("1-3")
    assert ranges == [(1, 3)]


def test_parse_range_spec_multiple():
    engine = SplitEngine()
    ranges = engine._parse_range_spec("1-3,5,7-9")
    assert ranges == [(1, 3), (5, 5), (7, 9)]


def test_parse_range_spec_single_page():
    engine = SplitEngine()
    ranges = engine._parse_range_spec("5")
    assert ranges == [(5, 5)]
