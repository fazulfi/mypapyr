"""U-SEC RED: concrete ClamAV scanner and fail-closed admission wiring.

RED-phase contract tests for the U-SEC unit (BLKR-01, SEC-01/03/09): a
concrete production ``ThreatScanner`` client for clamd (no mock ships as the
production client), scanner Settings fields, ``resolve_probe_scanner`` with
the app.state-or-Settings fallback seam, the ``/health/ready`` scanner check
(unavailable scanner forces 503), and fail-closed ``classify_payload``
enforcement in all five admission routers with zero upload/enqueue side
effects.

These tests FAIL before the U-SEC implementation lands (missing scanner
module, missing Settings fields, unwired routers, unextended readiness).
Evidence: audit-outputs/phase-5/tdd/U-SEC-red.txt (git-ignored).
"""

from __future__ import annotations

import contextlib
import io
import socket
import struct
import threading
import time
from collections.abc import Iterator, Mapping
from datetime import UTC, datetime
from typing import Final

import fakeredis
import pikepdf
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from starlette.requests import Request

from app import health
from app.config import InvalidSettingError, Settings
from app.errors import register_error_handlers
from app.main import create_app
from app.queue.queue import JobQueue, QueueOptions
from app.queue.store import TaskStore
from app.routers import compress, image_to_pdf, merge, pdf_to_jpg, split
from app.security.classification import ScannerStatus, ScannerVerdict, ThreatScanner
from app.security.scanner import ClamdScanner
from app.utils.r2 import R2Client

_FULL_ENV: Final[Mapping[str, str]] = {
    "R2_ACCOUNT_ID": "test-account",
    "R2_ACCESS_KEY_ID": "test-key",
    "R2_SECRET_ACCESS_KEY": "test-secret",
    "R2_BUCKET_NAME": "test-bucket",
    "ALLOWED_ORIGINS": "http://localhost:3000",
}


def _settings(**overrides: str) -> Settings:
    env = dict(_FULL_ENV)
    env.update({key.upper(): value for key, value in overrides.items()})
    return Settings.from_env(env)


def _valid_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _valid_jpg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color=(255, 255, 255)).save(buf, format="JPEG")
    return buf.getvalue()


class _FixedScanner:
    """Deterministic ``ThreatScanner`` double reporting a fixed verdict."""

    def __init__(self, status: ScannerStatus) -> None:
        self._status = status
        self.calls: list[bytes] = []

    def scan(self, data: bytes) -> ScannerVerdict:
        self.calls.append(data)
        return ScannerVerdict(status=self._status)


class _FakeR2(R2Client):
    """R2 seam recording uploads so no-side-effect assertions are observable."""

    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes]] = []
        # Skip parent __init__ to avoid real AWS/boto3 construction

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        return f"tmp/test/{len(self.uploaded)}.{extension or 'bin'}"

    def upload_object(self, key: str, body: bytes, **kwargs: object) -> tuple[str, int]:
        self.uploaded.append((key, body))
        return key, len(body)

    def delete_object(self, key: str) -> bool:
        return True


class _RecordingQueue:
    """Queue seam recording enqueue attempts without any Redis reach."""

    def __init__(self) -> None:
        self.enqueued: list[object] = []

    def enqueue(self, record: object, *, origin: object = None, route: str) -> object:
        self.enqueued.append(record)
        return record


def _request_for(app: FastAPI) -> Request:
    scope = {
        "type": "http",
        "app": app,
        "method": "GET",
        "path": "/health/ready",
        "headers": [],
        "query_string": b"",
    }
    return Request(scope)


def _healthy_store() -> TaskStore:
    return TaskStore(_settings(), client=fakeredis.FakeRedis())


def _registered_app(
    env: Mapping[str, str],
    *,
    store: TaskStore | None = None,
    scanner: object = None,
) -> FastAPI:
    """Readiness test app with injectable store/scanner seams."""
    app = FastAPI()
    health.register_health_routes(app)
    app.dependency_overrides[health.env_provider] = lambda: env
    if env:
        app.state.settings = Settings.from_env(dict(env))
    if store is not None:
        app.state.task_store = store
    if scanner is not None:
        app.state.scanner = scanner
    return app


# --- fake clamd transport (deterministic, no live daemon required) ---


