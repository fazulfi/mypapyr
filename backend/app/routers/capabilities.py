"""Canonical capability and limits contract (BE-08).

Owned by BE-08 (execution-matrix.md); consumed by BE-10, TL-01, SEC-01,
SEO and the tool tasks. The R-03-approved per-tool table (gate-entry.md
section 2, verbatim from the C2 brief table) is the single source of truth
hard-coded here as the typed, immutable :data:`TOOL_LIMITS` registry; the
global contract fields (C2:162) default to :data:`GLOBAL_LIMITS` (the
approved R-03 values) and are derived from the runtime
:class:`app.config.Settings` when supplied (F-5), so the advertised
``maxQueueLength``/``maxWaitSeconds``/``retentionSeconds``/
``maxConcurrentPerOrigin``/``defaultTimeoutSeconds`` can never diverge
from what the queue, store, and fair-use policy enforce. Per-tool
execution ceilings are never advertised below the enforced default
timeout. Backend validation stays authoritative (DEC-165): the versioned
``GET /api/v1/capabilities`` endpoint is cacheable and deterministic, the
frontend reads it instead of keeping a hardcoded copy, and browser-specific
limits stay frontend logic.

The closed machine-readable failure-code vocabulary
(:class:`FailureCode` + :data:`FAILURE_CODES`) is the stable vocabulary
that BE-10 (fair use) and SEC-01 (fail-closed threat classification)
consume. Every code maps to a message key from the existing envelope
vocabulary (``app/errors.py``); keys resolve at the presentation layer.
The deterministic mapping from the BE-02 :class:`ValidationFailure`
categories (:func:`failure_code_for`) makes "a violating upload returns the
matching machine-readable code" true at admission time, and
:func:`failure_code_for_queue_error` maps each typed queue/admission error
to the matching stable code (F-5).

Contract shape: JSON keys use the canonical C2 camelCase axis names
(``maxFiles``, ``maxPixelsPerPage``, ...); n/a axes serialize as ``null``.
There is no mutable global state: the registry is a
:class:`types.MappingProxyType` over frozen Pydantic models, and every
request builds a fresh payload. No deployment/private internals, secrets,
or raw settings objects are part of the contract.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.config import Settings
from app.security.validation import (
    MESSAGE_KEY_BAD_REQUEST,
    MESSAGE_KEY_INVALID_REQUEST,
    MESSAGE_KEY_PAYLOAD_TOO_LARGE,
    MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
    ValidationFailure,
)

__all__ = [
    "CACHE_CONTROL",
    "CONTRACT_VERSION",
    "FAILURE_CODES",
    "GLOBAL_LIMITS",
    "TOOL_LIMITS",
    "CapabilitiesResponse",
    "FailureCode",
    "FailureCodeEntry",
    "FailureCodeMeta",
    "GlobalLimits",
    "ToolId",
    "ToolLimits",
    "capabilities_payload",
    "failure_code_for",
    "failure_code_for_queue_error",
    "failure_code_meta",
    "router",
]

CONTRACT_VERSION: Final[int] = 1
#: Operational caching default: the contract changes only on deploy, so a
#: one-hour cache (the product's retention convention) is safe (DEC-165).
CACHE_CONTROL: Final[str] = "public, max-age=3600"

# Byte units: MB/MiB follow the established codebase convention (BE-02
# validation defaults), decimal for pixel caps (BE-02 20_000_000 precedent).
_MB: Final[int] = 1024**2
_GIB: Final[int] = 1024**3

# Message keys from the existing envelope vocabulary (app/errors.py) that
# are not exported there as constants; the four validation keys are
# imported from BE-02 to keep a single copy.
MESSAGE_KEY_RATE_LIMITED: Final[str] = "error.rateLimited"
MESSAGE_KEY_NOT_FOUND: Final[str] = "error.notFound"


class ToolId(StrEnum):
    """Closed canonical tool identifiers (frontend route slugs)."""

    COMPRESS_PDF = "compress-pdf"
    MERGE_PDF = "merge-pdf"
    SPLIT_PDF = "split-pdf"
    JPG_TO_PDF = "jpg-to-pdf"
    PDF_TO_JPG = "pdf-to-jpg"


class FailureCode(StrEnum):
    """Closed stable machine-readable failure codes (DEC-165, C2 brief).

    Codes are stable forever; metadata (message key, retryability) is
    resolved through :func:`failure_code_meta` and advertised in the
    contract's ``failureCodes`` vocabulary. ``message_key`` values stay
    within the existing envelope vocabulary (``app/errors.py``) so the
    presentation layer localizes every failure.
    """

    EMPTY = "empty"
    TYPE_MISMATCH = "type_mismatch"
    SIZE_EXCEEDED = "size_exceeded"
    CORRUPT = "corrupt"
    RESOURCE_EXCEEDED = "resource_exceeded"
    TOO_MANY_FILES = "too_many_files"
    TOTAL_TOO_LARGE = "total_too_large"
    TOO_MANY_PAGES = "too_many_pages"
    TOO_MANY_PIXELS = "too_many_pixels"
    TOO_MANY_OUTPUTS = "too_many_outputs"
    ESTIMATED_MEMORY_EXCEEDED = "estimated_memory_exceeded"
    ZIP_TOO_LARGE = "zip_too_large"
    RESULT_TOO_LARGE = "result_too_large"
    QUEUE_FULL = "queue_full"
    MAX_WAIT_EXCEEDED = "max_wait_exceeded"
    TOO_MANY_CONCURRENT = "too_many_concurrent"
    RATE_LIMITED = "rate_limited"
    NOT_FOUND = "not_found"
    EXPIRED = "expired"


@dataclass(frozen=True)
class FailureCodeMeta:
    """Stable metadata for a :class:`FailureCode`."""

    message_key: str
    retryable: bool


_FAILURE_CODE_META: Final[Mapping[FailureCode, FailureCodeMeta]] = {
    FailureCode.EMPTY: FailureCodeMeta(message_key=MESSAGE_KEY_BAD_REQUEST, retryable=False),
    FailureCode.TYPE_MISMATCH: FailureCodeMeta(
        message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE, retryable=False
    ),
    FailureCode.SIZE_EXCEEDED: FailureCodeMeta(
        message_key=MESSAGE_KEY_PAYLOAD_TOO_LARGE, retryable=False
    ),
    FailureCode.CORRUPT: FailureCodeMeta(message_key=MESSAGE_KEY_BAD_REQUEST, retryable=False),
    FailureCode.RESOURCE_EXCEEDED: FailureCodeMeta(
        message_key=MESSAGE_KEY_INVALID_REQUEST, retryable=False
    ),
    FailureCode.TOO_MANY_FILES: FailureCodeMeta(
        message_key=MESSAGE_KEY_INVALID_REQUEST, retryable=False
    ),
    FailureCode.TOTAL_TOO_LARGE: FailureCodeMeta(
        message_key=MESSAGE_KEY_PAYLOAD_TOO_LARGE, retryable=False
    ),
    FailureCode.TOO_MANY_PAGES: FailureCodeMeta(
        message_key=MESSAGE_KEY_INVALID_REQUEST, retryable=False
    ),
    FailureCode.TOO_MANY_PIXELS: FailureCodeMeta(
        message_key=MESSAGE_KEY_INVALID_REQUEST, retryable=False
    ),
    FailureCode.TOO_MANY_OUTPUTS: FailureCodeMeta(
        message_key=MESSAGE_KEY_INVALID_REQUEST, retryable=False
    ),
    FailureCode.ESTIMATED_MEMORY_EXCEEDED: FailureCodeMeta(
        message_key=MESSAGE_KEY_INVALID_REQUEST, retryable=False
    ),
    FailureCode.ZIP_TOO_LARGE: FailureCodeMeta(
        message_key=MESSAGE_KEY_PAYLOAD_TOO_LARGE, retryable=False
    ),
    FailureCode.RESULT_TOO_LARGE: FailureCodeMeta(
        message_key=MESSAGE_KEY_PAYLOAD_TOO_LARGE, retryable=False
    ),
    FailureCode.QUEUE_FULL: FailureCodeMeta(message_key=MESSAGE_KEY_RATE_LIMITED, retryable=True),
    FailureCode.MAX_WAIT_EXCEEDED: FailureCodeMeta(
        message_key=MESSAGE_KEY_RATE_LIMITED, retryable=True
    ),
    FailureCode.TOO_MANY_CONCURRENT: FailureCodeMeta(
        message_key=MESSAGE_KEY_RATE_LIMITED, retryable=True
    ),
    FailureCode.RATE_LIMITED: FailureCodeMeta(message_key=MESSAGE_KEY_RATE_LIMITED, retryable=True),
    FailureCode.NOT_FOUND: FailureCodeMeta(message_key=MESSAGE_KEY_NOT_FOUND, retryable=False),
    FailureCode.EXPIRED: FailureCodeMeta(message_key=MESSAGE_KEY_NOT_FOUND, retryable=False),
}

_VALIDATION_TO_FAILURE_CODE: Final[Mapping[ValidationFailure, FailureCode]] = {
    ValidationFailure.EMPTY: FailureCode.EMPTY,
    ValidationFailure.TYPE_MISMATCH: FailureCode.TYPE_MISMATCH,
    ValidationFailure.SIZE_EXCEEDED: FailureCode.SIZE_EXCEEDED,
    ValidationFailure.CORRUPT: FailureCode.CORRUPT,
    ValidationFailure.RESOURCE_EXCEEDED: FailureCode.RESOURCE_EXCEEDED,
}


def failure_code_meta(code: FailureCode) -> FailureCodeMeta:
    """Stable metadata for *code*; unknown codes fail closed.

    The ``isinstance`` guard matters: ``StrEnum`` members compare equal to
    their string value, so a plain string would otherwise pass the lookup.
    """
    if not isinstance(code, FailureCode):
        raise ValueError(f"unknown failure code: {code!r}")
    return _FAILURE_CODE_META[code]


def failure_code_for(failure: ValidationFailure) -> FailureCode:
    """The matching machine-readable code for a BE-02 validation failure."""
    if not isinstance(failure, ValidationFailure):
        raise ValueError(f"unknown validation failure: {failure!r}")
    return _VALIDATION_TO_FAILURE_CODE[failure]


def failure_code_for_queue_error(err: object) -> FailureCode:
    """The stable BE-08 code for a typed queue/admission error (F-5).

    Each :class:`QueueError` subclass carries its ``failure_code`` (the
    single source of truth next to the error), so the mapping is
    deterministic and closed; unknown errors fail closed with
    :class:`ValueError` so no silent misclassification reaches the client.
    """
    code = getattr(err, "failure_code", None)
    if isinstance(code, FailureCode):
        return code
    raise ValueError(f"unknown queue error: {type(err).__name__}")


class ToolLimits(BaseModel):
    """Per-tool server limits; n/a axes are ``None`` (R-03 table verbatim)."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    max_files: int = Field(title="Max files")
    max_file_bytes: int = Field(title="Max file bytes")
    max_total_bytes: int = Field(title="Max total bytes")
    max_pages: int | None = Field(title="Max pages")
    max_outputs: int = Field(title="Max outputs")
    max_pixels_per_image: int | None = Field(title="Max pixels per image")
    max_pixels_per_page: int | None = Field(title="Max pixels per page")
    max_total_pixels: int | None = Field(title="Max total pixels")
    max_estimated_memory_bytes: int = Field(title="Max estimated memory bytes")
    max_execution_seconds: int = Field(title="Max execution seconds")
    max_zip_bytes: int | None = Field(title="Max zip bytes")
    max_result_bytes: int = Field(title="Max result bytes")


