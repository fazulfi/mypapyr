"""Liveness and readiness contracts for the backend service.

Liveness stays exactly where ``app.main`` registered it (``GET /health`` →
``{"status": "ok"}``); this module owns only the additive readiness
surface. Readiness claims what the delivered API requires: the process
answered, the required configuration loads, and the Redis task-store
dependency (BE-04, consumed by the BE-06 status and BE-09 download
routers) is reachable through the app's wired store. Only the worker — no
image exists at this SHA (``papyr-workers:__SET_ME__`` placeholder) — is
named as deferred.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal, TypedDict, cast

from fastapi import APIRouter, Depends, FastAPI, Request, Response, status

from app import config
from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskStore

#: The worker has no image at this SHA (compose ``papyr-workers:__SET_ME__``
#: placeholder); readiness names it deferred and never probes it. Redis was
#: promoted from deferred to a real probe because the delivered BE-04/06/09
#: API reads the task store.
DEFERRED_DEPENDENCIES: tuple[str, ...] = ("worker",)

_FOUNDATION_OK: Literal["ok"] = "ok"
_FOUNDATION_MISSING_CONFIG: Literal["missing_required_config"] = "missing_required_config"
_REDIS_OK: Literal["ok"] = "ok"
_REDIS_UNAVAILABLE: Literal["unavailable"] = "unavailable"


class ReadinessCheck(TypedDict):
    """Check outcomes; each carries one of its two closed literal values."""

    foundation: Literal["ok", "missing_required_config"]
    redis: Literal["ok", "unavailable"]


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


def resolve_probe_store(request: Request) -> TaskStore | None:
    """Resolve the store the readiness probe pings.

    The app's wired store (``app.state.task_store``, preset by
    ``create_app``) when present; otherwise the store built from
    ``app.state.settings`` when present (cached on the app, mirroring the
    router seam); otherwise ``None`` — the dependency cannot be probed.
    """
    application = cast(FastAPI, request.app)
    cached = getattr(application.state, "task_store", None)
    if isinstance(cached, TaskStore):
        return cached
    settings = getattr(application.state, "settings", None)
    if not isinstance(settings, Settings):
        return None
    store = TaskStore(settings)
    application.state.task_store = store
    return store


def redis_ready(request: Request) -> bool:
    """Probe the store bound to *request*'s app; only reachable is ready."""
    store = resolve_probe_store(request)
    if store is None:
        return False
    try:
        store.ping()
    except StoreUnavailableError:
        return False
    return True


@router.get("/health/ready")
async def readiness(
    response: Response,
    request: Request,
    env: Mapping[str, str] = Depends(env_provider),
) -> ReadinessResponse:
    """Additive readiness: 200 ready, 503 not ready, deferred deps always named."""
    foundation_ok = foundation_ready(env)
    redis_ok = redis_ready(request)
    ready = foundation_ok and redis_ok
    response.status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready else "not_ready",
        "checks": {
            "foundation": _FOUNDATION_OK if foundation_ok else _FOUNDATION_MISSING_CONFIG,
            "redis": _REDIS_OK if redis_ok else _REDIS_UNAVAILABLE,
        },
        "deferred": list(DEFERRED_DEPENDENCIES),
    }


def register_health_routes(app: FastAPI) -> None:
    """Mount the additive readiness surface on *app*.

    ``create_app()`` calls this inside the factory so each application
    instance receives the readiness route.
    """
    app.include_router(router)
