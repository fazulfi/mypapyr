"""Typed environment configuration for the backend service.

The five CI-injected variables (ci.yml backend-test job) are the only
required settings. Settings are read explicitly from the process
environment — never from dotfiles — so behavior is deterministic
regardless of local `.env*` files.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields

REQUIRED_ENV_VARS: tuple[str, ...] = (
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET_NAME",
    "ALLOWED_ORIGINS",
)

_SECRET_FIELD = "r2_secret_access_key"
_REDACTED = "**********"


class MissingEnvVarError(RuntimeError):
    """Raised when a required environment variable is absent or unusable."""


def _require(env: Mapping[str, str], name: str) -> str:
    value = env.get(name)
    if not value:
        raise MissingEnvVarError(f"Required environment variable {name!r} is not set")
    return value


def _parse_allowed_origins(raw: str) -> tuple[str, ...]:
    origins = tuple(part.strip() for part in raw.split(",") if part.strip())
    if not origins:
        raise MissingEnvVarError(
            "Required environment variable 'ALLOWED_ORIGINS' is set but contains no origins"
        )
    return origins


@dataclass(frozen=True)
class Settings:
    """Typed, immutable backend settings."""

    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    allowed_origins: tuple[str, ...]

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        """Build settings from *env*, defaulting to the process environment."""
        source = os.environ if env is None else env
        return cls(
            r2_account_id=_require(source, "R2_ACCOUNT_ID"),
            r2_access_key_id=_require(source, "R2_ACCESS_KEY_ID"),
            r2_secret_access_key=_require(source, "R2_SECRET_ACCESS_KEY"),
            r2_bucket_name=_require(source, "R2_BUCKET_NAME"),
            allowed_origins=_parse_allowed_origins(_require(source, "ALLOWED_ORIGINS")),
        )

    def __repr__(self) -> str:
        rendered = []
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name == _SECRET_FIELD:
                value = _REDACTED
            rendered.append(f"{field.name}={value!r}")
        return f"{type(self).__name__}({', '.join(rendered)})"

    __str__ = __repr__


def load() -> Settings:
    """Load settings from the process environment, failing fast if incomplete."""
    return Settings.from_env(os.environ)
