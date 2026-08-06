from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_pdf_to_jpg_route_exists() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("sample.pdf", b"%PDF-1.7", "application/pdf")},
    )
    assert response.status_code != 404
