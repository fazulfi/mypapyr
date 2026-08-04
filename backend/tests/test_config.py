"""Backend settings tests.

Verify that the five CI-injected variables are the only *required*
settings, missing/invalid values fail fast, ALLOWED_ORIGINS parses
deterministically, settings are frozen, the R2 secret and credential-
carrying URLs are redacted from repr/str, and the Phase 3 operational
knobs (R-03/R-07/R-09 approved defaults) apply with safe defaults and
deterministic environment overrides.
"""

from __future__ import annotations

import dataclasses
from dataclasses import MISSING, fields
from typing import get_type_hints

import pytest

from app.config import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_CONCURRENT_PER_ORIGIN,
    DEFAULT_MAX_QUEUE_LENGTH,
    DEFAULT_MAX_WAIT_SECONDS,
    DEFAULT_R2_REGION,
    DEFAULT_REDIS_EVICTION_POLICY,
    DEFAULT_REDIS_MAXMEMORY_BYTES,
    DEFAULT_REDIS_URL,
    DEFAULT_RETENTION_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_WORKER_CPUS,
    DEFAULT_WORKER_MEMORY_BYTES,
    REQUIRED_ENV_VARS,
    InvalidSettingError,
    MissingEnvVarError,
    Settings,
    load,
)

# CI injects exactly these five (ci.yml backend-test job env block).
CI_ENV_CONTRACT: tuple[str, ...] = (
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET_NAME",
    "ALLOWED_ORIGINS",
)

REQUIRED_FIELD_NAMES: frozenset[str] = frozenset(name.lower() for name in CI_ENV_CONTRACT)


def _env(**overrides: str) -> dict[str, str]:
    env = {name: "test" for name in REQUIRED_ENV_VARS}
    env.update(overrides)
    return env


def _settings(**overrides: str) -> Settings:
    return Settings.from_env(_env(**overrides))


# --- C-1: the five required vars raise when missing ---


@pytest.mark.parametrize("missing", CI_ENV_CONTRACT)
def test_missing_required_var_raises(missing: str) -> None:
    env = _env()
    del env[missing]
    with pytest.raises(MissingEnvVarError, match=missing):
        Settings.from_env(env)


def test_empty_required_var_raises() -> None:
    env = _env(R2_BUCKET_NAME="")
    with pytest.raises(MissingEnvVarError, match="R2_BUCKET_NAME"):
        Settings.from_env(env)


# --- C-2: documented defaults only — none invented for required fields ---


def test_required_fields_have_no_defaults() -> None:
    for field in fields(Settings):
        if field.name in REQUIRED_FIELD_NAMES:
            assert field.default is MISSING
            assert field.default_factory is MISSING


def test_optional_fields_carry_approved_defaults() -> None:
    settings = _settings()
    assert settings.retention_seconds == DEFAULT_RETENTION_SECONDS == 3600
    assert settings.max_wait_seconds == DEFAULT_MAX_WAIT_SECONDS == 900
    assert settings.max_queue_length == DEFAULT_MAX_QUEUE_LENGTH == 2000
    assert settings.max_concurrent_per_origin == DEFAULT_MAX_CONCURRENT_PER_ORIGIN == 4
    assert settings.default_timeout_seconds == DEFAULT_TIMEOUT_SECONDS == 180
    assert settings.worker_memory_bytes == DEFAULT_WORKER_MEMORY_BYTES == 2 * 1024**3
    assert settings.worker_cpus == DEFAULT_WORKER_CPUS == 1.5
    assert settings.redis_maxmemory_bytes == DEFAULT_REDIS_MAXMEMORY_BYTES == 384 * 1024**2
    assert settings.redis_eviction_policy == DEFAULT_REDIS_EVICTION_POLICY == "noeviction"
    assert settings.redis_url == DEFAULT_REDIS_URL == "redis://localhost:6379/0"
    assert settings.log_level == DEFAULT_LOG_LEVEL == "info"
    assert settings.r2_region == DEFAULT_R2_REGION == "auto"
    assert settings.r2_endpoint is None


# --- C-3: ALLOWED_ORIGINS comma parsing, deterministic ---