class _FakeClamd:
    """A real localhost TCP listener speaking one scripted clamd exchange."""

    def __init__(self, responder: object) -> None:
        self._responder = responder
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(("127.0.0.1", 0))
        self._server.listen(1)
        self.received: list[bytes] = []
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    @property
    def port(self) -> int:
        return int(self._server.getsockname()[1])

    def _serve(self) -> None:
        try:
            conn, _ = self._server.accept()
        except OSError:
            return
        with conn:
            data = b""
            conn.settimeout(2.0)
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if self._stream_complete(data):
                        break
            except OSError:
                pass
            self.received.append(data)
            with contextlib.suppress(OSError):
                self._responder(conn, data)

    @staticmethod
    def _stream_complete(data: bytes) -> bool:
        """True when *data* holds zINSTREAM plus chunks ending in the 4-byte
        zero-length terminator, parsed by the exact INSTREAM framing rules."""
        command = b"zINSTREAM\x00"
        if not data.startswith(command):
            return False
        offset = len(command)
        while offset + 4 <= len(data):
            (length,) = struct.unpack(">I", data[offset : offset + 4])
            offset += 4
            if length == 0:
                return offset == len(data)
            offset += length
        return False

    def close(self) -> None:
        self._server.close()


@pytest.fixture
def fake_clamd_factory() -> Iterator[list[_FakeClamd]]:
    created: list[_FakeClamd] = []
    yield created
    for daemon in created:
        daemon.close()


def _make_clamd(created: list[_FakeClamd], responder: object) -> tuple[str, int]:
    daemon = _FakeClamd(responder)
    created.append(daemon)
    return "127.0.0.1", daemon.port


# =============================================================================
# Settings fields (U-SEC owns backend/app/config.py for these)
# =============================================================================


def test_settings_default_scanner_fields() -> None:
    settings = Settings.from_env(dict(_FULL_ENV))
    assert settings.clamd_host == "localhost"
    assert settings.clamd_port == 3310
    assert settings.scanner_timeout_seconds == 10
    assert settings.scanner_enabled is True


def test_settings_parse_scanner_overrides() -> None:
    settings = _settings(
        clamd_host="clamav.internal",
        clamd_port="3311",
        scanner_timeout_seconds="3",
        scanner_enabled="false",
    )
    assert settings.clamd_host == "clamav.internal"
    assert settings.clamd_port == 3311
    assert settings.scanner_timeout_seconds == 3
    assert settings.scanner_enabled is False


def test_settings_reject_invalid_scanner_port() -> None:
    with pytest.raises(InvalidSettingError):
        _settings(clamd_port="0")
    with pytest.raises(InvalidSettingError):
        _settings(clamd_port="70000")


def test_settings_reject_invalid_scanner_timeout() -> None:
    with pytest.raises(InvalidSettingError):
        _settings(scanner_timeout_seconds="0")
    with pytest.raises(InvalidSettingError):
        _settings(scanner_timeout_seconds="3601")


def test_settings_reject_invalid_scanner_enabled() -> None:
    with pytest.raises(InvalidSettingError):
        _settings(scanner_enabled="maybe")


# =============================================================================
# Concrete scanner client protocol behavior (fake clamd transport)
# =============================================================================


def test_scanner_implements_protocol_and_lazy_construction() -> None:
    scanner = ClamdScanner(_settings())
    assert isinstance(scanner, ThreatScanner)
    # Construction performed no network I/O: the object exists even though no
    # clamd listens at the default localhost:3310 in this environment.
    assert scanner is not None


def test_scanner_clean_verdict_from_clamd_ok(fake_clamd_factory: list[_FakeClamd]) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        conn.sendall(b"stream: OK\x00")

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(_settings(clamd_host=host, clamd_port=str(port)))
    verdict = scanner.scan(b"%PDF-1.4 clean payload")
    assert verdict.status is ScannerStatus.CLEAN


def test_scanner_malicious_verdict_from_clamd_found(
    fake_clamd_factory: list[_FakeClamd],
) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        conn.sendall(b"stream: Eicar-Signature FOUND\x00")

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(_settings(clamd_host=host, clamd_port=str(port)))
    verdict = scanner.scan(b"EICAR payload")
    assert verdict.status is ScannerStatus.MALICIOUS


def test_scanner_unavailable_on_connection_refused() -> None:
    # Bind and immediately close a port so connects are refused promptly.
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = int(probe.getsockname()[1])
    probe.close()
    scanner = ClamdScanner(_settings(clamd_host="127.0.0.1", clamd_port=str(port)))
    verdict = scanner.scan(b"payload")
    assert verdict.status is ScannerStatus.UNAVAILABLE