class GlobalLimits(BaseModel):
    """Global contract fields (C2:162; gate-entry.md section 2)."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    retention_seconds: int = Field(title="Retention seconds")
    max_wait_seconds: int = Field(title="Max wait seconds")
    max_queue_length: int = Field(title="Max queue length")
    max_concurrent_per_origin: int = Field(title="Max concurrent per origin")
    default_timeout_seconds: int = Field(title="Default timeout seconds")


class FailureCodeEntry(BaseModel):
    """One advertised failure code with its localization key."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    code: str = Field(title="Code")
    message_key: str = Field(title="Message key")
    retryable: bool = Field(title="Retryable")


class CapabilitiesResponse(BaseModel):
    """The versioned capability and limits contract payload."""

    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    version: int = Field(title="Version")
    tools: dict[str, ToolLimits] = Field(title="Tools")
    global_limits: GlobalLimits = Field(alias="global", title="Global limits")
    failure_codes: list[FailureCodeEntry] = Field(title="Failure codes")


TOOL_LIMITS: Final[Mapping[ToolId, ToolLimits]] = MappingProxyType(
    {
        ToolId.COMPRESS_PDF: ToolLimits(
            max_files=1,
            max_file_bytes=100 * _MB,
            max_total_bytes=100 * _MB,
            max_pages=1000,
            max_outputs=1,
            max_pixels_per_image=None,
            max_pixels_per_page=None,
            max_total_pixels=None,
            max_estimated_memory_bytes=3 * _GIB // 2,
            max_execution_seconds=180,
            max_zip_bytes=None,
            max_result_bytes=512 * _MB,
        ),
        ToolId.MERGE_PDF: ToolLimits(
            max_files=20,
            max_file_bytes=100 * _MB,
            max_total_bytes=200 * _MB,
            max_pages=1000,
            max_outputs=1,
            max_pixels_per_image=None,
            max_pixels_per_page=None,
            max_total_pixels=None,
            max_estimated_memory_bytes=3 * _GIB // 2,
            max_execution_seconds=180,
            max_zip_bytes=None,
            max_result_bytes=512 * _MB,
        ),
        ToolId.SPLIT_PDF: ToolLimits(
            max_files=1,
            max_file_bytes=100 * _MB,
            max_total_bytes=100 * _MB,
            max_pages=1000,
            max_outputs=100,
            max_pixels_per_image=None,
            max_pixels_per_page=None,
            max_total_pixels=None,
            max_estimated_memory_bytes=5 * _GIB // 4,
            max_execution_seconds=180,
            max_zip_bytes=200 * _MB,
            max_result_bytes=512 * _MB,
        ),
        ToolId.JPG_TO_PDF: ToolLimits(
            max_files=50,
            max_file_bytes=20 * _MB,
            max_total_bytes=200 * _MB,
            max_pages=None,
            max_outputs=1,
            max_pixels_per_image=20_000_000,
            max_pixels_per_page=None,
            max_total_pixels=100_000_000,
            max_estimated_memory_bytes=3 * _GIB // 2,
            max_execution_seconds=180,
            max_zip_bytes=None,
            max_result_bytes=512 * _MB,
        ),
        ToolId.PDF_TO_JPG: ToolLimits(
            max_files=1,
            max_file_bytes=100 * _MB,
            max_total_bytes=100 * _MB,
            max_pages=200,
            max_outputs=200,
            max_pixels_per_image=None,
            max_pixels_per_page=16_000_000,
            max_total_pixels=None,
            max_estimated_memory_bytes=3 * _GIB // 4,
            max_execution_seconds=300,
            max_zip_bytes=256 * _MB,
            max_result_bytes=512 * _MB,
        ),
    }
)

