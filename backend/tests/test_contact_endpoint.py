"""PT-03 Contact endpoint HTTP tests: POST /api/v1/support/contact.

Covers the full wire contract: 202 acceptance shape, 400 validation
envelope, silent 202 honeypot, 429 rate limiting, soft Turnstile gating,
background email delivery with an injected fake sender (exact body),
202-with-provider-failure, and router mounting.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services.contact_service import (
    ContactMetrics,
    EmailPayload,
    OriginRateLimiter,
)

CONTACT_URL = "/api/v1/support/contact"
VALID_PAYLOAD: dict[str, object] = {
    "category": "bug",
    "message": "I found a bug in the tool",
    "email": "user@example.com",
    "page": "/en/compress-pdf",
    "locale": "en",
}


class RecordingSender:
    """Fake EmailSender capturing payloads; optional forced failure."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[EmailPayload] = []

    async def send(self, payload: EmailPayload) -> None:
        if self.fail:
            raise RuntimeError("provider outage")
        self.sent.append(payload)


class FakeVerifier:
    """Fake TurnstileVerifier returning a scripted outcome."""

    def __init__(self, *, success: bool = True) -> None:
        self.success = success
        self.calls: list[tuple[str | None, str | None]] = []

    async def verify(
        self,
        token: str | None,
        *,
        secret: str,
        remoteip: str | None,
    ) -> bool:
        self.calls.append((token, remoteip))
        return self.success


class _App:
    """Test harness: fresh app with injected sender/limiter/verifier."""

    def __init__(
        self,
        *,
        sender: RecordingSender | None = None,
        verifier: FakeVerifier | None = None,
        limiter: OriginRateLimiter | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.sender = sender or RecordingSender()
        self.verifier = verifier
        # Fresh limiter per harness so tests never share rate-limit state.
        self.limiter = limiter or OriginRateLimiter()
        self.metrics = ContactMetrics()
        self.app: FastAPI = create_app(settings=settings)
        self.app.state.contact_sender = self.sender
        self.app.state.contact_metrics = self.metrics
        self.app.state.contact_rate_limiter = self.limiter
        if self.verifier is not None:
            self.app.state.contact_turnstile_verifier = self.verifier
        self.client = TestClient(self.app)


def _settings(**overrides: str) -> Settings:
    env = {
        "R2_ACCOUNT_ID": "account-123",
        "R2_ACCESS_KEY_ID": "key",
        "R2_SECRET_ACCESS_KEY": "secret",
        "R2_BUCKET_NAME": "bucket",
        "ALLOWED_ORIGINS": "http://localhost:3000",
    }
    env.update(overrides)
    return Settings.from_env(env)


@pytest.fixture
def harness() -> _App:
    return _App()


def _mounted_api_routes(application: FastAPI) -> list[Any]:
    """Resolve direct and FastAPI 0.141+ included-router API routes."""
    routes: list[Any] = []
    for route in application.routes:
        path = getattr(route, "path", None)
        if path is not None:
            routes.append(route)
            continue
        original_router = getattr(route, "original_router", None)
        if original_router is not None:
            routes.extend(
                nested
                for nested in getattr(original_router, "routes", [])
                if getattr(nested, "path", None) is not None
            )
    return routes


def test_router_is_mounted_on_factory_app(harness: _App) -> None:
    mounted = {route.path for route in _mounted_api_routes(harness.app)}
    assert CONTACT_URL in mounted


def test_accepts_valid_submission_returns_202(harness: _App) -> None:
    response = harness.client.post(CONTACT_URL, json=VALID_PAYLOAD)
    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}


def test_accepts_all_categories(harness: _App) -> None:
    for cat in ("bug", "suggestion", "question", "privacy", "advertising", "other"):
        # Fresh app per category so the per-origin limiter never trips.
        fresh = _App()
        payload = dict(VALID_PAYLOAD, category=cat)
        response = fresh.client.post(CONTACT_URL, json=payload)
        assert response.status_code == 202, f"category {cat} rejected"
        assert len(fresh.sender.sent) == 1


def test_accepts_submission_without_optional_fields(harness: _App) -> None:
    payload = {"category": "question", "message": "Just asking"}
    response = harness.client.post(CONTACT_URL, json=payload)
    assert response.status_code == 202


