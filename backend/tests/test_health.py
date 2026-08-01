"""Liveness and readiness contract tests.

``GET /health`` stays exactly ``{"status": "ok"}`` and never gains fields.
Unknown health paths and methods are rejected (404/405); the readiness
surface is additive under ``/health/ready`` and never alters liveness.
Readiness checks the process and
     the required foundation configuration only, and names Redis/worker as
     deferred in every response — it never claims them available.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import health
from app.main import app

# The five CI-injected foundation variables (ci.yml backend-test job);
# readiness is ready only when all of them load.
_FULL_ENV: Mapping[str, str] = {
    "R2_ACCOUNT_ID": "test-account",
    "R2_ACCESS_KEY_ID": "test-key",
    "R2_SECRET_ACCESS_KEY": "test-secret",
    "R2_BUCKET_NAME": "test-bucket",
    "ALLOWED_ORIGINS": "http://localhost:3000",
}


def _registered_app(env: Mapping[str, str]) -> FastAPI:
    """Fresh app with liveness and readiness routes.

    The environment override keeps negative cases free of global-environment
    mutation.
    """
    application = FastAPI()
    application.get("/health")(health_ok)
    health.register_health_routes(application)
    application.dependency_overrides[health.env_provider] = lambda: env
    return application


async def health_ok() -> dict[str, str]:
    """Liveness handler for the registered test app (main.py contract)."""
    return {"status": "ok"}


def test_health_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_env_provider_returns_process_environment() -> None:
    assert health.env_provider() is os.environ


def test_health_unknown_path_returns_404() -> None:
    client = TestClient(app)
    response = client.get("/health/unknown")
    assert response.status_code == 404


def test_health_rejects_non_get_method() -> None:
    client = TestClient(app)
    response = client.post("/health")
    assert response.status_code == 405


def test_readiness_healthy_with_full_config() -> None:
    client = TestClient(_registered_app(_FULL_ENV))
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"foundation": "ok"},
        "deferred": ["redis", "worker"],
    }


def test_readiness_degraded_without_config() -> None:
    client = TestClient(_registered_app({}))
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"foundation": "missing_required_config"},
        "deferred": ["redis", "worker"],
    }


def test_readiness_registration_is_additive() -> None:
    client = TestClient(_registered_app(_FULL_ENV))
    liveness = client.get("/health")
    assert liveness.status_code == 200
    assert liveness.json() == {"status": "ok"}
    readiness = client.get("/health/ready")
    assert readiness.status_code == 200


def test_factory_integration_mounts_readiness_on_real_app() -> None:
    """The module-level app serves both health surfaces.

    ``create_app()`` registers readiness while preserving the exact liveness
    response.
    """
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    readiness = client.get("/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"
