"""PDF and image input validation with closed-category fail-closed rejections.

Owned by BE-02 (execution-matrix.md); consumed by BE-08 (capabilities),
SEC-01 (threat classification) and the tool tasks. The validation order
follows the legacy reference (``papyr-reference/backend/utils/pdf_validator.py``):
empty payload, declared MIME, declared extension, magic bytes, size, then
decode. Magic bytes are authoritative — declared MIME/extension are
cross-checked against each other and against the detected content, never
trusted on their own.

Rejections raise :class:`ValidationRejection` carrying only a safe closed
category (:class:`ValidationFailure`) plus a message key from the existing
envelope vocabulary (``app/errors.py``). Filenames, contents, passwords,
decoded bytes, engine details and parser warnings are never part of any
exception or inspection field (DEC-175, DEC-169, DEC-088).

PDFs are inspected with pikepdf (the R-28-approved engine, pinned runtime
dependency): ``PasswordError`` and ``PdfError`` are handled distinctly
internally, but the only observable outcome is ``is_encrypted`` (an
inspection field) or the generic ``corrupt`` category — the password is
never attempted. ``attempt_recovery=True`` (pikepdf default) means
recoverable damage passes with a warning count; only unparseable files are
rejected as corrupt.

Images are inspected with Pillow (a hard transitive of the pinned pikepdf
runtime dependency; see the dependency-foundation record). Declared
dimensions are checked against the approved pixel cap *before* any decode
(DEC-093): a hand-crafted header declaring more than ``max_pixels`` is
rejected without allocating or decompressing anything, and Pillow's own
``DecompressionBombError`` is mapped to the same category as a defensive
second layer. Structural corruption is detected via ``verify()``; a file
that passes the magic gate but decodes to an unsupported container (for
example an MPO, which shares JPEG magic) is rejected as corrupt. Files
whose MIME or extension conflicts with the detected format are rejected as
``type_mismatch`` before any decode.

Limits default to the R-03-approved table (gate-entry.md section 2):
100 MB / 1000 pages for PDFs, 20 MB / 20 MP for images. Callers (BE-08/TL)
may override per tool; the module constants are the single reference copy
outside the BE-08 capabilities table.
"""

from __future__ import annotations

import io
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Literal

import pikepdf
from PIL import Image
from PIL.Image import DecompressionBombError

PDF_MAGIC: Final = b"%PDF"
PNG_MAGIC: Final = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC: Final = b"\xff\xd8\xff"
WEBP_RIFF_MAGIC: Final = b"RIFF"
WEBP_MAGIC: Final = b"WEBP"
WEBP_MAGIC_OFFSET: Final = 8
WEBP_HEADER_SIZE: Final = 12

PDF_MIME_TYPES: Final[frozenset[str]] = frozenset({"application/pdf"})
PDF_EXTENSIONS: Final[frozenset[str]] = frozenset({".pdf"})
PDF_EXTENSIONS_BY_MIME: Final[dict[str, frozenset[str]]] = {
    "application/pdf": frozenset({".pdf"}),
}

IMAGE_MIME_TYPES: Final[frozenset[str]] = frozenset({"image/jpeg", "image/png", "image/webp"})
IMAGE_EXTENSIONS: Final[frozenset[str]] = frozenset({".jpg", ".jpeg", ".png", ".webp"})
IMAGE_EXTENSIONS_BY_MIME: Final[dict[str, frozenset[str]]] = {
    "image/jpeg": frozenset({".jpg", ".jpeg"}),
    "image/png": frozenset({".png"}),
    "image/webp": frozenset({".webp"}),
}
IMAGE_MIMES_BY_FORMAT: Final[dict[str, frozenset[str]]] = {
    "jpeg": frozenset({"image/jpeg"}),
    "png": frozenset({"image/png"}),
    "webp": frozenset({"image/webp"}),
}
IMAGE_EXTENSIONS_BY_FORMAT: Final[dict[str, frozenset[str]]] = {
    "jpeg": frozenset({".jpg", ".jpeg"}),
    "png": frozenset({".png"}),
    "webp": frozenset({".webp"}),
}
_IMAGE_FORMATS_BY_NAME: Final[dict[str, Literal["jpeg", "png", "webp"]]] = {
    "JPEG": "jpeg",
    "PNG": "png",
    "WEBP": "webp",
}

DEFAULT_MAX_PDF_SIZE_BYTES: Final = 100 * 1024 * 1024
DEFAULT_MAX_IMAGE_SIZE_BYTES: Final = 20 * 1024 * 1024
DEFAULT_MAX_PDF_PAGES: Final = 1000
DEFAULT_MAX_IMAGE_PIXELS: Final = 20_000_000

