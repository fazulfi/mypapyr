"""Single-integration-owner wiring tests (BE-09 wiring wave).

``app/main.py`` is the sole owner that mounts the BE-06 status, BE-08
capabilities, and BE-09 download routers — each exactly once — while
preserving the health/readiness, request-id, security-header, logging, and
stable-error-envelope contracts. ``app/routers/__init__.py`` stays free of
APIRouter re-exports (locked in test_schemas.py). These tests run against
``create_app()`` only; the module-level ``app`` export is checked
separately.
"""

from __future__ import annotations

import io
import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

import fakeredis
import pikepdf
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app import routers as routers_package
from app.config import Settings
from app.main import app, create_app
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskRecord, TaskStore, TransitionPayload
from app.routers.download import router as download_router
from app.schemas.job import ResultSummary
from app.tasks.state_machine import JobEvent, JobState
from app.utils.r2 import R2Client, UploadReceipt

STATUS_PATH = "/api/v1/tools/{tool}/tasks/{task_id}/status"
CAPABILITIES_PATH = "/api/v1/capabilities"
DOWNLOAD_PATH = "/api/v1/tools/{tool}/tasks/{task_id}/download/{output}"
COMPRESS_TASKS_PATH = "/api/v1/tools/compress-pdf/tasks"

ROUTER_PATHS = (STATUS_PATH, CAPABILITIES_PATH, COMPRESS_TASKS_PATH, DOWNLOAD_PATH)


class _RecordingR2(R2Client):
    """R2Client-backed stub returning a fixed presigned URL."""

    def generate_signed_url(
        self, key: str, expires_at: datetime, *, now: datetime | None = None
    ) -> str:
        return "https://example.invalid/presigned"


class _UploadR2(R2Client):
    """R2Client-backed stub recording uploads without a network client."""

    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes]] = []

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        del extension, now
        return f"tmp/2026-08-06/{uuid.uuid4().hex}.pdf"

    def upload_object(self, key: str, body: bytes, **kwargs: object) -> UploadReceipt:
        del kwargs
        self.uploaded.append((key, body))
        return UploadReceipt(
            key=key,
            size_bytes=len(body),
            content_type="application/pdf",
            uploaded_at=datetime.now(UTC),
        )


def _settings() -> Settings:
    return Settings(
        r2_account_id="test-account",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test-bucket",
        allowed_origins=("http://localhost:3000",),
    )


def _injected_app(*, store: TaskStore | None = None, r2: R2Client | None = None) -> FastAPI:
    instance = create_app()
    if store is not None:
        instance.state.task_store = store
    if r2 is not None:
        instance.state.r2_client = r2
    return instance


def _make_store() -> TaskStore:
    return TaskStore(_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))


