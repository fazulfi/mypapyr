"""Contract tests for ImageToPdfExecutor (U-EXEC).

Follows the test_compress_service.py fake-injection pattern: fake store, fake
R2, and fake read client replace live clients so executor behavior is
verifiable without network or Redis.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime, timedelta

import pytest
from PIL import Image

from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskNotFoundError, TaskRecord
from app.services.image_to_pdf_service import ImageToPdfExecutor
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
        task_id="task-img2pdf-1",
        state=state,
        tool="jpg-to-pdf",
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
    fail_delete: bool = False,
    fail_download_key: str | None = None,
) -> tuple[ImageToPdfExecutor, FakeR2, FakeStore]:
    executor = ImageToPdfExecutor(settings=_SETTINGS_MOCK)
    objects = record.objects if record is not None else ("input-1",)
    # 24x24 RGB JPEG: large enough for img2pdf's 3-point minimum PDF
    # dimension (a 1x1 image is rejected by img2pdf).
    buffer = io.BytesIO()
    Image.new("RGB", (24, 24), color=(200, 30, 60)).save(buffer, format="JPEG")
    jpeg_bytes = buffer.getvalue()
    data_by_key = {key: jpeg_bytes for key in objects}
    r2 = FakeR2(data_by_key)
    r2.fail_delete = fail_delete
    store = FakeStore(record=record, error=store_error)
    executor._store = store  # type: ignore[assignment]
    executor._r2 = r2  # type: ignore[assignment]
    executor._read_client = FakeReadClient(data_by_key, fail_key=fail_download_key)
    return executor, r2, store


def test_executor_happy_path_converts_images_to_single_pdf() -> None:
    record = _record(objects=("input-a", "input-b"))
    executor, r2, store = _executor(record=record)
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 1
    assert outcome.objects == ("tmp/2026-01-01/output-key.pdf",)
    assert store.get_calls == ["task-img2pdf-1"]
    assert len(r2.uploaded) == 1
    assert r2.uploaded[0][2] == "application/pdf"
    # Verify it's a valid PDF
    assert r2.uploaded[0][1].startswith(b"%PDF")


def test_executor_deletes_all_inputs_after_upload() -> None:
    record = _record(objects=("input-a", "input-b", "input-c"))
    executor, r2, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.SUCCESS
    assert sorted(r2.deleted) == ["input-a", "input-b", "input-c"]


def test_executor_input_delete_failure_still_returns_success() -> None:
    record = _record(objects=("input-a", "input-b"))
    executor, r2, _ = _executor(record=record, fail_delete=True)
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.error is None
    assert len(r2.uploaded) == 1


def test_executor_download_failure_returns_failure_without_upload() -> None:
    record = _record(objects=("input-a", "input-b"))
    executor, r2, _ = _executor(record=record, fail_download_key="input-b")
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_record_not_processing_refused_with_no_effects() -> None:
    record = _record(state=JobState.DONE)
    executor, r2, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_task_not_found_returns_failure() -> None:
    executor, r2, _ = _executor(record=None, store_error=TaskNotFoundError())
    job = ClaimedJob(task_id="missing", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_store_unavailable_retryable() -> None:
    executor, r2, _ = _executor(record=None, store_error=StoreUnavailableError())
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert outcome.error.retryable is True
    assert r2.uploaded == []


def test_executor_invalid_image_bytes_returns_failure() -> None:
    record = _record(objects=("input-a",))
    executor, r2, _ = _executor(record=record)
    executor._read_client = FakeReadClient({"input-a": b"not-an-image"})
    job = ClaimedJob(task_id="task-img2pdf-1", tool="jpg-to-pdf", route="jpg-to-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_max_image_pixels_guard_is_set() -> None:
    """Defense-in-depth: ensure Pillow decompression-bomb guard is active."""
    assert Image.MAX_IMAGE_PIXELS == 20_000_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