def test_allowed_origins_parses_comma_separated_stripped() -> None:
    settings = _settings(ALLOWED_ORIGINS=" http://a.test , http://b.test , ")
    assert settings.allowed_origins == ("http://a.test", "http://b.test")


def test_allowed_origins_single_origin() -> None:
    settings = _settings(ALLOWED_ORIGINS="http://localhost:3000")
    assert settings.allowed_origins == ("http://localhost:3000",)


def test_allowed_origins_empty_string_raises() -> None:
    with pytest.raises(MissingEnvVarError, match="ALLOWED_ORIGINS"):
        _settings(ALLOWED_ORIGINS="")


def test_allowed_origins_only_separators_raise() -> None:
    with pytest.raises(MissingEnvVarError, match="ALLOWED_ORIGINS"):
        _settings(ALLOWED_ORIGINS=" , , ")


# --- C-4: frozen immutability ---


def test_settings_are_frozen() -> None:
    settings = _settings()
    # Direct assignment is a strict-mypy error on the frozen dataclass, so the
    # frozen guard is exercised through the generated ``__setattr__``, which
    # raises FrozenInstanceError at runtime (same path as an assignment).
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.__setattr__("r2_bucket_name", "other")


# --- C-5: type coercion behavior — no coercion in the scaffold ---


def test_no_numeric_coercion_values_stay_str() -> None:
    settings = _settings(ALLOWED_ORIGINS="not-a-number,123")
    assert settings.allowed_origins == ("not-a-number", "123")


def test_required_fields_are_string_typed() -> None:
    hints = get_type_hints(Settings)
    required_hints = {name: hints[name] for name in REQUIRED_FIELD_NAMES}
    assert required_hints == {
        "r2_account_id": str,
        "r2_access_key_id": str,
        "r2_secret_access_key": str,
        "r2_bucket_name": str,
        "allowed_origins": tuple[str, ...],
    }


def test_optional_field_types() -> None:
    hints = get_type_hints(Settings)
    assert hints["r2_endpoint"] == str | None
    assert hints["r2_region"] is str
    assert hints["redis_url"] is str
    assert hints["redis_maxmemory_bytes"] is int
    assert hints["redis_eviction_policy"] is str
    assert hints["log_level"] is str
    assert hints["retention_seconds"] is int
    assert hints["max_wait_seconds"] is int
    assert hints["max_queue_length"] is int
    assert hints["max_concurrent_per_origin"] is int
    assert hints["default_timeout_seconds"] is int
    assert hints["worker_cpus"] is float
    assert hints["worker_memory_bytes"] is int


# --- C-6: CI env contract is exactly the scaffold's required set ---


def test_required_env_vars_match_ci_contract_exactly() -> None:
    assert REQUIRED_ENV_VARS == CI_ENV_CONTRACT


def test_required_fields_map_one_to_one_to_required_env_vars() -> None:
    field_names = {field.name for field in fields(Settings)}
    assert field_names >= REQUIRED_FIELD_NAMES
    assert {name.upper() for name in REQUIRED_FIELD_NAMES} == set(CI_ENV_CONTRACT)


def test_optional_fields_never_enter_required_set() -> None:
    field_names = {field.name for field in fields(Settings)}
    optional_names = field_names - REQUIRED_FIELD_NAMES
    assert optional_names
    assert {name.upper() for name in optional_names}.isdisjoint(REQUIRED_ENV_VARS)


# --- CSR T17: secret redacted from repr and str ---


def test_repr_redacts_secret() -> None:
    secret = "s3cr3t-value-never-shown"
    settings = _settings(R2_SECRET_ACCESS_KEY=secret)
    assert secret not in repr(settings)
    assert secret not in str(settings)
    assert "**********" in repr(settings)


def test_repr_keeps_non_secret_values_visible() -> None:
    settings = _settings()
    rendered = repr(settings)
    assert "r2_account_id='test'" in rendered
    assert "r2_secret_access_key='**********'" in rendered


# --- load(): reads the process environment, never dotfiles ---


