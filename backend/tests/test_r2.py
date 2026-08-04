"""Cloudflare R2 client contract tests (BE-03).

Covers the privacy-safe object-key scheme (``tmp/<YYYY-MM-DD>/<32-hex>``
plus a safe-extension allowlist, with no original-filename leakage), upload
with bounded ASCII-only metadata (``expires-at`` mirrored; client-side
8,192-byte guard), idempotent delete (missing key counts as success, real
service failures propagate), and presigned GET URLs capped at
``min(remaining lifetime, 300 s)`` (DEC-170) with expired artifacts
rejected.

Fixture boundaries follow r2-pikepdf-reference-audit.md (section C.3 and
E): **moto performs no authentication and never enforces expiry or
signatures**, so no test here claims R2 403 ``ExpiredRequest`` /
``SignatureDoesNotMatch`` behavior or the 8,192-byte server-side limit —
those are real-R2 integration concerns. moto proves S3 object behavior
(put/head/delete round-trips, idempotent deletes, URL fetch of a stored
object); the R2-specific configuration (endpoint, region ``auto``, SigV4,
credential scope) is asserted through client-side URL inspection and
botocore behavior, which requires no network.

boto3/moto/botocore do not ship ``py.typed`` (test_dependencies.py notes
the same), so they are reached through importlib with a single typed cast
crossing point; the presigned-URL fetch uses ``requests`` (a moto
transitive dependency) because moto's interception does not cover a bare
``urllib3.PoolManager`` request.
"""

from __future__ import annotations

import importlib
import io
import logging
import re
import urllib.parse
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest

from app.config import Settings
from app.utils.logging import PapyrJsonHandler
from app.utils.r2 import (
    MAX_METADATA_BYTES,
    MAX_SIGNED_URL_SECONDS,
    InvalidContentTypeError,
    InvalidObjectKeyError,
    MetadataTooLargeError,
    NonAsciiMetadataError,
    ObjectExpiredError,
    R2Client,
    R2Error,
)

# --- untyped third-party crossing points (audit C.3; test_dependencies.py) ---
boto3 = cast(Any, importlib.import_module("boto3"))
moto = cast(Any, importlib.import_module("moto"))
requests = cast(Any, importlib.import_module("requests"))
ClientError = cast(Any, importlib.import_module("botocore.exceptions")).ClientError

R2_ENDPOINT = "https://test-account.r2.cloudflarestorage.com"
TEST_BUCKET = "test-bucket"
TEST_ACCESS_KEY_ID = "test-access-key-id"
TEST_SECRET_ACCESS_KEY = "test-secret-access-key"
KEY = "tmp/2026-08-03/" + "0" * 32 + ".pdf"
NOW = datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC)

_KEY_RE = re.compile(r"^tmp/\d{4}-\d{2}-\d{2}/[0-9a-f]{32}(?:\.[a-z0-9]+)?$")


class _FakeClient:
    """Minimal S3 surface used to stub client-side behavior under test."""

    def __init__(
        self,
        *,
        put_error: Exception | None = None,
        delete_error: Exception | None = None,
    ) -> None:
        self._put_error = put_error
        self._delete_error = delete_error
        self.put_calls: list[dict[str, object]] = []
        self.deleted_keys: list[str] = []

    def put_object(self, **kwargs: object) -> dict[str, object]:
        self.put_calls.append(kwargs)
        if self._put_error is not None:
            raise self._put_error
        return {}

    def delete_object(self, **kwargs: object) -> dict[str, object]:
        deleted = kwargs.get("Key")
        if isinstance(deleted, str):
            self.deleted_keys.append(deleted)
        if self._delete_error is not None:
            raise self._delete_error
        return {}

    def generate_presigned_url(self, *args: object, **kwargs: object) -> str:
        return "https://example.invalid/presigned"


def _client_error(code: str) -> Any:
    return ClientError(
        {"Error": {"Code": code, "Message": "boom"}, "ResponseMetadata": {}},
        "DeleteObject",
    )


def _parse_params(url: str) -> dict[str, str]:
    parsed = urllib.parse.urlsplit(url)
    return {key: values[0] for key, values in urllib.parse.parse_qs(parsed.query).items()}