GLOBAL_LIMITS: Final[GlobalLimits] = GlobalLimits(
    retention_seconds=3600,
    max_wait_seconds=900,
    max_queue_length=2000,
    max_concurrent_per_origin=4,
    default_timeout_seconds=180,
)


def _build_failure_codes() -> tuple[FailureCodeEntry, ...]:
    entries = []
    for code in FailureCode:
        meta = _FAILURE_CODE_META[code]
        entries.append(
            FailureCodeEntry(
                code=code.value,
                message_key=meta.message_key,
                retryable=meta.retryable,
            )
        )
    return tuple(entries)


FAILURE_CODES: Final[tuple[FailureCodeEntry, ...]] = _build_failure_codes()


def _global_limits_for(settings: Settings | None) -> GlobalLimits:
    """The advertised global contract: runtime Settings, canonical when absent.

    Deriving from the runtime Settings (F-5) keeps the advertised
    maxQueueLength / maxWaitSeconds / retentionSeconds /
    maxConcurrentPerOrigin / defaultTimeoutSeconds identical to what the
    queue, store, and fair-use policy actually enforce, so an operator
    override can never make the contract a lie to the client.
    """
    if settings is None:
        return GLOBAL_LIMITS
    return GlobalLimits(
        retention_seconds=settings.retention_seconds,
        max_wait_seconds=settings.max_wait_seconds,
        max_queue_length=settings.max_queue_length,
        max_concurrent_per_origin=settings.max_concurrent_per_origin,
        default_timeout_seconds=settings.default_timeout_seconds,
    )