MESSAGE_KEY_BAD_REQUEST: Final = "error.badRequest"
MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE: Final = "error.unsupportedMediaType"
MESSAGE_KEY_PAYLOAD_TOO_LARGE: Final = "error.payloadTooLarge"
MESSAGE_KEY_INVALID_REQUEST: Final = "error.invalidRequest"


class ValidationFailure(StrEnum):
    """Closed safe rejection categories (DEC-169, DEC-088).

    Each maps to a message key in the existing envelope vocabulary; the
    values never carry payload details.
    """

    EMPTY = "empty"
    TYPE_MISMATCH = "type_mismatch"
    SIZE_EXCEEDED = "size_exceeded"
    CORRUPT = "corrupt"
    RESOURCE_EXCEEDED = "resource_exceeded"


class ValidationRejection(Exception):
    """Fail-closed rejection carrying only safe closed-category fields.

    ``str()`` yields the bare category value; filenames, contents,
    passwords, and engine details never reach the exception.
    """

    failure: ValidationFailure
    message_key: str
    retryable: bool

    def __init__(
        self,
        failure: ValidationFailure,
        *,
        message_key: str,
        retryable: bool = False,
    ) -> None:
        super().__init__(failure.value)
        self.failure = failure
        self.message_key = message_key
        self.retryable = retryable


@dataclass(frozen=True)
class PdfInspection:
    """Typed metadata for an admitted PDF payload.

    ``page_count`` is ``None`` only when the file is encrypted and the
    password is required to open it (pages unknown until decryption); an
    encrypted file with an empty user password opens without a password and
    therefore carries a real page count. ``recovery_warnings_count`` counts
    parser recovery warnings — the warnings themselves are never exposed.
    """

    format: Literal["pdf"]
    size_bytes: int
    page_count: int | None
    is_encrypted: bool
    recovery_warnings_count: int


@dataclass(frozen=True)
class ImageInspection:
    """Typed metadata for an admitted image payload.

    ``width``/``height`` are the decoded declared dimensions and ``pixels``
    is their product — the decoded pixel bound that gates decompression
    (DEC-093).
    """

    format: Literal["jpeg", "png", "webp"]
    size_bytes: int
    width: int
    height: int
    pixels: int


def _normalize_extension(raw: str) -> str:
    extension = raw.strip().lower()
    if not extension:
        return ""
    if not extension.startswith("."):
        extension = f".{extension}"
    return extension


def _check_declared_type(
    *,
    declared_mime: str | None,
    declared_extension: str | None,
    mime_types: frozenset[str],
    extensions: frozenset[str],
    extensions_by_mime: Mapping[str, frozenset[str]],
) -> tuple[str | None, str | None]:
    """Validate declared MIME/extension against the allowed family.

    Blank declarations are treated as absent (the magic gate stays
    authoritative); present declarations must be allowed and mutually
    consistent. Returns the normalized ``(mime, extension)`` pair.
    """
    mime = None if declared_mime is None else declared_mime.strip().lower()
    ext = None if declared_extension is None else _normalize_extension(declared_extension)
    if mime == "":
        mime = None
    if ext == "":
        ext = None
    if mime is not None and mime not in mime_types:
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    if ext is not None and ext not in extensions:
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    if mime is not None and ext is not None and ext not in extensions_by_mime[mime]:
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    return mime, ext


def _detect_image_format(data: bytes) -> Literal["jpeg", "png", "webp"] | None:
    """Detect the image family from magic bytes, never from declarations."""
    if data.startswith(PNG_MAGIC):
        return "png"
    if data.startswith(JPEG_MAGIC):
        return "jpeg"
    if (
        len(data) >= WEBP_HEADER_SIZE
        and data[:4] == WEBP_RIFF_MAGIC
        and (data[WEBP_MAGIC_OFFSET:WEBP_HEADER_SIZE] == WEBP_MAGIC)
    ):
        return "webp"
    return None


