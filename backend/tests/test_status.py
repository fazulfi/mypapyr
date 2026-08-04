"""BE-06 status API contract tests.

Locks the ``app.routers.status`` contract (execution-matrix.md BE-06 row;
plan:620-629; arch 13; DEC-033, DEC-070): ``GET
/api/v1/tools/{tool}/tasks/{task_id}/status`` serves the typed
:class:`app.schemas.job.TaskStatus` payload (14 fields, READ-ONLY) built
from the BE-04 :class:`app.queue.store.TaskStore` record and the locked
``app.tasks.state_machine`` vocabulary — neither module is re-implemented
or refactored here. Unknown or expired ids and tool mismatches return the
stable 404 not-found envelope (arch 13.5); store failure fails closed with
the generic 500 envelope; responses never carry filenames, object keys,
signed URLs, or content. The router is mounted in ``app/main.py`` by the
single integration owner (BE-09 wiring wave); the store is injected through
the documented ``app.state.task_store`` seam.

The store is exercised through the same fakeredis seam as ``test_store.py``
(FakeServer + injectable clock); the dependency seam is ``app.state.task_store``
with a documented settings/environment fallback in :func:`get_task_store`.
"""

from __future__ import annotations

import dataclasses
import json
import re
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import ClassVar, cast

import fakeredis
import pytest
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError

from app.config import Settings
from app.main import create_app
from app.queue.store import RedisLike, TaskRecord, TaskStore, TransitionPayload
from app.routers import status as status_module
from app.routers.status import get_task_store, router, status_payload
from app.schemas.job import ErrorSummary, Progress, ResultSummary, TaskStatus
from app.tasks.state_machine import JobEvent, JobState

T0 = datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC)

STATUS_PATH = "/api/v1/tools/{tool}/tasks/{task_id}/status"

TOOL = "merge-pdf"
OTHER_TOOL = "compress-pdf"

#: The exact TaskStatus field set (locked upstream at test_schemas.py:299-316;
#: mirrored here to lock the OpenAPI response schema of this router).
EXPECTED_STATUS_FIELDS = (
    "task_id",
    "tool",
    "state",
    "created_at",
    "accepted_at",
    "updated_at",
    "expires_at",
    "progress",
    "result",
    "error",
    "queued_at",
    "started_at",
    "completed_at",
    "cancellable",
)

RESULT = ResultSummary(output_count=1, total_bytes=4096)
ERROR = ErrorSummary(
    code="engine_error",
    category="engine",
    retryable=False,
    message_key="error.processingFailed",
)

#: Private internals that must never appear in a status response.
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

#: OpenAPI scan terms (word-boundary matched): ``content`` is deliberately
#: absent — it is standard OpenAPI vocabulary ("content" response keys) —
#: and its structural exclusion is locked by the TaskStatus field-set tests.
OPENAPI_FORBIDDEN_TERMS = (
    "filename",
    "password",
    "signed",
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


class _RecordingStore(TaskStore):
    """TaskStore subclass recording the settings it was constructed with.

    Monkeypatched over ``app.routers.status.TaskStore``; being a subclass it
    still satisfies the dependency's ``isinstance`` guard while recording the
    settings the dependency resolved for construction.
    """

    captured: ClassVar[list[Settings]] = []

    def __init__(self, settings: Settings, client: RedisLike | None = None) -> None:
        _RecordingStore.captured.append(settings)
        super().__init__(
            settings,
            client=client if client is not None else cast(RedisLike, fakeredis.FakeRedis()),
        )


def make_settings(*, retention_seconds: int = 3600) -> Settings:
    return Settings(
        r2_account_id="test",
        r2_access_key_id="test",
        r2_secret_access_key="test",
        r2_bucket_name="test",
        allowed_origins=("http://localhost:3000",),
        retention_seconds=retention_seconds,
    )


def make_record(
    clock: FakeClock,
    *,
    task_id: str | None = None,
    state: JobState = JobState.QUEUED,
    tool: str = TOOL,
    expires_in: int = 3600,
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=task_id or uuid.uuid4().hex,
        state=state,
        tool=tool,
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=expires_in),
    )


def make_terminal_record(
    clock: FakeClock,
    *,
    state: JobState,
    result: ResultSummary | None = None,
    error: ErrorSummary | None = None,
    completed_at: datetime | None = None,
) -> TaskRecord:
    now = clock()
    return TaskRecord(
        task_id=uuid.uuid4().hex,
        state=state,
        tool=TOOL,
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        completed_at=completed_at,
        result=result,
        error=error,
    )


def _status_url(task_id: str, tool: str = TOOL) -> str:
    return f"/api/v1/tools/{tool}/tasks/{task_id}/status"


def _router_app() -> FastAPI:
    """A bare app carrying only the BE-06 status router (wiring-owner pattern)."""
    instance = FastAPI()
    instance.include_router(router)
    return instance


