"""CORS and application-layer security-header middleware.

The application factory mounts this module through
``add_security_middleware(app, settings)``.

Boundaries locked here:

* CORS is an explicit allowlist driven by ``Settings.allowed_origins``
  (``ALLOWED_ORIGINS`` env). Wildcard origins are rejected at config-build
  time (``WildcardOriginError``), so credentials can never pair with ``*``.
* Credentials default off (``allow_credentials=False``): no auth exists in
  the service.
* Only application-layer safe headers are emitted. HSTS, CSP placement,
  ``server_tokens off`` and the rest of the edge set are Nginx/edge
  responsibilities and are not claimed
  here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypedDict

from fastapi import FastAPI
from starlette.datastructures import MutableHeaders
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config import Settings

CORS_ALLOW_METHODS: tuple[str, ...] = ("GET", "POST", "OPTIONS")
"""Methods allowed on cross-origin requests."""

CORS_ALLOW_HEADERS: tuple[str, ...] = ("Content-Type", "Authorization", "X-Request-ID")
"""Headers allowed on cross-origin requests."""

SECURITY_HEADERS: Mapping[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
"""Application-layer safe headers (OWASP). Edge-only headers are not here."""

_MOUNTED_FLAG = "_papyr_security_mounted"


class WildcardOriginError(ValueError):
    """Raised when an allowlist entry contains ``*``; the allowlist must be explicit."""


class CorsConfig(TypedDict):
    """Typed ``CORSMiddleware`` keyword arguments (the ``build_cors_config`` result).

    A TypedDict — not ``dict[str, object]`` — preserves the per-key types
    across the ``**`` unpack into ``add_middleware``, so the strict-mypy gate
    still checks the CORS wiring.
    """

    allow_origins: list[str]
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]


def build_cors_config(
    origins: Sequence[str],
    *,
    allow_credentials: bool = False,
) -> CorsConfig:
    """Validate *origins* and return the ``CORSMiddleware`` keyword arguments.

    Explicit allowlist only: an empty allowlist, an empty entry, or any
    origin containing ``*`` raises, which makes a credentials+wildcard pair
    structurally impossible (``CORSMiddleware`` forbids it at construction).
    """
    if not origins:
        raise ValueError("CORS allowlist must contain at least one origin")
    for origin in origins:
        if not origin:
            raise ValueError("CORS allowlist contains an empty origin")
        if "*" in origin:
            raise WildcardOriginError(
                f"wildcard origin {origin!r} is not allowed; the CORS allowlist must be explicit"
            )
    return {
        "allow_origins": list(origins),
        "allow_credentials": allow_credentials,
        "allow_methods": list(CORS_ALLOW_METHODS),
        "allow_headers": list(CORS_ALLOW_HEADERS),
    }


class SecurityHeadersMiddleware:
    """ASGI middleware adding application-layer safe headers to HTTP responses.

    Only absent headers are set, so an upstream component (route handler,
    proxy, or a later edge layer) is never overridden.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in SECURITY_HEADERS.items():
                    if name not in headers:
                        headers[name] = value
            await send(message)

        await self.app(scope, receive, send_with_headers)


def add_security_middleware(
    app: FastAPI,
    settings: Settings,
    *,
    allow_credentials: bool = False,
) -> None:
    """Mount CORS and security-header middleware on *app*.

    Idempotent: a marker on ``app.state`` makes repeated calls a no-op.
    """
    if getattr(app.state, _MOUNTED_FLAG, False):
        return
    app.add_middleware(
        CORSMiddleware,
        **build_cors_config(
            settings.allowed_origins,
            allow_credentials=allow_credentials,
        ),
    )
    app.add_middleware(SecurityHeadersMiddleware)
    setattr(app.state, _MOUNTED_FLAG, True)
