"""Stable machine-readable error envelope and handlers.

Every error response uses a unified envelope with stable error fields and a
request ID. ``message`` is a non-sensitive developer-facing fallback, while
``messageKey`` is resolved at the presentation layer. Validation errors may
also include ``details`` containing sanitized field locations only — never
submitted values.

Fail-closed normalization: the handlers derive everything from status codes
and error types; exception messages, ``HTTPException.detail``, Pydantic
``input`` values, stack traces, filenames, passwords, signed URLs, and
object keys are never rendered. The taxonomy (codes, categories) is
intentionally limited until concrete processing endpoints define their
closed error-code vocabulary.

Unexpected errors are logged server-side with only the exception class name
and the request id — never the message, payload, or traceback — keeping
server logs free of sensitive values.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware import REQUEST_ID_HEADER, resolve_request_id

logger = logging.getLogger(__name__)

HTTP_CLIENT_ERROR_MIN: Final = 400
HTTP_CLIENT_ERROR_MAX: Final = 499
HTTP_INTERNAL_ERROR: Final = 500

_MOUNTED_FLAG = "_papyr_error_handlers_mounted"


class ErrorCategory(StrEnum):
    """Category vocabulary for the public error envelope."""

    VALIDATION = "validation"
    AUTH = "auth"
    THREAT = "threat"
    SYSTEM = "system"
    RATE_LIMIT = "rate_limit"
    NOT_FOUND = "not_found"
    ENGINE = "engine"


@dataclass(frozen=True)
class HttpErrorSpec:
    """Envelope fields derived deterministically from an HTTP status code."""

    code: str
    category: str
    message: str
    message_key: str
    retryable: bool


_STATUS_SPECS: Mapping[int, HttpErrorSpec] = {
    400: HttpErrorSpec(
        code="bad_request",
        category=ErrorCategory.VALIDATION.value,
        message="Bad request",
        message_key="error.badRequest",
        retryable=False,
    ),
    401: HttpErrorSpec(
        code="unauthorized",
        category=ErrorCategory.AUTH.value,
        message="Authentication required",
        message_key="error.unauthorized",
        retryable=False,
    ),
    403: HttpErrorSpec(
        code="forbidden",
        category=ErrorCategory.AUTH.value,
        message="Forbidden",
        message_key="error.forbidden",
        retryable=False,
    ),
    404: HttpErrorSpec(
        code="not_found",
        category=ErrorCategory.NOT_FOUND.value,
        message="Not found",
        message_key="error.notFound",
        retryable=False,
    ),
    405: HttpErrorSpec(
        code="method_not_allowed",
        category=ErrorCategory.VALIDATION.value,
        message="Method not allowed",
        message_key="error.methodNotAllowed",
        retryable=False,
    ),
    409: HttpErrorSpec(
        code="conflict",
        category=ErrorCategory.VALIDATION.value,
        message="Conflict",
        message_key="error.conflict",
        retryable=False,
    ),
    413: HttpErrorSpec(
        code="payload_too_large",
        category=ErrorCategory.VALIDATION.value,
        message="Payload too large",
        message_key="error.payloadTooLarge",
        retryable=False,
    ),
    415: HttpErrorSpec(
        code="unsupported_media_type",
        category=ErrorCategory.VALIDATION.value,
        message="Unsupported media type",
        message_key="error.unsupportedMediaType",
        retryable=False,
    ),
    422: HttpErrorSpec(
        code="unprocessable_entity",
        category=ErrorCategory.VALIDATION.value,
        message="Unprocessable entity",
        message_key="error.unprocessableEntity",
        retryable=False,
    ),
    429: HttpErrorSpec(
        code="rate_limited",
        category=ErrorCategory.RATE_LIMIT.value,
        message="Too many requests",
        message_key="error.rateLimited",
        retryable=True,
    ),
}

_VALIDATION_SPEC = HttpErrorSpec(
    code="invalid_request",
    category=ErrorCategory.VALIDATION.value,
    message="Invalid request",
    message_key="error.invalidRequest",
    retryable=False,
)


def spec_for_status(status: int) -> HttpErrorSpec:
    """Envelope spec for *status*: known table first, then deterministic fallbacks.

    Unknown 4xx statuses normalize to ``client_error``/validation; every
    other unknown status (5xx) normalizes to ``internal_error``/system.
    """
    known = _STATUS_SPECS.get(status)
    if known is not None:
        return known
    if HTTP_CLIENT_ERROR_MIN <= status <= HTTP_CLIENT_ERROR_MAX:
        return HttpErrorSpec(
            code="client_error",
            category=ErrorCategory.VALIDATION.value,
            message="Client error",
            message_key="error.clientError",
            retryable=False,
        )
    return HttpErrorSpec(
        code="internal_error",
        category=ErrorCategory.SYSTEM.value,
        message="Internal server error",
        message_key="error.internalError",
        retryable=False,
    )


def build_error_envelope(
    spec: HttpErrorSpec,
    *,
    request_id: str,
    details: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Build the stable error envelope; *details* are optional safe context only."""
    error: dict[str, object] = {
        "code": spec.code,
        "category": spec.category,
        "message": spec.message,
        "messageKey": spec.message_key,
        "retryable": spec.retryable,
    }
    if details:
        error["details"] = [dict(item) for item in details]
    return {"error": error, "request_id": request_id}


