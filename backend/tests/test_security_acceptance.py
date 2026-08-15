"""U-FIXTURES: Hostile PDF fixture acceptance tests (BLKR-03, SEC-08).

Strict RED-GREEN-REFACTOR unit for Phase 5 U-FIXTURES atomic unit.

Fixture matrix (canonical committed bytes; see tests/verify_fixtures.py
for the sole SHA256 integrity mechanism):
1. js_auto_launch.pdf          - JavaScript /OpenAction auto-execute
2. embedded_attachment.pdf     - File attachment via /AF or FileAnnotation
3. openaction_launch.pdf       - Launch action executor
4. encrypted_protected.pdf     - Password-encrypted requires non-empty user password
5. corrupt_structure.pdf       - Structurally corrupt but recognizable header
6. benign_control.pdf          - Clean control should pass through

Behavioral acceptance proven:
- Active-content PDFs sanitized+uploaded under CLEAN scanner (SANITIZED-ACCEPTED)
- Password-protected PDF passes validation, then sanitizer REFUSES (PasswordError)
- Corrupt PDF rejected at validation (4xx)
- MALICIOUS scanner verdict causes zero R2/store/queue side effects
- Scanner-unavailable path uses hostile fixtures, zero side effects
- Benign PDF follows happy path (scan OK -> sanitize -> enqueue)
"""

from __future__ import annotations

import hashlib
import io
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import fakeredis
import pikepdf
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pikepdf import Name

from app.config import Settings
from app.errors import register_error_handlers
from app.queue.queue import STREAM_KEY, JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore
from app.routers import pdf_to_jpg
from app.security.classification import ScannerStatus, ScannerVerdict
from app.utils.r2 import R2Client, UploadReceipt

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "hostile"

_FIXTURE_HASHES = {
    "js_auto_launch.pdf": "a29b9f6dc9cd1ffc3258b4873f95d171e11cc8fc49bc1b8dcd8774c540f6b33e",
    "embedded_attachment.pdf": "40b32b232bff384e9b96c2598f9b30967e18be6014b8796e840d3a1b3af75652",
    "openaction_launch.pdf": "881dd83c01d40bec1075c6b5365daf352b43eff7bf45973424348863a7442908",
    "encrypted_protected.pdf": "f672bd3bb2cdbe6498f87f800283e3095660b0a1c87e05284851d7a0e925c3a5",
    "corrupt_structure.pdf": "102243890ddd86c465f70549a40252643564f94783d744b25eeb970d266c9f16",
    "benign_control.pdf": "070624b0807f199945362e54fe5fd67d9fdff56f3b49cee45ebaf36dd2756e40",
}


