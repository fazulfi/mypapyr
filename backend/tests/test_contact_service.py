"""PT-03 Contact service tests: validation, sanitization, rate limiting,
email-payload building, and delivery failure accounting.

The service layer keeps all pure logic (validation, sanitization, payload
rendering, rate limiting, counters) network-free and injection-ready; only
the concrete ``CloudflareEmailSender``/``CloudflareTurnstileVerifier``
implementations touch httpx and are exercised indirectly through fakes.
"""

from __future__ import annotations

import asyncio

import pytest

from app.config import Settings
from app.services.contact_service import (
    CONTACT_CATEGORIES,
    MAX_MESSAGE_LENGTH,
    ContactAccepted,
    ContactMetrics,
    ContactSubmission,
    EmailPayload,
    OriginRateLimiter,
    build_email_payload,
    deliver_contact_email,
    sanitize_locale,
    sanitize_page,
)


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


def _submission(**overrides: object) -> ContactSubmission:
    data: dict[str, object] = {
        "category": "bug",
        "message": "I found a bug",
        "email": "user@example.com",
        "page": "/en/compress-pdf",
        "locale": "en",
    }
    data.update(overrides)
    return ContactSubmission.model_validate(data)


class TestContactSubmissionModel:
    """Pydantic model: field validation and sanitization."""

    def test_accepts_valid_submission(self) -> None:
        model = _submission()
        assert model.category == "bug"
        assert model.message == "I found a bug"
        assert model.email == "user@example.com"

    def test_accepts_all_categories(self) -> None:
        for cat in CONTACT_CATEGORIES:
            model = _submission(category=cat)
            assert model.category == cat

    def test_rejects_invalid_category(self) -> None:
        with pytest.raises(ValueError):
            _submission(category="spam")

    def test_message_required_non_empty_after_trim(self) -> None:
        with pytest.raises(ValueError):
            _submission(message="   ")

    def test_message_trimmed(self) -> None:
        model = _submission(message="  hello  ")
        assert model.message == "hello"

    def test_message_rejects_over_2000(self) -> None:
        with pytest.raises(ValueError):
            _submission(message="a" * (MAX_MESSAGE_LENGTH + 1))

    def test_message_at_2000_accepted(self) -> None:
        model = _submission(message="a" * MAX_MESSAGE_LENGTH)
        assert len(model.message) == MAX_MESSAGE_LENGTH

    def test_message_strips_control_chars(self) -> None:
        model = _submission(message="hello\x00world\x01")
        assert model.message == "helloworld"

    def test_optional_email_null_and_empty_ok(self) -> None:
        assert _submission(email=None).email is None
        assert _submission(email="").email is None

    def test_rejects_malformed_email(self) -> None:
        with pytest.raises(ValueError):
            _submission(email="not-an-email")

    def test_rejects_email_over_254(self) -> None:
        local = "a" * 200
        domain = "b" * 50
        with pytest.raises(ValueError):
            _submission(email=f"{local}@{domain}.com")

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValueError):
            _submission(extra_field="nope")

    def test_turnstile_and_honeypot_aliases(self) -> None:
        model = _submission(**{"_hp": "bot", "turnstileToken": "tok"})
        assert model.hp == "bot"
        assert model.turnstile_token == "tok"


class TestSanitizers:
    """Page/locale context sanitizers."""

    def test_page_allows_alphanumeric_hyphen_slash(self) -> None:
        assert sanitize_page("/en/compress-pdf") == "/en/compress-pdf"

    def test_page_strips_disallowed_chars(self) -> None:
        assert sanitize_page("</script><b>hi</b>") == "/scriptbhi/b"

    def test_page_caps_at_120(self) -> None:
        long_page = "/en/" + "a" * 200
        assert len(sanitize_page(long_page) or "") == 120

    def test_page_empty_returns_none(self) -> None:
        assert sanitize_page("") is None
        assert sanitize_page("   ") is None
        assert sanitize_page("###") is None

    def test_locale_allows_letters_and_hyphen(self) -> None:
        assert sanitize_locale("en") == "en"
        assert sanitize_locale("pt-BR") == "pt-BR"

    def test_locale_strips_disallowed_chars(self) -> None:
        assert sanitize_locale("en_US.UTF-8") == "enUSUTF-"

    def test_locale_caps_at_16(self) -> None:
        value = "a" * 30
        assert len(sanitize_locale(value) or "") == 16

    def test_locale_empty_returns_none(self) -> None:
        assert sanitize_locale("") is None
        assert sanitize_locale("123!") is None


