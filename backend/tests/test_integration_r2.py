"""R2 S3-compatible fixture integration tests (BE-03/07/09, Phase 3 gate exit).

moto serves as the S3-compatible test fixture for the R2 client's
plumbing: upload/head/delete round-trips through the typed
:class:`app.utils.r2.R2Client`, presigned-URL mapping, and the BE-07
cleanup + BE-09 download cross-boundary flows over a REAL Redis task
store.

Documented limitations (r2-pikepdf-reference-audit.md section C.3/E):
moto performs no authentication and never enforces presigned-URL expiry
or signatures — those guarantees are R2-integrational. Two tests here
PROVE the limitation (an expired URL and a tampered signature both still
fetch from moto) so nobody mistakes moto for an authz oracle, and the
client-side contracts (SigV4 query parameters, expiry capped at
min(remaining, 300 s)) are asserted on the URL itself.

The BE-07/BE-09 cross-integration tests are gated on ``REDIS_URL``
exactly like ``test_integration_redis.py``: they run in CI against the
pinned Redis service container and skip locally unless a real Redis is
available. The moto-only plumbing tests always run.
"""

from __future__ import annotations

import importlib
import os
import time
import urllib.parse
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast

import pytest
import redis
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.queue.store import (
    RedisLike,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
    TransitionPayload,
)
from app.schemas.job import ResultSummary
from app.tasks.cleanup import CleanupCoordinator
from app.tasks.state_machine import JobEvent, JobState
from app.utils.r2 import R2Client

REDIS_URL = os.environ.get("REDIS_URL")

needs_real_redis = pytest.mark.skipif(
    not REDIS_URL,
    reason="REDIS_URL unset: cross-boundary R2 integration tests opt in",
)

boto3 = cast(Any, importlib.import_module("boto3"))
moto = cast(Any, importlib.import_module("moto"))
requests = cast(Any, importlib.import_module("requests"))
ClientError = cast(Any, importlib.import_module("botocore.exceptions")).ClientError

R2_ENDPOINT = "https://test-account.r2.cloudflarestorage.com"
TEST_BUCKET = "test-bucket"
TEST_ACCESS_KEY_ID = "test-access-key-id"
TEST_SECRET_ACCESS_KEY = "test-secret-access-key"

_RESULT = ResultSummary(output_count=1, total_bytes=2048)
_BODY = b"%PDF-1.7 fake document bytes for integration round-trip"


class RealRedis(Protocol):
    """Minimal typed surface of the real Redis client for the store seam."""

    def ping(self) -> bool: ...
    def flushdb(self) -> bool: ...
    def close(self) -> None: ...
    def hgetall(self, name: str) -> dict[bytes, bytes]: ...
    def ttl(self, name: str) -> int: ...
    def delete(self, name: str) -> int: ...
    def scan_iter(self, match: str | None = None, count: int = 100) -> Iterator[bytes]: ...
    def pipeline(self, transaction: bool = True) -> Any: ...


