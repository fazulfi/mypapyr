"""Shared pytest fixtures for the backend suite.

The rootdir ``backend/conftest.py`` seeds the
five CI-injected settings variables before this module is imported (pytest
loads rootdir conftests first), so importing ``app.main`` at module level is
safe and the module-level ``app = create_app()`` never fails at collection.
The ``client`` fixture builds a fresh app per test from the factory.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """A TestClient wrapping a fresh factory-built app instance."""
    return TestClient(create_app())