def _status_app(store: TaskStore) -> FastAPI:
    """The factory app (routers mounted in main.py) with an injected store.

    The store is injected via ``app.state.task_store``, the documented test
    seam of :func:`get_task_store`.
    """
    instance = create_app()
    instance.state.task_store = store
    return instance


def _request_for(app: FastAPI) -> Request:
    scope: dict[str, object] = {"type": "http", "app": app, "headers": []}
    return Request(scope)


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


# --- router shape and ownership boundary -----------------------------------


def test_router_exposes_only_the_status_get_route() -> None:
    assert len(router.routes) == 1
    route = router.routes[0]
    assert isinstance(route, APIRoute)
    assert route.path == STATUS_PATH
    assert route.methods == {"GET"}


def test_status_endpoint_mounted_on_factory_app(store: TaskStore, clock: FakeClock) -> None:
    record = store.create(make_record(clock))
    instance = create_app()
    instance.state.task_store = store
    response = TestClient(instance).get(_status_url(record.task_id))
    assert response.status_code == 200
    assert response.json()["state"] == "queued"


def test_status_endpoint_composes_with_factory_middleware(
    store: TaskStore, clock: FakeClock
) -> None:
    record = store.create(make_record(clock))
    client = TestClient(_status_app(store))
    response = client.get(_status_url(record.task_id))
    assert response.status_code == 200
    assert response.headers["x-request-id"]
    assert response.json()["state"] == "queued"


# --- store dependency seam --------------------------------------------------


def test_store_dependency_prefers_app_state_store() -> None:
    app = FastAPI()
    store = TaskStore(make_settings(), client=cast(RedisLike, fakeredis.FakeRedis()))
    app.state.task_store = store
    assert get_task_store(_request_for(app)) is store


def test_store_dependency_caches_constructed_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    _RecordingStore.captured = []
    monkeypatch.setattr(status_module, "TaskStore", _RecordingStore)
    request = _request_for(app)
    first = get_task_store(request)
    second = get_task_store(request)
    assert first is second
    assert _RecordingStore.captured == [Settings.from_env()]


def test_store_dependency_builds_from_app_state_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    settings = make_settings(retention_seconds=77)
    app.state.settings = settings
    _RecordingStore.captured = []
    monkeypatch.setattr(status_module, "TaskStore", _RecordingStore)
    result = get_task_store(_request_for(app))
    assert _RecordingStore.captured == [settings]
    assert isinstance(result, TaskStore)


def test_store_dependency_falls_back_to_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    _RecordingStore.captured = []
    monkeypatch.setattr(status_module, "TaskStore", _RecordingStore)
    result = get_task_store(_request_for(app))
    assert _RecordingStore.captured == [Settings.from_env()]
    assert isinstance(result, TaskStore)


# --- status_payload: record -> TaskStatus mapping --------------------------


def test_status_payload_maps_queued_record_exactly(clock: FakeClock) -> None:
    record = make_record(clock)
    payload = status_payload(record)
    assert payload.task_id == record.task_id
    assert payload.tool == record.tool
    assert payload.state is JobState.QUEUED
    assert payload.created_at == record.created_at
    assert payload.accepted_at == record.accepted_at
    assert payload.updated_at == record.updated_at
    assert payload.expires_at == record.expires_at
    assert payload.queued_at is None
    assert payload.started_at is None
    assert payload.completed_at is None
    assert payload.progress is None
    assert payload.result is None
    assert payload.error is None
    assert payload.cancellable is True


def test_status_payload_cancellable_only_while_queued(clock: FakeClock) -> None:
    assert status_payload(make_record(clock)).cancellable is True
    assert status_payload(make_record(clock, state=JobState.PROCESSING)).cancellable is False
    assert status_payload(make_record(clock, state=JobState.CANCELLED)).cancellable is False
    assert (
        status_payload(
            make_terminal_record(clock, state=JobState.DONE, result=RESULT, completed_at=clock())
        ).cancellable
        is False
    )
    assert (
        status_payload(
            make_terminal_record(clock, state=JobState.FAILED, error=ERROR, completed_at=clock())
        ).cancellable
        is False
    )


def test_status_payload_done_carries_result(clock: FakeClock) -> None:
    record = make_terminal_record(clock, state=JobState.DONE, result=RESULT, completed_at=clock())
    payload = status_payload(record)
    assert payload.state is JobState.DONE
    assert payload.result == RESULT
    assert payload.error is None
    assert payload.completed_at == clock()


def test_status_payload_failed_carries_safe_error(clock: FakeClock) -> None:
    record = make_terminal_record(clock, state=JobState.FAILED, error=ERROR, completed_at=clock())
    payload = status_payload(record)
    assert payload.state is JobState.FAILED
    assert payload.error == ERROR
    assert payload.result is None


