"""Security middleware package for the FastAPI service.

Promoted from the former ``app.security`` module (Phase 3 prerequisite):
the implementation moved to :mod:`app.security.middleware`, and this
package re-exports the exact public surface the existing consumers import,
so ``from app.security import add_security_middleware`` remains valid.

Phase 3 will add sibling modules under this package namespace
(``validation``, ``classification``, ``sanitize``, ``fair_use``), which a
plain module would shadow — hence the package layout.
"""

from app.security.middleware import (
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    SECURITY_HEADERS,
    SecurityHeadersMiddleware,
    WildcardOriginError,
    add_security_middleware,
    build_cors_config,
)

__all__ = [
    "CORS_ALLOW_HEADERS",
    "CORS_ALLOW_METHODS",
    "SECURITY_HEADERS",
    "SecurityHeadersMiddleware",
    "WildcardOriginError",
    "add_security_middleware",
    "build_cors_config",
]
