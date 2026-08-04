"""Typed Cloudflare R2 client (BE-03).

Privacy-first temporary-object storage: opaque keys that never derive from
the original filename, upload with bounded ASCII-only metadata, idempotent
delete, and presigned GET URLs whose lifetime is capped at
``min(remaining artifact lifetime, 300 s)`` (DEC-170).

Key scheme (C3 brief): ``tmp/<YYYY-MM-DD>/<32-lowercase-hex><safe-ext>``
where ``<safe-ext>`` is drawn from :data:`SAFE_EXTENSIONS` only — anything
else yields no extension, so no filename content can leak into object keys.

R2 behavior this module relies on (verified against
developers.cloudflare.com/r2, 2026-08-03; see
``audit-outputs/phase-3/r2-pikepdf-reference-audit.md``):

* S3-compatible endpoint ``https://<ACCOUNT_ID>.r2.cloudflarestorage.com``
  with ``region_name="auto"`` and SigV4 (``signature_version="s3v4"``).
* Presigned GET URLs are valid for 1..604,800 s; 300 s is always within
  range, and expired/tampered URLs fail server-side with 403.
* Custom metadata is limited to 8,192 bytes total (keys + values) and must
  be ASCII; Unicode metadata keys are stripped by the S3 API
  (``x-amz-missing-meta``). The ``expires-at`` marker is stored as custom
  metadata with an ASCII key so it round-trips (C3).
* moto does not authenticate and never enforces expiry or metadata limits
  (audit section C.3): those guarantees are R2-integrational. This module
  therefore enforces the ASCII and 8,192-byte bounds client-side before the
  upload leaves the process.

Privacy contract: no object key and no signed URL is ever passed to the
logger — keys are opaque identifiers that must never appear in telemetry
(DEC-170, DEC-025, DEC-175).

boto3/botocore do not ship ``py.typed``, so they are reached through
importlib with a single cast crossing point; :class:`S3Client` is the
typed surface consumed here, which is also what downstream tasks (BE-07
delete, BE-09 signed download) rely on.
"""

from __future__ import annotations

import importlib
import logging
import re
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol, cast

from app.config import Settings

logger = logging.getLogger(__name__)

# R2 object-metadata limit: 8,192 bytes total for all custom metadata
# (https://developers.cloudflare.com/r2/platform/limits/).
MAX_METADATA_BYTES = 8192
# Presigned-URL lifetime cap (DEC-170); within R2's 1..604,800 s range.
MAX_SIGNED_URL_SECONDS = 300
MIN_SIGNED_URL_SECONDS = 1
DEFAULT_CONTENT_TYPE = "application/octet-stream"
OBJECT_KEY_PREFIX = "tmp"
_METADATA_KEY_EXPIRES_AT = "expires-at"
_MAX_CONTENT_TYPE_LENGTH = 200
# Type/subtype[;param=value] with tokens only; rejects control characters
# (header injection) and anything outside the HTTP token charset.
_CONTENT_TYPE_RE = re.compile(
    r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+"
    r"(?:;[ \t]*[A-Za-z0-9!#$&^_.+-]+=[A-Za-z0-9!#$&^_.+-]+)*$"
)
# The only extensions Papyr objects may carry (tool outputs plus the image
# launch candidates). Everything else is dropped: no original-filename
# characters survive into object keys.
SAFE_EXTENSIONS = frozenset({"pdf", "jpg", "jpeg", "png", "webp"})
_OPAQUE_OBJECT_KEY_RE = re.compile(
    r"^tmp/\d{4}-\d{2}-\d{2}/[0-9a-f]{32}(?:\.(?:pdf|jpg|jpeg|png|webp))?$"
)

# botocore.exceptions.ClientError; untyped, so imported via the crossing
# point below and used only in except clauses.
_ClientError: Any = cast(Any, importlib.import_module("botocore.exceptions")).ClientError


