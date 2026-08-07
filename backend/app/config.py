"""Typed environment configuration for the backend service.

The five CI-injected variables (ci.yml backend-test job) are the only
required settings. Settings are read explicitly from the process
environment — never from dotfiles — so behavior is deterministic
regardless of local `.env*` files.

Phase 3 (BE-01) adds optional operational knobs carrying the owner-approved
defaults from audit-outputs/phase-3/gate-entry.md: R-03 global contract
fields (retention 3600 s, max wait 900 s, queue 2000, per-origin 4, default
timeout 180 s), R-07 per-worker bounds (2 GiB memory, 1.5 CPU), R-09 Redis
(maxmemory ~384 MiB, ``noeviction``), plus the logging level and the R2
endpoint/region consumed by BE-03. Optional knobs never enter
``REQUIRED_ENV_VARS``: the five-variable CI contract is unchanged.
"""

from __future__ import annotations

import logging
import math
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

# --- Approved Phase 3 defaults (gate-entry.md sections 2-5) ---
# R-03 global contract fields (C2:162); retention is DEC-070 (one hour).
DEFAULT_RETENTION_SECONDS = 3600
MAX_RETENTION_SECONDS = DEFAULT_RETENTION_SECONDS
DEFAULT_MAX_WAIT_SECONDS = 900
DEFAULT_MAX_QUEUE_LENGTH = 2000
DEFAULT_MAX_CONCURRENT_PER_ORIGIN = 4
DEFAULT_TIMEOUT_SECONDS = 180
# R-07 per-worker container bounds (C1:140-141).
DEFAULT_WORKER_MEMORY_BYTES = 2 * 1024**3
DEFAULT_WORKER_CPUS = 1.5
# R-09 Redis: ~384 MiB maxmemory with noeviction; the server-side
# persistence/eviction configuration itself is deploy scope (BE-04).
DEFAULT_REDIS_MAXMEMORY_BYTES = 384 * 1024**2
DEFAULT_REDIS_EVICTION_POLICY = "noeviction"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
# R13 reconciliation: LOG_LEVEL (deploy/.env.production.example:32) and
# R2_ENDPOINT (root .env.example:35) documented but unconsumed — now consumed.
DEFAULT_LOG_LEVEL = "info"
DEFAULT_R2_REGION = "auto"
# --- Scanner settings (U-SEC owns these fields) ---
DEFAULT_CLAMD_HOST = "localhost"
DEFAULT_CLAMD_PORT = 3310
DEFAULT_SCANNER_TIMEOUT_SECONDS = 10
MAX_SCANNER_TIMEOUT_SECONDS = 3600

_SECRET_FIELD = "r2_secret_access_key"
_REDACTED = "**********"
# redis_url may embed credentials (redis://user:password@host) and is
# therefore redacted from repr/str like the R2 secret.
_REDACTED_FIELDS: frozenset[str] = frozenset({_SECRET_FIELD, "redis_url"})


class MissingEnvVarError(RuntimeError):
    """Raised when a required environment variable is absent or unusable."""


class InvalidSettingError(ValueError):
    """Raised when an optional setting is present but cannot be used."""


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


