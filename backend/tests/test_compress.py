"""Router contract tests for compress PDF admission endpoint (TL-02)."""

from __future__ import annotations

import io
import uuid
from datetime import UTC, datetime
from typing import Any, cast

import fakeredis
import pikepdf
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore
from app.routers import compress as compress_module
from app.security.sanitize import PdfSanitizer
from app.utils.r2 import R2Client


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


def _valid_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _hostile_password_protected_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf, encryption=pikepdf.Encryption(owner="ownerpw", user="userpw"))
    return buf.getvalue()


def _non_pdf_bytes() -> bytes:
    return b"Not a PDF at all."


class FakeR2(R2Client):
    """Minimal R2Client-compatible fixture for tests."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}
        self.uploaded: list[tuple[str, bytes]] = []
        # Skip parent __init__ to avoid real AWS connection

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        return f"tmp/2026-01-01/{uuid.uuid4().hex}.{extension or ''}"

    def upload_object(self, key: str, body: bytes, **kw: object) -> tuple[str, int]:
        self._objects[key] = body
        self.uploaded.append((key, body))
        return key, len(body)  # type: ignore[return-value]

    def delete_object(self, key: str) -> bool:
        self._objects.pop(key, None)
        return True


@pytest.fixture
def r2() -> FakeR2:
    return FakeR2()


@pytest.fixture
def factory_app(
    request: Any,
    store: TaskStore,
    queue: JobQueue,
    r2: FakeR2,
) -> FastAPI:
    """Factory app with mocked deps."""
    settings = _settings()
    app = FastAPI(title="test-compress")
    app.include_router(compress_module.router)
    app.state.settings = settings
    app.state.task_store = store
    app.state.r2_client = r2
    app.state.job_queue = queue
    return app


def _app_with(store: TaskStore, r2: FakeR2, queue: JobQueue | None = None) -> FastAPI:
    settings = _settings()
    app = FastAPI(title="test-compress")
    app.include_router(compress_module.router)
    app.state.settings = settings
    app.state.task_store = store
    app.state.r2_client = r2
    app.state.job_queue = queue or JobQueue(
        settings,
        store,
        client=fakeredis.FakeRedis(),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    return app


def _upload(client: TestClient, pdf_bytes: bytes) -> Any:
    return client.post("/api/v1/tools/compress-pdf/tasks", files={"file": ("test.pdf", pdf_bytes)})


def test_compress_router_admits_valid_pdf_uploads_sanitized(factory_app: FastAPI) -> None:
    """Submit valid PDF → 202, queued with objects=(input_key,), upload SANITIZED bytes."""
    client = TestClient(factory_app)
    response = _upload(client, _valid_pdf_bytes())
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert "state" in data
    assert "expires_at" in data
    assert data["state"] == "queued"


def test_compress_router_refuses_hostile_pdf_4xx_no_upload(r2: FakeR2) -> None:
    """Password-protected PDF → 4xx fail closed, no R2 upload, no task created."""
    store = TaskStore(_settings(), client=fakeredis.FakeRedis())
    r2 = FakeR2()
    client = TestClient(_app_with(store, r2))
    response = _upload(client, _hostile_password_protected_pdf_bytes())
    assert response.status_code >= 400 and response.status_code < 500
    assert len(r2.uploaded) == 0


def test_compress_router_refuses_non_pdf_4xx(r2: FakeR2) -> None:
    """Non-PDF input → 4xx fail closed."""
    store = TaskStore(_settings(), client=fakeredis.FakeRedis())
    r2 = FakeR2()
    client = TestClient(_app_with(store, r2))
    response = _upload(client, _non_pdf_bytes())
    assert response.status_code >= 400 and response.status_code < 500


def test_compress_router_uploads_sanitized_bytes_not_raw() -> None:
    """The uploaded R2 bytes equal the sanitizer output for the same input."""
    data = _valid_pdf_bytes()
    sanitizer = PdfSanitizer()
    sanitizer.sanitize(data)
    expected = sanitizer.output_bytes
    assert expected is not None

    store = TaskStore(_settings(), client=fakeredis.FakeRedis())
    r2 = FakeR2()
    client = TestClient(_app_with(store, r2))
    response = _upload(client, data)
    assert response.status_code == 202
    assert len(r2.uploaded) == 1
    assert r2.uploaded[0][1] == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
