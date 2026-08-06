"""BE-09 signed download authorization contract tests.

Locks the ``app.routers.download`` contract (execution-matrix.md BE-09 row;
plan:650-659; arch 15; DEC-170, DEC-075): ``GET
/api/v1/tools/{tool}/tasks/{task_id}/download/{output}`` issues a short-lived
presigned R2 GET URL — through the BE-03 :class:`app.utils.r2.R2Client`
``generate_signed_url`` ``min(remaining, 300 s)`` contract, never a local
re-implementation — only for a terminal ``done`` task whose result is
present and whose opaque object refs hold *output*. Every denial (unknown,
expired, tool mismatch, non-ready, cancelled, object-missing, out-of-range,
deadline race) returns the same stable 404 not-found envelope; store and R2
failures fail closed through the generic 500 envelope. Responses carry
``Cache-Control: no-store`` (the body embeds a credential) and the
authoritative artifact ``expires_at`` unchanged — a refreshed URL never
extends retention. Failure responses, OpenAPI, and logs never expose ids,
object keys, buckets, signed URLs, filenames, or provider details.

The store and R2 dependencies resolve per app through the same seams BE-06
established: ``app.state.task_store`` / ``app.state.r2_client`` when preset
(test/wiring seam), else lazy per-app construction bound to
``app.state.settings`` (falling back to the process environment). The router
is wired into ``app/main.py`` by the single integration owner; these tests
exercise the factory path.
"""

from __future__ import annotations

import dataclasses
import importlib
import json
import logging
import re
import urllib.parse
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar, cast

import fakeredis
import pytest
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError
from redis.exceptions import ConnectionError

from app.config import Settings
from app.main import create_app
from app.queue.store import RedisLike, TaskRecord, TaskStore, TransitionPayload
from app.routers import download as download_module
from app.routers.download import (
    DownloadContext,
    DownloadGrant,
    authorize_download,
    get_download_context,
    get_r2_client,
    router,
)
from app.routers.status import get_task_store
from app.schemas.job import ErrorSummary, ResultSummary
from app.tasks.state_machine import JobEvent, JobState
from app.utils.r2 import MAX_SIGNED_URL_SECONDS, ObjectExpiredError, R2Client

#: Untyped third-party crossing point (repo pattern, cf. test_r2.py).
ClientError = cast(Any, importlib.import_module("botocore.exceptions")).ClientError

T0 = datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC)

DOWNLOAD_PATH = "/api/v1/tools/{tool}/tasks/{task_id}/download/{output}"

TOOL = "merge-pdf"
OTHER_TOOL = "compress-pdf"

RESULT = ResultSummary(output_count=2, total_bytes=4096)

#: Opaque temporary-object refs (DEC-174); never filenames or user data.
KEY_A = "tmp/2026-08-03/" + "a" * 32 + ".pdf"
KEY_B = "tmp/2026-08-03/" + "b" * 32 + ".pdf"

FAKE_URL = "https://example.invalid/presigned"

#: Private internals that must never appear in a download response (success
#: or failure), response bodies, or OpenAPI surface. ``url`` is excluded
#: from the OpenAPI scan: ``DownloadGrant.url`` is the deliverable field,
#: locked structurally by the field-set test.
FORBIDDEN_RESPONSE_TERMS = (
    "filename",
    "password",
    "signed",
    "secret",
    "token",
    "content",
    "preview",
    "object_key",
    "redis",
    "bucket",
    "access_key",
    "account_id",
    "endpoint",
    "allowed_origins",
    "worker",
    "env",
)

#: OpenAPI scan terms (word-boundary matched); ``signed`` is legitimate
#: summary vocabulary ("Signed download") and ``url`` is the deliverable
#: field — both excluded with the scan list documented here.
OPENAPI_FORBIDDEN_TERMS = (
    "filename",
    "password",
    "secret",
    "token",
    "preview",
    "object_key",
    "redis",
    "bucket",
    "access_key",
    "account_id",
    "allowed_origins",
    "worker",
    "env",
    "endpoint",
)