def test_scanner_unavailable_on_read_timeout(fake_clamd_factory: list[_FakeClamd]) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        # Accept and read, then never answer: the client must time out.
        time.sleep(3.0)

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(
        _settings(clamd_host=host, clamd_port=str(port), scanner_timeout_seconds="1")
    )
    start = datetime.now(UTC)
    verdict = scanner.scan(b"payload")
    elapsed = (datetime.now(UTC) - start).total_seconds()
    assert verdict.status is ScannerStatus.UNAVAILABLE
    assert elapsed < 2.5, "read timeout not bounded by scanner_timeout_seconds"


def test_scanner_indeterminate_on_malformed_response(
    fake_clamd_factory: list[_FakeClamd],
) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        conn.sendall(b"banana pancakes")

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(_settings(clamd_host=host, clamd_port=str(port)))
    verdict = scanner.scan(b"payload")
    assert verdict.status is ScannerStatus.INDETERMINATE


def test_scanner_indeterminate_on_clamd_error_response(
    fake_clamd_factory: list[_FakeClamd],
) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        conn.sendall(b"stream: INSTREAM size limit exceeded ERROR\x00")

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(_settings(clamd_host=host, clamd_port=str(port)))
    verdict = scanner.scan(b"payload")
    assert verdict.status is ScannerStatus.INDETERMINATE


def test_scanner_bounded_response_read_never_hangs(
    fake_clamd_factory: list[_FakeClamd],
) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        # Flood far more bytes than the bounded response window and keep the
        # connection open; the client must stop reading and classify.
        conn.sendall(b"x" * 1024 * 1024)
        time.sleep(3.0)

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(
        _settings(clamd_host=host, clamd_port=str(port), scanner_timeout_seconds="1")
    )
    start = datetime.now(UTC)
    verdict = scanner.scan(b"payload")
    elapsed = (datetime.now(UTC) - start).total_seconds()
    assert verdict.status is ScannerStatus.INDETERMINATE
    assert elapsed < 2.5, "response parsing is not bounded"


def test_scanner_sends_instream_protocol(fake_clamd_factory: list[_FakeClamd]) -> None:
    def respond(conn: socket.socket, _data: bytes) -> None:
        conn.sendall(b"stream: OK\x00")

    host, port = _make_clamd(fake_clamd_factory, respond)
    scanner = ClamdScanner(_settings(clamd_host=host, clamd_port=str(port)))
    payload = b"%PDF-1.4 in-stream body"
    assert scanner.scan(payload).status is ScannerStatus.CLEAN
    daemon = fake_clamd_factory[-1]
    deadline = time.monotonic() + 2.0
    while not daemon.received and time.monotonic() < deadline:
        time.sleep(0.01)
    assert daemon.received, "fake clamd recorded no exchange"
    wire = daemon.received[0]
    terminator = struct.pack(">I", 0)
    expected = b"zINSTREAM\x00" + struct.pack(">I", len(payload)) + payload + terminator
    assert wire == expected, "wire does not match exact INSTREAM framing"


def test_scanner_disabled_fails_closed_without_network() -> None:
    # A disabled scanner never reaches the network and still fails closed.
    scanner = ClamdScanner(_settings(scanner_enabled="false"))
    verdict = scanner.scan(b"payload")
    assert verdict.status is ScannerStatus.UNAVAILABLE


# =============================================================================
# resolve_probe_scanner: both seam branches
# =============================================================================


def test_resolve_probe_scanner_returns_preset_scanner() -> None:
    app = FastAPI()
    app.state.settings = _settings()
    preset = _FixedScanner(ScannerStatus.CLEAN)
    app.state.scanner = preset
    assert health.resolve_probe_scanner(_request_for(app)) is preset


def test_resolve_probe_scanner_builds_and_memoizes_from_settings() -> None:
    app = FastAPI()
    app.state.settings = _settings()
    built = health.resolve_probe_scanner(_request_for(app))
    assert isinstance(built, ClamdScanner)
    assert app.state.scanner is built
    assert health.resolve_probe_scanner(_request_for(app)) is built


def test_resolve_probe_scanner_none_without_settings() -> None:
    app = FastAPI()
    assert health.resolve_probe_scanner(_request_for(app)) is None


