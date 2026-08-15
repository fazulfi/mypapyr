"""Split PDF tool router tests (TL-04).

Verifies the POST /api/v1/tools/split-pdf/tasks contract exists and
follows the same pattern as compress/merge.
"""

from __future__ import annotations

from app.routers.split import router


def test_router_prefix():
    assert router.prefix == "/api/v1/tools/split-pdf"


def test_router_tag():
    assert router.tags == ["split"]


def test_tasks_endpoint_exists():
    routes = [r for r in router.routes if hasattr(r, "path") and r.path == "/api/v1/tools/split-pdf/tasks"]
    assert len(routes) == 1
