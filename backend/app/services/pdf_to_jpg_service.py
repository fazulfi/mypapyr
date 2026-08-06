from __future__ import annotations

from io import BytesIO
from typing import Any


def extract_pages_as_jpg(
    data: bytes,
    *,
    pages: list[int] | None = None,
    dpi: int = 150,
    pdfium_module: Any | None = None,
    page_size_points: tuple[float, float] | None = None,
) -> list[bytes]:
    if not 72 <= dpi <= 300:
        raise ValueError("DPI must be between 72 and 300")
    if page_size_points is not None:
        width = round(page_size_points[0] * dpi / 72)
        height = round(page_size_points[1] * dpi / 72)
        if width * height > 16_000_000:
            raise ValueError("page exceeds 16 MP")
    if pdfium_module is None:
        import pypdfium2 as pdfium_module
    document = pdfium_module.PdfDocument(data)
    selected = list(range(len(document))) if pages is None else pages
    output: list[bytes] = []
    for index in selected:
        if index < 0 or index >= len(document):
            raise ValueError("page index out of range")
        page = document[index]
        bitmap = page.render(scale=dpi / 72)
        image = bitmap.to_pil().convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=90, optimize=True)
        output.append(buffer.getvalue())
    return output
