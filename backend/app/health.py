"""Liveness and readiness contracts for the backend service.

Liveness stays exactly where ``app.main`` registered it (``GET /health`` →
``{"status": "ok"}``); this module owns only the additive readiness
surface. Readiness claims only what the service can currently assert: the
process answered and the required configuration loads. Redis and the worker
are named as deferred dependencies and are never probed or reported available.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal, TypedDict

from fastapi import APIRouter, Depends, FastAPI, Response, status

from app import config

#: External dependencies intentionally outside the foundation scope.
DEFERRED_DEPENDENCIES: tuple[str, ...] = ("redis", "worker")

_FOUNDATION_OK: Literal["ok"] = "ok"
_FOUNDATION_MISSING_CONFIG: Literal["missing_required_config"] = "missing_required_config"


class ReadinessCheck(TypedDict):
    """Foundation check outcome; one of the two closed literal values."""

    foundation: Literal["ok", "missing_required_config"]


class ReadinessResponse(TypedDict):
    """Stable readiness payload; same shape in the ready and not_ready states."""

    status: Literal["ready", "not_ready"]
    checks: ReadinessCheck
    deferred: list[str]


router = APIRouter(tags=["ops"])


def env_provider() -> Mapping[str, str]:
    """Environment source for the readiness check (dependency override seam)."""
    return os.environ


def foundation_ready(env: Mapping[str, str]) -> bool:
    """Return whether the required service settings load from *env*."""
    try:
        config.Settings.from_env(env)
    except config.MissingEnvVarError:
        return False
    return True


@router.get("/health/ready")
async def readiness(
    response: Response,
    env: Mapping[str, str] = Depends(env_provider),
) -> ReadinessResponse:
    """Additive readiness: 200 ready, 503 not ready, deferred deps always named."""
    ready = foundation_ready(env)
    response.status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready else "not_ready",
        "checks": {"foundation": _FOUNDATION_OK if ready else _FOUNDATION_MISSING_CONFIG},
        "deferred": list(DEFERRED_DEPENDENCIES),
    }


def register_health_routes(app: FastAPI) -> None:
    """Mount the additive readiness surface on *app*.

    ``create_app()`` calls this inside the factory so each application
    instance receives the readiness route.
    """
    app.include_router(router)
