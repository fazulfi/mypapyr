"""Backend settings tests.

Verify that the five CI-injected variables are the
only required settings, missing/invalid values fail fast, ALLOWED_ORIGINS
parses deterministically, settings are frozen, no type coercion exists in
the scaffold, and the R2 secret is redacted from repr/str.
"""

from __future__ import annotations

import dataclasses
from dataclasses import MISSING, fields
from typing import get_type_hints

import pytest

from app.config import (
    REQUIRED_ENV_VARS,
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


def test_no_defaults_invented_for_required_fields() -> None:
    for field in fields(Settings):
        assert field.default is MISSING
        assert field.default_factory is MISSING


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


def test_all_fields_are_string_typed() -> None:
    hints = get_type_hints(Settings)
    assert hints == {
        "r2_account_id": str,
        "r2_access_key_id": str,
        "r2_secret_access_key": str,
        "r2_bucket_name": str,
        "allowed_origins": tuple[str, ...],
    }


# --- C-6: CI env contract is exactly the scaffold's required set ---


def test_required_env_vars_match_ci_contract_exactly() -> None:
    assert REQUIRED_ENV_VARS == CI_ENV_CONTRACT


def test_settings_fields_map_one_to_one_to_required_env_vars() -> None:
    field_names = {field.name for field in fields(Settings)}
    assert {name.upper() for name in field_names} == set(CI_ENV_CONTRACT)


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
