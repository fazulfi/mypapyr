"""Liveness and readiness contracts for the backend service.

Liveness stays exactly where ``app.main`` registered it (``GET /health`` →
``{"status": "ok"}``); this module owns only the additive readiness
surface. Readiness claims what the delivered API requires: the process
answered, the required configuration loads, the Redis task-store
dependency (BE-04, consumed by the BE-06 status and BE-09 download
routers) is reachable through the app's wired store, and the threat
scanner (U-SEC/SEC-09) resolves to a concrete client. Only the worker —
no image exists at this SHA (``papyr-workers:__SET_ME__`` placeholder) —
is named as deferred.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final, Literal, TypedDict, cast

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response, status

from app import config
from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskStore
from app.security.classification import (
    ScannerStatus,
    SecurityDecision,
    ThreatClass,
    ThreatScanner,
    classify_payload,
)
from app.security.scanner import ClamdScanner

#: The worker has no image at this SHA (compose ``papyr-workers:__SET_ME__``
#: placeholder); readiness names it deferred and never probes it. Redis was
#: promoted from deferred to a real probe because the delivered BE-04/06/09
#: API reads the task store.
DEFERRED_DEPENDENCIES: tuple[str, ...] = ("worker",)

_FOUNDATION_OK: Literal["ok"] = "ok"
_FOUNDATION_MISSING_CONFIG: Literal["missing_required_config"] = "missing_required_config"
_REDIS_OK: Literal["ok"] = "ok"
_REDIS_UNAVAILABLE: Literal["unavailable"] = "unavailable"
_SCANNER_OK: Literal["ok"] = "ok"
_SCANNER_UNAVAILABLE: Literal["unavailable"] = "unavailable"

# HTTP status for each fail-closed threat class. Derived from the existing
# envelope vocabulary (app/errors.py spec_for_status): error.forbidden -> 403,
# error.rateLimited -> 429, error.internalError -> 500. Blocking verdicts are
# raised as HTTPException so the stable error envelope renders them; payload
# details never reach the envelope (errors.py normalizes by status only).
_THREAT_CLASS_TO_STATUS: Final[Mapping[ThreatClass, int]] = {
    ThreatClass.MALICIOUS: 403,
    ThreatClass.ACTIVE_CONTENT: 403,
    ThreatClass.INDETERMINATE: 500,
    ThreatClass.SCANNER_UNAVAILABLE: 429,
    ThreatClass.SANITIZATION_UNAVAILABLE: 429,
}


class ReadinessCheck(TypedDict):
    """Check outcomes; each carries one of its two closed literal values."""

    foundation: Literal["ok", "missing_required_config"]
    redis: Literal["ok", "unavailable"]
    scanner: Literal["ok", "unavailable"]


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


def resolve_probe_scanner(request: Request) -> ThreatScanner | None:
    """Resolve the scanner the readiness probe and admission gates use.

    The app's preset scanner (``app.state.scanner``) when present; otherwise
    the concrete :class:`ClamdScanner` built lazily from
    ``app.state.settings`` when present (cached on the app, mirroring the
    store seam); otherwise ``None`` — the dependency cannot be probed.
    """
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "scanner", None)
    if isinstance(preset, ThreatScanner):
        return preset
    settings = getattr(application.state, "settings", None)
    if not isinstance(settings, Settings):
        return None
    scanner = ClamdScanner(settings)
    application.state.scanner = scanner
    return scanner


def enforce_scan_gate(request: Request, data: bytes) -> None:
    """Run the fail-closed scanner gate over *data*; raise on block.

    Resolves the scanner via :func:`resolve_probe_scanner`, scans *data*,
    and enforces the SEC-01 :func:`classify_payload` matrix with scanning
    required. A CLEAN verdict returns silently; MALICIOUS, UNAVAILABLE,
    INDETERMINATE, and unresolvable-scanner outcomes all raise a
    :class:`HTTPException` whose status maps to the stable public error
    envelope (never leaking payload or signature details). Called by every
    admission router after validation and before sanitization/upload/enqueue.
    """
    scanner = resolve_probe_scanner(request)
    scanner_verdict = scanner.scan(data) if scanner is not None else None
    verdict = classify_payload(scanning_required=True, scanner_verdict=scanner_verdict)
    if verdict.decision is SecurityDecision.ALLOW:
        return
    assert verdict.threat_class is not None
    status_code = _THREAT_CLASS_TO_STATUS[verdict.threat_class]
    raise HTTPException(status_code=status_code, detail={"messageKey": verdict.message_key})


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


def scanner_ready(request: Request) -> bool:
    """Probe the scanner bound to *request*'s app; only CLEAN verdicts are ready.

    An unresolvable scanner (no preset, no usable settings) or any verdict
    other than CLEAN (disabled/unreachable daemon reports UNAVAILABLE) fails
    readiness — readiness must never claim ready while the scanner is down.
    """
    scanner = resolve_probe_scanner(request)
    if scanner is None:
        return False
    verdict = scanner.scan(b"")
    return verdict.status is ScannerStatus.CLEAN


@router.get("/health/ready")
async def readiness(
    response: Response,
    request: Request,
    env: Mapping[str, str] = Depends(env_provider),
) -> ReadinessResponse:
    """Additive readiness: 200 ready, 503 not ready, deferred deps always named."""
    foundation_ok = foundation_ready(env)
    redis_ok = redis_ready(request)
    scanner_ok = scanner_ready(request)
    ready = foundation_ok and redis_ok and scanner_ok
    response.status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready else "not_ready",
        "checks": {
            "foundation": _FOUNDATION_OK if foundation_ok else _FOUNDATION_MISSING_CONFIG,
            "redis": _REDIS_OK if redis_ok else _REDIS_UNAVAILABLE,
            "scanner": _SCANNER_OK if scanner_ok else _SCANNER_UNAVAILABLE,
        },
        "deferred": list(DEFERRED_DEPENDENCIES),
    }


def register_health_routes(app: FastAPI) -> None:
    """Mount the additive readiness surface on *app*.

    ``create_app()`` calls this inside the factory so each application
    instance receives the readiness route.
    """
    app.include_router(router)
