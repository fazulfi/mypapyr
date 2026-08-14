"""JPG-to-PDF router tests (TL-05)."""

from __future__ import annotations

import io
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

import fakeredis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore
from app.routers import image_to_pdf as image_to_pdf_module
from app.routers.image_to_pdf import router
from app.security.classification import ScannerStatus, ScannerVerdict
from app.utils.r2 import R2Client, UploadReceipt


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
        del data
        return ScannerVerdict(status=ScannerStatus.CLEAN)


class _FakeR2(R2Client):
    """Minimal R2Client-compatible fixture; records uploads and deletes."""

    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes]] = []
        self.deleted: list[str] = []
        # Skip parent __init__ to avoid real AWS connection

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        del now
        return f"tmp/{extension or 'bin'}/{len(self.uploaded)}"

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
        self.uploaded.append((key, body))
        return UploadReceipt(
            key=key,
            size_bytes=len(body),
            content_type="image/jpeg",
            uploaded_at=datetime.now(UTC),
        )

    def delete_object(self, key: str) -> bool:
        self.deleted.append(key)
        return True


def _app_with(store: TaskStore, r2: _FakeR2) -> FastAPI:
    settings = _settings()
    app = FastAPI(title="test-jpg-to-pdf")
    app.include_router(image_to_pdf_module.router)
    app.state.settings = settings
    app.state.task_store = store
    app.state.r2_client = r2
    app.state.job_queue = JobQueue(
        settings,
        store,
        client=cast(StreamsRedisLike, fakeredis.FakeRedis()),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    app.state.scanner = _CleanScanner()
    return app


def _valid_jpg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color=(255, 255, 255)).save(buf, format="JPEG")
    return buf.getvalue()


def test_router_prefix() -> None:
    assert router.prefix == "/api/v1/tools/jpg-to-pdf"


def test_router_tag() -> None:
    assert router.tags == ["jpg-to-pdf"]


def test_tasks_endpoint_exists(client: TestClient) -> None:
    """Test that the /tasks endpoint exists."""
    response = client.post(
        "/api/v1/tools/jpg-to-pdf/tasks",
        files={"files": ("test.jpg", b"fake image content", "image/jpeg")},
    )
    # Should return 202 or a validation error, not 404
    assert response.status_code in [202, 400, 429]


def test_merge_mid_loop_orphan_cleanup_on_validation_failure() -> None:
    """I4: a validation failure after earlier uploads must not orphan them."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    r2 = _FakeR2()
    client = TestClient(_app_with(store, r2))

    response = client.post(
        "/api/v1/tools/jpg-to-pdf/tasks",
        files=[
            ("files", ("a.jpg", _valid_jpg_bytes(), "image/jpeg")),
            ("files", ("b.jpg", b"Not an image at all.", "image/jpeg")),
        ],
    )

    assert response.status_code >= 400 and response.status_code < 500
    assert len(r2.uploaded) == 1, "file 1 was uploaded before file 2 failed validation"
    uploaded_key = r2.uploaded[0][0]
    assert (
        uploaded_key in r2.deleted
    ), "file 1 must be deleted when a later file fails validation (no orphans)"