def _optional_str(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def _optional_str_or_none(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    if value is None or not value.strip():
        return None
    return value.strip()


def _optional_int(env: Mapping[str, str], name: str, default: int) -> int:
    value = env.get(name)
    if value is None or not value.strip():
        return default
    raw = value.strip()
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise InvalidSettingError(f"Setting {name!r} must be an integer, got {raw!r}") from exc
    if parsed <= 0:
        raise InvalidSettingError(f"Setting {name!r} must be a positive integer, got {raw!r}")
    return parsed


def _optional_bounded_int(env: Mapping[str, str], name: str, default: int, maximum: int) -> int:
    value = _optional_int(env, name, default)
    if value > maximum:
        raise InvalidSettingError(f"Setting {name!r} must not exceed {maximum}, got {value!r}")
    return value


def _optional_float(env: Mapping[str, str], name: str, default: float) -> float:
    value = env.get(name)
    if value is None or not value.strip():
        return default
    raw = value.strip()
    try:
        parsed = float(raw)
    except ValueError as exc:
        raise InvalidSettingError(f"Setting {name!r} must be a number, got {raw!r}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise InvalidSettingError(f"Setting {name!r} must be a positive number, got {raw!r}")
    return parsed


def _optional_log_level(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name)
    if value is None or not value.strip():
        return default
    raw = value.strip()
    if raw.upper() not in logging.getLevelNamesMapping():
        raise InvalidSettingError(f"Setting {name!r} must be a valid log level, got {raw!r}")
    return raw


def _optional_bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    value = env.get(name)
    if value is None or not value.strip():
        return default
    raw = value.strip().lower()
    if raw in {"true", "1", "yes", "on"}:
        return True
    if raw in {"false", "0", "no", "off"}:
        return False
    raise InvalidSettingError(f"Setting {name!r} must be a boolean, got {raw!r}")


@dataclass(frozen=True)
class Settings:
    """Typed, immutable backend settings."""

    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    allowed_origins: tuple[str, ...]
    r2_endpoint: str | None = None
    r2_region: str = DEFAULT_R2_REGION
    redis_url: str = DEFAULT_REDIS_URL
    redis_maxmemory_bytes: int = DEFAULT_REDIS_MAXMEMORY_BYTES
    redis_eviction_policy: str = DEFAULT_REDIS_EVICTION_POLICY
    log_level: str = DEFAULT_LOG_LEVEL
    retention_seconds: int = DEFAULT_RETENTION_SECONDS
    max_wait_seconds: int = DEFAULT_MAX_WAIT_SECONDS
    max_queue_length: int = DEFAULT_MAX_QUEUE_LENGTH
    max_concurrent_per_origin: int = DEFAULT_MAX_CONCURRENT_PER_ORIGIN
    default_timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    worker_cpus: float = DEFAULT_WORKER_CPUS
    worker_memory_bytes: int = DEFAULT_WORKER_MEMORY_BYTES
    clamd_host: str = DEFAULT_CLAMD_HOST
    clamd_port: int = DEFAULT_CLAMD_PORT
    scanner_timeout_seconds: int = DEFAULT_SCANNER_TIMEOUT_SECONDS
    scanner_enabled: bool = True

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
            r2_endpoint=_optional_str_or_none(source, "R2_ENDPOINT"),
            r2_region=_optional_str(source, "R2_REGION", DEFAULT_R2_REGION),
            redis_url=_optional_str(source, "REDIS_URL", DEFAULT_REDIS_URL),
            redis_maxmemory_bytes=_optional_int(
                source, "REDIS_MAXMEMORY_BYTES", DEFAULT_REDIS_MAXMEMORY_BYTES
            ),
            redis_eviction_policy=_optional_str(
                source, "REDIS_EVICTION_POLICY", DEFAULT_REDIS_EVICTION_POLICY
            ),
            log_level=_optional_log_level(source, "LOG_LEVEL", DEFAULT_LOG_LEVEL),
            retention_seconds=_optional_bounded_int(
                source,
                "RETENTION_SECONDS",
                DEFAULT_RETENTION_SECONDS,
                MAX_RETENTION_SECONDS,
            ),
            max_wait_seconds=_optional_int(source, "MAX_WAIT_SECONDS", DEFAULT_MAX_WAIT_SECONDS),
            max_queue_length=_optional_int(source, "MAX_QUEUE_LENGTH", DEFAULT_MAX_QUEUE_LENGTH),
            max_concurrent_per_origin=_optional_int(
                source, "MAX_CONCURRENT_PER_ORIGIN", DEFAULT_MAX_CONCURRENT_PER_ORIGIN
            ),
            default_timeout_seconds=_optional_int(
                source, "DEFAULT_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS
            ),
            worker_cpus=_optional_float(source, "WORKER_CPUS", DEFAULT_WORKER_CPUS),
            worker_memory_bytes=_optional_int(
                source, "WORKER_MEMORY_BYTES", DEFAULT_WORKER_MEMORY_BYTES
            ),
            clamd_host=_optional_str(source, "CLAMD_HOST", DEFAULT_CLAMD_HOST),
            clamd_port=_optional_bounded_int(source, "CLAMD_PORT", DEFAULT_CLAMD_PORT, 65535),
            scanner_timeout_seconds=_optional_bounded_int(
                source,
                "SCANNER_TIMEOUT_SECONDS",
                DEFAULT_SCANNER_TIMEOUT_SECONDS,
                MAX_SCANNER_TIMEOUT_SECONDS,
            ),
            scanner_enabled=_optional_bool(source, "SCANNER_ENABLED", True),
        )

    def __repr__(self) -> str:
        rendered = []
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name in _REDACTED_FIELDS:
                value = _REDACTED
            rendered.append(f"{field.name}={value!r}")
        return f"{type(self).__name__}({', '.join(rendered)})"

    __str__ = __repr__


def load() -> Settings:
    """Load settings from the process environment, failing fast if incomplete."""
    return Settings.from_env(os.environ)