class TestValidationErrors:
    """Invalid submissions -> 400 stable envelope, never user content."""

    def _env(self) -> dict[str, str]:
        return {"messageKey": "support.invalidRequest"}

    def _assert_400(self, app: _App, payload: dict[str, object]) -> None:
        response = app.client.post(CONTACT_URL, json=payload)
        assert response.status_code == 400
        body = response.json()
        assert body["error"]["messageKey"] == "support.invalidRequest"
        # Never echo user content in the envelope
        assert "bug" not in str(body)
        assert "I found a bug" not in str(body)

    def test_invalid_category(self, harness: _App) -> None:
        self._assert_400(harness, dict(VALID_PAYLOAD, category="spam"))

    def test_missing_message(self, harness: _App) -> None:
        payload = dict(VALID_PAYLOAD)
        del payload["message"]
        self._assert_400(harness, payload)

    def test_empty_message(self, harness: _App) -> None:
        self._assert_400(harness, dict(VALID_PAYLOAD, message="   "))

    def test_message_too_long(self, harness: _App) -> None:
        self._assert_400(harness, dict(VALID_PAYLOAD, message="a" * 2001))

    def test_malformed_email(self, harness: _App) -> None:
        self._assert_400(harness, dict(VALID_PAYLOAD, email="nope"))

    def test_email_too_long(self, harness: _App) -> None:
        local = "a" * 200
        domain = "b" * 50
        self._assert_400(harness, dict(VALID_PAYLOAD, email=f"{local}@{domain}.com"))

    def test_extra_field_rejected(self, harness: _App) -> None:
        self._assert_400(harness, dict(VALID_PAYLOAD, evil="x"))

    def test_malformed_json(self, harness: _App) -> None:
        response = harness.client.post(
            CONTACT_URL,
            content=b"{not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["messageKey"] == "support.invalidRequest"


class TestHoneypot:
    """Filled honeypot -> silent 202, no delivery, no content logs."""

    def test_filled_honeypot_silently_accepted(self, harness: _App) -> None:
        payload = dict(VALID_PAYLOAD, **{"_hp": "spammy bot text"})
        response = harness.client.post(CONTACT_URL, json=payload)
        assert response.status_code == 202
        assert response.json() == {"status": "accepted"}
        assert harness.sender.sent == []

    def test_empty_honeypot_still_accepted(self, harness: _App) -> None:
        payload = dict(VALID_PAYLOAD, **{"_hp": ""})
        response = harness.client.post(CONTACT_URL, json=payload)
        assert response.status_code == 202
        assert len(harness.sender.sent) == 1


class TestRateLimit:
    """Third successful delivery per origin/min allowed; 4th -> 429."""

    def test_429_after_limit_exceeded(self, harness: _App) -> None:
        limiter = OriginRateLimiter(limit=3, window_seconds=60.0, clock=lambda: 100.0)
        app = _App(limiter=limiter)
        for _ in range(3):
            response = app.client.post(CONTACT_URL, json=VALID_PAYLOAD)
            assert response.status_code == 202
        response = app.client.post(CONTACT_URL, json=VALID_PAYLOAD)
        assert response.status_code == 429
        assert response.json()["error"]["messageKey"] == "error.rateLimited"
        assert len(app.sender.sent) == 3

    def test_different_origins_have_independent_budgets(self) -> None:
        limiter = OriginRateLimiter(limit=1, window_seconds=60.0, clock=lambda: 100.0)
        app = _App(limiter=limiter)
        first = app.client.post(
            CONTACT_URL, json=VALID_PAYLOAD, headers={"Origin": "https://a.example"}
        )
        assert first.status_code == 202
        second = app.client.post(
            CONTACT_URL, json=VALID_PAYLOAD, headers={"Origin": "https://b.example"}
        )
        assert second.status_code == 202
        third = app.client.post(
            CONTACT_URL, json=VALID_PAYLOAD, headers={"Origin": "https://a.example"}
        )
        assert third.status_code == 429


class TestDelivery:
    """Email Sending invoked with the exact body via the injected fake."""

    def test_sender_called_with_exact_payload(self, harness: _App) -> None:
        response = harness.client.post(CONTACT_URL, json=VALID_PAYLOAD)
        assert response.status_code == 202
        assert len(harness.sender.sent) == 1
        payload = harness.sender.sent[0]
        assert payload.to == "privacy@mypapyr.com"
        assert payload.from_address == "no-reply@mypapyr.com"
        assert payload.from_name == "Papyr Support"
        assert payload.reply_to_address == "privacy@mypapyr.com"
        assert payload.reply_to_name == "Papyr Support"
        assert payload.subject == "Papyr contact: bug"
        assert "I found a bug in the tool" in payload.text
        assert "user@example.com" in payload.text
        assert "/en/compress-pdf" in payload.text
        assert "I found a bug in the tool" in payload.html

    def test_202_even_when_provider_raises(self) -> None:
        app = _App(sender=RecordingSender(fail=True))
        response = app.client.post(CONTACT_URL, json=VALID_PAYLOAD)
        assert response.status_code == 202
        assert app.metrics.delivery_failures == 1
        assert app.metrics.delivered == 0

    def test_delivery_success_counts(self, harness: _App) -> None:
        harness.client.post(CONTACT_URL, json=VALID_PAYLOAD)
        assert harness.metrics.delivered == 1
        assert harness.metrics.delivery_failures == 0


class TestTurnstile:
    """Soft gate: failures still accept, counted internally only."""

    def test_verify_failure_still_accepts(self) -> None:
        settings = _settings(TURNSTILE_SITE_SECRET="secret")
        app = _App(verifier=FakeVerifier(success=False), settings=settings)
        payload = dict(VALID_PAYLOAD, turnstileToken="tok")
        response = app.client.post(CONTACT_URL, json=payload)
        assert response.status_code == 202
        assert app.metrics.turnstile_rejections == 1
        assert len(app.sender.sent) == 1

    def test_secret_configured_token_absent_still_accepts(self) -> None:
        settings = _settings(TURNSTILE_SITE_SECRET="secret")
        app = _App(verifier=FakeVerifier(success=False), settings=settings)
        response = app.client.post(CONTACT_URL, json=VALID_PAYLOAD)
        assert response.status_code == 202
        assert app.metrics.turnstile_rejections == 1

    def test_verify_success_no_rejection(self) -> None:
        settings = _settings(TURNSTILE_SITE_SECRET="secret")
        app = _App(verifier=FakeVerifier(success=True), settings=settings)
        payload = dict(VALID_PAYLOAD, turnstileToken="tok")
        response = app.client.post(CONTACT_URL, json=payload)
        assert response.status_code == 202
        assert app.metrics.turnstile_rejections == 0

    def test_verifier_receives_token_and_remoteip(self) -> None:
        settings = _settings(TURNSTILE_SITE_SECRET="secret")
        verifier = FakeVerifier(success=True)
        app = _App(verifier=verifier, settings=settings)
        payload = dict(VALID_PAYLOAD, turnstileToken="tok")
        app.client.post(CONTACT_URL, json=payload)
        token, remoteip = verifier.calls[0]
        assert token == "tok"
        assert remoteip is None or isinstance(remoteip, str)


class TestSettingsRedaction:
    """Secrets never appear in Settings repr."""

    def test_repr_redacts_secrets(self) -> None:
        settings = _settings(
            CF_EMAIL_API_TOKEN="cf-token-secret",
            TURNSTILE_SITE_SECRET="turnstile-secret",
        )
        rendered = repr(settings)
        assert "cf-token-secret" not in rendered
        assert "turnstile-secret" not in rendered
        assert "cf_email_api_token='**********'" in rendered
        assert "turnstile_site_secret='**********'" in rendered

    def test_optional_settings_parse(self) -> None:
        settings = _settings(
            CF_EMAIL_API_TOKEN="tok",
            CF_EMAIL_ACCOUNT_ID="acct",
            CONTACT_RECIPIENT="owner@example.com",
            CONTACT_FROM_DOMAIN="example.org",
            TURNSTILE_SITE_SECRET="sec",
        )
        assert settings.cf_email_api_token == "tok"
        assert settings.cf_email_account_id == "acct"
        assert settings.contact_recipient == "owner@example.com"
        assert settings.contact_from_domain == "example.org"
        assert settings.turnstile_site_secret == "sec"
