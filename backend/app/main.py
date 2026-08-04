"""Application factory for the backend service.

``create_app()`` is the single construction seam: each call builds a fresh
:class:`FastAPI` instance with no import-time side effects and no lifespan
handlers. Settings are injected explicitly; when omitted they are loaded
from the process environment — never from dotfiles — via
:func:`app.config.load`, which fails fast when any required variable is
missing.

``app/main.py`` is the single integration owner (execution-matrix.md file
ownership table, BE-01 row): it mounts the BE-06 status, BE-08
capabilities, and BE-09 download routers exactly once each, preserving the
health/readiness, request-id, CORS/security-header, logging, and
stable-error-envelope contracts. ``app/routers/__init__.py`` carries no
APIRouter re-exports.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.config import Settings, load
from app.errors import register_error_handlers
from app.health import register_health_routes
from app.middleware import add_request_id_middleware
from app.routers.capabilities import router as capabilities_router
from app.routers.download import router as download_router
from app.routers.status import router as status_router
from app.security import add_security_middleware
from app.utils.logging import setup_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a standalone FastAPI application instance.

    Args:
        settings: Injected settings, attached to ``app.state.settings`` and
            consumed by the security middleware (CORS allowlist). When omitted,
            loaded from the process environment with :func:`app.config.load`.
            Passing a ``Settings`` instance explicitly is the test override
            seam — the module-level ``app`` is never touched.

    Returns:
        A fresh FastAPI instance with the liveness route, readiness route,
        and the mounted versioned routers registered.
    """
    if settings is None:
        settings = load()

    # BE-01 logging wiring: installs the structured JSON handler once per
    # process (idempotent) at the validated level. This changes no health,
    # request-id, error-envelope, or security-header contract.
    setup_logging(settings.log_level)

    application = FastAPI(title="papyr-backend", version="0.1.0")

    @application.get("/health")
    async def health_ok() -> dict[str, str]:
        return {"status": "ok"}

    # Readiness is additive: liveness remains unchanged while
    # /health/ready reports whether required configuration is available.
    register_health_routes(application)

    # BE-09 wiring wave: the versioned routers are mounted exactly once by
    # the single integration owner. Each router keeps its own dependency
    # resolution (app.state task_store/r2_client seams, settings/environment
    # fallbacks); mounting is purely declarative.
    application.include_router(status_router)
    application.include_router(capabilities_router)
    application.include_router(download_router)

    application.state.settings = settings
    # Mount the explicit CORS allowlist and application-layer security
    # headers using the injected settings.
    add_security_middleware(application, settings)
    # Every response carries an X-Request-ID correlation header, and
    # failures use the stable machine-readable error envelope.
    add_request_id_middleware(application)
    register_error_handlers(application)
    return application


# Backward-compatible module-level export: `from app.main import app` and the
# `/health` contract remain backward compatible.
app = create_app()
