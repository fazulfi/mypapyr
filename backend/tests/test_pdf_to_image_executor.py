"""Contract tests for PdfToImageExecutor (U-EXEC).

Follows the test_compress_service.py fake-injection pattern: fake store, fake
R2, and fake read client replace live clients so executor behavior is
verifiable without network or Redis.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskNotFoundError, TaskRecord
from app.services.pdf_to_jpg_service import RENDER_DPI, PdfToImageExecutor, Renderer
from app.tasks.state_machine import JobState
from app.worker.worker import ClaimedJob, ExecutionKind

_SETTINGS_MOCK = Settings(
    r2_account_id="fake-account-id",
    r2_access_key_id="fake-access-key",
    r2_secret_access_key="fake-secret-key",
    r2_bucket_name="fake-bucket",
    allowed_origins=("http://localhost:3000",),
    retention_seconds=3600,
    default_timeout_seconds=180,
    redis_url="redis://localhost:6379/0",
    worker_cpus=1,
    worker_memory_bytes=2 * 1024**3,
)


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeReadClient:
    def __init__(self, data_by_key: dict[str, bytes], *, fail_key: str | None = None) -> None:
        self._data_by_key = data_by_key
        self._fail_key = fail_key

    def get_object(self, **kwargs: object) -> dict[str, object]:
        key = kwargs["Key"]
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if key == self._fail_key:
            raise RuntimeError("download failed")
        return {"Body": FakeBody(self._data_by_key[key])}


class FakeR2:
    def __init__(self, objects: dict[str, bytes]) -> None:
        self.bucket_name = "fake-bucket"
        self._objects = dict(objects)
        self.uploaded: list[tuple[str, bytes, str | None]] = []
        self.deleted: list[str] = []
        self.fail_delete: bool = False

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        return (
            f"tmp/2026-01-01/output-key.{extension}" if extension else "tmp/2026-01-01/output-key"
        )

    def upload_object(
        self,
        key: str,
        body: bytes,
        *,
        content_type: str | None = None,
        expires_at: datetime | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.uploaded.append((key, body, content_type))

    def delete_object(self, key: str) -> bool:
        if self.fail_delete:
            raise RuntimeError("delete failed")
        self.deleted.append(key)
        return True


class FakeStore:
    def __init__(self, record: TaskRecord | None = None, error: Exception | None = None) -> None:
        self._record = record
        self._error = error
        self.get_calls: list[str] = []

    def get(self, task_id: str) -> TaskRecord:
        self.get_calls.append(task_id)
        if self._error is not None:
            raise self._error
        return self._record  # type: ignore[return-value]


def _record(
    *, state: JobState = JobState.PROCESSING, objects: tuple[str, ...] = ("input-1",)
) -> TaskRecord:
    now = datetime.now(UTC)
    return TaskRecord(
        task_id="task-pdf2jpg-1",
        state=state,
        tool="pdf-to-jpg",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        queued_at=now,
        objects=objects,
    )


def _executor(
    record: TaskRecord | None = None,
    store_error: Exception | None = None,
    *,
    renderer: Renderer | None = None,
    fail_delete: bool = False,
    fail_download_key: str | None = None,
) -> tuple[PdfToImageExecutor, FakeR2, FakeStore]:
    executor = PdfToImageExecutor(settings=_SETTINGS_MOCK, renderer=renderer)
    objects = record.objects if record is not None else ("input-1",)
    data_by_key = {key: b"%PDF-1.7 fake" for key in objects}
    r2 = FakeR2(data_by_key)
    r2.fail_delete = fail_delete
    store = FakeStore(record=record, error=store_error)
    executor._store = store  # type: ignore[assignment]
    executor._r2 = r2  # type: ignore[assignment]
    executor._read_client = FakeReadClient(data_by_key, fail_key=fail_download_key)
    return executor, r2, store


def test_executor_happy_path_renders_pages_and_uploads_jpegs() -> None:
    record = _record(objects=("input-pdf",))
    render_calls: list[dict[str, object]] = []

    def fake_renderer(data: bytes, *, pages: list[int] | None, dpi: int) -> list[bytes]:
        render_calls.append({"data": data, "pages": pages, "dpi": dpi})
        return [b"jpeg-page-1", b"jpeg-page-2", b"jpeg-page-3"]

    executor, r2, store = _executor(record=record, renderer=fake_renderer)
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 3
    assert outcome.result.total_bytes == len(b"jpeg-page-1") * 3
    assert outcome.objects is not None
    assert len(outcome.objects) == 3
    assert store.get_calls == ["task-pdf2jpg-1"]
    assert len(r2.uploaded) == 3
    assert all(ct == "image/jpeg" for _, _, ct in r2.uploaded)
    assert all(key.endswith(".jpg") for key, _, _ in r2.uploaded)
    assert render_calls[0]["pages"] is None
    assert render_calls[0]["dpi"] == RENDER_DPI


def test_executor_page_order_preserved_in_output_objects() -> None:
    record = _record(objects=("input-pdf",))
    outputs: list[bytes] = [b"page-1-jpeg", b"page-2-jpeg", b"page-3-jpeg"]

    def fake_renderer(data: bytes, *, pages: list[int] | None, dpi: int) -> list[bytes]:
        return outputs

    executor, r2, _ = _executor(record=record, renderer=fake_renderer)
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)

    uploaded_bytes = [body for _, body, _ in r2.uploaded]
    assert uploaded_bytes == outputs
    assert outcome.objects is not None
    assert len(outcome.objects) == 3


def test_executor_deletes_input_after_uploads() -> None:
    record = _record(objects=("input-pdf",))

    def fake_renderer(data: bytes, *, pages: list[int] | None, dpi: int) -> list[bytes]:
        return [b"jpeg-page-1"]

    executor, r2, _ = _executor(record=record, renderer=fake_renderer)
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.SUCCESS
    assert r2.deleted == ["input-pdf"]


def test_executor_input_delete_failure_still_returns_success() -> None:
    record = _record(objects=("input-pdf",))

    def fake_renderer(data: bytes, *, pages: list[int] | None, dpi: int) -> list[bytes]:
        return [b"jpeg-page-1"]

    executor, r2, _ = _executor(record=record, renderer=fake_renderer, fail_delete=True)
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.error is None
    assert len(r2.uploaded) == 1


def test_executor_render_failure_returns_failure_without_deleting_input() -> None:
    record = _record(objects=("input-pdf",))

    def failing_renderer(data: bytes, *, pages: list[int] | None, dpi: int) -> list[bytes]:
        raise ValueError("render failed")

    executor, r2, _ = _executor(record=record, renderer=failing_renderer)
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_download_failure_returns_failure_without_upload() -> None:
    record = _record(objects=("input-pdf",))
    executor, r2, _ = _executor(record=record, fail_download_key="input-pdf")
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_record_not_processing_refused_with_no_effects() -> None:
    record = _record(state=JobState.DONE)
    executor, r2, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_task_not_found_returns_failure() -> None:
    executor, r2, _ = _executor(record=None, store_error=TaskNotFoundError())
    job = ClaimedJob(task_id="missing", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_store_unavailable_retryable() -> None:
    executor, r2, _ = _executor(record=None, store_error=StoreUnavailableError())
    job = ClaimedJob(task_id="task-pdf2jpg-1", tool="pdf-to-jpg", route="pdf-to-jpg", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert outcome.error.retryable is True
    assert r2.uploaded == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
