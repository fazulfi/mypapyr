"""Liveness and readiness contract tests.

``GET /health`` stays exactly ``{"status": "ok"}`` and never gains fields.
Unknown health paths and methods are rejected (404/405); the readiness
surface is additive under ``/health/ready`` and never alters liveness.

Readiness reports what the delivered API actually requires: the required
foundation configuration (the five CI-injected variables) AND the Redis
task-store dependency the BE-04/06/09 status and download routers consume.
The Redis check probes the app's wired store (``app.state.task_store``) and
is reported accurately as ``ok``/``unavailable``; only the worker — which has
no image at this SHA (``papyr-workers:__SET_ME__`` placeholder) — stays
named as deferred. The probe is dependency-injectable so the contract is
tested deterministically with a fakeredis-backed store.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import cast

import fakeredis
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError

from app import health
from app.config import Settings
from app.main import create_app
from app.queue.store import RedisLike, TaskStore
from app.security.classification import ScannerStatus, ScannerVerdict

# The five CI-injected foundation variables (ci.yml backend-test job);
# readiness is ready only when all of them load.
_FULL_ENV: Mapping[str, str] = {
    "R2_ACCOUNT_ID": "test-account",
    "R2_ACCESS_KEY_ID": "test-key",
    "R2_SECRET_ACCESS_KEY": "test-secret",
    "R2_BUCKET_NAME": "test-bucket",
    "ALLOWED_ORIGINS": "http://localhost:3000",
}

_FOUNDATION_SETTINGS = Settings.from_env(dict(_FULL_ENV))


class _CleanScanner:
    """Scanner double returning CLEAN verdict (U-SEC seam for readiness)."""

    def scan(self, data: bytes) -> ScannerVerdict:
        return ScannerVerdict(status=ScannerStatus.CLEAN)


def _fake_store() -> TaskStore:
    """A healthy fakeredis-backed store (readiness redis: ok seam)."""
    return TaskStore(_FOUNDATION_SETTINGS, client=cast(RedisLike, fakeredis.FakeRedis()))


class _UnreachableClient:
    """Redis client whose ping fails exactly like an unreachable server."""

    def ping(self) -> bool:
        raise ConnectionError("connection refused")

    def close(self) -> None:
        pass


def _unreachable_store() -> TaskStore:
    """A store whose probe fails (readiness redis: unavailable seam)."""
    return TaskStore(_FOUNDATION_SETTINGS, client=cast(RedisLike, _UnreachableClient()))


def _registered_app(env: Mapping[str, str], store: TaskStore | None = None) -> FastAPI:
    """Fresh app with liveness and readiness routes.

    The environment override keeps negative cases free of global-environment
    mutation; the store override makes the Redis probe deterministic; the
    scanner override keeps the U-SEC scanner probe deterministic.
    """
    application = FastAPI()
    application.get("/health")(health_ok)
    health.register_health_routes(application)
    application.dependency_overrides[health.env_provider] = lambda: env
    if store is not None:
        application.state.task_store = store
    application.state.scanner = _CleanScanner()
    return application


async def health_ok() -> dict[str, str]:
    """Liveness handler for the registered test app (main.py contract)."""
    return {"status": "ok"}


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_env_provider_returns_process_environment() -> None:
    assert health.env_provider() is os.environ


def test_health_unknown_path_returns_404() -> None:
    client = TestClient(create_app())
    response = client.get("/health/unknown")
    assert response.status_code == 404


def test_health_rejects_non_get_method() -> None:
    client = TestClient(create_app())
    response = client.post("/health")
    assert response.status_code == 405


def test_readiness_healthy_with_config_and_redis() -> None:
    client = TestClient(_registered_app(_FULL_ENV, _fake_store()))
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"foundation": "ok", "redis": "ok", "scanner": "ok"},
        "deferred": ["worker"],
    }


def test_readiness_degraded_without_config() -> None:
    client = TestClient(_registered_app({}))
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {
            "foundation": "missing_required_config",
            "redis": "unavailable",
            "scanner": "ok",
        },
        "deferred": ["worker"],
    }


def test_readiness_not_ready_when_redis_unavailable() -> None:
    client = TestClient(_registered_app(_FULL_ENV, _unreachable_store()))
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"foundation": "ok", "redis": "unavailable", "scanner": "ok"},
        "deferred": ["worker"],
    }


def test_readiness_redis_failure_never_leaks_connection_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = TestClient(_registered_app(_FULL_ENV, _unreachable_store()))
    response = client.get("/health/ready")
    body = response.text
    assert "redis://" not in body
    assert "connection refused" not in body
    assert "localhost" not in body
    for record in caplog.records:
        assert "connection refused" not in record.getMessage()


def test_readiness_registration_is_additive() -> None:
    client = TestClient(_registered_app(_FULL_ENV, _fake_store()))
    liveness = client.get("/health")
    assert liveness.status_code == 200
    assert liveness.json() == {"status": "ok"}
    readiness = client.get("/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"


def test_factory_integration_mounts_readiness_on_real_app() -> None:
    """``create_app()`` registers readiness and wires the store seam.

    The factory presets ``app.state.task_store`` from the injected settings,
    so the readiness probe reports the wired store. A healthy fakeredis
    store and a clean scanner are injected to keep the checks deterministic.
    """
    instance = create_app(settings=_FOUNDATION_SETTINGS)
    instance.state.task_store = _fake_store()
    instance.state.scanner = _CleanScanner()
    client = TestClient(instance)
    assert client.get("/health").json() == {"status": "ok"}
    readiness = client.get("/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"
    assert readiness.json()["checks"]["redis"] == "ok"
    assert readiness.json()["deferred"] == ["worker"]