class FakeClock:
    """Deterministic injectable time source."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def __call__(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += timedelta(seconds=seconds)


def _settings(*, redis_url: str | None = REDIS_URL) -> Settings:
    return Settings(
        r2_account_id="test-account",
        r2_access_key_id=TEST_ACCESS_KEY_ID,
        r2_secret_access_key=TEST_SECRET_ACCESS_KEY,
        r2_bucket_name=TEST_BUCKET,
        allowed_origins=("http://localhost:3000",),
        r2_endpoint=R2_ENDPOINT,
        redis_url=redis_url if redis_url is not None else "redis://localhost:6379/0",
    )


def _record(
    task_id: str,
    *,
    tool: str = "compress",
    created_at: datetime,
    expires_at: datetime,
    objects: tuple[str, ...] = (),
) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        state=JobState.QUEUED,
        tool=tool,
        created_at=created_at,
        accepted_at=created_at,
        updated_at=created_at,
        expires_at=expires_at,
        objects=objects,
    )


@pytest.fixture
def moto_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """A moto S3 backend served at the R2-style endpoint (audit C.2)."""
    monkeypatch.setenv("MOTO_S3_CUSTOM_ENDPOINTS", R2_ENDPOINT)
    with moto.mock_aws():
        client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=TEST_ACCESS_KEY_ID,
            aws_secret_access_key=TEST_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
        client.create_bucket(Bucket=TEST_BUCKET)
        yield client


@pytest.fixture
def r2_client(moto_client: Any) -> R2Client:
    return R2Client(_settings(), client=moto_client)


@pytest.fixture
def redis_client() -> Iterator[RealRedis]:
    if REDIS_URL is None:
        pytest.skip("REDIS_URL unset")
    client = cast(
        RealRedis,
        redis.Redis.from_url(
            REDIS_URL, decode_responses=False, socket_timeout=5.0, socket_connect_timeout=5.0
        ),
    )
    client.ping()
    client.flushdb()
    try:
        yield client
    finally:
        client.flushdb()
        client.close()


@pytest.fixture
def store(redis_client: RealRedis) -> TaskStore:
    return TaskStore(_settings(), client=cast(RedisLike, redis_client))


# --- BE-03 plumbing through the typed client over moto ----------------------


def test_r2_client_full_lifecycle_plumbing(r2_client: R2Client, moto_client: Any) -> None:
    key = r2_client.build_object_key(extension="pdf")
    expires_at = datetime.now(UTC) + timedelta(seconds=300)

    receipt = r2_client.upload_object(
        key, _BODY, content_type="application/pdf", expires_at=expires_at
    )
    assert receipt.key == key
    assert receipt.size_bytes == len(_BODY)

    head = moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert head["ContentType"] == "application/pdf"
    assert head["Metadata"]["expires-at"] == expires_at.isoformat(timespec="seconds")
    assert head["ContentLength"] == len(_BODY)

    # SigV4 URL shape is asserted on the production-built client (offline);
    # moto's injected client signs with its own session config.
    url = R2Client(_settings()).generate_signed_url(key, expires_at)
    params = urlsplit_params(url)
    assert params["X-Amz-Algorithm"] == "AWS4-HMAC-SHA256"
    assert "X-Amz-Signature" in params
    assert int(params["X-Amz-Expires"]) <= 300

    response = requests.get(url, timeout=10)
    assert response.status_code == 200
    assert response.content == _BODY

    assert r2_client.delete_object(key) is True
    with pytest.raises(ClientError) as excinfo:
        moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
    assert excinfo.value.response["ResponseMetadata"]["HTTPStatusCode"] == 404
    assert r2_client.delete_object(key) is True


def test_moto_does_not_enforce_presign_expiry_documented_limitation(
    r2_client: R2Client, moto_client: Any
) -> None:
    key = r2_client.build_object_key(extension="pdf")
    r2_client.upload_object(key, _BODY, content_type="application/pdf")

    now = datetime.now(UTC)
    url = R2Client(_settings()).generate_signed_url(key, now + timedelta(seconds=1), now=now)
    assert int(urlsplit_params(url)["X-Amz-Expires"]) == 1

    time.sleep(1.2)
    response = requests.get(url, timeout=10)
    assert response.status_code == 200
    assert response.content == _BODY


def test_moto_does_not_authenticate_documented_limitation(
    r2_client: R2Client, moto_client: Any
) -> None:
    key = r2_client.build_object_key(extension="pdf")
    r2_client.upload_object(key, _BODY, content_type="application/pdf")

    url = R2Client(_settings()).generate_signed_url(key, datetime.now(UTC) + timedelta(seconds=300))
    params = urlsplit_params(url)
    assert "X-Amz-Signature" in params
    assert "X-Amz-Credential" in params

    tampered = url.replace(params["X-Amz-Signature"], "0" * 64)
    response = requests.get(tampered, timeout=10)
    assert response.status_code == 200


# --- BE-07 cleanup over the real store + moto R2 ----------------------------


@needs_real_redis
def test_cleanup_drain_deletes_r2_objects_and_records(
    store: TaskStore, redis_client: RealRedis, r2_client: R2Client, moto_client: Any
) -> None:
    clock = FakeClock(datetime(2026, 8, 3, 12, 0, 0, tzinfo=UTC))
    deadline_store = TaskStore(_settings(), client=cast(RedisLike, redis_client), clock=clock)
    coordinator = CleanupCoordinator(deadline_store, r2_client, clock=clock)
    t0 = clock()

    keys: list[str] = []
    for index in range(2):
        key = r2_client.build_object_key(extension="pdf")
        r2_client.upload_object(key, _BODY, content_type="application/pdf")
        keys.append(key)
        deadline_store.create(
            _record(
                f"task-r2-clean-{index}",
                created_at=t0,
                expires_at=t0 + timedelta(seconds=30),
                objects=(key,),
            )
        )
    live_key = r2_client.build_object_key(extension="pdf")
    r2_client.upload_object(live_key, _BODY, content_type="application/pdf")
    deadline_store.create(
        _record(
            "task-r2-live",
            created_at=t0,
            expires_at=t0 + timedelta(seconds=300),
            objects=(live_key,),
        )
    )

    clock.advance(31)
    run = coordinator.run_expired(limit=2)

    assert run.cleaned == 2
    for key in keys:
        with pytest.raises(ClientError) as excinfo:
            moto_client.head_object(Bucket=TEST_BUCKET, Key=key)
        assert excinfo.value.response["ResponseMetadata"]["HTTPStatusCode"] == 404
    with pytest.raises(TaskNotFoundError):
        deadline_store.get("task-r2-clean-0")
    with pytest.raises(TaskNotFoundError):
        deadline_store.get("task-r2-clean-1")
    assert deadline_store.get("task-r2-live").state is JobState.QUEUED
    assert r2_client.delete_object(live_key) is True


# --- BE-09 download authorization over the real store + moto R2 -------------


def _make_done_record(
    store: TaskStore, *, task_id: str, tool: str = "compress", objects: tuple[str, ...]
) -> TaskRecord:
    now = datetime.now(UTC)
    created = store.create(
        _record(
            task_id,
            tool=tool,
            created_at=now,
            expires_at=now + timedelta(seconds=300),
            objects=objects,
        )
    )
    store.transition_state(task_id, JobEvent.WORKER_CLAIMED, expected_state=created.state)
    return store.transition_state(
        task_id,
        JobEvent.RESULT_UPLOADED,
        expected_state=JobState.PROCESSING,
        payload=TransitionPayload(result=_RESULT, objects=objects),
    )


@needs_real_redis
def test_download_router_grants_authorized_signed_url(
    store: TaskStore, redis_client: RealRedis, r2_client: R2Client
) -> None:
    key = r2_client.build_object_key(extension="pdf")
    r2_client.upload_object(key, _BODY, content_type="application/pdf")
    record = _make_done_record(store, task_id="task-dl-ok", objects=(key,))

    app = create_app()
    app.state.task_store = store
    app.state.r2_client = r2_client
    client = TestClient(app)

    response = client.get("/api/v1/tools/compress/tasks/task-dl-ok/download/0")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    grant = response.json()
    assert grant["expires_at"] == record.expires_at.isoformat().replace("+00:00", "Z")

    download = requests.get(grant["url"], timeout=10)
    assert download.status_code == 200
    assert download.content == _BODY


@needs_real_redis
def test_download_router_denies_unauthorized(
    store: TaskStore, redis_client: RealRedis, r2_client: R2Client
) -> None:
    key = r2_client.build_object_key(extension="pdf")
    r2_client.upload_object(key, _BODY, content_type="application/pdf")
    _make_done_record(store, task_id="task-dl-deny", objects=(key,))

    app = create_app()
    app.state.task_store = store
    app.state.r2_client = r2_client
    client = TestClient(app)

    assert client.get("/api/v1/tools/compress/tasks/unknown-id/download/0").status_code == 404
    assert client.get("/api/v1/tools/merge/tasks/task-dl-deny/download/0").status_code == 404
    assert client.get("/api/v1/tools/compress/tasks/task-dl-deny/download/5").status_code == 404

    processing = store.create(
        _record(
            "task-dl-processing",
            tool="compress",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(seconds=300),
        )
    )
    store.transition_state(
        "task-dl-processing", JobEvent.WORKER_CLAIMED, expected_state=processing.state
    )
    assert (
        client.get("/api/v1/tools/compress/tasks/task-dl-processing/download/0").status_code == 404
    )


def urlsplit_params(url: str) -> dict[str, str]:
    parsed = urllib.parse.urlsplit(url)
    return {k: values[0] for k, values in urllib.parse.parse_qs(parsed.query).items()}
