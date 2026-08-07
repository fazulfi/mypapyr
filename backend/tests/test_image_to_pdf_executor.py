"""Contract tests for ImageToPdfExecutor (U-EXEC).

Follows the test_compress_service.py fake-injection pattern: fake store, fake
R2, and fake read client replace live clients so executor behavior is
verifiable without network or Redis.
"""

from __future__ import annotations

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
    # Simple 1x1 JPEG bytes
    jpeg_bytes = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14"
        b"\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.'"
        b" \",#\x1c\x1c(7),01444\x1f'9=82<.342"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
        b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
        b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa"
        b'\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n'
        b"\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz"
        b"\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99"
        b"\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7"
        b"\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5"
        b"\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1"
        b"\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa"
        b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfe\xa8(\xa2\x80\x0a(\xa0\x02"
        b"\x8a(\x00\xff\xd9"
    )
    data_by_key = {key: jpeg_bytes for key in objects}
    r2 = FakeR2(data_by_key)
    r2.fail_delete = fail_delete
    store = FakeStore(record=record, error=store_error)
    executor._store = store  # type: ignore[assignment]
    executor._r2 = r2  # type: ignore[assignment]
    executor._read_client = FakeReadClient(data_by_key, fail_key=fail_download_key)  # type: ignore[assignment]
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
    executor._read_client = FakeReadClient({"input-a": b"not-an-image"})  # type: ignore[assignment]
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