class _FakeR2(R2Client):
    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes]] = []

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        return f"tmp/test/{len(self.uploaded)}.{extension or 'bin'}"

    def upload_object(
        self,
        key: str,
        body: bytes,
        *,
        content_type: str | None = None,
        expires_at: datetime | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> UploadReceipt:
        self.uploaded.append((key, body))
        return UploadReceipt(
            key=key,
            size_bytes=len(body),
            content_type=content_type or "application/pdf",
            uploaded_at=datetime.now(UTC),
        )

    def delete_object(self, key: str) -> bool:
        return True


class _MaliciousScanner:
    def scan(self, data: bytes) -> ScannerVerdict:
        return ScannerVerdict(status=ScannerStatus.MALICIOUS)


class _UnavailableScanner:
    def scan(self, data: bytes) -> ScannerVerdict:
        return ScannerVerdict(status=ScannerStatus.UNAVAILABLE)


class _CleanScanner:
    def scan(self, data: bytes) -> ScannerVerdict:
        return ScannerVerdict(status=ScannerStatus.CLEAN)


def _fixture_bytes(filename: str) -> bytes:
    filepath = _FIXTURE_DIR / filename
    assert filepath.exists(), f"Fixture missing: {filepath}"
    return filepath.read_bytes()


def _make_test_app(
    scanner_obj: object,
) -> tuple[FastAPI, _FakeR2, JobQueue, fakeredis.FakeServer]:
    r2 = _FakeR2()
    server = fakeredis.FakeServer()

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(pdf_to_jpg.router)

    settings = Settings(
        r2_account_id="fake-account-id",
        r2_access_key_id="fake-access-key",
        r2_secret_access_key="fake-secret-key",
        r2_bucket_name="fake-bucket",
        allowed_origins=("http://localhost:3000",),
        retention_seconds=3600,
        default_timeout_seconds=180,
        redis_url="redis://localhost:6379/15",
        worker_cpus=1,
        worker_memory_bytes=2 * 1024**3,
        clamd_host="localhost",
        clamd_port=3310,
        scanner_timeout_seconds=10,
        scanner_enabled=True,
    )

    app.state.settings = settings
    app.state.task_store = TaskStore(
        settings,
        client=cast(RedisLike, fakeredis.FakeRedis(server=server)),
        clock=lambda: datetime.now(UTC),
    )
    app.state.r2_client = r2
    app.state.job_queue = JobQueue(
        settings,
        app.state.task_store,
        client=cast(StreamsRedisLike, fakeredis.FakeRedis(server=server)),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    app.state.scanner = scanner_obj

    return app, r2, app.state.job_queue, server


def _get_pdf_structure(data: bytes) -> dict[str, bool]:
    """Inspect PDF object model for dangerous structures."""
    try:
        with pikepdf.open(io.BytesIO(data)) as pdf:
            root = pdf.Root
            result: dict[str, bool] = {}
            if Name.OpenAction in root:
                result["has_open_action"] = True
            else:
                result["has_open_action"] = False
            names_dict = root.get(Name.Names)
            has_js = isinstance(names_dict, pikepdf.Dictionary) and Name.JavaScript in names_dict
            result["has_javascript_names"] = has_js
            result["has_attachments"] = bool(pdf.attachments)
            return result
    except Exception:
        return {"parse_error": True}


# --- SHA256 hash verification tests ---


def test_fixture_js_auto_launch_sha256() -> None:
    data = _fixture_bytes("js_auto_launch.pdf")
    computed = hashlib.sha256(data).hexdigest()
    assert computed == _FIXTURE_HASHES["js_auto_launch.pdf"]


def test_fixture_embedded_attachment_sha256() -> None:
    data = _fixture_bytes("embedded_attachment.pdf")
    computed = hashlib.sha256(data).hexdigest()
    assert computed == _FIXTURE_HASHES["embedded_attachment.pdf"]


def test_fixture_openaction_launch_sha256() -> None:
    data = _fixture_bytes("openaction_launch.pdf")
    computed = hashlib.sha256(data).hexdigest()
    assert computed == _FIXTURE_HASHES["openaction_launch.pdf"]


def test_fixture_encrypted_protected_sha256() -> None:
    data = _fixture_bytes("encrypted_protected.pdf")
    computed = hashlib.sha256(data).hexdigest()
    assert computed == _FIXTURE_HASHES["encrypted_protected.pdf"]


def test_fixture_corrupt_structure_sha256() -> None:
    data = _fixture_bytes("corrupt_structure.pdf")
    computed = hashlib.sha256(data).hexdigest()
    assert computed == _FIXTURE_HASHES["corrupt_structure.pdf"]


def test_fixture_benign_control_sha256() -> None:
    data = _fixture_bytes("benign_control.pdf")
    computed = hashlib.sha256(data).hexdigest()
    assert computed == _FIXTURE_HASHES["benign_control.pdf"]


# --- Sanitizer matrix tests (CLEAN scanner, active-content sanitized+uploaded) ---


def test_js_auto_launch_sanitized_and_uploaded_with_clean_scanner() -> None:
    """JS/OpenAction fixture is SANITIZED (not blocked), uploaded, and 202."""
    app, r2, _queue, server = _make_test_app(_CleanScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("js_auto_launch.pdf"))},
    )

    assert response.status_code == 202, (
        f"JS fixture should be sanitized+uploaded, got {response.status_code}"
    )

    assert len(r2.uploaded) == 1, "Sanitized JS PDF must upload to R2"

    # Verify uploaded bytes have JavaScript REMOVED
    uploaded_pdf = r2.uploaded[0][1]
    structure = _get_pdf_structure(uploaded_pdf)
    assert structure.get("has_open_action") is False, "OpenAction must be removed"
    assert structure.get("has_javascript_names") is False, "JavaScript must be removed"

    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 1, f"Sanitized JS PDF must enqueue once, got {queue_len}"


def test_embedded_attachment_sanitized_and_uploaded_with_clean_scanner() -> None:
    """Embedded attachment fixture is SANITIZED (not blocked), uploaded, and 202."""
    app, r2, _queue, server = _make_test_app(_CleanScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("embedded_attachment.pdf"))},
    )

    assert response.status_code == 202, (
        f"Embedded attachment should be sanitized+uploaded, got {response.status_code}"
    )

    assert len(r2.uploaded) == 1, "Sanitized attachment PDF must upload to R2"

    uploaded_pdf = r2.uploaded[0][1]
    structure = _get_pdf_structure(uploaded_pdf)
    assert structure.get("has_attachments") is False, "Attachments must be removed"

    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 1


