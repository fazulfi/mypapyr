"""Contract tests for MergeExecutor and the MergeResult byte contract (U-EXEC).

Follows the test_compress_service.py fake-injection pattern: fake store, fake
R2, and fake read client replace live clients so executor behavior is
verifiable without network or Redis.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass
from datetime import UTC, datetime, timedelta

import pytest

from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskNotFoundError, TaskRecord
from app.schemas.job import Progress
from app.services.merge_service import (
    MergeEngine,
    MergeExecutor,
    MergeResult,
    PikepdfError,
)
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


@dataclass(frozen=True)
class FakeEngineResult:
    data: bytes
    total_pages: int
    total_bytes: int


class FakeMergeEngine:
    def __init__(self, *, result: FakeEngineResult | None = None, error: Exception | None = None):
        self._result = result
        self._error = error
        self.calls: list[tuple[list[bytes], timedelta]] = []

    def merge(self, sources: list[bytes], *, timeout: timedelta) -> FakeEngineResult:
        self.calls.append((list(sources), timeout))
        if self._error is not None:
            raise self._error
        assert self._result is not None, "FakeMergeEngine built without a result"
        return self._result


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
    *,
    state: JobState = JobState.PROCESSING,
    objects: tuple[str, ...] = ("input-1", "input-2"),
) -> TaskRecord:
    now = datetime.now(UTC)
    return TaskRecord(
        task_id="task-merge-1",
        state=state,
        tool="merge-pdf",
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
    engine: FakeMergeEngine | None = None,
    fail_delete: bool = False,
    fail_download_key: str | None = None,
) -> tuple[MergeExecutor, FakeR2, FakeStore, FakeMergeEngine]:
    engine = engine or FakeMergeEngine(
        result=FakeEngineResult(data=b"%PDF-1.7 merged", total_pages=4, total_bytes=15)
    )
    executor = MergeExecutor(settings=_SETTINGS_MOCK, engine=engine)  # type: ignore[arg-type]
    objects = record.objects if record is not None else ("input-1", "input-2")
    data_by_key = {key: f"%PDF-1.7 {key}".encode() for key in objects}
    r2 = FakeR2(data_by_key)
    r2.fail_delete = fail_delete
    store = FakeStore(record=record, error=store_error)
    executor._store = store  # type: ignore[assignment]
    executor._r2 = r2  # type: ignore[assignment]
    executor._read_client = FakeReadClient(data_by_key, fail_key=fail_download_key)
    return executor, r2, store, engine


def test_merge_result_frozen_dataclass_carries_data_and_metadata() -> None:
    result = MergeResult(data=b"%PDF-1.7 merged", total_pages=3, total_bytes=15)
    assert result.data == b"%PDF-1.7 merged"
    assert result.total_pages == 3
    assert result.total_bytes == 15
    with pytest.raises(FrozenInstanceError):
        result.total_pages = 4  # type: ignore[misc]


def test_merge_engine_returns_bytes_plus_metadata_for_real_pdfs() -> None:
    pikepdf = pytest.importorskip("pikepdf")
    one = pikepdf.new()
    one.add_blank_page(page_size=(612, 792))
    two = pikepdf.new()
    two.add_blank_page(page_size=(612, 792))
    two.add_blank_page(page_size=(612, 792))
    buf_one, buf_two = __import__("io").BytesIO(), __import__("io").BytesIO()
    one.save(buf_one)
    two.save(buf_two)

    engine = MergeEngine()
    result = engine.merge([buf_one.getvalue(), buf_two.getvalue()], timeout=timedelta(seconds=180))

    assert isinstance(result.data, bytes)
    assert result.data.startswith(b"%PDF")
    assert result.total_pages == 3
    assert result.total_bytes == len(result.data)
    reopened = pikepdf.open(__import__("io").BytesIO(result.data))
    assert len(reopened.pages) == 3
    reopened.close()


def test_merge_engine_preserves_file_and_page_order() -> None:
    pikepdf = pytest.importorskip("pikepdf")
    first = pikepdf.new()
    first.add_blank_page(page_size=(100, 100))
    second = pikepdf.new()
    second.add_blank_page(page_size=(200, 200))
    second.add_blank_page(page_size=(300, 300))
    buf_first, buf_second = __import__("io").BytesIO(), __import__("io").BytesIO()
    first.save(buf_first)
    second.save(buf_second)

    engine = MergeEngine()
    result = engine.merge(
        [buf_first.getvalue(), buf_second.getvalue()], timeout=timedelta(seconds=60)
    )

    reopened = pikepdf.open(__import__("io").BytesIO(result.data))
    mediaboxes = [page.MediaBox for page in reopened.pages]
    assert len(mediaboxes) == 3
    assert float(mediaboxes[0][2]) == 100
    assert float(mediaboxes[1][2]) == 200
    assert float(mediaboxes[2][2]) == 300
    reopened.close()


def test_merge_engine_empty_sources_raises() -> None:
    engine = MergeEngine()
    with pytest.raises(PikepdfError):
        engine.merge([], timeout=timedelta(seconds=1))


def test_merge_engine_invalid_bytes_raise_pikepdf_error() -> None:
    engine = MergeEngine()
    with pytest.raises(PikepdfError):
        engine.merge([b"not-a-pdf"], timeout=timedelta(seconds=1))


def test_executor_happy_path_preserves_input_order_and_uploads_merged_bytes() -> None:
    record = _record(objects=("input-a", "input-b"))
    executor, r2, store, engine = _executor(record=record)
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 1
    assert outcome.result.total_bytes == 15
    assert outcome.objects == ("tmp/2026-01-01/output-key.pdf",)
    assert store.get_calls == ["task-merge-1"]
    assert engine.calls[0][0] == [b"%PDF-1.7 input-a", b"%PDF-1.7 input-b"]
    assert len(r2.uploaded) == 1
    assert r2.uploaded[0][1] == b"%PDF-1.7 merged"
    assert r2.uploaded[0][2] == "application/pdf"


def test_executor_reports_progress() -> None:
    record = _record(objects=("input-a",))
    executor, _, _, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    progress: list[Progress] = []
    executor.execute(job, progress.append)
    assert all(isinstance(p, Progress) for p in progress)
    assert len(progress) >= 1


def test_executor_deletes_all_inputs_after_upload() -> None:
    record = _record(objects=("input-a", "input-b", "input-c"))
    executor, r2, _, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.SUCCESS
    assert sorted(r2.deleted) == ["input-a", "input-b", "input-c"]


def test_executor_input_delete_failure_still_returns_success() -> None:
    record = _record(objects=("input-a", "input-b"))
    executor, r2, _, _ = _executor(record=record, fail_delete=True)
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.error is None
    assert len(r2.uploaded) == 1


def test_executor_engine_failure_returns_failure_without_deleting_inputs() -> None:
    record = _record(objects=("input-a",))
    engine = FakeMergeEngine(error=PikepdfError("boom"))
    executor, r2, _, _ = _executor(record=record, engine=engine)
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_download_failure_returns_failure_without_upload() -> None:
    record = _record(objects=("input-a", "input-b"))
    executor, r2, _, _ = _executor(record=record, fail_download_key="input-b")
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_record_not_processing_refused_with_no_effects() -> None:
    record = _record(state=JobState.DONE)
    executor, r2, _, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_task_not_found_returns_failure() -> None:
    executor, r2, _, _ = _executor(record=None, store_error=TaskNotFoundError())
    job = ClaimedJob(task_id="missing", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_store_unavailable_retryable() -> None:
    executor, r2, _, _ = _executor(record=None, store_error=StoreUnavailableError())
    job = ClaimedJob(task_id="task-merge-1", tool="merge-pdf", route="merge-pdf", entry_id=b"e")
    outcome = executor.execute(job, lambda p: None)
    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert outcome.error.retryable is True
    assert r2.uploaded == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
