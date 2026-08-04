"""CORS and security-header tests.

Verify that the CORS allowlist is explicit and driven by
``Settings.allowed_origins``, wildcard origins are rejected, credentials
default off, only the configured methods and headers are allowed, and
the application layer emits only the safe headers it can own — never the
edge (Nginx) header set.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from app.config import REQUIRED_ENV_VARS, Settings
from app.main import create_app
from app.security import (
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    SECURITY_HEADERS,
    SecurityHeadersMiddleware,
    WildcardOriginError,
    add_security_middleware,
    build_cors_config,
)

CI_ALLOWED_ORIGIN = "http://localhost:3000"
DISALLOWED_ORIGIN = "http://evil.example"


def _settings(*, origins: str = CI_ALLOWED_ORIGIN) -> Settings:
    env = {name: "test" for name in REQUIRED_ENV_VARS}
    env["ALLOWED_ORIGINS"] = origins
    return Settings.from_env(env)


def _client(*, settings: Settings, allow_credentials: bool = False) -> TestClient:
    app = FastAPI()
    add_security_middleware(app, settings, allow_credentials=allow_credentials)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"ok": "yes"}

    return TestClient(app)


# --- explicit allowlist behavior: allowed echoes, disallowed stays silent ---


def test_simple_request_from_allowed_origin_echoes_origin() -> None:
    client = _client(settings=_settings())
    response = client.get("/ping", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN


def test_simple_request_from_disallowed_origin_has_no_cors_headers() -> None:
    client = _client(settings=_settings())
    response = client.get("/ping", headers={"Origin": DISALLOWED_ORIGIN})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_simple_request_without_origin_has_no_cors_headers() -> None:
    client = _client(settings=_settings())
    response = client.get("/ping")
    assert "access-control-allow-origin" not in response.headers


def test_preflight_from_allowed_origin_echoes_origin() -> None:
    client = _client(settings=_settings())
    response = client.options(
        "/ping",
        headers={
            "Origin": CI_ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN


def test_preflight_from_disallowed_origin_has_no_allow_origin() -> None:
    client = _client(settings=_settings())
    response = client.options(
        "/ping",
        headers={
            "Origin": DISALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers


def test_multiple_allowed_origins_all_echo() -> None:
    settings = _settings(origins="http://localhost:3000,http://app.example")
    client = _client(settings=settings)
    for origin in ("http://localhost:3000", "http://app.example"):
        response = client.get("/ping", headers={"Origin": origin})
        assert response.headers["access-control-allow-origin"] == origin


def test_cors_header_is_never_a_wildcard() -> None:
    client = _client(settings=_settings())
    for method in ("get", "options"):
        for origin in (CI_ALLOWED_ORIGIN, DISALLOWED_ORIGIN):
            headers = {"Origin": origin}
            if method == "options":
                headers["Access-Control-Request-Method"] = "POST"
            response = client.request(method, "/ping", headers=headers)
            echoed = response.headers.get("access-control-allow-origin")
            assert echoed in (None, origin)
            assert echoed != "*"


# --- methods, headers, and credentials policy ---


def test_preflight_advertises_configured_methods() -> None:
    client = _client(settings=_settings())
    response = client.options(
        "/ping",
        headers={
            "Origin": CI_ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    allowed = response.headers["access-control-allow-methods"]
    for method in CORS_ALLOW_METHODS:
        assert method in allowed


def test_preflight_advertises_configured_headers_when_requested() -> None:
    client = _client(settings=_settings())
    response = client.options(
        "/ping",
        headers={
            "Origin": CI_ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type, authorization",
        },
    )
    allowed = response.headers["access-control-allow-headers"]
    for header in CORS_ALLOW_HEADERS:
        assert header in allowed


def test_preflight_permits_request_id_correlation_header() -> None:
    client = _client(settings=_settings())
    response = client.options(
        "/ping",
        headers={
            "Origin": CI_ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-request-id",
        },
    )
    assert response.status_code == 200
    assert "x-request-id" in response.headers["access-control-allow-headers"].lower()


def test_credentials_header_absent_by_default() -> None:
    client = _client(settings=_settings())
    response = client.get("/ping", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert "access-control-allow-credentials" not in response.headers


def test_credentials_header_only_with_explicit_origins() -> None:
    client = _client(settings=_settings(), allow_credentials=True)
    response = client.get("/ping", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert response.headers["access-control-allow-credentials"] == "true"
    # Credentials may only pair with the exact origin echo — never "*".
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN


# --- config builder: explicit allowlist only, no wildcard credentials ---


def test_build_cors_config_uses_explicit_origins() -> None:
    config = build_cors_config(("http://a.test", "http://b.test"))
    assert config["allow_origins"] == ["http://a.test", "http://b.test"]
    assert config["allow_credentials"] is False
    assert config["allow_methods"] == ["GET", "POST", "OPTIONS"]
    assert config["allow_headers"] == [
        "Content-Type",
        "Authorization",
        "X-Request-ID",
    ]


def test_build_cors_config_rejects_wildcard_origin() -> None:
    with pytest.raises(WildcardOriginError):
        build_cors_config(("*",))
    with pytest.raises(WildcardOriginError):
        build_cors_config(("https://*.example.com",))
    with pytest.raises(WildcardOriginError):
        build_cors_config(("http://a.test", "*"))


def test_build_cors_config_rejects_empty_allowlist() -> None:
    with pytest.raises(ValueError, match="at least one origin"):
        build_cors_config(())
    with pytest.raises(ValueError, match="empty origin"):
        build_cors_config(("http://a.test", ""))


def test_build_cors_config_credentials_never_pair_with_wildcard() -> None:
    config = build_cors_config((CI_ALLOWED_ORIGIN,), allow_credentials=True)
    assert config["allow_credentials"] is True
    assert "*" not in config["allow_origins"]


# --- application-layer security headers ---


def test_security_headers_present_on_success_response() -> None:
    client = _client(settings=_settings())
    response = client.get("/ping")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_security_headers_present_on_error_response() -> None:
    client = _client(settings=_settings())
    response = client.get("/no-such-path")
    assert response.status_code == 404
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_security_headers_present_on_preflight_response() -> None:
    client = _client(settings=_settings())
    response = client.options(
        "/ping",
        headers={
            "Origin": CI_ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_security_headers_do_not_override_existing_values() -> None:
    app = FastAPI()

    @app.get("/custom")
    def custom() -> dict[str, str]:
        return {"ok": "yes"}

    @app.middleware("http")
    async def set_frame_options(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    add_security_middleware(app, _settings())
    response = TestClient(app).get("/custom")
    assert response.headers["x-frame-options"] == "SAMEORIGIN"


def test_secure_header_set_is_exactly_the_application_layer_set() -> None:
    assert dict(SECURITY_HEADERS) == {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }


def test_hsts_is_not_claimed_by_app_middleware() -> None:
    # HSTS and the rest of the edge header set are Nginx responsibilities
    # The app must not claim edge-layer headers.
    assert "Strict-Transport-Security" not in SECURITY_HEADERS
    client = _client(settings=_settings())
    response = client.get("/ping")
    assert "strict-transport-security" not in response.headers


# --- seam: add_security_middleware is idempotent and settings-driven ---


def test_add_security_middleware_is_idempotent() -> None:
    app = FastAPI()
    settings = _settings()
    add_security_middleware(app, settings)
    add_security_middleware(app, settings)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"ok": "yes"}

    response = TestClient(app).get("/ping", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN
    assert response.headers["x-content-type-options"] == "nosniff"


def test_seam_is_driven_by_settings_allowed_origins() -> None:
    settings = _settings(origins=DISALLOWED_ORIGIN)
    client = _client(settings=settings)
    response = client.get("/ping", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert "access-control-allow-origin" not in response.headers
    response = client.get("/ping", headers={"Origin": DISALLOWED_ORIGIN})
    assert response.headers["access-control-allow-origin"] == DISALLOWED_ORIGIN


# --- factory integration mounts CORS and security headers ---


def test_factory_echoes_allowed_origin_on_simple_request() -> None:
    client = TestClient(create_app())
    response = client.get("/health", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN


def test_factory_does_not_echo_disallowed_origin() -> None:
    client = TestClient(create_app())
    response = client.get("/health", headers={"Origin": DISALLOWED_ORIGIN})
    assert "access-control-allow-origin" not in response.headers


def test_factory_answers_preflight_from_allowed_origin() -> None:
    client = TestClient(create_app())
    response = client.options(
        "/health",
        headers={
            "Origin": CI_ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN
    assert "POST" in response.headers["access-control-allow-methods"]


def test_factory_mounts_application_security_headers() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_factory_security_headers_present_on_error_response() -> None:
    client = TestClient(create_app())
    response = client.get("/no-such-path")
    assert response.status_code == 404
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_factory_mount_keeps_credentials_off() -> None:
    # Factory integration: explicit-origin echo only, no credentials
    # header, never "*".
    client = TestClient(create_app())
    response = client.get("/health", headers={"Origin": CI_ALLOWED_ORIGIN})
    assert response.headers["access-control-allow-origin"] == CI_ALLOWED_ORIGIN
    assert "access-control-allow-credentials" not in response.headers


# --- non-HTTP ASGI scopes pass through unchanged ---


def test_security_headers_middleware_passes_through_non_http_scopes() -> None:
    seen: list[str] = []

    async def downstream(scope: Scope, receive: Receive, send: Send) -> None:
        seen.append(str(scope["type"]))

    async def receive() -> Message:
        return {"type": "http.request"}

    async def send(message: Message) -> None:
        del message

    async def run() -> None:
        middleware = SecurityHeadersMiddleware(downstream)
        await middleware({"type": "websocket"}, receive, send)

    asyncio.run(run())
    assert seen == ["websocket"]
