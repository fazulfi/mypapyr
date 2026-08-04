"""PDF and image input validation tests (BE-02).

Locks the ``app.security.validation`` contract: typed inspection outputs
(``PdfInspection``, ``ImageInspection``), fail-closed rejections that carry
only safe closed categories (DEC-169, DEC-088), the legacy validation order
(empty, declared MIME, declared extension, magic bytes, size, decode —
``papyr-reference/backend/utils/pdf_validator.py``), real magic-byte
validation that never trusts MIME/extension, distinct internal handling of
encrypted vs corrupt PDFs (only ``is_encrypted`` is exposed), page bounds,
decoded pixel bounds that reject decompression bombs before any decode
(DEC-093), and message keys drawn from the existing envelope vocabulary
(``app/errors.py``: badRequest, unsupportedMediaType, payloadTooLarge,
invalidRequest).

Fixtures are generated in-test with pikepdf (pinned runtime dependency)
and Pillow (hard transitive of pikepdf, per the dependency-foundation
record): valid PDFs, password-protected PDFs (user and empty-user
passwords), truncated/recoverable PDFs, valid JPEG/PNG/WebP images,
truncated images, and hand-crafted PNG/JPEG headers that declare
dimensions above the approved 20 MP pixel cap (R-03 gate-entry section 2)
while carrying no decodable pixel data — proving the limit fires on
declared bounds before any decode. A two-frame MPO (JPEG magic, decoded by
Pillow as format ``MPO``) exercises the unsupported-container branch.
"""

from __future__ import annotations

import io
import struct
import warnings
import zlib

import pikepdf
import pytest
from PIL import Image

from app.security.validation import (
    DEFAULT_MAX_IMAGE_PIXELS,
    DEFAULT_MAX_IMAGE_SIZE_BYTES,
    DEFAULT_MAX_PDF_PAGES,
    DEFAULT_MAX_PDF_SIZE_BYTES,
    ImageInspection,
    PdfInspection,
    ValidationFailure,
    ValidationRejection,
    validate_image,
    validate_pdf,
)


def _pdf_bytes(page_count: int = 2) -> bytes:
    buffer = io.BytesIO()
    pdf = pikepdf.Pdf.new()
    for _ in range(page_count):
        pdf.add_blank_page(page_size=(100, 100))
    pdf.save(buffer)
    pdf.close()
    return buffer.getvalue()


def _encrypted_pdf_bytes(*, user: str, owner: str) -> bytes:
    buffer = io.BytesIO()
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page(page_size=(100, 100))
    pdf.save(buffer, encryption=pikepdf.Encryption(owner=owner, user=user, R=6))
    pdf.close()
    return buffer.getvalue()


def _image_bytes(fmt: str, size: tuple[int, int] = (8, 6)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, (200, 30, 40)).save(buffer, format=fmt)
    return buffer.getvalue()


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    length = struct.pack(">I", len(payload))
    crc = struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
    return length + tag + payload + crc


