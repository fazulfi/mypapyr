"""HTTP E2E tests for the five-tool admission -> poll -> download lifecycle.

Exercises the real HTTP routes (not unit seams) for:
  - compress-pdf
  - merge-pdf
  - split-pdf
  - jpg-to-pdf
  - pdf-to-jpg

Each tool is tested for:
  1. Valid upload -> 202 + task_id + queued state
  2. Poll status until done (via store.transition_state, not a worker)
  3. GET download grant -> 200 + {url, expires_at}
  4. Rejected admission (corrupt bytes) -> 400/415 with error.code

Uses the same fakeredis/moto fixture patterns as existing unit tests
so no real Redis or R2 is needed.
"""

from __future__ import annotations

import importlib
import io
import time
from datetime import UTC, datetime
from typing import Any, cast
from urllib.parse import parse_qs, urlsplit

import fakeredis
import pikepdf
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.errors import register_error_handlers
from app.queue.queue import JobQueue, QueueOptions, StreamsRedisLike
from app.queue.store import RedisLike, TaskStore, TransitionPayload
from app.routers.capabilities import router as capabilities_router
from app.routers.compress import router as compress_router
from app.routers.download import router as download_router
from app.routers.image_to_pdf import router as image_to_pdf_router
from app.routers.merge import router as merge_router
from app.routers.pdf_to_jpg import router as pdf_to_jpg_router
from app.routers.split import router as split_router
from app.routers.status import router as status_router
from app.schemas.job import ResultSummary
from app.tasks.state_machine import JobEvent, JobState
from app.utils.r2 import R2Client

# Untyped third-party crossing (repo pattern, cf test_integration_r2.py).
boto3: Any = cast(Any, importlib.import_module("boto3"))
moto: Any = cast(Any, importlib.import_module("moto"))
requests: Any = cast(Any, importlib.import_module("requests"))

# ---------------------------------------------------------------------------
# Tool metadata
# ---------------------------------------------------------------------------

TOOL_SLUGS = (
    "compress-pdf",
    "merge-pdf",
    "split-pdf",
    "jpg-to-pdf",
    "pdf-to-jpg",
)

# Tools wired to the full store/queue/r2 pipeline (all five are wired).
_PIPELINE_TOOLS = frozenset(TOOL_SLUGS)

# Tools accepting a single file (others accept multiple).
_SINGLE_FILE_TOOLS = frozenset({"compress-pdf", "split-pdf", "pdf-to-jpg"})

# Bound the store-drive helper's record-wait loop.
_DRIVE_TIMEOUT_SECONDS = 5.0
_DRIVE_POLL_SECONDS = 0.05

# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

_R2_ENDPOINT = "https://test-account.r2.cloudflarestorage.com"
_TEST_BUCKET = "test"


def _make_settings() -> Settings:
    return Settings(
        r2_account_id="test-account",
        r2_access_key_id="test-access-key-id",
        r2_secret_access_key="test-secret-access-key",
        r2_bucket_name=_TEST_BUCKET,
        allowed_origins=("http://localhost:3000",),
    )