# =============================================================================
# /health/ready scanner check (typed response + 503)
# =============================================================================


def test_readiness_ready_includes_scanner_ok() -> None:
    app = _registered_app(
        dict(_FULL_ENV),
        store=_healthy_store(),
        scanner=_FixedScanner(ScannerStatus.CLEAN),
    )
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"foundation": "ok", "redis": "ok", "scanner": "ok"},
        "deferred": ["worker"],
    }


def test_readiness_not_ready_when_scanner_unavailable() -> None:
    app = _registered_app(
        dict(_FULL_ENV),
        store=_healthy_store(),
        scanner=_FixedScanner(ScannerStatus.UNAVAILABLE),
    )
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["scanner"] == "unavailable"


def test_readiness_not_ready_when_scanner_cannot_resolve() -> None:
    # No preset scanner and no settings -> the dependency cannot be probed;
    # readiness fails closed instead of claiming ready.
    app = FastAPI()
    health.register_health_routes(app)
    app.dependency_overrides[health.env_provider] = lambda: dict(_FULL_ENV)
    app.state.task_store = _healthy_store()
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 503
    assert response.json()["checks"]["scanner"] == "unavailable"


# =============================================================================
# Five-router fail-closed admission (no upload/enqueue side effects)
# =============================================================================


def _single_file_app(path: str, scanner: object) -> tuple[FastAPI, _FakeR2, _RecordingQueue]:
    router = {
        "/api/v1/tools/compress-pdf/tasks": compress.router,
        "/api/v1/tools/split-pdf/tasks": split.router,
        "/api/v1/tools/pdf-to-jpg/tasks": pdf_to_jpg.router,
    }[path]
    r2 = _FakeR2()
    queue = _RecordingQueue()
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)
    app.state.settings = _settings()
    app.state.task_store = TaskStore(_settings(), client=fakeredis.FakeRedis())
    app.state.r2_client = r2
    app.state.job_queue = queue
    app.state.scanner = scanner
    return app, r2, queue


def _multi_file_app(router: object, scanner: object) -> tuple[FastAPI, _FakeR2, _RecordingQueue]:
    r2 = _FakeR2()
    queue = _RecordingQueue()
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)
    app.state.settings = _settings()
    app.state.task_store = TaskStore(_settings(), client=fakeredis.FakeRedis())
    app.state.r2_client = r2
    app.state.job_queue = queue
    app.state.scanner = scanner
    return app, r2, queue


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/tools/compress-pdf/tasks",
        "/api/v1/tools/split-pdf/tasks",
        "/api/v1/tools/pdf-to-jpg/tasks",
    ],
)
def test_single_file_routers_block_malicious_without_side_effects(path: str) -> None:
    app, r2, queue = _single_file_app(path, _FixedScanner(ScannerStatus.MALICIOUS))
    response = TestClient(app).post(
        path, files={"file": ("test.pdf", _valid_pdf_bytes(), "application/pdf")}
    )
    assert response.status_code == 403
    body = response.json()
    assert body["error"]["messageKey"] == "error.forbidden"
    assert body["error"]["retryable"] is False
    assert r2.uploaded == [], "malicious payload must never reach R2"
    assert queue.enqueued == [], "malicious payload must never be enqueued"


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/tools/compress-pdf/tasks",
        "/api/v1/tools/split-pdf/tasks",
        "/api/v1/tools/pdf-to-jpg/tasks",
    ],
)
def test_single_file_routers_block_scanner_unavailable_without_side_effects(path: str) -> None:
    app, r2, queue = _single_file_app(path, _FixedScanner(ScannerStatus.UNAVAILABLE))
    response = TestClient(app).post(
        path, files={"file": ("test.pdf", _valid_pdf_bytes(), "application/pdf")}
    )
    assert response.status_code == 429
    body = response.json()
    assert body["error"]["messageKey"] == "error.rateLimited"
    assert body["error"]["retryable"] is True
    assert r2.uploaded == []
    assert queue.enqueued == []


def test_merge_blocks_malicious_before_any_upload() -> None:
    app, r2, queue = _multi_file_app(merge.router, _FixedScanner(ScannerStatus.MALICIOUS))
    pdf = _valid_pdf_bytes()
    response = TestClient(app).post(
        "/api/v1/tools/merge-pdf/tasks",
        files=[
            ("files", ("a.pdf", pdf, "application/pdf")),
            ("files", ("b.pdf", pdf, "application/pdf")),
        ],
    )
    assert response.status_code == 403
    assert r2.uploaded == [], "no input may upload when any input is malicious"
    assert queue.enqueued == []