@pytest.fixture
def settings() -> Settings:
    return Settings(
        r2_account_id="test-account",
        r2_access_key_id=TEST_ACCESS_KEY_ID,
        r2_secret_access_key=TEST_SECRET_ACCESS_KEY,
        r2_bucket_name=TEST_BUCKET,
        allowed_origins=("http://localhost:3000",),
        r2_endpoint=R2_ENDPOINT,
    )


@pytest.fixture
def moto_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """A moto S3 backend served at the R2-style endpoint (audit C.2).

    ``MOTO_S3_CUSTOM_ENDPOINTS`` must be set before the mock starts. The
    bucket is created with ``us-east-1`` because moto does not implement
    R2's region-auto aliasing (audit gap list item 10); the production
    client keeps ``region_name="auto"`` and is asserted separately.
    """
    monkeypatch.setenv("MOTO_S3_CUSTOM_ENDPOINTS", R2_ENDPOINT)
    with moto.mock_aws():
        client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=TEST_ACCESS_KEY_ID,
            aws_secret_access_key=TEST_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
        client.create_bucket(Bucket=TEST_BUCKET)
        yield client


@pytest.fixture
def r2_client(settings: Settings, moto_client: Any) -> R2Client:
    return R2Client(settings, client=moto_client)


# --- object-key generation: shape and no filename leakage ---


def test_build_object_key_shape(settings: Settings) -> None:
    client = R2Client(settings)
    with_ext = client.build_object_key(extension="pdf", now=NOW)
    without_ext = client.build_object_key(now=NOW)
    assert re.fullmatch(_KEY_RE, with_ext) is not None
    assert re.fullmatch(_KEY_RE, without_ext) is not None
    assert with_ext.startswith("tmp/2026-08-03/")
    assert with_ext.endswith(".pdf")
    assert not without_ext.endswith(".")


@pytest.mark.parametrize(
    ("raw", "expected_suffix"),
    [
        (".PDF", ".pdf"),
        ("pdf", ".pdf"),
        ("JPEG", ".jpeg"),
        (".exe", ""),
        (".html", ""),
        (".pdf.js", ""),
        ("/etc/passwd", ""),
        ("..\\..\\..\\evil.pdf", ""),
        ("my secret report (FINAL).PDF", ""),
        ("", ""),
        (None, ""),
    ],
)
def test_build_object_key_safe_extension_allowlist(
    settings: Settings, raw: str | None, expected_suffix: str
) -> None:
    key = R2Client(settings).build_object_key(extension=raw, now=NOW)
    assert re.fullmatch(_KEY_RE, key) is not None
    assert key.endswith(expected_suffix)


def test_build_object_key_never_leaks_original_filename(settings: Settings) -> None:
    key = R2Client(settings).build_object_key(extension="my secret report (FINAL).PDF", now=NOW)
    lowered = key.lower()
    assert "secret" not in lowered
    assert "report" not in lowered
    assert "final" not in lowered
    assert "(" not in key and ")" not in key


def test_build_object_key_uses_utc_partition(settings: Settings) -> None:
    client = R2Client(settings)
    key = client.build_object_key(now=datetime(2026, 8, 3, 23, 59, 59, tzinfo=UTC))
    assert key.startswith("tmp/2026-08-03/")
    naive = client.build_object_key(now=datetime(2026, 8, 3, 0, 30, 0))
    assert naive.startswith("tmp/2026-08-03/")


def test_build_object_key_ids_are_unique(settings: Settings) -> None:
    client = R2Client(settings)
    assert client.build_object_key(now=NOW) != client.build_object_key(now=NOW)


# --- client construction: R2 endpoint, region auto, SigV4 (no network) ---


def test_client_endpoint_derived_from_account_id(settings: Settings) -> None:
    no_endpoint = Settings(
        r2_account_id="test-account",
        r2_access_key_id=TEST_ACCESS_KEY_ID,
        r2_secret_access_key=TEST_SECRET_ACCESS_KEY,
        r2_bucket_name=TEST_BUCKET,
        allowed_origins=("http://localhost:3000",),
    )
    url = R2Client(no_endpoint).generate_signed_url(
        KEY, expires_at=NOW + timedelta(seconds=300), now=NOW
    )
    assert urllib.parse.urlsplit(url).netloc == "test-account.r2.cloudflarestorage.com"