def test_openaction_launch_sanitized_and_uploaded_with_clean_scanner() -> None:
    """Launch action fixture is SANITIZED (not blocked), uploaded, and 202."""
    app, r2, _queue, server = _make_test_app(_CleanScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("openaction_launch.pdf"))},
    )

    assert response.status_code == 202, (
        f"Launch fixture should be sanitized+uploaded, got {response.status_code}"
    )

    assert len(r2.uploaded) == 1, "Sanitized launch PDF must upload to R2"

    uploaded_pdf = r2.uploaded[0][1]
    structure = _get_pdf_structure(uploaded_pdf)
    assert structure.get("has_open_action") is False, "Launch action must be removed"

    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 1


# --- Encrypted fixture: passes validation, sanitizer refuses ---


def test_encrypted_protected_passes_validation_then_sanitizer_refuses() -> None:
    """Password-protected PDF passes validation (is_encrypted=True),
    but sanitizer REFUSES due to required non-empty password."""
    app, r2, _queue, server = _make_test_app(_CleanScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("encrypted_protected.pdf"))},
    )

    # Sanitizer refuses encrypted PDF (PasswordError -> REFUSED)
    # Router returns 400 (badRequest) for sanitization refusal
    assert 400 <= response.status_code < 500, (
        f"Expected 4xx for sanitizer refusal, got {response.status_code}"
    )

    assert len(r2.uploaded) == 0, "Sanitizer-refused PDF must NOT upload"

    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 0, "Sanitizer-refused PDF must NOT enqueue"


# --- Corrupt fixture: validation rejects ---


def test_corrupt_structure_rejected_by_validation() -> None:
    app, r2, _queue, server = _make_test_app(_CleanScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("corrupt_structure.pdf"))},
    )

    assert 400 <= response.status_code < 500
    body = response.json()
    assert body["error"]["category"] in ["validation", "security"]

    assert len(r2.uploaded) == 0
    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 0


# --- Benign control: happy path ---


def test_benign_clean_pdf_passes_with_scanner_and_sanitizer() -> None:
    app, r2, _queue, server = _make_test_app(_CleanScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("benign_control.pdf"))},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["state"] == "queued"
    assert body["task_id"]
    assert body["expires_at"]

    assert len(r2.uploaded) == 1
    uploaded_data = r2.uploaded[0][1]
    assert len(uploaded_data) > 0

    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 1, f"Clean PDF must enqueue once, got {queue_len}"


# --- MALICIOUS/UNAVAILABLE fake-scanner zero-side-effect tests ---


def test_scanner_blocks_malicious_pdf_with_side_effect_assertions() -> None:
    app, r2, _queue, server = _make_test_app(_MaliciousScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("js_auto_launch.pdf"))},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["error"]["messageKey"] == "error.forbidden"
    assert body["error"]["retryable"] is False

    assert len(r2.uploaded) == 0, "MALICIOUS payload must NEVER upload"
    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 0, f"MALICIOUS payload must NEVER enqueue, got {queue_len}"


def test_scanner_unavailable_blocks_without_side_effects() -> None:
    app, r2, _queue, server = _make_test_app(_UnavailableScanner())
    client = TestClient(app)

    response = client.post(
        "/api/v1/tools/pdf-to-jpg/tasks",
        files={"file": ("test.pdf", _fixture_bytes("benign_control.pdf"))},
    )

    assert response.status_code == 429
    body = response.json()
    assert body["error"]["messageKey"] == "error.rateLimited"
    assert body["error"]["retryable"] is True

    assert len(r2.uploaded) == 0
    redis_client = fakeredis.FakeRedis(server=server)
    queue_len = redis_client.xlen(STREAM_KEY)
    assert queue_len == 0


def test_all_hostile_fixtures_blocked_or_rejected_with_malicious_scanner() -> None:
    """Under MALICIOUS scanner, ALL hostile fixtures are blocked with zero side effects."""
    hostile_fixtures = [
        "js_auto_launch.pdf",
        "embedded_attachment.pdf",
        "openaction_launch.pdf",
        "encrypted_protected.pdf",
        "corrupt_structure.pdf",
    ]

    for fixture_name in hostile_fixtures:
        app, r2, _queue, server = _make_test_app(_MaliciousScanner())
        client = TestClient(app)

        response = client.post(
            "/api/v1/tools/pdf-to-jpg/tasks",
            files={"file": ("test.pdf", _fixture_bytes(fixture_name))},
        )

        status_ok = response.status_code in [400, 403, 429]
        assert status_ok, (
            f"{fixture_name} should be blocked/rejected, got "
            f"{response.status_code}: {response.text[:100]}"
        )

        assert len(r2.uploaded) == 0, f"{fixture_name} uploaded despite hostile classification"
        redis_client = fakeredis.FakeRedis(server=server)
        queue_len = redis_client.xlen(STREAM_KEY)
        assert queue_len == 0, f"{fixture_name} enqueued despite hostile classification"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
