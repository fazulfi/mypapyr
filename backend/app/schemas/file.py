"""Typed metadata-only file contracts.

Metadata-only by construction: byte counts and authoritative timestamps.
Content bytes, previews, passwords, signed URLs, object keys, and original
filenames are structurally excluded through ``extra="forbid"``.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileMetadata(BaseModel):
    """Metadata record for an admitted server-side file.

    Grounded fields only: byte count (exact byte counts are contract metadata
    on the capabilities surface) and the authoritative absolute expiry
    timestamp. Every other field is forbidden: content bytes, previews,
    passwords, signed URLs, object keys, and original filenames.
    """

    model_config = ConfigDict(extra="forbid")

    size_bytes: int = Field(ge=0, description="File size in bytes (metadata, not content).")
    expires_at: datetime = Field(description="Authoritative absolute expiry timestamp.")


class FileObjectMetadata(BaseModel):
    """R2 object custom metadata containing only the expiry timestamp.

    Additional custom metadata would violate the opaque-key and
    no-sensitive-metadata rule.
    """

    model_config = ConfigDict(extra="forbid")

    expires_at: datetime