class FakeClock:
    """Injectable store clock: fixed start, explicit advances."""

    def __init__(self, start: datetime) -> None:
        self._now = start

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)

    def __call__(self) -> datetime:
        return self._now


class _FailingClient:
    """Raises the configured error from every store-facing operation."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def hgetall(self, name: str) -> dict[bytes, bytes]:
        raise self._error

    def pipeline(self, transaction: bool = True) -> object:
        raise self._error

    def ttl(self, name: str) -> int:
        raise self._error

    def delete(self, name: str) -> int:
        raise self._error


class _RecordingR2(R2Client):
    """R2Client subclass recording ``generate_signed_url`` calls.

    Satisfies the dependency's ``isinstance`` guard while capturing the
    exact delegated contract arguments; optionally raises the configured
    error (the R2 failure path). No network: the base constructor only
    builds a boto3 client object.
    """

    captured: ClassVar[list[Settings]] = []

    def __init__(
        self,
        settings: Settings,
        *,
        error: Exception | None = None,
        url: str = FAKE_URL,
    ) -> None:
        _RecordingR2.captured.append(settings)
        super().__init__(settings)
        self._error = error
        self._url = url
        self.calls: list[tuple[str, datetime, datetime | None]] = []

    def generate_signed_url(
        self, key: str, expires_at: datetime, *, now: datetime | None = None
    ) -> str:
        self.calls.append((key, expires_at, now))
        if self._error is not None:
            raise self._error
        return self._url


def make_settings() -> Settings:
    return Settings(
        r2_account_id="test-account",
        r2_access_key_id="test-access-key-id",
        r2_secret_access_key="test-secret-access-key",
        r2_bucket_name="test-bucket",
        allowed_origins=("http://localhost:3000",),
    )


def make_record(
    clock: FakeClock,
    *,
    state: JobState = JobState.QUEUED,
    tool: str = TOOL,
    expires_in: int = 3600,
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=uuid.uuid4().hex,
        state=state,
        tool=tool,
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=expires_in),
        objects=objects,
    )


def done_record(clock: FakeClock, *, objects: tuple[str, ...] = (KEY_A,)) -> TaskRecord:
    """A done record with result present (the terminal-eligible shape)."""
    return dataclasses.replace(
        make_record(clock, state=JobState.DONE, objects=objects), result=RESULT
    )


def create_done(
    store: TaskStore,
    clock: FakeClock,
    *,
    tool: str = TOOL,
    expires_in: int = 3600,
    objects: tuple[str, ...] = (KEY_A, KEY_B),
) -> TaskRecord:
    """Persist a done record with result and object refs (real round-trip)."""
    record = store.create(make_record(clock, tool=tool, expires_in=expires_in, objects=objects))
    clock.advance(10)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(10)
    return store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(
            result=ResultSummary(output_count=len(objects), total_bytes=RESULT.total_bytes),
            objects=objects,
        ),
    )


def create_failed(store: TaskStore, clock: FakeClock) -> TaskRecord:
    record = store.create(make_record(clock))
    clock.advance(10)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(10)
    return store.transition_state(
        record.task_id,
        JobEvent.ENGINE_ERROR,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(
            error=ErrorSummary(
                code="engine_error",
                category="engine",
                retryable=False,
                message_key="error.processingFailed",
            )
        ),
    )


def _download_url(task_id: str, tool: str = TOOL, output: int = 0) -> str:
    return f"/api/v1/tools/{tool}/tasks/{task_id}/download/{output}"


def _router_app() -> FastAPI:
    """A bare app carrying only the BE-09 router (wiring-owner pattern)."""
    instance = FastAPI()
    instance.include_router(router)
    return instance


def _download_app(store: TaskStore, r2: R2Client) -> FastAPI:
    """The factory app (routers mounted in main.py) with injected deps."""
    instance = create_app()
    instance.state.task_store = store
    instance.state.r2_client = r2
    return instance


def _request_for(app: FastAPI) -> Request:
    scope: dict[str, object] = {"type": "http", "app": app, "headers": []}
    return Request(scope)


def _json_dt(value: datetime) -> str:
    """The pydantic JSON serialization of an aware datetime (UTC renders as ``Z``)."""
    return value.isoformat().replace("+00:00", "Z")


def _parse_params(url: str) -> dict[str, str]:
    parsed = urllib.parse.urlsplit(url)
    return {key: values[0] for key, values in urllib.parse.parse_qs(parsed.query).items()}


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(T0)


@pytest.fixture
def server() -> fakeredis.FakeServer:
    return fakeredis.FakeServer()


@pytest.fixture
def store_client(server: fakeredis.FakeServer) -> RedisLike:
    return cast(RedisLike, fakeredis.FakeRedis(server=server))


@pytest.fixture
def store(store_client: RedisLike, clock: FakeClock) -> TaskStore:
    return TaskStore(make_settings(), client=store_client, clock=clock)


@pytest.fixture
def r2(clock: FakeClock) -> _RecordingR2:
    return _RecordingR2(make_settings())


# --- router shape and ownership boundary -----------------------------------


def test_router_exposes_only_the_download_get_route() -> None:
    assert len(router.routes) == 1
    route = router.routes[0]
    assert isinstance(route, APIRoute)
    assert route.path == DOWNLOAD_PATH
    assert route.methods == {"GET"}


def test_download_uses_the_status_store_dependency() -> None:
    assert get_r2_client is not None
    assert download_module.get_task_store is get_task_store


# --- authorize_download: pure fail-closed matrix ---------------------------


def test_authorize_grants_done_task_output_key(clock: FakeClock) -> None:
    record = done_record(clock, objects=(KEY_A, KEY_B))
    assert authorize_download(record, TOOL, output=1) == KEY_B


@pytest.mark.parametrize(
    "state",
    [JobState.QUEUED, JobState.PROCESSING, JobState.FAILED, JobState.CANCELLED],
)
def test_authorize_denies_non_done_states(clock: FakeClock, state: JobState) -> None:
    record = make_record(clock, state=state, objects=(KEY_A,))
    assert authorize_download(record, TOOL, output=0) is None


def test_authorize_denies_tool_mismatch(clock: FakeClock) -> None:
    record = done_record(clock, objects=(KEY_A,))
    assert authorize_download(record, OTHER_TOOL, output=0) is None
    assert authorize_download(record, TOOL, output=0) == KEY_A


def test_authorize_denies_missing_result(clock: FakeClock) -> None:
    record = make_record(clock, state=JobState.DONE, objects=(KEY_A,))
    assert record.result is None
    assert authorize_download(record, TOOL, output=0) is None


def test_authorize_denies_missing_objects(clock: FakeClock) -> None:
    record = done_record(clock, objects=())
    assert authorize_download(record, TOOL, output=0) is None


def test_authorize_denies_out_of_range_and_negative_output(clock: FakeClock) -> None:
    record = done_record(clock, objects=(KEY_A,))
    assert authorize_download(record, TOOL, output=1) is None
    assert authorize_download(record, TOOL, output=-1) is None


# --- R2 dependency seam -----------------------------------------------------


def test_r2_dependency_prefers_app_state_client() -> None:
    app = FastAPI()
    client = R2Client(make_settings())
    app.state.r2_client = client
    assert get_r2_client(_request_for(app)) is client


def test_r2_dependency_caches_constructed_client(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    _RecordingR2.captured = []
    monkeypatch.setattr(download_module, "R2Client", _RecordingR2)
    request = _request_for(app)
    first = get_r2_client(request)
    second = get_r2_client(request)
    assert first is second
    assert _RecordingR2.captured == [Settings.from_env()]


def test_r2_dependency_builds_from_app_state_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    settings = make_settings()
    app.state.settings = settings
    _RecordingR2.captured = []
    monkeypatch.setattr(download_module, "R2Client", _RecordingR2)
    result = get_r2_client(_request_for(app))
    assert _RecordingR2.captured == [settings]
    assert isinstance(result, R2Client)


def test_r2_dependency_falls_back_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    _RecordingR2.captured = []
    monkeypatch.setattr(download_module, "R2Client", _RecordingR2)
    result = get_r2_client(_request_for(app))
    assert _RecordingR2.captured == [Settings.from_env()]
    assert isinstance(result, R2Client)


def test_download_context_composes_the_two_dependencies(store: TaskStore, r2: _RecordingR2) -> None:
    app = FastAPI()
    app.state.task_store = store
    app.state.r2_client = r2
    request = _request_for(app)
    context = get_download_context(
        get_task_store(request),
        get_r2_client(request),
    )
    assert isinstance(context, DownloadContext)
    assert context.store is store
    assert context.r2 is r2


# --- endpoint: success contract ---------------------------------------------


def test_download_success_returns_grant_with_authoritative_expiry(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock)
    response = TestClient(_download_app(store, r2)).get(_download_url(done.task_id, output=0))
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"url", "expires_at"}
    assert body["url"] == FAKE_URL
    assert body["expires_at"] == _json_dt(done.expires_at)
    assert response.headers["cache-control"] == "no-store"


def test_download_delegates_exact_contract_args_to_r2_client(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock)
    response = TestClient(_download_app(store, r2)).get(_download_url(done.task_id, output=1))
    assert response.status_code == 200
    # The router mints exactly one URL per request, delegating the opaque
    # object key and the authoritative expiry — never its own lifetime math.
    assert r2.calls == [(KEY_B, done.expires_at, None)]


def test_download_success_response_carries_request_id_and_security_headers(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock)
    response = TestClient(_download_app(store, r2)).get(_download_url(done.task_id, output=0))
    assert response.status_code == 200
    assert response.headers["x-request-id"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_refreshed_url_never_extends_retention(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock)
    client = TestClient(_download_app(store, r2))
    first = client.get(_download_url(done.task_id, output=0)).json()
    second = client.get(_download_url(done.task_id, output=0)).json()
    assert r2.calls == [(KEY_A, done.expires_at, None), (KEY_A, done.expires_at, None)]
    assert first["expires_at"] == second["expires_at"] == _json_dt(done.expires_at)


# --- endpoint: expiry-cap delegation through a real R2Client -----------------


def _real_clock_store(real_now: datetime) -> TaskStore:
    """A fakeredis store whose clock matches the record timestamps."""
    return TaskStore(
        make_settings(),
        client=cast(RedisLike, fakeredis.FakeRedis()),
        clock=FakeClock(real_now),
    )


def test_real_signed_url_through_router_capped_at_300_seconds() -> None:
    real_now = datetime.now(UTC)
    store = _real_clock_store(real_now)
    done = create_done(store, FakeClock(real_now), expires_in=3600)
    app = _download_app(store, R2Client(make_settings()))
    response = TestClient(app).get(_download_url(done.task_id, output=0))
    assert response.status_code == 200
    url = response.json()["url"]
    params = _parse_params(url)
    assert params["X-Amz-Expires"] == str(MAX_SIGNED_URL_SECONDS)
    assert int(params["X-Amz-Expires"]) <= 3600
    assert urllib.parse.urlsplit(url).netloc == "test-account.r2.cloudflarestorage.com"
    assert response.json()["expires_at"] == _json_dt(done.expires_at)


def test_real_signed_url_never_exceeds_remaining_lifetime() -> None:
    real_now = datetime.now(UTC)
    store = _real_clock_store(real_now)
    done = create_done(store, FakeClock(real_now), expires_in=45)
    app = _download_app(store, R2Client(make_settings()))
    response = TestClient(app).get(_download_url(done.task_id, output=0))
    assert response.status_code == 200
    url = response.json()["url"]
    remaining = int(_parse_params(url)["X-Amz-Expires"])
    assert 1 <= remaining <= 45


# --- endpoint: fail-closed authorization matrix ------------------------------


def test_unknown_task_returns_not_found_envelope(store: TaskStore, r2: _RecordingR2) -> None:
    task_id = uuid.uuid4().hex
    response = TestClient(_download_app(store, r2)).get(_download_url(task_id))
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["category"] == "not_found"
    assert body["error"]["messageKey"] == "error.notFound"
    assert body["error"]["retryable"] is False
    assert body["request_id"]
    assert task_id not in response.text
    assert r2.calls == []


def test_tool_mismatch_returns_not_found_and_reveals_nothing(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock)
    client = TestClient(_download_app(store, r2))
    wrong = client.get(_download_url(done.task_id, tool=OTHER_TOOL))
    assert wrong.status_code == 404
    assert wrong.json()["error"]["code"] == "not_found"
    assert done.task_id not in wrong.text
    right = client.get(_download_url(done.task_id))
    assert right.status_code == 200
    assert r2.calls == [(KEY_A, done.expires_at, None)]


def test_cancelled_task_returns_not_found_envelope(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    record = store.create(make_record(clock))
    store.transition_state(record.task_id, JobEvent.USER_CANCELLED, expected_state=JobState.QUEUED)
    response = TestClient(_download_app(store, r2)).get(_download_url(record.task_id))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert r2.calls == []


def test_failed_task_returns_not_found_envelope(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    failed = create_failed(store, clock)
    response = TestClient(_download_app(store, r2)).get(_download_url(failed.task_id))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert r2.calls == []


@pytest.mark.parametrize("state", [JobState.QUEUED, JobState.PROCESSING])
def test_non_ready_task_returns_not_found_envelope(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2, state: JobState
) -> None:
    record = store.create(make_record(clock))
    if state is JobState.PROCESSING:
        store.transition_state(
            record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
        )
    response = TestClient(_download_app(store, r2)).get(_download_url(record.task_id))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert r2.calls == []


def test_done_task_without_objects_returns_not_found_envelope(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock, objects=())
    response = TestClient(_download_app(store, r2)).get(_download_url(done.task_id))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert r2.calls == []


def test_out_of_range_output_returns_not_found_without_leaking_count(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    done = create_done(store, clock, objects=(KEY_A,))
    response = TestClient(_download_app(store, r2)).get(_download_url(done.task_id, output=7))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert r2.calls == []


def test_negative_output_is_rejected_by_validation(store: TaskStore, r2: _RecordingR2) -> None:
    response = TestClient(_download_app(store, r2)).get(_download_url(uuid.uuid4().hex, output=-1))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_deadline_race_object_expired_returns_not_found(store: TaskStore, clock: FakeClock) -> None:
    done = create_done(store, clock)
    expired = _RecordingR2(make_settings(), error=ObjectExpiredError("artifact lifetime expired"))
    response = TestClient(_download_app(store, expired)).get(_download_url(done.task_id))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert done.task_id not in response.text


def test_store_unavailable_fails_closed_with_generic_500(
    clock: FakeClock, r2: _RecordingR2
) -> None:
    broken = cast(RedisLike, _FailingClient(ConnectionError("secret redis detail")))
    store = TaskStore(make_settings(), client=broken, clock=clock)
    client = TestClient(_download_app(store, r2), raise_server_exceptions=False)
    response = client.get(_download_url(uuid.uuid4().hex))
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["category"] == "system"
    assert body["error"]["messageKey"] == "error.internalError"
    assert body["error"]["retryable"] is False
    assert body["request_id"]
    assert "secret redis detail" not in response.text


def test_r2_failure_fails_closed_with_generic_500(store: TaskStore, clock: FakeClock) -> None:
    done = create_done(store, clock)
    failing = _RecordingR2(
        make_settings(),
        error=ClientError(
            {"Error": {"Code": "SignatureDoesNotMatch", "Message": "boom"}, "ResponseMetadata": {}},
            "GetObject",
        ),
    )
    client = TestClient(_download_app(store, failing), raise_server_exceptions=False)
    response = client.get(_download_url(done.task_id))
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["category"] == "system"
    assert "boom" not in response.text
    assert "SignatureDoesNotMatch" not in response.text


# --- privacy: no sensitive values in bodies, logs, or OpenAPI ----------------


def test_download_responses_carry_no_private_internals(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2
) -> None:
    client = TestClient(_download_app(store, r2))
    done = create_done(store, clock, objects=(KEY_A, KEY_B))
    denied = client.get(_download_url(done.task_id, tool=OTHER_TOOL))
    success = client.get(_download_url(done.task_id, output=0))
    not_found = client.get(_download_url(uuid.uuid4().hex))
    assert success.status_code == 200
    assert denied.status_code == 404
    assert not_found.status_code == 404
    for body in (denied.text.lower(), not_found.text.lower()):
        for term in FORBIDDEN_RESPONSE_TERMS:
            assert term not in body
    # The success body carries the signed URL (the deliverable); the URL
    # itself contains no key, bucket, or provider internals (recording
    # client), and the opaque refs stay out of the envelope.
    success_body = success.text.lower()
    for term in FORBIDDEN_RESPONSE_TERMS:
        if term == "signed":
            continue
        assert term not in success_body
    assert KEY_A.lower() not in success_body
    assert KEY_B.lower() not in success_body
    assert "test-bucket" not in success_body
    assert "test-account" not in success_body


def test_download_minting_leaves_no_sensitive_logs(
    store: TaskStore, clock: FakeClock, r2: _RecordingR2, caplog: pytest.LogCaptureFixture
) -> None:
    done = create_done(store, clock, objects=(KEY_A,))
    with caplog.at_level(logging.INFO):
        response = TestClient(_download_app(store, r2)).get(_download_url(done.task_id))
    assert response.status_code == 200
    assert response.json()["url"] == FAKE_URL
    for record in caplog.records:
        message = record.getMessage()
        assert KEY_A not in message
        assert FAKE_URL not in message
        assert done.task_id not in message


def test_openapi_leaks_no_private_internals() -> None:
    openapi = _router_app().openapi()
    surface = {
        "paths": openapi["paths"],
        "download_grant_schema": openapi["components"]["schemas"]["DownloadGrant"],
    }
    serialized = json_lower(surface)
    for term in OPENAPI_FORBIDDEN_TERMS:
        assert re.search(rf"\b{re.escape(term)}\b", serialized) is None


def json_lower(value: object) -> str:
    return json.dumps(value).lower()


# --- OpenAPI determinism and locks ------------------------------------------


def test_openapi_paths_and_operation_locked() -> None:
    openapi = _router_app().openapi()
    assert list(openapi["paths"]) == [DOWNLOAD_PATH]
    operation = openapi["paths"][DOWNLOAD_PATH]["get"]
    assert operation["operationId"] == (
        "get_signed_download_api_v1_tools__tool__tasks__task_id__download__output__get"
    )
    assert operation["tags"] == ["download"]
    assert operation["summary"] == "Signed download"
    assert list(operation["responses"]) == ["200", "422"]
    assert operation["responses"]["200"] == {
        "description": "Successful Response",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DownloadGrant"}}},
    }
    assert operation["responses"]["422"] == {
        "description": "Validation Error",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}
        },
    }


def test_openapi_parameters_locked() -> None:
    parameters = _router_app().openapi()["paths"][DOWNLOAD_PATH]["get"]["parameters"]
    assert parameters == [
        {
            "name": "tool",
            "in": "path",
            "required": True,
            "schema": {"type": "string", "title": "Tool"},
        },
        {
            "name": "task_id",
            "in": "path",
            "required": True,
            "schema": {"type": "string", "title": "Task Id"},
        },
        {
            "name": "output",
            "in": "path",
            "required": True,
            "schema": {"type": "integer", "title": "Output", "minimum": 0},
        },
    ]


def test_openapi_download_grant_schema_locked() -> None:
    schema = _router_app().openapi()["components"]["schemas"]["DownloadGrant"]
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert list(schema["properties"]) == ["url", "expires_at"]
    assert schema["required"] == ["url", "expires_at"]


def test_openapi_schema_is_deterministic_across_app_instances() -> None:
    assert _router_app().openapi() == _router_app().openapi()


def test_response_model_is_the_locked_download_grant_schema() -> None:
    assert set(DownloadGrant.model_fields) == {"url", "expires_at"}
    grant = DownloadGrant(url=FAKE_URL, expires_at=T0 + timedelta(seconds=300))
    assert grant.url == FAKE_URL
    assert grant.expires_at == T0 + timedelta(seconds=300)
    with pytest.raises(ValidationError):
        DownloadGrant.model_validate(
            {"url": FAKE_URL, "expires_at": T0 + timedelta(seconds=300), "extra": "x"}
        )
