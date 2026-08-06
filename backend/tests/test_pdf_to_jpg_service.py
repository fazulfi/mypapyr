from __future__ import annotations

from unittest.mock import MagicMock, Mock

import pytest

from app.services.pdf_to_jpg_service import extract_pages_as_jpg


def test_extract_pages_defaults_to_all_pages() -> None:
    pdfium = Mock()
    document = MagicMock()
    page = Mock()
    bitmap = Mock()
    bitmap.to_pil.return_value.convert.return_value.save = Mock()
    pdfium.PdfDocument.return_value = document
    document.__len__.return_value = 2
    document[0] = page
    document[1] = page
    page.render.return_value = bitmap

    result = extract_pages_as_jpg(b"%PDF-1.7", pdfium_module=pdfium)

    assert isinstance(result, list)
    assert len(result) == 2


def test_extract_pages_rejects_dpi_outside_range() -> None:
    with pytest.raises(ValueError, match="DPI"):
        extract_pages_as_jpg(b"%PDF-1.7", dpi=301)


def test_extract_pages_rejects_page_over_16mp() -> None:
    with pytest.raises(ValueError, match="16 MP"):
        extract_pages_as_jpg(b"%PDF-1.7", dpi=300, page_size_points=(10000, 10000))
