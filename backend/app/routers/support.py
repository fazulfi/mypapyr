"""PT-03 Support contact endpoint: POST /api/v1/support/contact.

Validates JSON submissions server-side, silently accepts honeypot spam,
rate-limits per origin, soft-gates on Turnstile, and returns 202
immediately — email delivery runs in a FastAPI background task so a slow
Cloudflare Email Sending provider never blocks the confirmation. Errors
use the stable envelope (``support.invalidRequest`` / ``error.rateLimited``)
and never echo user content.
"""

from __future__ import annotations

import logging
from typing import cast

import httpx
from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.config import Settings, load
from app.errors import HttpErrorSpec, build_error_envelope
from app.middleware import REQUEST_ID_HEADER, resolve_request_id
from app.services.contact_service import (
    EMAIL_SENDING_URL,
    TURNSTILE_VERIFY_URL,
    ContactAccepted,
    ContactMetrics,
    ContactSubmission,
    EmailPayload,
    EmailSender,
    OriginRateLimiter,
    TurnstileVerifier,
    build_email_payload,
    deliver_contact_email,
    email_payload_to_dict,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/support", tags=["support"])

# Module-level defaults: per-process limiter/metrics. Routers prefer
# app.state presets (injected in tests); these are the production fallbacks.
_DEFAULT_LIMITER = OriginRateLimiter()
_DEFAULT_METRICS = ContactMetrics()

_INVALID_REQUEST_KEY = "support.invalidRequest"
_RATE_LIMITED_KEY = "error.rateLimited"


class ContactValidationError(HTTPException):
    """400 raised for invalid contact payloads.

    A dedicated ``HTTPException`` subclass so the app-level exception
    registry (``create_app``) can map precisely this error to the
    ``support.invalidRequest`` messageKey while every other 400 keeps the
    locked global envelope. ``detail`` carries the key only — no user
    content.
    """

    def __init__(self) -> None:
        super().__init__(status_code=400, detail={"messageKey": _INVALID_REQUEST_KEY})


async def contact_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    """Render the 400 envelope with the ``support.invalidRequest`` messageKey.

    Registered in ``create_app`` for the exact ``ContactValidationError``
    class; mirrors ``errors.http_exception_handler`` but carries the
    PT-03-specific message key. Never echoes submitted content.
    """
    spec = HttpErrorSpec(
        code="invalid_request",
        category="validation",
        message="Invalid request",
        message_key=_INVALID_REQUEST_KEY,
        retryable=False,
    )
    request_id = resolve_request_id(request)
    return JSONResponse(
        status_code=400,
        content=build_error_envelope(spec, request_id=request_id),
        headers={REQUEST_ID_HEADER: request_id},
    )


def resolve_contact_sender(request: Request, settings: Settings) -> EmailSender:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "contact_sender", None)
    if preset is not None:
        return cast(EmailSender, preset)
    return CloudflareEmailSender(settings)


def resolve_contact_verifier(request: Request, settings: Settings) -> TurnstileVerifier:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "contact_turnstile_verifier", None)
    if preset is not None:
        return cast(TurnstileVerifier, preset)
    return CloudflareTurnstileVerifier(settings)


def _resolve_settings(request: Request) -> Settings:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "settings", None)
    if isinstance(preset, Settings):
        return preset
    return load()


def _resolve_limiter(request: Request) -> OriginRateLimiter:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "contact_rate_limiter", None)
    if isinstance(preset, OriginRateLimiter):
        return preset
    return _DEFAULT_LIMITER


def _resolve_metrics(request: Request) -> ContactMetrics:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "contact_metrics", None)
    if isinstance(preset, ContactMetrics):
        return preset
    return _DEFAULT_METRICS


def _origin_fingerprint(request: Request) -> str:
    """Per-origin fingerprint: the Origin header, else the client host."""
    origin = request.headers.get("origin")
    if origin:
        return origin
    client = request.client
    return client.host if client is not None else "unknown"


def _client_ip(request: Request) -> str | None:
    client = request.client
    return client.host if client is not None else None


@router.post(
    "/contact",
    response_model=ContactAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_contact(
    request: Request,
    background_tasks: BackgroundTasks,
) -> ContactAccepted:
    """Accept a validated contact submission and deliver by email async.

    202 always returns first; only validation (400), honeypot (silent 202),
    and rate limiting (429) short-circuit before scheduling delivery.
    Never log message/email/category/submission content.
    """
    settings = _resolve_settings(request)
    metrics = _resolve_metrics(request)

    try:
        body: object = await request.json()
    except Exception:
        raise ContactValidationError() from None

    try:
        submission = ContactSubmission.model_validate(body)
    except Exception:
        raise ContactValidationError() from None

    if submission.is_honeypot():
        # Bot trap: accept silently, no delivery, no content logs.
        metrics.discarded += 1
        return ContactAccepted()

    limiter = _resolve_limiter(request)
    if not limiter.check_and_record(_origin_fingerprint(request)):
        logger.warning("contact rate limited", extra={"fields": {"limit": limiter.limit}})
        raise HTTPException(status_code=429, detail={"messageKey": _RATE_LIMITED_KEY})

    # Turnstile is a soft gate: verification failure or a missing token when
    # a secret is configured still accepts (UX) but is counted internally.
    verifier = resolve_contact_verifier(request, settings)
    if settings.turnstile_site_secret is not None:
        ok = await verifier.verify(
            submission.turnstile_token,
            secret=settings.turnstile_site_secret,
            remoteip=_client_ip(request),
        )
        if not ok:
            metrics.turnstile_rejections += 1
            logger.info(
                "contact turnstile soft-rejected",
                extra={"fields": {"count": metrics.turnstile_rejections}},
            )

    sender = resolve_contact_sender(request, settings)
    payload = build_email_payload(submission, settings)
    background_tasks.add_task(deliver_contact_email, sender, payload, metrics)
    return ContactAccepted()


class CloudflareEmailSender:
    """Real ``EmailSender``: the Cloudflare Email Sending REST API (async)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def send(self, payload: EmailPayload) -> None:
        """POST the payload; raises on non-2xx/provider failure."""
        account_id = self._settings.cf_email_account_id or self._settings.r2_account_id
        token = self._settings.cf_email_api_token
        if not token:
            raise RuntimeError("CF_EMAIL_API_TOKEN is not configured")
        url = EMAIL_SENDING_URL.format(account_id=account_id)
        headers = {"Authorization": f"Bearer {token}"}
        body = email_payload_to_dict(payload)
        if self._client is not None:
            response = await self._client.post(url, json=body, headers=headers)
        else:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=body, headers=headers)
        response.raise_for_status()


class CloudflareTurnstileVerifier:
    """Real ``TurnstileVerifier``: server-side siteverify (async, soft gate)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def verify(
        self,
        token: str | None,
        *,
        secret: str,
        remoteip: str | None,
    ) -> bool:
        if not token:
            return False
        data: dict[str, str] = {"secret": secret, "response": token}
        if remoteip:
            data["remoteip"] = remoteip
        try:
            if self._client is not None:
                response = await self._client.post(TURNSTILE_VERIFY_URL, data=data)
            else:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(TURNSTILE_VERIFY_URL, data=data)
            response.raise_for_status()
            result = response.json()
            return bool(result.get("success"))
        except Exception:
            return False
