"""Tests for merge PDF router (TL-03)."""

import pytest

from app.routers.merge import router


def test_merge_router_exists():
    """Router has correct prefix."""
    assert router.prefix == '/api/v1/tools/merge-pdf'
    assert 'merge' in router.tags


def test_merge_router_has_tasks_endpoint():
    """Router has POST /tasks endpoint."""
    routes = [route.path for route in router.routes]
    assert '/api/v1/tools/merge-pdf/tasks' in routes
