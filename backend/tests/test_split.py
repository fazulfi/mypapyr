"""Split PDF tool router tests (TL-04).

Verifies the POST /api/v1/tools/split-pdf/tasks contract exists and
follows the same pattern as compress/merge, plus the admission-time range
validation contract (FR-SPLIT-01/02/04): default one-per-page mode, custom
range normalization, and fail-closed rejection of malformed/out-of-bounds
specs.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.routers.split import _validate_split_ranges, router
from app.schemas.job import SplitOptions
from app.security.validation import PdfInspection


def test_router_prefix() -> None:
    assert router.prefix == "/api/v1/tools/split-pdf"


def test_router_tag() -> None:
    assert router.tags == ["split"]


def test_tasks_endpoint_exists() -> None:
    routes = [r for r in router.routes if hasattr(r, "path") and "/split-pdf/tasks" in r.path]
    assert len(routes) == 1


def _inspection(page_count: int | None) -> PdfInspection:
    return PdfInspection(
        format="pdf",
        size_bytes=1024,
        page_count=page_count,
        is_encrypted=page_count is None,
        recovery_warnings_count=0,
    )


def test_admission_default_mode_returns_no_options() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    options = _validate_split_ranges("", _inspection(10), limit)
    assert options is None


def test_admission_custom_ranges_normalized_and_persisted() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    options = _validate_split_ranges("2-5,7", _inspection(10), limit)
    assert options == SplitOptions(ranges="2-5,7")


def test_admission_inner_whitespace_in_range_token_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("2 - 5,7", _inspection(10), limit)
    assert exc_info.value.status_code == 400


def test_admission_surrounding_whitespace_stripped_for_valid_spec() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    options = _validate_split_ranges(" 2-5 , 7 ", _inspection(10), limit)
    assert options == SplitOptions(ranges="2-5,7")


def test_admission_malformed_ranges_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("1-a", _inspection(10), limit)
    assert exc_info.value.status_code == 400


def test_admission_reversed_range_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("5-2", _inspection(10), limit)
    assert exc_info.value.status_code == 400


def test_admission_out_of_bounds_range_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("8-12", _inspection(10), limit)
    assert exc_info.value.status_code == 400


def test_admission_too_many_ranges_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    spec = ",".join(str(page) for page in range(1, limit.max_outputs + 2))
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges(spec, _inspection(limit.max_outputs + 1), limit)
    assert exc_info.value.status_code == 400


def test_admission_default_mode_over_output_cap_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("", _inspection(limit.max_outputs + 1), limit)
    assert exc_info.value.status_code == 400


def test_admission_encrypted_input_with_ranges_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("1-3", _inspection(None), limit)
    assert exc_info.value.status_code == 400


def test_admission_zero_page_default_mode_rejected_400() -> None:
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    with pytest.raises(HTTPException) as exc_info:
        _validate_split_ranges("", _inspection(0), limit)
    assert exc_info.value.status_code == 400