def _crafted_png(width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IEND", b"")


def _jpeg_segment(marker: bytes, payload: bytes) -> bytes:
    return marker + struct.pack(">H", len(payload) + 2) + payload


def _crafted_jpeg(width: int, height: int) -> bytes:
    app0 = _jpeg_segment(b"\xff\xe0", b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
    sof0 = _jpeg_segment(b"\xff\xc0", struct.pack(">BHHB", 8, height, width, 3))
    sos = _jpeg_segment(b"\xff\xda", b"\x01\x01\x00\x00\x3f\x00")
    return b"\xff\xd8" + app0 + sof0 + sos + (b"\x00" * 32) + b"\xff\xd9"


def _mpo_bytes() -> bytes:
    buffer = io.BytesIO()
    first = Image.new("RGB", (4, 4), (1, 2, 3))
    second = Image.new("RGB", (4, 4), (4, 5, 6))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        first.save(buffer, format="MPO", append_images=[second])
    return buffer.getvalue()


def _corrupt_png_pixel_data(data: bytes) -> bytes:
    offset = 8
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        if data[offset + 4 : offset + 8] == b"IDAT" and length > 8:
            corrupted = bytearray(data)
            corrupted[offset + 12] ^= 0xFF
            return bytes(corrupted)
        offset += 12 + length
    raise AssertionError("fixture PNG has no IDAT chunk")


def _pdf_rejection(
    data: bytes,
    *,
    declared_mime: str | None = None,
    declared_extension: str | None = None,
    max_size_bytes: int = DEFAULT_MAX_PDF_SIZE_BYTES,
    max_pages: int = DEFAULT_MAX_PDF_PAGES,
) -> ValidationRejection:
    with pytest.raises(ValidationRejection) as excinfo:
        validate_pdf(
            data,
            declared_mime=declared_mime,
            declared_extension=declared_extension,
            max_size_bytes=max_size_bytes,
            max_pages=max_pages,
        )
    return excinfo.value


def test_default_limits_match_approved_r03_values() -> None:
    assert DEFAULT_MAX_PDF_SIZE_BYTES == 100 * 1024 * 1024
    assert DEFAULT_MAX_IMAGE_SIZE_BYTES == 20 * 1024 * 1024
    assert DEFAULT_MAX_PDF_PAGES == 1000
    assert DEFAULT_MAX_IMAGE_PIXELS == 20_000_000


class TestValidatePdf:
    def test_reports_valid_inspection(self) -> None:
        data = _pdf_bytes(2)
        inspection = validate_pdf(data)
        assert isinstance(inspection, PdfInspection)
        assert inspection.format == "pdf"
        assert inspection.size_bytes == len(data)
        assert inspection.page_count == 2
        assert inspection.is_encrypted is False
        assert inspection.recovery_warnings_count == 0

    def test_accepts_matching_declared_metadata(self) -> None:
        data = _pdf_bytes(2)
        inspection = validate_pdf(data, declared_mime="application/pdf", declared_extension=".pdf")
        assert inspection.page_count == 2

    def test_accepts_without_declared_metadata(self) -> None:
        inspection = validate_pdf(_pdf_bytes(1))
        assert inspection.page_count == 1

    def test_accepts_uppercase_extension(self) -> None:
        inspection = validate_pdf(_pdf_bytes(1), declared_extension=".PDF")
        assert inspection.page_count == 1

    def test_accepts_extension_without_leading_dot(self) -> None:
        inspection = validate_pdf(_pdf_bytes(1), declared_extension="pdf")
        assert inspection.page_count == 1

    def test_accepts_blank_declared_metadata(self) -> None:
        inspection = validate_pdf(_pdf_bytes(1), declared_mime="", declared_extension=" ")
        assert inspection.page_count == 1

    def test_rejects_empty_payload(self) -> None:
        rejection = _pdf_rejection(b"")
        assert rejection.failure is ValidationFailure.EMPTY
        assert rejection.message_key == "error.badRequest"
        assert rejection.retryable is False

    def test_rejects_unsupported_mime(self) -> None:
        rejection = _pdf_rejection(_pdf_bytes(1), declared_mime="text/plain")
        assert rejection.failure is ValidationFailure.TYPE_MISMATCH
        assert rejection.message_key == "error.unsupportedMediaType"

    def test_rejects_unsupported_extension(self) -> None:
        rejection = _pdf_rejection(_pdf_bytes(1), declared_extension=".txt")
        assert rejection.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_non_pdf_magic(self) -> None:
        rejection = _pdf_rejection(b"PK\x03\x04zip-like bytes")
        assert rejection.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_oversized(self) -> None:
        rejection = _pdf_rejection(_pdf_bytes(2), max_size_bytes=64)
        assert rejection.failure is ValidationFailure.SIZE_EXCEEDED
        assert rejection.message_key == "error.payloadTooLarge"

    def test_rejects_corrupt_content(self) -> None:
        rejection = _pdf_rejection(b"%PDF-1.7\n" + b"x" * 128)
        assert rejection.failure is ValidationFailure.CORRUPT
        assert rejection.message_key == "error.badRequest"

    def test_accepts_recoverable_truncation_with_warning_count(self) -> None:
        data = _pdf_bytes(2)
        truncated = data[: len(data) // 2]
        inspection = validate_pdf(truncated)
        assert inspection.page_count == 2
        assert inspection.is_encrypted is False
        assert inspection.recovery_warnings_count > 0

    def test_reports_encrypted_requiring_password(self) -> None:
        data = _encrypted_pdf_bytes(user="user-pw", owner="owner-pw")
        inspection = validate_pdf(data)
        assert inspection.is_encrypted is True
        assert inspection.page_count is None
        assert inspection.recovery_warnings_count == 0

    def test_reports_encrypted_with_empty_user_password(self) -> None:
        data = _encrypted_pdf_bytes(user="", owner="owner-pw")
        inspection = validate_pdf(data)
        assert inspection.is_encrypted is True
        assert inspection.page_count == 1

    def test_rejects_page_limit_exceeded(self) -> None:
        rejection = _pdf_rejection(_pdf_bytes(3), max_pages=2)
        assert rejection.failure is ValidationFailure.RESOURCE_EXCEEDED
        assert rejection.message_key == "error.invalidRequest"

    def test_accepts_page_limit_boundary(self) -> None:
        inspection = validate_pdf(_pdf_bytes(2), max_pages=2)
        assert inspection.page_count == 2

    def test_accepts_under_default_page_limit(self) -> None:
        inspection = validate_pdf(_pdf_bytes(3))
        assert inspection.page_count == 3

    def test_rejection_is_safe_and_typed(self) -> None:
        rejection = _pdf_rejection(b"", declared_mime="application/pdf")
        assert str(rejection) == "empty"
        assert isinstance(rejection.failure, ValidationFailure)
        assert rejection.message_key == "error.badRequest"
        assert rejection.retryable is False


class TestValidateImage:
    def test_reports_valid_jpeg(self) -> None:
        data = _image_bytes("JPEG")
        inspection = validate_image(data)
        assert isinstance(inspection, ImageInspection)
        assert inspection.format == "jpeg"
        assert inspection.size_bytes == len(data)
        assert inspection.width == 8
        assert inspection.height == 6
        assert inspection.pixels == 48

    def test_reports_valid_png(self) -> None:
        inspection = validate_image(_image_bytes("PNG"))
        assert inspection.format == "png"
        assert inspection.width == 8
        assert inspection.height == 6

    def test_reports_valid_webp(self) -> None:
        inspection = validate_image(_image_bytes("WEBP"))
        assert inspection.format == "webp"
        assert inspection.width == 8
        assert inspection.height == 6

    def test_accepts_matching_declared_metadata(self) -> None:
        inspection = validate_image(
            _image_bytes("JPEG"),
            declared_mime="image/jpeg",
            declared_extension=".jpg",
        )
        assert inspection.format == "jpeg"

    def test_accepts_uppercase_mime(self) -> None:
        inspection = validate_image(_image_bytes("PNG"), declared_mime="IMAGE/PNG")
        assert inspection.format == "png"

    def test_rejects_empty_payload(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(b"")
        assert excinfo.value.failure is ValidationFailure.EMPTY
        assert excinfo.value.message_key == "error.badRequest"

    def test_rejects_unsupported_mime(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_image_bytes("JPEG"), declared_mime="text/plain")
        assert excinfo.value.failure is ValidationFailure.TYPE_MISMATCH
        assert excinfo.value.message_key == "error.unsupportedMediaType"

    def test_rejects_unsupported_extension(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_image_bytes("JPEG"), declared_extension=".pdf")
        assert excinfo.value.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_inconsistent_mime_and_extension(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(
                _image_bytes("PNG"), declared_mime="image/png", declared_extension=".jpg"
            )
        assert excinfo.value.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_magic_mismatch_with_declared_mime(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_image_bytes("JPEG"), declared_mime="image/png")
        assert excinfo.value.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_magic_mismatch_with_declared_extension(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_image_bytes("JPEG"), declared_extension=".png")
        assert excinfo.value.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_missing_image_magic(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(b"not an image at all")
        assert excinfo.value.failure is ValidationFailure.TYPE_MISMATCH

    def test_rejects_oversized(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_image_bytes("JPEG"), max_size_bytes=64)
        assert excinfo.value.failure is ValidationFailure.SIZE_EXCEEDED
        assert excinfo.value.message_key == "error.payloadTooLarge"

    def test_rejects_truncated_png(self) -> None:
        data = _image_bytes("PNG")
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(data[: len(data) // 2])
        assert excinfo.value.failure is ValidationFailure.CORRUPT
        assert excinfo.value.message_key == "error.badRequest"

    def test_rejects_truncated_jpeg(self) -> None:
        data = _image_bytes("JPEG")
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(data[: len(data) // 2])
        assert excinfo.value.failure is ValidationFailure.CORRUPT

    def test_rejects_png_magic_with_garbage(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(b"\x89PNG\r\n\x1a\n" + b"garbage" * 20)
        assert excinfo.value.failure is ValidationFailure.CORRUPT

    def test_rejects_png_with_corrupt_pixel_data(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_corrupt_png_pixel_data(_image_bytes("PNG")))
        assert excinfo.value.failure is ValidationFailure.CORRUPT

    def test_rejects_declared_pixel_bomb_png_before_decode(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_crafted_png(5000, 4500))
        assert excinfo.value.failure is ValidationFailure.RESOURCE_EXCEEDED
        assert excinfo.value.message_key == "error.invalidRequest"

    def test_rejects_declared_pixel_bomb_jpeg_before_decode(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_crafted_jpeg(5000, 4500))
        assert excinfo.value.failure is ValidationFailure.RESOURCE_EXCEEDED

    def test_accepts_pixel_limit_boundary(self) -> None:
        inspection = validate_image(_image_bytes("PNG", (200, 100)), max_pixels=20_000)
        assert inspection.pixels == 20_000

    def test_rejects_pixel_limit_just_above(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_image_bytes("PNG", (201, 100)), max_pixels=20_000)
        assert excinfo.value.failure is ValidationFailure.RESOURCE_EXCEEDED

    def test_decompression_bomb_error_is_resource_exceeded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pytest.raises(ValidationRejection) as excinfo:
                validate_image(_image_bytes("PNG", (10, 10)))
        assert excinfo.value.failure is ValidationFailure.RESOURCE_EXCEEDED

    def test_rejects_unsupported_container_with_jpeg_magic(self) -> None:
        with pytest.raises(ValidationRejection) as excinfo:
            validate_image(_mpo_bytes(), declared_mime="image/jpeg")
        assert excinfo.value.failure is ValidationFailure.CORRUPT

    def test_pixels_are_decoded_bounds(self) -> None:
        inspection = validate_image(_image_bytes("WEBP", (12, 7)))
        assert inspection.pixels == inspection.width * inspection.height == 84