def test_client_explicit_endpoint_wins(settings: Settings) -> None:
    explicit = Settings(
        r2_account_id="test-account",
        r2_access_key_id=TEST_ACCESS_KEY_ID,
        r2_secret_access_key=TEST_SECRET_ACCESS_KEY,
        r2_bucket_name=TEST_BUCKET,
        allowed_origins=("http://localhost:3000",),
        r2_endpoint="https://storage.example.com",
    )
    url = R2Client(explicit).generate_signed_url(
        KEY, expires_at=NOW + timedelta(seconds=300), now=NOW
    )
    assert urllib.parse.urlsplit(url).netloc == "storage.example.com"


def test_presigned_url_signature_params(settings: Settings) -> None:
    url = R2Client(settings).generate_signed_url(
        KEY, expires_at=NOW + timedelta(seconds=300), now=NOW
    )
    params = _parse_params(url)
    assert params["X-Amz-Algorithm"] == "AWS4-HMAC-SHA256"
    assert params["X-Amz-Expires"] == "300"
    credential = params["X-Amz-Credential"]
    assert credential.startswith(f"{TEST_ACCESS_KEY_ID}/")
    assert credential.endswith("/auto/s3/aws4_request")
    assert params["X-Amz-SignedHeaders"] == "host"
    assert "X-Amz-Date" in params
    assert len(params["X-Amz-Signature"]) == 64
    assert urllib.parse.urlsplit(url).netloc == "test-account.r2.cloudflarestorage.com"


# --- presigned URLs: expiry cap and expired-artifact rejection ---


@pytest.mark.parametrize(
    ("remaining", "expected"),
    [
        (1, 1),
        (60, 60),
        (299, 299),
        (300, 300),
        (301, 300),
        (3600, 300),
        (604800, 300),
    ],
)
def test_presigned_url_expiry_never_exceeds_authoritative_deadline(
    settings: Settings, remaining: int, expected: int
) -> None:
    expires_at = NOW + timedelta(seconds=remaining)
    url = R2Client(settings).generate_signed_url(KEY, expires_at=expires_at, now=NOW)
    assert _parse_params(url)["X-Amz-Expires"] == str(expected)
    assert expected <= remaining
    assert expected <= MAX_SIGNED_URL_SECONDS


def test_presigned_url_rejects_expired_artifact(settings: Settings) -> None:
    client = R2Client(settings)
    with pytest.raises(ObjectExpiredError):
        client.generate_signed_url(KEY, expires_at=NOW, now=NOW)
    with pytest.raises(ObjectExpiredError):
        client.generate_signed_url(KEY, expires_at=NOW - timedelta(seconds=1), now=NOW)


def test_presigned_url_treats_naive_datetimes_as_utc(settings: Settings) -> None:
    url = R2Client(settings).generate_signed_url(
        KEY,
        expires_at=datetime(2026, 8, 3, 12, 2, 0),
        now=datetime(2026, 8, 3, 12, 0, 0),
    )
    assert _parse_params(url)["X-Amz-Expires"] == "120"


def test_presigned_url_fetches_object_while_valid(r2_client: R2Client, moto_client: Any) -> None:
    """moto accepts unsigned fetches (audit C.3): this proves the URL maps
    to the stored object, NOT that R2 enforces expiry or signatures."""
    key = r2_client.build_object_key(extension="pdf", now=NOW)
    body = b"%PDF-1.4 fake content"
    r2_client.upload_object(key, body, content_type="application/pdf")
    url = r2_client.generate_signed_url(key, expires_at=NOW + timedelta(seconds=300), now=NOW)
    response = requests.get(url, timeout=5)
    assert response.status_code == 200
    assert response.content == body


# --- upload: materialized bytes, opaque keys, safe content type, bounded ASCII metadata ---


