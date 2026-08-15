"""PT-03 Contact submission service.

Pure validation/sanitization, the Cloudflare Email Sending payload shape,
an in-memory per-origin rate limiter, counts-only delivery metrics, and
best-effort asynchronous delivery. Network I/O (Cloudflare Email Sending,
Turnstile siteverify) sits behind ``EmailSender``/``TurnstileVerifier``
protocols so tests inject fakes and the router stays deterministic.

Privacy contract (PT-03): message/email/page/locale content is PII never
logged nor included in error envelopes; only counts, exception class
names, and sanitized category labels appear in logs or metrics.
"""

from __future__ import annotations

import html
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import Settings

logger = logging.getLogger(__name__)

# --- Constants (match frontend src/lib/support.ts) ---

CONTACT_CATEGORIES: tuple[str, ...] = (
    "bug",
    "suggestion",
    "question",
    "privacy",
    "advertising",
    "other",
)
ContactCategory = Literal[
    "bug",
    "suggestion",
    "question",
    "privacy",
    "advertising",
    "other",
]

MAX_MESSAGE_LENGTH = 2000
EMAIL_MAX_LENGTH = 254
MAX_PAGE_LENGTH = 120
MAX_LOCALE_LENGTH = 16

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
EMAIL_SENDING_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send"

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
_PAGE_KEEP_RE = re.compile(r"[^A-Za-z0-9/-]")
_LOCALE_KEEP_RE = re.compile(r"[^A-Za-z-]")
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Message-length band thresholds for monitoring (no exact lengths logged)
_SHORT_LIMIT = 100
_MEDIUM_LIMIT = 500
_LONG_LIMIT = 1000


def _strip_control_chars(value: str) -> str:
    """Strip ASCII control characters (U+0000-U+001F excluding tab/newline)."""
    return _CONTROL_CHAR_RE.sub("", value)


def sanitize_page(value: str | None) -> str | None:
    """Sanitize a page path: keep alphanumerics, hyphen, slash; cap at 120.

    Returns ``None`` when nothing survives sanitization.
    """
    if value is None:
        return None
    cleaned = _PAGE_KEEP_RE.sub("", _strip_control_chars(value))[:MAX_PAGE_LENGTH]
    return cleaned or None


def sanitize_locale(value: str | None) -> str | None:
    """Sanitize a locale tag: keep letters and hyphen; cap at 16."""
    if value is None:
        return None
    cleaned = _LOCALE_KEEP_RE.sub("", _strip_control_chars(value))[:MAX_LOCALE_LENGTH]
    return cleaned or None


# --- Request model ---


class ContactSubmission(BaseModel):
    """Validated contact submission payload.

    Mirrors ``frontend/src/lib/support.ts`` (defense-in-depth). Extra
    fields are forbidden; ``_hp`` and ``turnstileToken`` use their wire
    names via aliases.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    category: ContactCategory
    message: str = Field(min_length=1)
    email: str | None = None
    page: str | None = None
    locale: str | None = None
    hp: str | None = Field(default=None, alias="_hp")
    turnstile_token: str | None = Field(default=None, alias="turnstileToken")

    @field_validator("message")
    @classmethod
    def _sanitize_and_validate_message(cls, value: str) -> str:
        sanitized = _strip_control_chars(value).strip()
        if not sanitized:
            raise ValueError("message must not be empty")
        if len(sanitized) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"message must be at most {MAX_MESSAGE_LENGTH} characters")
        return sanitized

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        sanitized = _strip_control_chars(value).strip()
        if len(sanitized) > EMAIL_MAX_LENGTH:
            raise ValueError(f"email must be at most {EMAIL_MAX_LENGTH} characters")
        if not _EMAIL_RE.match(sanitized):
            raise ValueError("Invalid email format")
        return sanitized

    @field_validator("page")
    @classmethod
    def _sanitize_page(cls, value: str | None) -> str | None:
        return sanitize_page(value)

    @field_validator("locale")
    @classmethod
    def _sanitize_locale(cls, value: str | None) -> str | None:
        return sanitize_locale(value)

    def is_honeypot(self) -> bool:
        """True when the hidden honeypot field carries content (bot)."""
        return bool(self.hp and self.hp.strip())


# --- Response model ---


class ContactAccepted(BaseModel):
    """202 acceptance body: ``{"status": "accepted"}``."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["accepted"] = "accepted"


# --- Email payload ---


