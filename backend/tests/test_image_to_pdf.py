"""JPG-to-PDF router tests (TL-05)."""

from fastapi.testclient import TestClient


def test_router_prefix():
    from app.routers.image_to_pdf import router

    assert router.prefix == "/api/v1/tools/jpg-to-pdf"


def test_router_tag():
    from app.routers.image_to_pdf import router

    assert router.tags == ["jpg-to-pdf"]


def test_tasks_endpoint_exists(client: TestClient) -> None:
    """Test that the /tasks endpoint exists."""
    response = client.post(
        "/api/v1/tools/jpg-to-pdf/tasks",
        files={"files": ("test.jpg", b"fake image content", "image/jpeg")},
    )
    # Should return 202 or a validation error, not 404
    assert response.status_code in [202, 400, 429]