@pytest.mark.parametrize(
    "unsafe_key",
    [
        "Alice-tax-return.pdf",
        "uploads/Alice-tax-return.pdf",
        "tmp/2026-08-03/../../Alice-tax-return.pdf",
        "tmp/2026-08-03/" + "0" * 32 + ".exe",
    ],
)
def test_upload_object_rejects_non_opaque_keys_before_storage(
    settings: Settings, unsafe_key: str
) -> None:
    fake = _FakeClient()
    client = R2Client(settings, client=fake)

    with pytest.raises(InvalidObjectKeyError):
        client.upload_object(unsafe_key, b"data")

    assert fake.put_calls == []


def test_upload_object_accepts_generated_opaque_key(settings: Settings) -> None:
    fake = _FakeClient()
    client = R2Client(settings, client=fake)
    key = client.build_object_key(extension="pdf", now=NOW)

    receipt = client.upload_object(key, b"data")

    assert receipt.key == key
    assert fake.put_calls[0]["Key"] == key


def test_upload_object_round_trip_with_expiry_metadata(
    r2_client: R2Client, moto_client: Any
) -> None:
    key = r2_client.build_object_key(extension="pdf", now=NOW)
    receipt = r2_client.upload_object(
        key,
        b"%PDF-1.4 fake",
        content_type="application/pdf",
        expires_at=NOW,
    )
    assert receipt.key == key
    assert receipt.size_bytes == 13
    assert receipt.content_type == "application/pdf"
    assert isinstance(receipt.uploaded_at, datetime)
    head = moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert head["ContentLength"] == 13
    assert head["ContentType"] == "application/pdf"
    assert head["Metadata"] == {"expires-at": "2026-08-03T12:00:00+00:00"}


def test_upload_object_default_content_type(r2_client: R2Client, moto_client: Any) -> None:
    key = r2_client.build_object_key(now=NOW)
    r2_client.upload_object(key, b"data")
    head = moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert head["ContentType"] == "application/octet-stream"


def test_upload_object_mirrors_expires_at_for_naive_datetime(
    r2_client: R2Client, moto_client: Any
) -> None:
    key = r2_client.build_object_key(now=NOW)
    r2_client.upload_object(key, b"data", expires_at=datetime(2026, 8, 3, 12, 0, 0))
    head = moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert head["Metadata"] == {"expires-at": "2026-08-03T12:00:00+00:00"}


def test_upload_object_rejects_non_bytes(r2_client: R2Client) -> None:
    with pytest.raises(TypeError):
        r2_client.upload_object("tmp/2026-08-03/abc.pdf", "not bytes")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "unsafe",
    [
        "application/pdf\r\nX-Evil: 1",
        "text/html<script>alert(1)</script>",
        "<application/pdf>",
        'application/pdf; charset=utf-8" onload="x',
        "application/ pdf",
    ],
)
def test_upload_object_rejects_unsafe_content_type(r2_client: R2Client, unsafe: str) -> None:
    with pytest.raises(InvalidContentTypeError):
        r2_client.upload_object(KEY, b"data", content_type=unsafe)


def test_upload_object_accepts_content_type_with_parameters(
    r2_client: R2Client, moto_client: Any
) -> None:
    key = r2_client.build_object_key(now=NOW)
    r2_client.upload_object(key, b"data", content_type="text/plain; charset=utf-8")
    head = moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert head["ContentType"] == "text/plain; charset=utf-8"


@pytest.mark.parametrize(
    "metadata",
    [{"note": "caf\u00e9"}, {"caf\u00e9": "x"}, {"a": "\u00fcber"}],
)
def test_upload_metadata_non_ascii_rejected(r2_client: R2Client, metadata: dict[str, str]) -> None:
    with pytest.raises(NonAsciiMetadataError):
        r2_client.upload_object(KEY, b"data", metadata=metadata)


def test_upload_metadata_over_8192_rejected(r2_client: R2Client, moto_client: Any) -> None:
    key = r2_client.build_object_key(now=NOW)
    oversized = {"k": "a" * MAX_METADATA_BYTES}  # key(1) + value(8192) = 8193 > 8192
    with pytest.raises(MetadataTooLargeError):
        r2_client.upload_object(key, b"data", metadata=oversized)
    with pytest.raises(ClientError):
        moto_client.head_object(Bucket=TEST_BUCKET, Key=key)