def test_load_reads_process_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in REQUIRED_ENV_VARS:
        monkeypatch.setenv(name, "test")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    settings = load()
    assert settings.r2_account_id == "test"
    assert settings.r2_bucket_name == "test"
    assert settings.allowed_origins == ("http://localhost:3000",)


# --- Phase 3 (BE-01): optional operational knobs ---


def test_optional_settings_read_from_environment() -> None:
    settings = _settings(
        RETENTION_SECONDS="3600",
        MAX_WAIT_SECONDS="1200",
        MAX_QUEUE_LENGTH="3000",
        MAX_CONCURRENT_PER_ORIGIN="8",
        DEFAULT_TIMEOUT_SECONDS="240",
        WORKER_MEMORY_BYTES="4294967296",
        WORKER_CPUS="2.5",
        REDIS_MAXMEMORY_BYTES="536870912",
        REDIS_EVICTION_POLICY="allkeys-lru",
        REDIS_URL="redis://cache.internal:6379/2",
        LOG_LEVEL="debug",
        R2_REGION="auto",
        R2_ENDPOINT="https://custom-endpoint.example.com",
    )
    assert settings.retention_seconds == 3600
    assert settings.max_wait_seconds == 1200
    assert settings.max_queue_length == 3000
    assert settings.max_concurrent_per_origin == 8
    assert settings.default_timeout_seconds == 240
    assert settings.worker_memory_bytes == 4294967296
    assert settings.worker_cpus == 2.5
    assert settings.redis_maxmemory_bytes == 536870912
    assert settings.redis_eviction_policy == "allkeys-lru"
    assert settings.redis_url == "redis://cache.internal:6379/2"
    assert settings.log_level == "debug"
    assert settings.r2_region == "auto"
    assert settings.r2_endpoint == "https://custom-endpoint.example.com"


@pytest.mark.parametrize("value", ["3601", "7200"])
def test_retention_seconds_above_hard_maximum_raises(value: str) -> None:
    with pytest.raises(InvalidSettingError, match=r"RETENTION_SECONDS.*3600"):
        _settings(RETENTION_SECONDS=value)


def test_empty_optional_settings_fall_back_to_defaults() -> None:
    settings = _settings(RETENTION_SECONDS="", REDIS_URL="", LOG_LEVEL="  ", R2_ENDPOINT="")
    assert settings.retention_seconds == DEFAULT_RETENTION_SECONDS
    assert settings.redis_url == DEFAULT_REDIS_URL
    assert settings.log_level == DEFAULT_LOG_LEVEL
    assert settings.r2_endpoint is None


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("RETENTION_SECONDS", "abc"),
        ("MAX_QUEUE_LENGTH", "3.5"),
        ("WORKER_MEMORY_BYTES", "1e3"),
        ("MAX_WAIT_SECONDS", "-900"),
        ("DEFAULT_TIMEOUT_SECONDS", "0"),
        ("MAX_CONCURRENT_PER_ORIGIN", "-1"),
        ("REDIS_MAXMEMORY_BYTES", "0"),
    ],
)
def test_invalid_integer_setting_raises(name: str, value: str) -> None:
    with pytest.raises(InvalidSettingError):
        _settings(**{name: value})


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("WORKER_CPUS", "abc"),
        ("WORKER_CPUS", "0"),
        ("WORKER_CPUS", "-1.5"),
        ("WORKER_CPUS", "nan"),
        ("WORKER_CPUS", "inf"),
    ],
)
def test_invalid_float_setting_raises(name: str, value: str) -> None:
    with pytest.raises(InvalidSettingError):
        _settings(**{name: value})


def test_invalid_log_level_raises() -> None:
    with pytest.raises(InvalidSettingError):
        _settings(LOG_LEVEL="verbose")


def test_log_level_validation_is_case_insensitive() -> None:
    settings = _settings(LOG_LEVEL="Warning")
    assert settings.log_level == "Warning"


def test_repr_redacts_redis_url_credentials() -> None:
    settings = _settings(REDIS_URL="redis://:topsecret@cache.internal:6379/0")
    rendered = repr(settings)
    assert "topsecret" not in rendered
    assert "redis_url='**********'" in rendered