def validate_pdf(
    data: bytes,
    *,
    declared_mime: str | None = None,
    declared_extension: str | None = None,
    max_size_bytes: int = DEFAULT_MAX_PDF_SIZE_BYTES,
    max_pages: int = DEFAULT_MAX_PDF_PAGES,
) -> PdfInspection:
    """Validate untrusted PDF bytes; returns metadata or raises rejection.

    Order: empty payload, declared MIME/extension consistency, ``%PDF``
    magic bytes, size cap, then pikepdf open. ``PasswordError`` (encrypted
    file, password never attempted) reports ``is_encrypted=True`` with an
    unknown page count; ``PdfError`` rejects as ``corrupt``. Page count is
    checked against ``max_pages`` only when the file could be opened.
    """
    if not data:
        raise ValidationRejection(ValidationFailure.EMPTY, message_key=MESSAGE_KEY_BAD_REQUEST)
    _check_declared_type(
        declared_mime=declared_mime,
        declared_extension=declared_extension,
        mime_types=PDF_MIME_TYPES,
        extensions=PDF_EXTENSIONS,
        extensions_by_mime=PDF_EXTENSIONS_BY_MIME,
    )
    if not data.startswith(PDF_MAGIC):
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    if len(data) > max_size_bytes:
        raise ValidationRejection(
            ValidationFailure.SIZE_EXCEEDED,
            message_key=MESSAGE_KEY_PAYLOAD_TOO_LARGE,
        )
    try:
        pdf = pikepdf.open(io.BytesIO(data))
    except pikepdf.PasswordError:
        return PdfInspection(
            format="pdf",
            size_bytes=len(data),
            page_count=None,
            is_encrypted=True,
            recovery_warnings_count=0,
        )
    except pikepdf.PdfError:
        raise ValidationRejection(
            ValidationFailure.CORRUPT,
            message_key=MESSAGE_KEY_BAD_REQUEST,
        ) from None
    with pdf:
        page_count = len(pdf.pages)
        if page_count > max_pages:
            raise ValidationRejection(
                ValidationFailure.RESOURCE_EXCEEDED,
                message_key=MESSAGE_KEY_INVALID_REQUEST,
            )
        return PdfInspection(
            format="pdf",
            size_bytes=len(data),
            page_count=page_count,
            is_encrypted=pdf.is_encrypted,
            recovery_warnings_count=len(pdf.get_warnings()),
        )


def validate_image(
    data: bytes,
    *,
    declared_mime: str | None = None,
    declared_extension: str | None = None,
    max_size_bytes: int = DEFAULT_MAX_IMAGE_SIZE_BYTES,
    max_pixels: int = DEFAULT_MAX_IMAGE_PIXELS,
) -> ImageInspection:
    """Validate untrusted image bytes; returns metadata or raises rejection.

    Order: empty payload, declared MIME/extension consistency, magic-byte
    family detection, declared-vs-detected consistency, size cap, header
    decode, decoded pixel bound, then structural ``verify()``. The pixel
    bound fires on declared dimensions before any pixel data is
    decompressed (DEC-093); Pillow's own ``DecompressionBombError`` maps to
    the same category as a second layer. Structural decode failures reject
    as ``corrupt``.
    """
    if not data:
        raise ValidationRejection(ValidationFailure.EMPTY, message_key=MESSAGE_KEY_BAD_REQUEST)
    mime, ext = _check_declared_type(
        declared_mime=declared_mime,
        declared_extension=declared_extension,
        mime_types=IMAGE_MIME_TYPES,
        extensions=IMAGE_EXTENSIONS,
        extensions_by_mime=IMAGE_EXTENSIONS_BY_MIME,
    )
    detected = _detect_image_format(data)
    if detected is None:
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    if mime is not None and mime not in IMAGE_MIMES_BY_FORMAT[detected]:
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    if ext is not None and ext not in IMAGE_EXTENSIONS_BY_FORMAT[detected]:
        raise ValidationRejection(
            ValidationFailure.TYPE_MISMATCH,
            message_key=MESSAGE_KEY_UNSUPPORTED_MEDIA_TYPE,
        )
    if len(data) > max_size_bytes:
        raise ValidationRejection(
            ValidationFailure.SIZE_EXCEEDED,
            message_key=MESSAGE_KEY_PAYLOAD_TOO_LARGE,
        )
    try:
        image = Image.open(io.BytesIO(data))
    except DecompressionBombError:
        raise ValidationRejection(
            ValidationFailure.RESOURCE_EXCEEDED,
            message_key=MESSAGE_KEY_INVALID_REQUEST,
        ) from None
    except OSError:
        raise ValidationRejection(
            ValidationFailure.CORRUPT,
            message_key=MESSAGE_KEY_BAD_REQUEST,
        ) from None
    try:
        width, height = image.size
        if width * height > max_pixels:
            raise ValidationRejection(
                ValidationFailure.RESOURCE_EXCEEDED,
                message_key=MESSAGE_KEY_INVALID_REQUEST,
            )
        image.verify()
    except (OSError, SyntaxError):
        raise ValidationRejection(
            ValidationFailure.CORRUPT,
            message_key=MESSAGE_KEY_BAD_REQUEST,
        ) from None
    decoded_format = _IMAGE_FORMATS_BY_NAME.get(image.format or "")
    if decoded_format is None:
        raise ValidationRejection(
            ValidationFailure.CORRUPT,
            message_key=MESSAGE_KEY_BAD_REQUEST,
        )
    return ImageInspection(
        format=decoded_format,
        size_bytes=len(data),
        width=width,
        height=height,
        pixels=width * height,
    )