def test_upload_metadata_exactly_8192_allowed(r2_client: R2Client, moto_client: Any) -> None:
    key = r2_client.build_object_key(now=NOW)
    boundary = {"k": "a" * (MAX_METADATA_BYTES - 1)}  # key(1) + value(8191) = 8192
    receipt = r2_client.upload_object(key, b"data", metadata=boundary)
    assert receipt.key == key
    head = moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert head["Metadata"] == boundary


# --- delete: idempotent, missing object counts as success ---


def test_delete_object_removes_object(r2_client: R2Client, moto_client: Any) -> None:
    key = r2_client.build_object_key(extension="pdf", now=NOW)
    r2_client.upload_object(key, b"data", content_type="application/pdf")
    assert r2_client.delete_object(key) is True
    with pytest.raises(ClientError):
        moto_client.head_object(Bucket=TEST_BUCKET, Key=key)


def test_delete_object_idempotent(r2_client: R2Client) -> None:
    key = r2_client.build_object_key(extension="pdf", now=NOW)
    assert r2_client.delete_object(key) is True
    assert r2_client.delete_object(key) is True


def test_delete_object_not_found_treated_as_success(settings: Settings) -> None:
    fake = _FakeClient(delete_error=_client_error("NoSuchKey"))
    client = R2Client(settings, client=fake)
    assert client.delete_object(KEY) is True
    assert fake.deleted_keys == [KEY]


def test_delete_object_propagates_service_failures(settings: Settings) -> None:
    fake = _FakeClient(delete_error=_client_error("InternalError"))
    client = R2Client(settings, client=fake)
    with pytest.raises(ClientError):
        client.delete_object(KEY)


# --- privacy: keys and signed URLs never reach logs (DEC-170, DEC-025) ---


def _capture_r2_logs() -> tuple[io.StringIO, PapyrJsonHandler, int]:
    stream = io.StringIO()
    handler = PapyrJsonHandler(stream=stream)
    logger = logging.getLogger("app.utils.r2")
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return stream, handler, previous


def test_r2_never_logs_keys_or_urls(r2_client: R2Client, settings: Settings) -> None:
    stream, handler, previous = _capture_r2_logs()
    logger = logging.getLogger("app.utils.r2")
    try:
        key = r2_client.build_object_key(extension="pdf", now=NOW)
        r2_client.upload_object(key, b"data", content_type="application/pdf", expires_at=NOW)
        url = r2_client.generate_signed_url(key, expires_at=NOW + timedelta(seconds=300), now=NOW)
        r2_client.delete_object(key)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)
    output = stream.getvalue()
    assert key not in output
    assert url not in output
    assert "r2 upload ok" in output
    assert '"size_bytes":4' in output
    # DEC-175 treats the "content" stem as prohibited, so even the content
    # type is redacted from telemetry; the client logs only size_bytes.
    assert "application/pdf" not in output


def test_upload_failure_logs_without_key(settings: Settings) -> None:
    fake = _FakeClient(put_error=_client_error("SlowDown"))
    client = R2Client(settings, client=fake)
    stream, handler, previous = _capture_r2_logs()
    logger = logging.getLogger("app.utils.r2")
    try:
        with pytest.raises(ClientError):
            client.upload_object(KEY, b"data", content_type="application/pdf")
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)
    output = stream.getvalue()
    assert KEY not in output
    assert "r2 upload failed" in output


# --- interface surface for downstream tasks (BE-07, BE-09) ---


def test_public_interface_exposed(settings: Settings) -> None:
    client = R2Client(settings)
    assert client.bucket_name == TEST_BUCKET
    for name in ("build_object_key", "upload_object", "delete_object", "generate_signed_url"):
        assert callable(getattr(client, name))


def test_error_types_share_r2_base() -> None:
    for error in (
        ObjectExpiredError,
        MetadataTooLargeError,
        NonAsciiMetadataError,
        InvalidContentTypeError,
    ):
        assert issubclass(error, R2Error)
        assert issubclass(error, RuntimeError)