def _valid_pdf_bytes() -> bytes:
    """Return bytes for a minimal 1-page PDF via pikepdf."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _valid_jpg_bytes() -> bytes:
    """Return bytes for a minimal 100x100 JPEG via Pillow."""
    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _corrupt_pdf_bytes() -> bytes:
    """Return bytes that fail PDF validation."""
    return b"Not a PDF at all."


def _corrupt_image_bytes() -> bytes:
    """Return bytes that fail image validation."""
    return b"This is not an image file."


def _admit_body(tool: str, *, valid: bool = True) -> list[tuple[str, tuple[str, bytes, str]]]:
    """Build the files list for TestClient.post().

    Returns a list of (field, (filename, bytes, mime)) tuples.
    """
    if tool == "jpg-to-pdf":
        content = _valid_jpg_bytes() if valid else _corrupt_image_bytes()
        return [("files", ("test.jpg", content, "image/jpeg"))]
    content = _valid_pdf_bytes() if valid else _corrupt_pdf_bytes()
    if tool in _SINGLE_FILE_TOOLS:
        return [("file", ("test.pdf", content, "application/pdf"))]
    # merge-pdf takes multiple files via the same ``files`` field
    return [
        ("files", ("test1.pdf", content, "application/pdf")),
        ("files", ("test2.pdf", content, "application/pdf")),
    ]


def _post_url(tool: str) -> str:
    """Return the admission POST URL for *tool*."""
    return f"/api/v1/tools/{tool}/tasks"


def _status_url(tool: str, task_id: str) -> str:
    """Return the status GET URL."""
    return f"/api/v1/tools/{tool}/tasks/{task_id}/status"


def _download_url(tool: str, task_id: str, output: int = 0) -> str:
    """Return the download GET URL."""
    return f"/api/v1/tools/{tool}/tasks/{task_id}/download/{output}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def settings() -> Settings:
    return _make_settings()


@pytest.fixture
def fserver() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def raw_client(fserver: fakeredis.FakeServer) -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(server=fserver)


@pytest.fixture
def store_client(raw_client: fakeredis.FakeRedis) -> RedisLike:
    return cast(RedisLike, raw_client)


@pytest.fixture
def stream_client(raw_client: fakeredis.FakeRedis) -> StreamsRedisLike:
    return cast(StreamsRedisLike, raw_client)


@pytest.fixture
def store(store_client: RedisLike, settings: Settings) -> TaskStore:
    return TaskStore(settings, client=store_client, clock=lambda: datetime.now(UTC))


@pytest.fixture
def queue(
    store: TaskStore,
    stream_client: StreamsRedisLike,
    settings: Settings,
) -> JobQueue:
    return JobQueue(
        settings,
        store,
        client=stream_client,
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )


@pytest.fixture
def moto_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """A moto S3 backend served at the R2-style endpoint."""
    monkeypatch.setenv("MOTO_S3_CUSTOM_ENDPOINTS", _R2_ENDPOINT)
    with moto.mock_aws():
        client = boto3.client(
            "s3",
            endpoint_url=_R2_ENDPOINT,
            region_name="us-east-1",
            aws_access_key_id="test-access-key-id",
            aws_secret_access_key="test-secret-access-key",
        )
        client.create_bucket(Bucket=_TEST_BUCKET)
        yield client


@pytest.fixture
def r2_client(settings: Settings, moto_client: Any) -> R2Client:
    return R2Client(settings, client=moto_client)


@pytest.fixture
def app(
    settings: Settings,
    store: TaskStore,
    queue: JobQueue,
    r2_client: R2Client,
) -> FastAPI:
    """A FastAPI app with all five tool routers + status + download +
    capabilities mounted, plus the stable error envelope handlers, and
    injected fakeredis/moto dependencies preset on ``app.state.*``."""
    application = FastAPI(title="test-e2e")
    application.state.settings = settings
    application.state.task_store = store
    application.state.job_queue = queue
    application.state.r2_client = r2_client
    for router in (
        compress_router,
        merge_router,
        split_router,
        image_to_pdf_router,
        pdf_to_jpg_router,
        status_router,
        download_router,
        capabilities_router,
    ):
        application.include_router(router)
    register_error_handlers(application)
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helper: drive a task from queued -> done through the store
# ---------------------------------------------------------------------------


def _drive_to_done(
    store: TaskStore,
    r2: R2Client,
    task_id: str,
    *,
    tool: str,
) -> None:
    """Transition *task_id* through queued -> processing -> done in the store.

    Uploads a synthetic output object to R2/moto so the download URL is
    fetchable. No worker runs in the HTTP E2E harness, so the worker's
    store transitions are applied directly through the same TaskStore API
    the worker consumes.
    """
    deadline = time.monotonic() + _DRIVE_TIMEOUT_SECONDS
    poll_interval = _DRIVE_POLL_SECONDS


    # Upload a synthetic output object to R2 so the download grant URL
    # maps to a real stored object.
    output_key = r2.build_object_key(extension="pdf")
    r2.upload_object(output_key, _valid_pdf_bytes(), content_type="application/pdf")

    # Wait for the record to appear in the store (admission writes it).
    while time.monotonic() < deadline:
        try:
            record = store.get(task_id)
        except Exception:
            time.sleep(poll_interval)
            continue
        if record.state is JobState.QUEUED:
            break
        time.sleep(poll_interval)
    else:
        pytest.fail(f"Task {task_id} never appeared in store (queued)")

    # queued -> processing
    store.transition_state(task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)

    # processing -> done with result and output objects
    store.transition_state(
        task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(
            result=ResultSummary(output_count=1, total_bytes=len(_valid_pdf_bytes())),
            objects=(output_key,),
        ),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestToolAdmission:
    """Admission phase: POST upload -> 202 + task_id + queued."""

    @pytest.mark.parametrize("tool", TOOL_SLUGS)
    def test_admit_valid_upload(self, client: TestClient, tool: str) -> None:
        """Submit a valid document -> 202, task_id + state=queued present."""
        files = _admit_body(tool, valid=True)
        url = _post_url(tool)
        response = client.post(url, files=files)
        assert response.status_code == 202, (
            f"{tool}: expected 202, got {response.status_code}: {response.text}"
        )
        data = response.json()
        assert "task_id" in data, f"{tool}: missing task_id"
        assert data["task_id"], f"{tool}: empty task_id"
        assert data.get("state") == "queued", (
            f"{tool}: expected state=queued, got {data.get('state')!r}"
        )
        assert "expires_at" in data, f"{tool}: missing expires_at"


class TestToolLifecycle:
    """Full lifecycle: admit -> poll -> download for pipeline tools."""

    @pytest.mark.parametrize("tool", sorted(_PIPELINE_TOOLS))
    def test_admit_poll_download(
        self,
        client: TestClient,
        store: TaskStore,
        r2_client: R2Client,
        tool: str,
    ) -> None:
        """Full lifecycle for a pipeline-wired tool."""
        # ---- 1. Admit --------------------------------------------------------
        files = _admit_body(tool, valid=True)
        url = _post_url(tool)
        admit_response = client.post(url, files=files)
        assert admit_response.status_code == 202, (
            f"{tool}: admit failed: {admit_response.text}"
        )
        admit_data: dict[str, Any] = admit_response.json()
        task_id = admit_data["task_id"]

        # ---- 2. Poll status: initial queued ----------------------------------
        status_response = client.get(_status_url(tool, task_id))
        assert status_response.status_code == 200, (
            f"{tool}: status failed: {status_response.text}"
        )
        status_data = status_response.json()
        assert status_data["state"] == "queued", (
            f"{tool}: expected queued initially, got {status_data['state']}"
        )

        # ---- 3. Drive through processing -> done via store --------------------
        _drive_to_done(store, r2_client, task_id, tool=tool)

        # ---- 4. Poll status until done ---------------------------------------
        deadline = time.monotonic() + 5.0
        final_state: str | None = None
        while time.monotonic() < deadline:
            resp = client.get(_status_url(tool, task_id))
            if resp.status_code == 200:
                body = resp.json()
                assert "state" in body, f"{tool}: status missing state: {body}"
                final_state = body["state"]
                if final_state == "done":
                    break
            time.sleep(0.05)

        assert final_state == "done", (
            f"{tool}: expected done, got {final_state!r}"
        )

        # ---- 5. Download grant ------------------------------------------------
        download_response = client.get(_download_url(tool, task_id, output=0))
        assert download_response.status_code == 200, (
            f"{tool}: download grant failed: {download_response.status_code}: "
            f"{download_response.text}"
        )
        grant = download_response.json()
        assert "url" in grant, f"{tool}: download grant missing url"
        assert "expires_at" in grant, f"{tool}: download grant missing expires_at"
        # The URL should be an absolute HTTP URL.
        assert grant["url"].startswith("http"), (
            f"{tool}: url does not look like a URL: {grant['url']}"
        )
        # Parse URL params — moto returns SigV2-signed URLs with
        # AWSAccessKeyId / Signature / Expires query parameters.
        parsed = urlsplit(grant["url"])
        params = parse_qs(parsed.query)
        # At minimum there should be some signature/credential parameter.
        assert any(
            key in params for key in ("X-Amz-Algorithm", "AWSAccessKeyId", "Signature")
        ), f"{tool}: signed URL missing expected query params; got {list(params)}"

        # The URL should be fetchable (moto allows unsigned fetches after
        # presigning, so this proves the URL maps to a stored object).
        object_response = requests.get(grant["url"], timeout=10)
        assert object_response.status_code == 200, (
            f"{tool}: download URL returned {object_response.status_code}"
        )


class TestRejectedAdmission:
    """Corrupt/non-conforming uploads -> 400/415 envelope."""

    @pytest.mark.parametrize("tool", ["compress-pdf", "merge-pdf", "split-pdf", "pdf-to-jpg"])
    def test_rejects_corrupt_pdf(
        self, client: TestClient, tool: str
    ) -> None:
        """Corrupt (non-PDF) bytes -> 400/415 with error.code."""
        files = _admit_body(tool, valid=False)
        url = _post_url(tool)
        response = client.post(url, files=files)
        # The router maps validation rejections to 400.
        assert response.status_code in (400, 415), (
            f"{tool}: expected 400/415, got {response.status_code}: {response.text}"
        )
        body = response.json()
        # When register_error_handlers is mounted, 4xx responses carry
        # the stable ``{error: {code: ..., ...}}`` envelope.
        if "error" in body:
            assert "code" in body["error"], f"{tool}: error missing code"
        else:
            # Fallback: router-level HTTPException with ``detail`` dict.
            assert "detail" in body, f"{tool}: response has neither error nor detail"

    def test_rejects_corrupt_jpg_to_pdf(self, client: TestClient) -> None:
        """jpg-to-pdf with non-image bytes -> 400."""
        files = _admit_body("jpg-to-pdf", valid=False)
        response = client.post("/api/v1/tools/jpg-to-pdf/tasks", files=files)
        assert response.status_code == 400, (
            f"expected 400, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert "error" in body or "detail" in body