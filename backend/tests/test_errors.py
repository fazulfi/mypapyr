"""Request-ID and machine-readable error contract tests.

Verify the public error contract:

* Every HTTP response carries an ``X-Request-ID`` header whose value is a
  canonical UUID: preserved when the inbound header is a valid UUID,
  normalized to canonical lowercase form, and generated fresh when the
  inbound header is absent or unsafe (never echoed).
* Error responses use the stable machine-readable envelope
  ``{"error": {code, category, message, messageKey, retryable}, "request_id"}``
  for validation (422), HTTP (4xx/5xx), and unexpected (500) failures.
* The envelope leaks nothing: no stack traces, exception text, submitted
  values, filenames, passwords, signed URLs, or object keys.
* The request-ID and error-handler seams compose independently, and the
  ``create_app()`` factory mounts both (idempotent).
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Mapping

import pytest
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.types import Message, Receive, Scope, Send

from app.errors import (
    HttpErrorSpec,
    build_error_envelope,
    http_exception_handler,
    register_error_handlers,
    request_validation_handler,
    spec_for_status,
)
from app.main import app, create_app
from app.middleware import (
    REQUEST_ID_HEADER,
    RequestIDMiddleware,
    _header_value,
    add_request_id_middleware,
    get_request_id,
    normalize_request_id,
)

#: The five keys every public error envelope carries.
BASE_ERROR_KEYS = frozenset({"code", "category", "message", "messageKey", "retryable"})
#: Validation errors additionally carry sanitized field locations only.
VALIDATION_ERROR_KEYS = BASE_ERROR_KEYS | frozenset({"details"})


class ProbePayload(BaseModel):
    value: int


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True


def _probe_app() -> FastAPI:
    """Compose both seams plus probe routes on a fresh instance."""
    instance = FastAPI()
    register_error_handlers(instance)
    add_request_id_middleware(instance)

    @instance.post("/probe")
    async def probe(payload: ProbePayload) -> dict[str, int]:
        return {"value": payload.value}

    @instance.get("/echo-id")
    async def echo_id(request_id: str = Depends(get_request_id)) -> dict[str, str]:
        return {"request_id": request_id}

    @instance.get("/client-error")
    async def client_error() -> None:
        raise HTTPException(status_code=400, detail="secret filename.pdf")

    @instance.get("/rate-limited")
    async def rate_limited() -> None:
        raise HTTPException(status_code=429, detail="slow down")

    @instance.get("/server-http-error")
    async def server_http_error() -> None:
        raise HTTPException(status_code=500, detail="secret boom")

    @instance.get("/unexpected")
    async def unexpected() -> None:
        raise RuntimeError("secret-internal-token")

    return instance


def _envelope_keys(body: Mapping[str, object]) -> set[str]:
    error = body["error"]
    assert isinstance(error, Mapping)
    return set(error)


# --- request/correlation ID: generated, preserved, normalized ---


def test_response_without_inbound_id_gets_generated_uuid4() -> None:
    response = TestClient(_probe_app()).get("/echo-id")
    assert _is_uuid(response.headers["x-request-id"])


def test_request_ids_differ_across_requests() -> None:
    client = TestClient(_probe_app())
    first = client.get("/echo-id").headers["x-request-id"]
    second = client.get("/echo-id").headers["x-request-id"]
    assert first != second


def test_response_with_valid_inbound_id_preserves_it() -> None:
    inbound = str(uuid.uuid4())
    client = TestClient(_probe_app())
    response = client.get("/echo-id", headers={REQUEST_ID_HEADER: inbound})
    assert response.headers["x-request-id"] == inbound


def test_response_with_uppercase_inbound_id_is_canonicalized() -> None:
    inbound = str(uuid.uuid4()).upper()
    client = TestClient(_probe_app())
    response = client.get("/echo-id", headers={REQUEST_ID_HEADER: inbound})
    assert response.headers["x-request-id"] == inbound.lower()


def test_unsafe_inbound_ids_are_rejected_with_fresh_uuid() -> None:
    for bad in ("not-a-uuid", "<script>alert(1)</script>", "a" * 300, "  "):
        client = TestClient(_probe_app())
        response = client.get("/echo-id", headers={REQUEST_ID_HEADER: bad})
        generated = response.headers["x-request-id"]
        assert _is_uuid(generated)
        assert generated != bad


def test_request_id_header_present_on_not_found_response() -> None:
    response = TestClient(_probe_app()).get("/no-such-path")
    assert response.status_code == 404
    assert _is_uuid(response.headers["x-request-id"])


def test_get_request_id_dependency_sees_middleware_value() -> None:
    inbound = str(uuid.uuid4())
    client = TestClient(_probe_app())
    response = client.get("/echo-id", headers={REQUEST_ID_HEADER: inbound})
    assert response.json() == {"request_id": inbound}
    assert response.headers["x-request-id"] == inbound


def test_normalize_request_id_generates_fresh_uuid_for_absent_or_empty() -> None:
    assert _is_uuid(normalize_request_id(None))
    assert _is_uuid(normalize_request_id(""))


def test_normalize_request_id_preserves_valid_uuid() -> None:
    raw = str(uuid.uuid4())
    assert normalize_request_id(raw) == raw


def test_normalize_request_id_canonicalizes_uppercase() -> None:
    raw = str(uuid.uuid4()).upper()
    assert normalize_request_id(raw) == raw.lower()


def test_normalize_request_id_rejects_non_uuid_values() -> None:
    for bad in ("not-a-uuid", "..", "<script>", "a" * 200, " "):
        generated = normalize_request_id(bad)
        assert _is_uuid(generated)
        assert generated != bad


def test_header_value_skips_non_bytes_entries() -> None:
    scope: dict[str, object] = {
        "headers": [
            (b"x-request-id", "not-bytes"),
            (b"x-request-id", b"11111111-1111-1111-1111-111111111111"),
        ],
    }
    assert _header_value(scope, "X-Request-ID") == "11111111-1111-1111-1111-111111111111"


def test_request_id_middleware_passes_through_non_http_scopes() -> None:
    seen: list[str] = []

    async def downstream(scope: Scope, receive: Receive, send: Send) -> None:
        seen.append(str(scope["type"]))

    async def receive() -> Message:
        return {"type": "http.request"}

    async def send(message: Message) -> None:
        del message

    async def run() -> None:
        middleware = RequestIDMiddleware(downstream)
        await middleware({"type": "websocket"}, receive, send)

    asyncio.run(run())
    assert seen == ["websocket"]


def _bare_request() -> Request:
    scope: dict[str, object] = {
        "type": "http",
        "method": "POST",
        "path": "/probe",
        "headers": [],
    }
    return Request(scope)


def test_validation_handler_fails_closed_on_wrong_exc_type() -> None:
    with pytest.raises(TypeError, match="RequestValidationError"):
        asyncio.run(request_validation_handler(_bare_request(), ValueError("wrong")))


def test_http_handler_fails_closed_on_wrong_exc_type() -> None:
    with pytest.raises(TypeError, match="HTTPException"):
        asyncio.run(http_exception_handler(_bare_request(), ValueError("wrong")))


# --- stable error envelope: validation (422) ---


def test_validation_error_returns_stable_envelope() -> None:
    response = TestClient(_probe_app()).post("/probe", json={"value": "s3cret-value-x"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "invalid_request"
    assert error["category"] == "validation"
    assert error["message"] == "Invalid request"
    assert error["messageKey"] == "error.invalidRequest"
    assert error["retryable"] is False


def test_validation_error_adds_only_sanitized_details() -> None:
    response = TestClient(_probe_app()).post("/probe", json={"value": "s3cret-value-x"})
    body = response.json()
    assert _envelope_keys(body) == VALIDATION_ERROR_KEYS
    details = body["error"]["details"]
    assert {"loc": ["body", "value"], "type": "int_parsing"} in details
    assert all(set(item) == {"loc", "type"} for item in details)


def test_validation_error_never_echoes_submitted_values() -> None:
    response = TestClient(_probe_app()).post("/probe", json={"value": "s3cret-value-x"})
    assert "s3cret-value-x" not in response.text
    assert "Traceback" not in response.text


def test_validation_error_via_query_parameter() -> None:
    instance = FastAPI()
    register_error_handlers(instance)

    @instance.get("/query-probe")
    async def query_probe(count: int) -> dict[str, int]:
        return {"count": count}

    response = TestClient(instance).get("/query-probe?count=abc")
    assert response.status_code == 422
    assert {"loc": ["query", "count"], "type": "int_parsing"} in response.json()["error"]["details"]


# --- stable error envelope: HTTP errors ---


def test_not_found_returns_stable_envelope() -> None:
    response = TestClient(_probe_app()).get("/no-such-path")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert error["category"] == "not_found"
    assert error["retryable"] is False


def test_method_not_allowed_returns_stable_envelope() -> None:
    response = TestClient(_probe_app()).post("/echo-id")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_http_exception_detail_is_never_echoed() -> None:
    response = TestClient(_probe_app()).get("/client-error")
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "bad_request"
    assert error["category"] == "validation"
    assert "filename.pdf" not in response.text
    assert "secret" not in response.text


def test_rate_limited_is_marked_retryable() -> None:
    response = TestClient(_probe_app()).get("/rate-limited")
    assert response.status_code == 429
    error = response.json()["error"]
    assert error["code"] == "rate_limited"
    assert error["category"] == "rate_limit"
    assert error["retryable"] is True


def test_http_500_exception_uses_generic_envelope() -> None:
    client = TestClient(_probe_app(), raise_server_exceptions=False)
    response = client.get("/server-http-error")
    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "internal_error"
    assert error["category"] == "system"
    assert error["message"] == "Internal server error"
    assert "boom" not in response.text


# --- stable error envelope: unexpected errors (500) ---


def test_unexpected_error_returns_stable_envelope() -> None:
    client = TestClient(_probe_app(), raise_server_exceptions=False)
    response = client.get("/unexpected")
    assert response.status_code == 500
    assert response.json()["error"] == {
        "code": "internal_error",
        "category": "system",
        "message": "Internal server error",
        "messageKey": "error.internalError",
        "retryable": False,
    }


def test_unexpected_error_leaks_nothing() -> None:
    client = TestClient(_probe_app(), raise_server_exceptions=False)
    response = client.get("/unexpected")
    body = response.text
    assert "secret-internal-token" not in body
    assert "RuntimeError" not in body
    assert "Traceback" not in body
    assert ".py" not in body


# --- correlation: request_id in body matches response header ---


def test_error_envelope_request_id_matches_response_header() -> None:
    client = TestClient(_probe_app())
    response = client.post("/probe", json={"value": "s3cret-value-x"})
    assert response.status_code == 422
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_unexpected_error_carries_request_id_in_header_and_body() -> None:
    client = TestClient(_probe_app(), raise_server_exceptions=False)
    response = client.get("/unexpected")
    assert _is_uuid(response.headers["x-request-id"])
    assert response.json()["request_id"] == response.headers["x-request-id"]


# --- envelope shape invariants ---


def test_build_error_envelope_locks_document_shape() -> None:
    envelope = build_error_envelope(
        HttpErrorSpec(
            code="not_found",
            category="not_found",
            message="Not found",
            message_key="error.notFound",
            retryable=False,
        ),
        request_id="req-1",
    )
    assert envelope == {
        "error": {
            "code": "not_found",
            "category": "not_found",
            "message": "Not found",
            "messageKey": "error.notFound",
            "retryable": False,
        },
        "request_id": "req-1",
    }


def test_error_envelope_top_level_keys_are_locked() -> None:
    response = TestClient(_probe_app()).get("/client-error")
    assert set(response.json()) == {"error", "request_id"}


def test_http_error_envelope_keys_are_locked() -> None:
    response = TestClient(_probe_app()).get("/client-error")
    assert _envelope_keys(response.json()) == BASE_ERROR_KEYS


def test_spec_for_status_known_mapping() -> None:
    assert spec_for_status(404).code == "not_found"
    assert spec_for_status(404).category == "not_found"
    assert spec_for_status(404).retryable is False
    assert spec_for_status(429).code == "rate_limited"
    assert spec_for_status(429).retryable is True


def test_spec_for_status_unknown_client_and_server_codes() -> None:
    assert spec_for_status(418).code == "client_error"
    assert spec_for_status(418).category == "validation"
    assert spec_for_status(503).code == "internal_error"
    assert spec_for_status(503).category == "system"
    assert spec_for_status(503).retryable is False


# --- composability: seams work standalone, idempotently, without settings ---


def test_request_id_middleware_composes_without_error_handlers() -> None:
    instance = FastAPI()
    add_request_id_middleware(instance)
    response = TestClient(instance).get("/no-such-path")
    assert response.status_code == 404
    assert _is_uuid(response.headers["x-request-id"])


def test_error_handlers_compose_without_middleware() -> None:
    instance = FastAPI()
    register_error_handlers(instance)

    @instance.get("/client-error")
    def client_error() -> None:
        raise HTTPException(status_code=400, detail="secret filename.pdf")

    response = TestClient(instance).get("/client-error")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"
    assert "filename.pdf" not in response.text


def test_register_error_handlers_is_idempotent() -> None:
    instance = FastAPI()
    register_error_handlers(instance)
    register_error_handlers(instance)

    @instance.get("/boom")
    def boom() -> None:
        raise RuntimeError("secret-internal-token")

    client = TestClient(instance, raise_server_exceptions=False)
    assert client.get("/boom").json()["error"]["code"] == "internal_error"


def test_add_request_id_middleware_is_idempotent() -> None:
    instance = FastAPI()
    add_request_id_middleware(instance)
    add_request_id_middleware(instance)
    response = TestClient(instance).get("/no-such-path")
    assert _is_uuid(response.headers["x-request-id"])


# --- factory integration mounts both seams ---


def test_module_level_app_mounts_error_and_request_id_seams() -> None:
    client = TestClient(app)
    ok = client.get("/health")
    assert ok.status_code == 200
    assert ok.json() == {"status": "ok"}
    assert _is_uuid(ok.headers["x-request-id"])
    missing = client.get("/no-such-path")
    assert missing.status_code == 404
    body = missing.json()
    assert body["error"]["code"] == "not_found"
    assert body["request_id"] == missing.headers["x-request-id"]


def test_factory_instance_mounts_u4_seams() -> None:
    client = TestClient(create_app())
    response = client.get("/no-such-path")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert _is_uuid(response.headers["x-request-id"])


def test_success_responses_keep_normal_shape() -> None:
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