@dataclass(frozen=True)
class EmailPayload:
    """Cloudflare Email Sending request body (exact wire shape)."""

    to: str
    from_address: str
    from_name: str
    reply_to_address: str
    reply_to_name: str
    subject: str
    text: str
    html: str


def build_email_payload(submission: ContactSubmission, settings: Settings) -> EmailPayload:
    """Render the Cloudflare Email Sending payload for *submission*.

    The recipient is the owner inbox; message/email are PII by nature and
    allowed in the payload (never in logs/analytics). HTML is escaped.
    """
    recipient = settings.contact_recipient
    from_address = f"no-reply@{settings.contact_from_domain}"
    subject = f"Papyr contact: {submission.category}"
    page = submission.page or "n/a"
    locale = submission.locale or "n/a"
    reply_email = submission.email or "not provided"
    text = (
        f"Category: {submission.category}\n"
        f"Page: {page}\n"
        f"Locale: {locale}\n"
        f"Reply-to email: {reply_email}\n\n"
        f"{submission.message}\n"
    )
    body_html = html.escape(submission.message).replace("\n", "<br>\n")
    html_body = (
        f"<p><strong>Category:</strong> {html.escape(submission.category)}</p>\n"
        f"<p><strong>Page:</strong> {html.escape(page)}</p>\n"
        f"<p><strong>Locale:</strong> {html.escape(locale)}</p>\n"
        f"<p><strong>Reply-to email:</strong> {html.escape(reply_email)}</p>\n"
        f"<p>{body_html}</p>\n"
    )
    return EmailPayload(
        to=recipient,
        from_address=from_address,
        from_name="Papyr Support",
        reply_to_address=recipient,
        reply_to_name="Papyr Support",
        subject=subject,
        text=text,
        html=html_body,
    )


def email_payload_to_dict(payload: EmailPayload) -> dict[str, object]:
    """Canonical JSON body for the Email Sending REST API."""
    return {
        "to": payload.to,
        "from": {"address": payload.from_address, "name": payload.from_name},
        "reply_to": {"address": payload.reply_to_address, "name": payload.reply_to_name},
        "subject": payload.subject,
        "text": payload.text,
        "html": payload.html,
    }


# --- Provider seams ---


class EmailSender(Protocol):
    """Injectable email delivery seam (async)."""

    async def send(self, payload: EmailPayload) -> None: ...


class TurnstileVerifier(Protocol):
    """Injectable Turnstile server-side verification seam (async)."""

    async def verify(
        self,
        token: str | None,
        *,
        secret: str,
        remoteip: str | None,
    ) -> bool: ...


# --- Counts-only metrics ---


@dataclass
class ContactMetrics:
    """Counts-only delivery/verification accounting; never content."""

    delivered: int = 0
    delivery_failures: int = 0
    turnstile_rejections: int = 0
    discarded: int = 0


async def deliver_contact_email(
    sender: EmailSender,
    payload: EmailPayload,
    metrics: ContactMetrics,
) -> None:
    """Best-effort delivery: provider errors increment a counter only.

    The caller already returned 202; this task must never raise. Only the
    exception class name is logged — never message/email content.
    """
    try:
        await sender.send(payload)
    except Exception as exc:
        metrics.delivery_failures += 1
        logger.error(
            "contact email delivery failed",
            extra={"fields": {"error": type(exc).__name__}},
        )
    else:
        metrics.delivered += 1


# --- Rate limiter ---


class OriginRateLimiter:
    """Small in-memory per-origin limiter with an injectable clock.

    ``limit`` successful deliveries per ``window_seconds`` per fingerprint.
    Deterministic and testable: the clock is a plain callable.
    """

    def __init__(
        self,
        *,
        limit: int = 3,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, list[float]] = {}

    def check_and_record(self, fingerprint: str) -> bool:
        """Record a hit and report whether it stays under the limit."""
        now = self._clock()
        hits = [t for t in self._hits.get(fingerprint, []) if now - t < self.window_seconds]
        if len(hits) >= self.limit:
            self._hits[fingerprint] = hits
            return False
        hits.append(now)
        self._hits[fingerprint] = hits
        return True


# --- Size band helper ---


def _size_band(length: int) -> str:
    """Coarse message-length band for monitoring (no exact lengths logged)."""
    if length <= _SHORT_LIMIT:
        return "short"
    if length <= _MEDIUM_LIMIT:
        return "medium"
    if length <= _LONG_LIMIT:
        return "long"
    return "xlong"