def test_status_payload_cancelled_is_terminal_without_summaries(
    clock: FakeClock,
) -> None:
    payload = status_payload(make_record(clock, state=JobState.CANCELLED))
    assert payload.state is JobState.CANCELLED
    assert payload.result is None
    assert payload.error is None


def test_status_payload_never_exposes_object_refs(clock: FakeClock) -> None:
    record = dataclasses.replace(
        make_terminal_record(clock, state=JobState.DONE, result=RESULT, completed_at=clock()),
        objects=("tmp/2026-08-03/0123456789abcdef0123456789abcdef.pdf",),
    )
    payload = status_payload(record)
    assert "objects" not in payload.model_dump()
    assert set(TaskStatus.model_fields) == set(EXPECTED_STATUS_FIELDS)


# --- endpoint: state-specific contract responses ---------------------------


def _json_dt(value: datetime) -> str:
    """The pydantic JSON serialization of an aware datetime (UTC renders as ``Z``)."""
    return value.isoformat().replace("+00:00", "Z")


def test_queued_status_endpoint_returns_full_contract(store: TaskStore, clock: FakeClock) -> None:
    record = store.create(make_record(clock))
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    assert response.json() == status_payload(record).model_dump(mode="json")


def test_processing_status_endpoint_carries_started_at(store: TaskStore, clock: FakeClock) -> None:
    record = store.create(make_record(clock))
    clock.advance(10)
    claimed = store.transition_state(
        record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
    )
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    body = response.json()
    started = claimed.started_at
    assert started is not None
    assert body["state"] == "processing"
    assert body["started_at"] == _json_dt(started)
    assert body["cancellable"] is False
    assert body["result"] is None
    assert body["error"] is None


def test_done_status_endpoint_carries_result_and_completed_at(
    store: TaskStore, clock: FakeClock
) -> None:
    record = store.create(make_record(clock))
    clock.advance(10)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(10)
    done = store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=RESULT),
    )
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    body = response.json()
    completed = done.completed_at
    assert completed is not None
    assert body["state"] == "done"
    assert body["result"] == {"output_count": 1, "total_bytes": 4096}
    assert body["error"] is None
    assert body["completed_at"] == _json_dt(completed)
    assert body["cancellable"] is False


def test_failed_status_endpoint_carries_safe_error(store: TaskStore, clock: FakeClock) -> None:
    record = store.create(make_record(clock))
    clock.advance(10)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(10)
    store.transition_state(
        record.task_id,
        JobEvent.ENGINE_ERROR,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(error=ERROR),
    )
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "failed"
    assert body["error"] == {
        "code": "engine_error",
        "category": "engine",
        "retryable": False,
        "message_key": "error.processingFailed",
    }
    assert body["result"] is None
    assert body["cancellable"] is False


def test_cancelled_status_endpoint_is_terminal_without_summaries(
    store: TaskStore, clock: FakeClock
) -> None:
    record = store.create(make_record(clock))
    cancelled = store.transition_state(
        record.task_id, JobEvent.USER_CANCELLED, expected_state=JobState.QUEUED
    )
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "cancelled"
    assert body["result"] is None
    assert body["error"] is None
    assert body["cancellable"] is False
    assert body["updated_at"] == _json_dt(cancelled.updated_at)


def test_progress_round_trips_through_endpoint(store: TaskStore, clock: FakeClock) -> None:
    record = store.create(make_record(clock))
    clock.advance(5)
    claimed = store.transition_state(
        record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED
    )
    clock.advance(5)
    store.update_progress(
        record.task_id,
        Progress(unit="pages_processed", value=5, total=10),
        expected_state=JobState.PROCESSING,
    )
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    body = response.json()
    started = claimed.started_at
    assert started is not None
    assert body["state"] == "processing"
    assert body["progress"] == {"unit": "pages_processed", "value": 5, "total": 10}
    assert body["started_at"] == _json_dt(started)


def test_status_never_extends_expiry_and_sets_no_store_cache(
    store: TaskStore, clock: FakeClock
) -> None:
    record = store.create(make_record(clock, expires_in=1800))
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 200
    assert response.json()["expires_at"] == _json_dt(record.expires_at)
    # M-4: status carries per-capability timing/progress metadata; a shared
    # proxy must never cache or replay it.
    assert response.headers["cache-control"] == "no-store"


# --- not-found behavior (arch 13.5) ----------------------------------------


def test_unknown_task_id_returns_not_found_envelope(
    store: TaskStore,
) -> None:
    task_id = uuid.uuid4().hex
    response = TestClient(_status_app(store)).get(_status_url(task_id))
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["category"] == "not_found"
    assert body["error"]["messageKey"] == "error.notFound"
    assert body["error"]["retryable"] is False
    assert body["request_id"]
    assert task_id not in response.text


