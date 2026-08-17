"""Tests for merge PDF router (TL-03) — including FR-SHARED-09 / FR-MERGE-04
per-index password handling for encrypted inputs."""

from __future__ import annotations

import io
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, cast

import fakeredis
import pikepdf
import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.config import Settings
from app.errors import register_error_handlers
from app.middleware import add_request_id_middleware
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore
from app.routers import merge as merge_module
from app.routers.merge import MergeWrongPasswordError, merge_password_handler, router
from app.security.classification import ScannerStatus, ScannerVerdict
from app.security.sanitize import PdfSanitizer
from app.utils.r2 import R2Client, UploadReceipt


def test_merge_router_exists() -> None:
    """Router has correct prefix."""
    assert router.prefix == "/api/v1/tools/merge-pdf"
    assert "merge" in router.tags


def test_merge_router_has_tasks_endpoint() -> None:
    """Router has POST /tasks endpoint."""
    routes = [route.path for route in router.routes if isinstance(route, APIRoute)]
    assert "/api/v1/tools/merge-pdf/tasks" in routes


def _settings() -> Settings:
    return Settings(
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
    )


class _CleanScanner:
    """Scanner double returning CLEAN verdict (U-SEC admission gate seam)."""

    def scan(self, data: bytes) -> ScannerVerdict:
        return ScannerVerdict(status=ScannerStatus.CLEAN)


@pytest.fixture
def store() -> TaskStore:
    return TaskStore(
        _settings(), client=cast(RedisLike, fakeredis.FakeRedis()), clock=lambda: datetime.now(UTC)
    )


@pytest.fixture
def queue(store: TaskStore) -> JobQueue:
    return JobQueue(
        _settings(),
        store,
        client=cast(StreamsRedisLike, fakeredis.FakeRedis()),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )


def _plain_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _encrypted_pdf_bytes(*, user: str = "userpw", owner: str = "ownerpw") -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf, encryption=pikepdf.Encryption(owner=owner, user=user, R=6))
    return buf.getvalue()


def _decrypted_expected_sanitized_bytes(data: bytes, password: str) -> bytes:
    sanitizer = PdfSanitizer()
    sanitizer.sanitize(data, password=password)
    output = sanitizer.output_bytes
    assert output is not None
    return output


_PDF_ID_RE = re.compile(rb"/ID\s*\[<[0-9a-fA-F]+>\s*<[0-9a-fA-F]+>\]")


def _without_pdf_id(data: bytes) -> bytes:
    """Strip the trailer ``/ID`` entry so PDFs from separate saves compare
    structurally: pikepdf regenerates the second file-identifier value on
    every ``save`` (pikepdf 10.x), so raw byte equality across two saves is
    never stable even for identical content."""
    return _PDF_ID_RE.sub(b"", data)


class FakeR2(R2Client):
    """Minimal R2Client-compatible fixture for tests."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}
        self.uploaded: list[tuple[str, bytes]] = []
        self.deleted: list[str] = []

    def upload_object(
        self,
        key: str,
        body: bytes,
        *,
        content_type: str | None = None,
        expires_at: datetime | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> UploadReceipt:
        del content_type, expires_at, metadata
        self._objects[key] = body
        self.uploaded.append((key, body))
        return UploadReceipt(
            key=key,
            size_bytes=len(body),
            content_type="application/pdf",
            uploaded_at=datetime.now(UTC),
        )

    def delete_object(self, key: str) -> bool:
        self._objects.pop(key, None)
        self.deleted.append(key)
        return True


@pytest.fixture
def r2() -> FakeR2:
    return FakeR2()


def _app_with(store: TaskStore, r2: FakeR2, queue: JobQueue | None = None) -> FastAPI:
    """App with the merge router wired exactly as ``create_app`` does.

    Error handlers and the request-id middleware are registered so envelope
    assertions (messageKey, request_id) behave like production; the
    contact-style password handler is what renders ``error.wrongPassword``.
    """
    settings = _settings()
    app = FastAPI(title="test-merge")
    register_error_handlers(app)
    add_request_id_middleware(app)
    app.add_exception_handler(MergeWrongPasswordError, merge_password_handler)
    app.include_router(merge_module.router)
    app.state.settings = settings
    app.state.task_store = store
    app.state.r2_client = r2
    app.state.job_queue = queue or JobQueue(
        settings,
        store,
        client=cast(StreamsRedisLike, fakeredis.FakeRedis()),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    app.state.scanner = _CleanScanner()
    return app


def _admit(
    client: TestClient,
    pdfs: list[bytes],
    *,
    passwords: dict[int, str] | None = None,
) -> Any:
    files = [("files", (f"doc{i}.pdf", data, "application/pdf")) for i, data in enumerate(pdfs)]
    data = {f"password_{i}": value for i, value in (passwords or {}).items()}
    return client.post("/api/v1/tools/merge-pdf/tasks", files=files, data=data)


def test_merge_admits_plain_pdfs_202_unchanged() -> None:
    """Plain PDFs still admit with 202 and upload sanitized (unchanged) bytes."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    r2 = FakeR2()
    client = TestClient(_app_with(store, r2))
    first, second = _plain_pdf_bytes(), _plain_pdf_bytes()
    response = _admit(client, [first, second])
    assert response.status_code == 202
    body = response.json()
    assert body["task_id"]
    assert body["state"] == "queued"
    assert len(r2.uploaded) == 2
    assert r2.uploaded[0][1] == first
    assert r2.uploaded[1][1] == second