class R2Error(RuntimeError):
    """Base class for client-side R2 contract violations."""


class ObjectExpiredError(R2Error):
    """The artifact lifetime is exhausted; a signed URL cannot be minted."""


class MetadataTooLargeError(R2Error):
    """Custom metadata exceeds R2's 8,192-byte limit (client-side guard)."""


class NonAsciiMetadataError(R2Error):
    """Custom metadata is not ASCII; R2 cannot round-trip it reliably."""


class InvalidContentTypeError(R2Error):
    """The content type is not a safe HTTP token sequence."""


class InvalidObjectKeyError(R2Error):
    """The object key is not opaque; keys must come from build_object_key."""


@dataclass(frozen=True)
class UploadReceipt:
    """Typed result of a successful upload, consumed by downstream tasks."""

    key: str
    size_bytes: int
    content_type: str
    uploaded_at: datetime


class S3Client(Protocol):
    """Minimal S3 surface this module consumes (typed crossing point)."""

    def put_object(self, **kwargs: object) -> dict[str, object]: ...
    def delete_object(self, **kwargs: object) -> dict[str, object]: ...
    def generate_presigned_url(self, *args: object, **kwargs: object) -> str: ...


def _ensure_utc(value: datetime) -> datetime:
    """Normalize a datetime to UTC; naive values are interpreted as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _error_code(exc: Exception) -> str:
    response = getattr(exc, "response", None)
    if not isinstance(response, Mapping):
        return ""
    error = response.get("Error")
    if not isinstance(error, Mapping):
        return ""
    code = error.get("Code")
    return code if isinstance(code, str) else ""


def _validate_content_type(content_type: str) -> None:
    if (
        len(content_type) > _MAX_CONTENT_TYPE_LENGTH
        or _CONTENT_TYPE_RE.fullmatch(content_type) is None
    ):
        raise InvalidContentTypeError(f"unsafe content type {content_type!r}")


def _validate_metadata(metadata: Mapping[str, str]) -> None:
    total = 0
    for name, value in metadata.items():
        try:
            total += len(name.encode("ascii")) + len(value.encode("ascii"))
        except UnicodeEncodeError as exc:
            raise NonAsciiMetadataError(
                f"metadata must be ASCII-only; key {name!r} is not"
            ) from exc
    if total > MAX_METADATA_BYTES:
        raise MetadataTooLargeError(f"metadata is {total} bytes; R2 limit is {MAX_METADATA_BYTES}")


def _build_client(settings: Settings) -> S3Client:
    boto3 = cast(Any, importlib.import_module("boto3"))
    botocore_config = cast(Any, importlib.import_module("botocore.config"))
    endpoint = settings.r2_endpoint or (
        f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    )
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name=settings.r2_region,
        config=botocore_config.Config(
            signature_version="s3v4",
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    return cast(S3Client, client)


class R2Client:
    """Typed client for Papyr's temporary R2 object lifecycle.

    Credentials are supplied out-of-band via :class:`app.config.Settings`
    (required environment variables, never dotfiles or the AWS chain).
    A boto3 client is built lazily at construction without any network
    activity; ``client`` exists as the test injection seam (moto fixture).
    """

    def __init__(self, settings: Settings, client: S3Client | None = None) -> None:
        self._settings = settings
        self._client = client if client is not None else _build_client(settings)

    @property
    def bucket_name(self) -> str:
        return self._settings.r2_bucket_name

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        """Return an opaque key: ``tmp/<YYYY-MM-DD>/<32-hex><safe-ext>``.

        The date partition is the UTC upload day; the name is 32 lowercase
        hex characters from a random UUID; the extension survives only if it
        is in :data:`SAFE_EXTENSIONS` after lowercasing — any other input
        (including paths or filenames) contributes nothing, so the original
        filename can never be recovered from the key.
        """
        partition = _ensure_utc(now if now is not None else datetime.now(UTC)).strftime("%Y-%m-%d")
        return f"{OBJECT_KEY_PREFIX}/{partition}/{uuid.uuid4().hex}{_safe_extension(extension)}"

    def upload_object(
        self,
        key: str,
        body: bytes,
        *,
        content_type: str | None = None,
        expires_at: datetime | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> UploadReceipt:
        """Upload materialized *body* bytes with bounded ASCII metadata.

        The object *key* must be an opaque key produced by
        :meth:`build_object_key`; filename-derived, path-bearing, or
        otherwise non-canonical keys are rejected before any request.

        ``expires_at`` (the authoritative artifact deadline) is mirrored as
        the ``expires-at`` custom metadata value (C3). Extra ``metadata`` is
        merged in and must stay minimal and ASCII-only; callers must never
        include filenames, passwords, URLs, contents, or keys (DEC-175).
        Keys, values and ``expires-at`` are counted together against R2's
        8,192-byte limit before any request is made.
        """
        if not isinstance(body, bytes):
            raise TypeError(f"body must be bytes, got {type(body).__name__}")
        if _OPAQUE_OBJECT_KEY_RE.fullmatch(key) is None:
            raise InvalidObjectKeyError("object key is not opaque; use build_object_key")
        content_type = content_type or DEFAULT_CONTENT_TYPE
        _validate_content_type(content_type)
        merged: dict[str, str] = dict(metadata) if metadata is not None else {}
        if expires_at is not None:
            merged[_METADATA_KEY_EXPIRES_AT] = _ensure_utc(expires_at).isoformat(timespec="seconds")
        _validate_metadata(merged)
        try:
            self._client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=body,
                ContentType=content_type,
                Metadata=merged,
            )
        except _ClientError:
            logger.error("r2 upload failed", extra={"fields": {"size_bytes": len(body)}})
            raise
        # Telemetry stays minimal: DEC-175 redacts anything with a
        # "content" stem, so even the content type is not logged.
        logger.info("r2 upload ok", extra={"fields": {"size_bytes": len(body)}})
        return UploadReceipt(
            key=key,
            size_bytes=len(body),
            content_type=content_type,
            uploaded_at=datetime.now(UTC),
        )

    def delete_object(self, key: str) -> bool:
        """Delete *key*; a missing object counts as success.

        Real service failures (anything other than ``NoSuchKey``) propagate
        to the caller so cleanup coordination (BE-07) can retry or surface
        them; the key itself never reaches the log.
        """
        try:
            self._client.delete_object(Bucket=self.bucket_name, Key=key)
        except _ClientError as exc:
            if _error_code(exc) == "NoSuchKey":
                logger.info("r2 delete ok (already absent)")
                return True
            logger.error("r2 delete failed")
            raise
        logger.info("r2 delete ok")
        return True

    def generate_signed_url(
        self, key: str, expires_at: datetime, *, now: datetime | None = None
    ) -> str:
        """Return a presigned GET URL valid for ``min(remaining, 300 s)``.

        ``expires_at`` is the authoritative artifact deadline; when the
        remaining lifetime is under one second the artifact is treated as
        expired and :class:`ObjectExpiredError` is raised, so a signed URL
        can never outlive the object (DEC-170, DEC-075). ``now`` is the
        injectable clock for tests. The URL is never logged.
        """
        current = _ensure_utc(now if now is not None else datetime.now(UTC))
        remaining = int((_ensure_utc(expires_at) - current).total_seconds())
        if remaining < MIN_SIGNED_URL_SECONDS:
            raise ObjectExpiredError(
                f"artifact lifetime expired or too short for a signed URL (remaining {remaining}s)"
            )
        lifetime = min(remaining, MAX_SIGNED_URL_SECONDS)
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=lifetime,
        )


def _safe_extension(extension: str | None) -> str:
    if not extension:
        return ""
    candidate = extension.strip().lower().lstrip(".")
    if candidate in SAFE_EXTENSIONS:
        return f".{candidate}"
    return ""
