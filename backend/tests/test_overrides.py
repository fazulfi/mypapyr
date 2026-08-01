"""Dependency-override seam tests.

Verify the structural override seam by overriding a route
dependency on a factory-created instance changes behavior, and restoring
the mapping returns the original behavior. The probe route is registered
on the throwaway factory instance only — no production endpoint is added.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.testclient import TestClient

from app.main import app, create_app


def test_dependency_override_changes_behavior_and_restores() -> None:
    instance = create_app()

    def probe_dep() -> str:
        return "real"

    @instance.get("/probe")
    async def probe(value: str = Depends(probe_dep)) -> dict[str, str]:
        return {"value": value}

    client = TestClient(instance)
    assert client.get("/probe").json() == {"value": "real"}

    instance.dependency_overrides[probe_dep] = lambda: "fake"
    assert client.get("/probe").json() == {"value": "fake"}

    instance.dependency_overrides.pop(probe_dep)
    assert client.get("/probe").json() == {"value": "real"}


def test_override_never_leaks_to_global_app() -> None:
    instance = create_app()

    def probe_dep() -> str:
        return "real"

    @instance.get("/probe")
    async def probe(value: str = Depends(probe_dep)) -> dict[str, str]:
        return {"value": value}

    instance.dependency_overrides[probe_dep] = lambda: "fake"
    client = TestClient(instance)
    assert client.get("/probe").json() == {"value": "fake"}
    assert probe_dep not in app.dependency_overrides