def capabilities_payload(settings: Settings | None = None) -> CapabilitiesResponse:
    """A fresh contract payload from the immutable registries and *settings*.

    With ``settings`` the advertised global axes track the enforced ones
    (F-5), and each per-tool execution ceiling is at least the enforced
    default timeout — a noncanonical ``DEFAULT_TIMEOUT_SECONDS`` override
    is advertised truthfully instead of being silently hidden.
    """
    default_timeout = (
        settings.default_timeout_seconds
        if settings is not None
        else GLOBAL_LIMITS.default_timeout_seconds
    )
    tools = {
        tool.value: limits.model_copy(
            update={"max_execution_seconds": max(limits.max_execution_seconds, default_timeout)}
        )
        for tool, limits in TOOL_LIMITS.items()
    }
    return CapabilitiesResponse.model_validate(
        {
            "version": CONTRACT_VERSION,
            "tools": tools,
            "global_limits": _global_limits_for(settings),
            "failure_codes": list(FAILURE_CODES),
        }
    )


router = APIRouter(prefix="/api/v1", tags=["capabilities"])


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
    summary="Capability and limits contract",
)
def get_capabilities(request: Request, response: Response) -> CapabilitiesResponse:
    """Serve the versioned, cacheable capabilities contract.

    The payload derives the global axes from the mounted runtime Settings
    (``app.state.settings``); a router mounted without settings (bare-app
    tests) falls back to the approved canonical defaults. The contract
    changes only on deploy, so the public cache remains safe.
    """
    settings = getattr(request.app.state, "settings", None)
    payload = capabilities_payload(settings)
    response.headers["Cache-Control"] = CACHE_CONTROL
    return payload