def test_merge_blocks_scanner_unavailable() -> None:
    app, r2, queue = _multi_file_app(merge.router, _FixedScanner(ScannerStatus.UNAVAILABLE))
    response = TestClient(app).post(
        "/api/v1/tools/merge-pdf/tasks",
        files=[("files", ("a.pdf", _valid_pdf_bytes(), "application/pdf"))],
    )
    assert response.status_code == 429
    assert r2.uploaded == []
    assert queue.enqueued == []


def test_image_to_pdf_blocks_malicious_before_any_upload() -> None:
    app, r2, queue = _multi_file_app(image_to_pdf.router, _FixedScanner(ScannerStatus.MALICIOUS))
    response = TestClient(app).post(
        "/api/v1/tools/jpg-to-pdf/tasks",
        files=[("files", ("a.jpg", _valid_jpg_bytes(), "image/jpeg"))],
    )
    assert response.status_code == 403
    assert r2.uploaded == []
    assert queue.enqueued == []


def test_image_to_pdf_blocks_scanner_unavailable() -> None:
    app, r2, queue = _multi_file_app(image_to_pdf.router, _FixedScanner(ScannerStatus.UNAVAILABLE))
    response = TestClient(app).post(
        "/api/v1/tools/jpg-to-pdf/tasks",
        files=[("files", ("a.jpg", _valid_jpg_bytes(), "image/jpeg"))],
    )
    assert response.status_code == 429
    assert r2.uploaded == []
    assert queue.enqueued == []


def test_compress_clean_scanner_still_admits() -> None:
    """CLEAN verdict preserves existing admission behavior (202 + upload)."""

    r2 = _FakeR2()
    store = TaskStore(_settings(), client=fakeredis.FakeRedis(), clock=lambda: datetime.now(UTC))
    queue = JobQueue(
        _settings(),
        store,
        client=fakeredis.FakeRedis(),
        options=QueueOptions(clock=lambda: datetime.now(UTC)),
    )
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(compress.router)
    app.state.settings = _settings()
    app.state.task_store = store
    app.state.r2_client = r2
    app.state.job_queue = queue
    app.state.scanner = _FixedScanner(ScannerStatus.CLEAN)

    response = TestClient(app).post(
        "/api/v1/tools/compress-pdf/tasks",
        files={"file": ("test.pdf", _valid_pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 202
    assert len(r2.uploaded) == 1


def test_validation_failure_precedes_scanner_reach() -> None:
    """Validation outcomes reject before any scanner call (matrix order)."""

    scanner = _FixedScanner(ScannerStatus.MALICIOUS)
    app, _r2, _queue = _single_file_app("/api/v1/tools/compress-pdf/tasks", scanner)
    response = TestClient(app).post(
        "/api/v1/tools/compress-pdf/tasks",
        files={"file": ("test.pdf", b"not a pdf at all", "application/pdf")},
    )
    assert response.status_code == 400
    assert scanner.calls == [], "scanner must not run when validation rejects"


def test_router_scan_gate_blocks_when_scanner_cannot_resolve() -> None:
    """No preset scanner and no settings -> fail closed, never silently admit."""

    r2 = _FakeR2()
    queue = _RecordingQueue()
    app = FastAPI()
    app.include_router(compress.router)
    # Deliberately no app.state.settings and no app.state.scanner.
    app.state.task_store = TaskStore(_settings(), client=fakeredis.FakeRedis())
    app.state.r2_client = r2
    app.state.job_queue = queue
    response = TestClient(app).post(
        "/api/v1/tools/compress-pdf/tasks",
        files={"file": ("test.pdf", _valid_pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 429
    assert r2.uploaded == []
    assert queue.enqueued == []


def test_factory_app_readiness_reports_scanner_from_settings() -> None:
    """create_app wires settings; readiness uses the build-from-settings branch."""
    instance = create_app(settings=_settings(scanner_enabled="false"))
    instance.state.task_store = _healthy_store()
    response = TestClient(instance).get("/health/ready")
    # Disabled scanner fails closed: readiness must report not-ready.
    assert response.status_code == 503
    assert response.json()["checks"]["scanner"] == "unavailable"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
