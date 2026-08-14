"""Tests for merge PDF router (TL-03) and the I3 origin fingerprint fix."""

from __future__ import annotations

import hashlib
import io
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, cast

import fakeredis
import pikepdf
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.config import Settings
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore
from app.routers import merge as merge_module
from app.security.classification import ScannerStatus, ScannerVerdict
from app.security.fair_use import fingerprint_origin
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
            content_type="application/pdf",
            uploaded_at=datetime.now(UTC),
        )

    def delete_object(self, key: str) -> bool:
        self.deleted.append(key)
        return True


class _RecordingQueue(JobQueue):
    """JobQueue subclass recording the origin passed to enqueue.

    Subclassing (not duck-typing) is required so the router's
    ``_resolve_queue`` isinstance gate admits this stub instead of
    replacing it with a real JobQueue over the environment Redis.
    """

    def __init__(self, settings: Settings, store: TaskStore) -> None:
        super().__init__(
            settings,
            store,
            client=cast(StreamsRedisLike, fakeredis.FakeRedis()),
            options=QueueOptions(clock=lambda: datetime.now(UTC)),
        )
        self.origins: list[str | None] = []
        self.routes: list[str] = []

    def enqueue(
        self, record: Any, *, origin: str | None = None, route: str | None = None
    ) -> Any:
        self.origins.append(origin)
        self.routes.append(route or record.tool)
        return record


def _app_with(
    store: TaskStore, queue: _RecordingQueue, r2: _FakeR2 | None = None
) -> FastAPI:
    settings = _settings()
    app = FastAPI(title="test-merge")
    app.include_router(merge_module.router)
    app.state.settings = settings
    app.state.task_store = store
    app.state.r2_client = r2 if r2 is not None else _FakeR2()
    app.state.job_queue = queue
    app.state.scanner = _CleanScanner()
    return app


def _valid_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _origin_request(
    *,
    headers: dict[str, str] | None = None,
    host: str = "198.51.100.5",
) -> Request:
    raw = [(k.lower().encode("utf-8"), v.encode("utf-8")) for k, v in (headers or {}).items()]
    scope = {
        "type": "http",
        "app": None,
        "method": "POST",
        "path": "/api/v1/tools/merge-pdf/tasks",
        "headers": raw,
        "query_string": b"",
        "client": (host, 54321),
    }
    return Request(scope)


def test_merge_router_exists() -> None:
    """Router has correct prefix."""
    assert merge_module.router.prefix == "/api/v1/tools/merge-pdf"
    assert "merge" in merge_module.router.tags


def test_merge_router_has_tasks_endpoint() -> None:
    """Router has POST /tasks endpoint."""
    routes = [route.path for route in merge_module.router.routes if isinstance(route, APIRoute)]
    assert "/api/v1/tools/merge-pdf/tasks" in routes


def test_resolve_origin_prefers_cf_connecting_ip() -> None:
    """CF-Connecting-IP wins over every fallback."""
    request = _origin_request(
        headers={
            "CF-Connecting-IP": "203.0.113.7",
            "X-Forwarded-For": "10.0.0.1, 10.0.0.2",
        }
    )
    assert merge_module._resolve_origin(request) == fingerprint_origin("203.0.113.7")


def test_resolve_origin_uses_first_x_forwarded_for_when_no_cf_header() -> None:
    """The first x-forwarded-for value is honored when CF-Connecting-IP is absent."""
    request = _origin_request(headers={"X-Forwarded-For": "10.0.0.1, 10.0.0.2"})
    assert merge_module._resolve_origin(request) == fingerprint_origin("10.0.0.1")


def test_resolve_origin_falls_back_to_client_host() -> None:
    """Without any proxy header the client host fingerprints admission."""
    request = _origin_request()
    assert merge_module._resolve_origin(request) == fingerprint_origin("198.51.100.5")


def test_resolve_origin_returns_hex_digest() -> None:
    """The helper returns a SHA-256 hexdigest, never a raw IP."""
    request = _origin_request(headers={"CF-Connecting-IP": "203.0.113.7"})
    origin = merge_module._resolve_origin(request)
    assert origin == hashlib.sha256(b"203.0.113.7").hexdigest()
    assert origin != "203.0.113.7"


def test_merge_admission_passes_real_origin_fingerprint() -> None:
    """Fair-use admission receives a real origin fingerprint (I3).

    The merge router must pass an origin derived from the request's
    ``CF-Connecting-IP`` header, never ``None`` and never the anonymous
    ``sha256(b"")`` bucket, otherwise every client shares one fair-use
    counter.
    """
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    queue = _RecordingQueue(_settings(), store)
    client = TestClient(_app_with(store, queue))
    ip_a = "203.0.113.7"
    ip_b = "198.51.100.9"

    first = client.post(
        "/api/v1/tools/merge-pdf/tasks",
        files=[("files", ("a.pdf", _valid_pdf_bytes(), "application/pdf"))],
        headers={"CF-Connecting-IP": ip_a},
    )
    second = client.post(
        "/api/v1/tools/merge-pdf/tasks",
        files=[("files", ("b.pdf", _valid_pdf_bytes(), "application/pdf"))],
        headers={"CF-Connecting-IP": ip_b},
    )

    assert first.status_code == 202
    assert second.status_code == 202
    assert queue.origins == [
        fingerprint_origin(ip_a),
        fingerprint_origin(ip_b),
    ], "the router must thread a real origin fingerprint into enqueue"


def test_merge_admission_origin_is_never_none_without_proxy_header() -> None:
    """Without any proxy header the client host still yields a real fingerprint."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    queue = _RecordingQueue(_settings(), store)
    client = TestClient(_app_with(store, queue))

    response = client.post(
        "/api/v1/tools/merge-pdf/tasks",
        files=[("files", ("a.pdf", _valid_pdf_bytes(), "application/pdf"))],
    )

    assert response.status_code == 202
    assert len(queue.origins) == 1
    assert queue.origins[0] is not None
    assert queue.origins[0] != fingerprint_origin("")


def test_merge_mid_loop_orphan_cleanup_on_validation_failure() -> None:
    """I4: a validation failure after earlier uploads must not orphan them."""
    store = TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    queue = _RecordingQueue(_settings(), store)
    r2 = _FakeR2()
    client = TestClient(_app_with(store, queue, r2=r2))

    response = client.post(
        "/api/v1/tools/merge-pdf/tasks",
        files=[
            ("files", ("a.pdf", _valid_pdf_bytes(), "application/pdf")),
            ("files", ("b.pdf", b"Not a PDF at all.", "application/pdf")),
        ],
    )

    assert response.status_code >= 400 and response.status_code < 500
    assert len(r2.uploaded) == 1, "file 1 was uploaded before file 2 failed validation"
    uploaded_key = r2.uploaded[0][0]
    assert (
        uploaded_key in r2.deleted
    ), "file 1 must be deleted when a later file fails validation (no orphans)"