def _valid_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _compress_app(*, store: TaskStore, r2: R2Client) -> FastAPI:
    instance = create_app()
    instance.state.task_store = store
    instance.state.r2_client = r2
    instance.state.job_queue = JobQueue(
        _settings(),
        store,
        client=cast(StreamsRedisLike, fakeredis.FakeRedis()),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    return instance


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


# --- each router mounted exactly once ---------------------------------------


def test_factory_mounts_each_router_path_exactly_once() -> None:
    routes = _mounted_api_routes(create_app())
    for path in ROUTER_PATHS:
        assert [route.path for route in routes].count(path) == 1


def test_factory_mounts_the_three_router_instances() -> None:
    instance = create_app()
    mounted = {route.path for route in _mounted_api_routes(instance)}
    assert CAPABILITIES_PATH in mounted
    assert STATUS_PATH in mounted
    assert COMPRESS_TASKS_PATH in mounted
    assert DOWNLOAD_PATH in mounted


def test_health_and_readiness_preserved_after_wiring() -> None:
    instance = create_app()
    instance.state.task_store = _make_store()
    client = TestClient(instance)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["checks"]["redis"] == "ok"


# --- routed endpoints reachable through the factory -------------------------


def test_capabilities_reachable_on_factory_app() -> None:
    response = TestClient(create_app()).get(CAPABILITIES_PATH)
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert response.headers["x-request-id"]
    assert response.headers["cache-control"] == "public, max-age=3600"


def test_status_reachable_on_factory_app_with_injected_store() -> None:
    store = _make_store()
    now = datetime.now(UTC)
    record = TaskRecord(
        task_id=uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
    )
    store.create(record)
    instance = _injected_app(store=store)
    response = TestClient(instance).get(f"/api/v1/tools/merge-pdf/tasks/{record.task_id}/status")
    assert response.status_code == 200
    assert response.json()["state"] == "queued"


def test_download_reachable_on_factory_app_with_injected_deps() -> None:
    store = _make_store()
    now = datetime.now(UTC)
    record = TaskRecord(
        task_id=uuid.uuid4().hex,
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        objects=("tmp/2026-08-03/" + "c" * 32 + ".pdf",),
    )
    store.create(record)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(
            result=ResultSummary(output_count=1, total_bytes=1024),
            objects=("tmp/2026-08-03/" + "c" * 32 + ".pdf",),
        ),
    )
    instance = _injected_app(store=store, r2=_RecordingR2(_settings()))
    response = TestClient(instance).get(
        f"/api/v1/tools/merge-pdf/tasks/{record.task_id}/download/0"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["url"] == "https://example.invalid/presigned"
    assert body["expires_at"]
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-request-id"]


def test_compress_admission_success_on_factory_app() -> None:
    """POST valid PDF via factory → 202 TaskAdmission envelope, queued task."""
    store = _make_store()
    r2 = _UploadR2()
    client = TestClient(_compress_app(store=store, r2=r2))
    response = client.post(COMPRESS_TASKS_PATH, files={"file": ("test.pdf", _valid_pdf_bytes())})
    assert response.status_code == 202
    data = response.json()
    assert data["state"] == "queued"
    assert data["task_id"]
    assert data["expires_at"]
    record = store.get(data["task_id"])
    assert record.tool == "compress-pdf"
    assert record.state == JobState.QUEUED
    assert len(record.objects) == 1
    assert len(r2.uploaded) == 1
    assert r2.uploaded[0][0] == record.objects[0]


def test_compress_admission_rejects_safe_4xx_on_factory_app() -> None:
    """Non-PDF upload → 400 validation envelope, no upload, no task created."""
    store = _make_store()
    r2 = _UploadR2()
    client = TestClient(_compress_app(store=store, r2=r2))
    response = client.post(COMPRESS_TASKS_PATH, files={"file": ("test.pdf", b"Not a PDF at all.")})
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "bad_request"
    assert body["error"]["category"] == "validation"
    assert body["error"]["messageKey"] == "error.badRequest"
    assert body["error"]["retryable"] is False
    assert body["request_id"]
    assert len(r2.uploaded) == 0


def test_factory_mounts_compress_tasks_route() -> None:
    routes = _mounted_api_routes(create_app())
    assert COMPRESS_TASKS_PATH in [route.path for route in routes], (
        "compress-pdf tasks route not found"
    )


def test_security_headers_present_on_routed_responses() -> None:
    client = TestClient(create_app())
    response = client.get(CAPABILITIES_PATH, headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_error_envelope_stable_on_routed_routes() -> None:
    client = TestClient(create_app())
    response = client.post(CAPABILITIES_PATH)
    assert response.status_code == 405
    body = response.json()
    assert body["error"]["code"] == "method_not_allowed"
    assert body["error"]["messageKey"] == "error.methodNotAllowed"
    assert body["request_id"]


# --- module-level export -----------------------------------------------------


def test_module_level_app_includes_routed_paths() -> None:
    routes = _mounted_api_routes(app)
    for path in ROUTER_PATHS:
        assert path in [route.path for route in routes]
    assert COMPRESS_TASKS_PATH in [route.path for route in routes]


def test_router_instances_stay_out_of_the_package_init() -> None:
    assert not any(type(value).__name__ == "APIRouter" for value in vars(routers_package).values())
    assert download_router.prefix == "/api/v1"