def test_merge_admits_encrypted_pdf_with_correct_password_202() -> None:
    """Encrypted input + its own password → 202; R2 receives the decrypted
    sanitized rewrite, never the encrypted original.

    Comparison strips the trailer ``/ID``: pikepdf regenerates the second
    file-identifier value on every save, so raw byte equality across two
    saves is not stable (the sanitizer itself is deterministic apart from
    that regenerated identifier)."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    r2 = FakeR2()
    client = TestClient(_app_with(store, r2))
    locked = _encrypted_pdf_bytes()
    plain = _plain_pdf_bytes()
    expected = _decrypted_expected_sanitized_bytes(locked, "userpw")
    response = _admit(client, [locked, plain], passwords={0: "userpw"})
    assert response.status_code == 202
    assert len(r2.uploaded) == 2
    assert _without_pdf_id(r2.uploaded[0][1]) == _without_pdf_id(expected)
    assert r2.uploaded[1][1] == plain
    with pikepdf.Pdf.open(io.BytesIO(r2.uploaded[0][1])) as out:
        assert not out.is_encrypted


def test_merge_wrong_password_400_distinct_key(r2: FakeR2) -> None:
    """Wrong password → 400 with the distinct ``error.wrongPassword`` key."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = _admit(client, [_encrypted_pdf_bytes()], passwords={0: "wrong"})
    assert response.status_code == 400
    assert response.json()["error"]["messageKey"] == "error.wrongPassword"
    assert len(r2.uploaded) == 0


def test_merge_missing_password_400_distinct_key(r2: FakeR2) -> None:
    """No password field for an encrypted input → 400 ``error.wrongPassword``
    (the empty default cannot open the document)."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = _admit(client, [_encrypted_pdf_bytes()])
    assert response.status_code == 400
    assert response.json()["error"]["messageKey"] == "error.wrongPassword"


def test_merge_encrypted_with_empty_user_password_and_empty_field_202(r2: FakeR2) -> None:
    """An empty-user-password PDF admits when the client sends an explicitly
    empty ``password_<i>`` field (the field is present, the value is blank)."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    data = _encrypted_pdf_bytes(user="", owner="ownerpw")
    response = _admit(client, [data], passwords={0: ""})
    assert response.status_code == 202
    assert len(r2.uploaded) == 1


def test_merge_too_long_password_400_bad_request(r2: FakeR2) -> None:
    """A password longer than 1024 UTF-8 bytes is rejected as badRequest."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = _admit(client, [_plain_pdf_bytes()], passwords={0: "x" * 1025})
    assert response.status_code == 400
    assert response.json()["error"]["messageKey"] == "error.badRequest"


def test_merge_password_field_beyond_file_count_400(r2: FakeR2) -> None:
    """A ``password_<i>`` field whose index has no matching file is malformed."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = _admit(client, [_plain_pdf_bytes()], passwords={1: "whatever"})
    assert response.status_code == 400
    assert response.json()["error"]["messageKey"] == "error.badRequest"


def test_merge_no_files_400(r2: FakeR2) -> None:
    """Empty multipart (no files fields) fails closed; no task is created.

    The router still declares the ``files`` and ``passwords`` form
    parameters, so FastAPI rejects a body missing the ``files`` part with
    its generic 422 envelope; either way no task exists and no bytes move.
    """
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = client.post("/api/v1/tools/merge-pdf/tasks", data={"password_0": "x"})
    assert response.status_code in (400, 422)
    assert "password" not in response.text


def test_merge_corrupt_pdf_400_bad_request_not_wrong_password(r2: FakeR2) -> None:
    """Corrupt input stays ``error.badRequest`` — distinct from wrong password."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = _admit(client, [b"not a pdf at all"], passwords={0: "userpw"})
    assert response.status_code == 400
    assert response.json()["error"]["messageKey"] == "error.badRequest"


def test_merge_password_response_never_echoes_value(r2: FakeR2) -> None:
    """The wrong-password envelope and error path never leak the submitted
    value; the admitted task body and stored record carry no passwords."""
    secret = "s3cr3t-merge-password"
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    client = TestClient(_app_with(store, r2))
    response = _admit(client, [_encrypted_pdf_bytes()], passwords={0: secret})
    assert response.status_code == 400
    assert secret not in response.text
    assert "wrongPassword" in response.text

    client_ok = TestClient(_app_with(store, r2))
    response_ok = _admit(client_ok, [_plain_pdf_bytes(), _plain_pdf_bytes()])
    assert response_ok.status_code == 202
    assert secret not in response_ok.text
    task_id = response_ok.json()["task_id"]
    record = store.get(task_id)
    assert record is not None
    # The admitted record is DEC-174 minimal metadata: no password content.
    assert secret not in str(record)
    assert "password" not in str(record)