def _sanitized_validation_details(
    errors: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Field locations and error types only — never ``msg`` or ``input``.

    Pydantic messages and input values can echo submitted payloads (e.g.
    passwords, filenames); both are deliberately excluded (ARCH:696).
    """
    details: list[dict[str, object]] = []
    for error in errors:
        raw_loc = error.get("loc", ())
        loc_parts = raw_loc if isinstance(raw_loc, tuple) else ()
        details.append(
            {
                "loc": [str(part) for part in loc_parts],
                "type": str(error.get("type", "")),
            }
        )
    return details


async def request_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    """Normalize request-shape validation failures to the stable 422 envelope.

    The ``isinstance`` guard is unreachable in practice — FastAPI dispatches
    ``RequestValidationError`` by exact class — and exists to satisfy the
    ``ExceptionHandler`` callable type (``exc: Exception``) while keeping
    precise typing inside the body.
    """
    if not isinstance(exc, RequestValidationError):
        raise TypeError(f"expected RequestValidationError, got {type(exc).__name__}")
    request_id = resolve_request_id(request)
    envelope = build_error_envelope(
        _VALIDATION_SPEC,
        request_id=request_id,
        details=_sanitized_validation_details(exc.errors()),
    )
    return JSONResponse(status_code=422, content=envelope, headers={REQUEST_ID_HEADER: request_id})


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Normalize HTTP errors by status code; ``exc.detail`` is never rendered.

    The ``isinstance`` guard is unreachable in practice — FastAPI dispatches
    ``HTTPException`` by class — and exists to satisfy the
    ``ExceptionHandler`` callable type while keeping precise typing inside
    the body.
    """
    if not isinstance(exc, StarletteHTTPException):
        raise TypeError(f"expected HTTPException, got {type(exc).__name__}")
    spec = spec_for_status(exc.status_code)
    request_id = resolve_request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_envelope(spec, request_id=request_id),
        headers={REQUEST_ID_HEADER: request_id},
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fail-closed 500 envelope: generic message, class name logged server-side.

    ``ServerErrorMiddleware`` runs outside the user middleware stack, so
    this handler sets the request-id header itself; the response never
    carries the exception message, payload, or traceback.
    """
    request_id = resolve_request_id(request)
    logger.error(
        "unhandled exception type=%s request_id=%s",
        type(exc).__name__,
        request_id,
    )
    return JSONResponse(
        status_code=HTTP_INTERNAL_ERROR,
        content=build_error_envelope(spec_for_status(HTTP_INTERNAL_ERROR), request_id=request_id),
        headers={REQUEST_ID_HEADER: request_id},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Mount the stable envelope handlers on *app*.

    Idempotent: a marker on ``app.state`` makes repeated calls a no-op.
    ``Exception`` is routed to Starlette's ``ServerErrorMiddleware``; the
    other handlers run inside the user middleware stack.
    """
    if getattr(app.state, _MOUNTED_FLAG, False):
        return
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    # FastAPI 0.129+ defines fastapi.exceptions.HTTPException as a distinct
    # subclass of starlette's; router-generated 404/405 raise the starlette
    # class while routes raise the fastapi one. Registering both keeps the
    # envelope on every HTTP error under the CI pin (0.123.5, same class
    # aliased twice — the second registration simply overwrites) and under
    # newer FastAPI (both classes handled).
    app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)
    setattr(app.state, _MOUNTED_FLAG, True)