class TestEmailPayload:
    """Payload rendered for the Cloudflare Email Sending API."""

    def test_payload_matches_cloudflare_shape(self) -> None:
        settings = _settings(
            CONTACT_RECIPIENT="support@mypapyr.com", CONTACT_FROM_DOMAIN="mypapyr.com"
        )
        payload = build_email_payload(_submission(), settings)
        assert payload.to == "support@mypapyr.com"
        assert payload.from_address == "no-reply@mypapyr.com"
        assert payload.from_name == "Papyr Support"
        assert payload.reply_to_address == "support@mypapyr.com"
        assert payload.reply_to_name == "Papyr Support"
        assert payload.subject == "Papyr contact: bug"

    def test_payload_includes_message_and_email(self) -> None:
        settings = _settings()
        payload = build_email_payload(
            _submission(message="Hello <world>", email="user@example.com"), settings
        )
        assert "Hello <world>" in payload.text
        assert "user@example.com" in payload.text
        assert "Hello &lt;world&gt;" in payload.html

    def test_payload_includes_sanitized_context_only(self) -> None:
        settings = _settings()
        payload = build_email_payload(
            _submission(page="/en/merge-pdf", locale="es"),
            settings,
        )
        assert "/en/merge-pdf" in payload.text
        assert "es" in payload.text

    def test_payload_defaults_used(self) -> None:
        settings = _settings()
        payload = build_email_payload(_submission(category="privacy"), settings)
        assert payload.to == "privacy@mypapyr.com"
        assert payload.from_address == "no-reply@mypapyr.com"
        assert payload.subject == "Papyr contact: privacy"

    def test_account_id_falls_back_to_r2(self) -> None:
        settings = _settings()
        assert settings.cf_email_account_id is None

    def test_settings_env_overrides(self) -> None:
        settings = _settings(
            CONTACT_RECIPIENT="owner@example.com",
            CONTACT_FROM_DOMAIN="example.org",
        )
        assert settings.contact_recipient == "owner@example.com"
        assert settings.contact_from_domain == "example.org"


class TestRateLimiter:
    """Deterministic in-memory per-origin limiter with injectable clock."""

    def test_allows_up_to_limit_per_origin(self) -> None:
        limiter = OriginRateLimiter(limit=3, window_seconds=60.0, clock=lambda: 10.0)
        assert limiter.check_and_record("origin-a") is True
        assert limiter.check_and_record("origin-a") is True
        assert limiter.check_and_record("origin-a") is True
        assert limiter.check_and_record("origin-a") is False

    def test_origins_are_independent(self) -> None:
        limiter = OriginRateLimiter(limit=2, window_seconds=60.0, clock=lambda: 10.0)
        assert limiter.check_and_record("origin-a") is True
        assert limiter.check_and_record("origin-a") is True
        assert limiter.check_and_record("origin-b") is True

    def test_window_expiry_resets_budget(self) -> None:
        now = [10.0]
        limiter = OriginRateLimiter(limit=1, window_seconds=60.0, clock=lambda: now[0])
        assert limiter.check_and_record("origin-a") is True
        assert limiter.check_and_record("origin-a") is False
        now[0] = 70.0
        assert limiter.check_and_record("origin-a") is True


class TestContactMetrics:
    """Counts-only delivery/verification accounting."""

    def test_defaults_are_zero(self) -> None:
        metrics = ContactMetrics()
        assert metrics.delivered == 0
        assert metrics.delivery_failures == 0
        assert metrics.turnstile_rejections == 0

    def test_counters_increment(self) -> None:
        metrics = ContactMetrics()
        metrics.delivered += 1
        metrics.delivery_failures += 1
        metrics.turnstile_rejections += 1
        assert metrics.delivered == 1
        assert metrics.delivery_failures == 1
        assert metrics.turnstile_rejections == 1


class TestDeliverContactEmail:
    """Delivery is best-effort: provider errors increment a counter only."""

    def test_success_counts_delivery(self) -> None:
        class FakeSender:
            async def send(self, payload: EmailPayload) -> None:
                return None

        metrics = ContactMetrics()
        payload = build_email_payload(_submission(), _settings())
        asyncio.run(deliver_contact_email(FakeSender(), payload, metrics))
        assert metrics.delivered == 1
        assert metrics.delivery_failures == 0

    def test_provider_error_counts_failure_only(self) -> None:
        class FailingSender:
            async def send(self, payload: EmailPayload) -> None:
                raise RuntimeError("mock provider outage")

        metrics = ContactMetrics()
        payload = build_email_payload(_submission(), _settings())
        asyncio.run(deliver_contact_email(FailingSender(), payload, metrics))
        assert metrics.delivery_failures == 1
        assert metrics.delivered == 0


class TestContactAccepted:
    """Response model shape: 202 body ``{"status": "accepted"}``."""

    def test_status_is_accepted(self) -> None:
        model = ContactAccepted()
        assert model.model_dump() == {"status": "accepted"}

    def test_status_literal_enforced(self) -> None:
        assert ContactAccepted(status="accepted").status == "accepted"
