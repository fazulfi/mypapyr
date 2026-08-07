"""Router contract tests for the consolidated pdf-to-jpg admission endpoint (TL-06, U-ROUTER).

Asserts that the real mounted ``/api/v1/tools/pdf-to-jpg/tasks`` route carries the full
validation/sanitization/admission pipeline with ``route="pdf-to-jpg"`` queue metadata, and that
the misspelled ``pdf_to_jgy`` module/route no longer exists. Mirrors the seams and fixtures of
``test_compress.py`` and ``test_wiring.py``.
"""

from __future__ import annotations

import importlib
import io
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

import fakeredis
import pikepdf
import pytest
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app, create_app
from app.queue.queue import STREAM_KEY, JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore
from app.security.sanitize import PdfSanitizer
from app.utils.r2 import R2Client, UploadReceipt

PDF_TO_JPG_TASKS_PATH = "/api/v1/tools/pdf-to-jpg/tasks"
ENTRY_FIELDS = frozenset({"task_id", "tool", "route", "origin"})


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


class _UploadR2(R2Client):
    """R2Client-backed stub recording uploads without a network client."""

    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes]] = []

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        del extension, now
        return f"tmp/2026-08-07/{uuid.uuid4().hex}.pdf"

    def upload_object(self, key: str, body: bytes, **kwargs: object) -> UploadReceipt:
        del kwargs
        self.uploaded.append((key, body))
        return UploadReceipt(
            key=key,
            size_bytes=len(body),
            content_type="application/pdf",
            uploaded_at=datetime.now(UTC),
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


def _pdf_to_jpg_app(*, store: TaskStore, r2: R2Client, queue: JobQueue | None = None) -> FastAPI:
    instance = create_app()
    instance.state.task_store = store
    instance.state.r2_client = r2
    instance.state.job_queue = queue or JobQueue(
        _settings(),
        store,
        client=fakeredis.FakeRedis(),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    return instance


def _make_store(client: RedisLike | None = None) -> TaskStore:
    return TaskStore(
        _settings(),
        client=client or cast(RedisLike, fakeredis.FakeRedis()),
        clock=lambda: datetime.now(UTC),
    )


def _mounted_api_routes(application: FastAPI) -> list[APIRoute]:
    """Resolve direct and FastAPI 0.141+ included-router API routes."""
    routes: list[APIRoute] = []
    for route in application.routes:
        if isinstance(route, APIRoute):
            routes.append(route)
            continue
        original_router = getattr(route, "original_router", None)
        if isinstance(original_router, APIRouter):
            routes.extend(
                nested_route
                for nested_route in original_router.routes
                if isinstance(nested_route, APIRoute)
            )
    return routes


def _stream_fields(server: fakeredis.FakeServer) -> list[Mapping[bytes, bytes]]:
    entries = fakeredis.FakeRedis(server=server).xrange(STREAM_KEY, "-", "+", count=100)
    return [fields for _, fields in entries]


# --- route identity and mounting ------------------------------------------------


def test_factory_mounts_pdf_to_jpg_tasks_route_exactly_once() -> None:
    """The factory app mounts POST /api/v1/tools/pdf-to-jpg/tasks exactly once."""
    routes = _mounted_api_routes(create_app())
    assert [route.path for route in routes].count(PDF_TO_JPG_TASKS_PATH) == 1


def test_module_level_app_mounts_pdf_to_jpg_tasks_route() -> None:
    """The module-level ``app`` export also carries the pdf-to-jpg tasks route."""
    assert PDF_TO_JPG_TASKS_PATH in [route.path for route in _mounted_api_routes(app)]


def test_typo_module_not_importable() -> None:
    """The misspelled ``app.routers.pdf_to_jgy`` module must not exist."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("app.routers.pdf_to_jgy")


def test_no_typo_route_is_mounted() -> None:
    """No mounted route path may carry the ``jgy`` misspelling."""
    for route in _mounted_api_routes(create_app()):
        assert "jgy" not in route.path


# --- full admission behavior on the real mounted route ---------------------------


def test_pdf_to_jpg_admission_success_on_factory_app() -> None:
    """POST valid PDF via factory → 202 TaskAdmission envelope, queued task, R2 upload."""
    store = _make_store()
    r2 = _UploadR2()
    client = TestClient(_pdf_to_jpg_app(store=store, r2=r2))
    response = client.post(PDF_TO_JPG_TASKS_PATH, files={"file": ("test.pdf", _valid_pdf_bytes())})
    assert response.status_code == 202
    data = response.json()
    assert data["state"] == "queued"
    assert data["task_id"]
    assert data["expires_at"]
    record = store.get(data["task_id"])
    assert record.tool == "pdf-to-jpg"
    assert len(record.objects) == 1
    assert len(r2.uploaded) == 1
    assert r2.uploaded[0][0] == record.objects[0]


def test_pdf_to_jpg_admission_uploads_sanitized_bytes_not_raw() -> None:
    """The uploaded R2 bytes equal the sanitizer output for the same input."""
    data = _valid_pdf_bytes()
    sanitizer = PdfSanitizer()
    sanitizer.sanitize(data)
    expected = sanitizer.output_bytes
    assert expected is not None

    store = _make_store()
    r2 = _UploadR2()
    client = TestClient(_pdf_to_jpg_app(store=store, r2=r2))
    response = client.post(PDF_TO_JPG_TASKS_PATH, files={"file": ("test.pdf", data)})
    assert response.status_code == 202
    assert len(r2.uploaded) == 1
    assert r2.uploaded[0][1] == expected


def test_pdf_to_jpg_enqueue_route_field_is_pdf_to_jpg() -> None:
    """The captured queue entry carries route=pdf-to-jpg with the locked vocabulary."""
    server = fakeredis.FakeServer()
    store = _make_store(cast(RedisLike, fakeredis.FakeRedis(server=server)))
    queue = JobQueue(
        _settings(),
        store,
        client=cast(StreamsRedisLike, fakeredis.FakeRedis(server=server)),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    r2 = _UploadR2()
    client = TestClient(_pdf_to_jpg_app(store=store, r2=r2, queue=queue))
    response = client.post(PDF_TO_JPG_TASKS_PATH, files={"file": ("test.pdf", _valid_pdf_bytes())})
    assert response.status_code == 202

    entries = _stream_fields(server)
    assert len(entries) == 1
    fields = {key.decode("utf-8"): value.decode("utf-8") for key, value in entries[0].items()}
    assert set(fields) == ENTRY_FIELDS
    assert fields["tool"] == "pdf-to-jpg"
    assert fields["route"] == "pdf-to-jpg"
    assert fields["task_id"] == response.json()["task_id"]


def test_pdf_to_jpg_admission_rejects_non_pdf_safe_4xx_no_effects() -> None:
    """Non-PDF upload → stable 400 envelope, no R2 upload, no stream entry."""
    server = fakeredis.FakeServer()
    store = _make_store(cast(RedisLike, fakeredis.FakeRedis(server=server)))
    r2 = _UploadR2()
    client = TestClient(_pdf_to_jpg_app(store=store, r2=r2))
    response = client.post(
        PDF_TO_JPG_TASKS_PATH, files={"file": ("test.pdf", b"Not a PDF at all.")}
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "bad_request"
    assert body["error"]["category"] == "validation"
    assert body["error"]["messageKey"] == "error.badRequest"
    assert body["error"]["retryable"] is False
    assert body["request_id"]
    assert len(r2.uploaded) == 0
    assert _stream_fields(server) == []


def test_pdf_to_jpg_refuses_password_protected_pdf_4xx_no_upload() -> None:
    """Password-protected PDF → 4xx fail closed, no R2 upload (SEC gate retained)."""
    store = _make_store()
    r2 = _UploadR2()
    client = TestClient(_pdf_to_jpg_app(store=store, r2=r2))
    response = client.post(
        PDF_TO_JPG_TASKS_PATH,
        files={"file": ("test.pdf", _hostile_password_protected_pdf_bytes())},
    )
    assert 400 <= response.status_code < 500
    assert len(r2.uploaded) == 0
