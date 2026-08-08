"""Tests for merge PDF router (TL-03)."""

from fastapi.routing import APIRoute

from app.routers.merge import router


def test_merge_router_exists() -> None:
    """Router has correct prefix."""
    assert router.prefix == "/api/v1/tools/merge-pdf"
    assert "merge" in router.tags


def test_merge_router_has_tasks_endpoint() -> None:
    """Router has POST /tasks endpoint."""
    routes = [route.path for route in router.routes if isinstance(route, APIRoute)]
    assert "/api/v1/tools/merge-pdf/tasks" in routes