def test_expired_task_id_returns_same_not_found_envelope(
    store: TaskStore, clock: FakeClock
) -> None:
    record = store.create(make_record(clock, expires_in=2))
    time.sleep(2.4)
    response = TestClient(_status_app(store)).get(_status_url(record.task_id))
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["messageKey"] == "error.notFound"
    assert record.task_id not in response.text


def test_tool_mismatch_returns_not_found_and_reveals_nothing(
    store: TaskStore, clock: FakeClock
) -> None:
    record = store.create(make_record(clock, tool=TOOL))
    client = TestClient(_status_app(store))
    wrong = client.get(_status_url(record.task_id, tool=OTHER_TOOL))
    assert wrong.status_code == 404
    assert wrong.json()["error"]["code"] == "not_found"
    assert record.task_id not in wrong.text
    right = client.get(_status_url(record.task_id, tool=TOOL))
    assert right.status_code == 200
    assert right.json()["tool"] == TOOL


def test_store_unavailable_fails_closed_with_generic_500(
    clock: FakeClock,
) -> None:
    broken = cast(RedisLike, _FailingClient(ConnectionError("secret redis detail")))
    store = TaskStore(make_settings(), client=broken, clock=clock)
    client = TestClient(_status_app(store), raise_server_exceptions=False)
    response = client.get(_status_url(uuid.uuid4().hex))
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["category"] == "system"
    assert body["error"]["messageKey"] == "error.internalError"
    assert body["error"]["retryable"] is False
    assert body["request_id"]
    assert "secret redis detail" not in response.text


def test_status_responses_carry_no_private_internals(store: TaskStore, clock: FakeClock) -> None:
    client = TestClient(_status_app(store))
    record = store.create(make_record(clock))
    clock.advance(10)
    store.transition_state(record.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(10)
    store.transition_state(
        record.task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=RESULT),
    )
    failed = store.create(make_record(clock))
    clock.advance(10)
    store.transition_state(failed.task_id, JobEvent.WORKER_CLAIMED, expected_state=JobState.QUEUED)
    clock.advance(10)
    store.transition_state(
        failed.task_id,
        JobEvent.ENGINE_ERROR,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(error=ERROR),
    )
    bodies = [
        client.get(_status_url(record.task_id)).text.lower(),
        client.get(_status_url(failed.task_id)).text.lower(),
    ]
    for body in bodies:
        for term in FORBIDDEN_RESPONSE_TERMS:
            assert term not in body


# --- OpenAPI determinism and safety ----------------------------------------


def test_openapi_paths_and_operation_locked() -> None:
    openapi = _router_app().openapi()
    assert list(openapi["paths"]) == [STATUS_PATH]
    operation = openapi["paths"][STATUS_PATH]["get"]
    assert (
        operation["operationId"] == "get_task_status_api_v1_tools__tool__tasks__task_id__status_get"
    )
    assert operation["tags"] == ["status"]
    assert operation["summary"] == "Task status"
    assert list(operation["responses"]) == ["200", "422"]
    assert operation["responses"]["200"] == {
        "description": "Successful Response",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TaskStatus"}}},
    }
    assert operation["responses"]["422"] == {
        "description": "Validation Error",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}
        },
    }


def test_openapi_parameters_locked() -> None:
    parameters = _router_app().openapi()["paths"][STATUS_PATH]["get"]["parameters"]
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
    ]


def test_openapi_task_status_schema_locked() -> None:
    schema = _router_app().openapi()["components"]["schemas"]["TaskStatus"]
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert list(schema["properties"]) == list(EXPECTED_STATUS_FIELDS)
    assert schema["required"] == [
        "task_id",
        "tool",
        "state",
        "created_at",
        "accepted_at",
        "updated_at",
        "expires_at",
    ]


def test_openapi_leaks_no_private_internals() -> None:
    openapi = _router_app().openapi()
    surface = {
        "paths": openapi["paths"],
        "task_status_schema": openapi["components"]["schemas"]["TaskStatus"],
    }
    serialized = json.dumps(surface).lower()
    for term in OPENAPI_FORBIDDEN_TERMS:
        assert re.search(rf"\b{re.escape(term)}\b", serialized) is None


def test_openapi_schema_is_deterministic_across_app_instances() -> None:
    assert _router_app().openapi() == _router_app().openapi()


def test_response_model_is_the_locked_task_status_schema() -> None:
    status = TaskStatus.model_validate(
        {
            "task_id": "a" * 32,
            "tool": TOOL,
            "state": "queued",
            "created_at": T0,
            "accepted_at": T0,
            "updated_at": T0,
            "expires_at": T0 + timedelta(seconds=3600),
            "cancellable": True,
        }
    )
    assert status.state is JobState.QUEUED
    assert status.cancellable is True
    assert set(TaskStatus.model_fields) == set(EXPECTED_STATUS_FIELDS)
