"""Request and correlation ID middleware.

The application factory mounts this module through
``add_request_id_middleware(app)``. It requires no settings and composes
anywhere in the middleware stack.

Semantics (standard UUID/correlation behavior):

* Every HTTP response carries ``X-Request-ID`` whose value is a canonical
  UUIDv4 string.
* A valid inbound ``X-Request-ID`` is preserved (normalized to canonical
  lowercase form). An absent, empty, malformed, or oversized inbound value
  is rejected and replaced with a fresh UUIDv4 — attacker-controlled header
  values are never echoed.
* The resolved value is stored on ``request.state.request_id`` and exposed
  to handlers through the ``get_request_id`` dependency.
* Nothing is logged here: the request id is an opaque, safe identifier that
  callers may log; request contents are never logged or stored.
"""

from __future__ import annotations

import uuid
from typing import Final

from fastapi import FastAPI, Request
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER: Final = "X-Request-ID"
"""Response header and accepted inbound header name (canonical form)."""

_REQUEST_STATE_KEY: Final = "request_id"
MAX_REQUEST_ID_LENGTH: Final = 64
"""Upper bound on accepted inbound values; longer values are rejected."""

_MOUNTED_FLAG = "_papyr_request_id_mounted"


def normalize_request_id(raw: str | None) -> str:
    """Return the canonical request id for *raw*: valid UUID in, fresh UUID4 out.

    None, empty/whitespace-only strings, values longer than
    ``MAX_REQUEST_ID_LENGTH``, and anything that is not a UUID are rejected;
    a fresh UUID4 is generated instead. Valid UUIDs are returned in
    canonical lowercase form via ``str(uuid.UUID(...))``.
    """
    if raw is not None:
        candidate = raw.strip()
        if 0 < len(candidate) <= MAX_REQUEST_ID_LENGTH:
            try:
                return str(uuid.UUID(candidate))
            except ValueError:
                pass
    return str(uuid.uuid4())


def _header_value(scope: Scope, name: str) -> str | None:
    raw_name = name.encode("latin-1").lower()
    for key, value in scope.get("headers", ()):
        if not isinstance(key, bytes) or not isinstance(value, bytes):
            continue
        if key.lower() == raw_name:
            return value.decode("latin-1")
    return None


class RequestIDMiddleware:
    """ASGI middleware resolving and propagating a request/correlation ID.

    The resolved id is stored on ``scope["state"]["request_id"]`` (visible
    as ``request.state.request_id``) and echoed on every response's
    ``X-Request-ID`` header. The header is only set when absent, so an
    upstream component is never overridden.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = normalize_request_id(_header_value(scope, REQUEST_ID_HEADER))
        scope.setdefault("state", {})[_REQUEST_STATE_KEY] = request_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                if REQUEST_ID_HEADER not in headers:
                    headers[REQUEST_ID_HEADER] = request_id
            await send(message)

        await self.app(scope, receive, send_with_request_id)


def resolve_request_id(request: Request) -> str:
    """The request id for *request*: middleware value, else header, else fresh.

    Handlers may call this directly; it degrades gracefully when the
    middleware is absent from the stack, so error handlers stay composable.
    """
    stored = getattr(request.state, _REQUEST_STATE_KEY, None)
    if isinstance(stored, str) and stored:
        return stored
    return normalize_request_id(request.headers.get(REQUEST_ID_HEADER))


def get_request_id(request: Request) -> str:
    """FastAPI dependency exposing the current request id to route handlers.

    Usage: ``request_id: str = Depends(get_request_id)``. The value is an
    opaque UUIDv4 — safe to log and safe to return in API payloads.
    """
    return resolve_request_id(request)


def add_request_id_middleware(app: FastAPI) -> None:
    """Mount :class:`RequestIDMiddleware` on *app*.

    Idempotent: a marker on ``app.state`` makes repeated calls a no-op.
    """
    if getattr(app.state, _MOUNTED_FLAG, False):
        return
    app.add_middleware(RequestIDMiddleware)
    setattr(app.state, _MOUNTED_FLAG, True)
