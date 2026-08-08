"""Split service engine and executor tests (TL-04).

Covers the strict range parser, the SplitEngine page-extraction contract,
and the SplitExecutor happy-path lifecycle (download -> split -> upload all
outputs -> delete input) for both default one-per-page mode and custom
ranges. Fake store/R2/read-client injection replaces live clients so the
executor is verifiable without network or Redis.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime, timedelta

import pytest

from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskNotFoundError, TaskRecord
from app.schemas.job import Progress, SplitOptions
from app.services.split_service import (
    RangeSpecError,
    SplitEngine,
    SplitError,
    SplitExecutor,
    canonical_range_spec,
    parse_range_spec,
)
from app.tasks.state_machine import JobState
from app.worker.worker import ClaimedJob, ExecutionKind


def _settings() -> Settings:
    return Settings(
        r2_account_id="fake-account-id",
        r2_access_key_id="fake-access-key",
        r2_secret_access_key="fake-secret-key",
        r2_bucket_name="fake-bucket",
        allowed_origins=("http://localhost:3000",),
        retention_seconds=3600,
        default_timeout_seconds=180,
        redis_url="redis://localhost:6379/15",
        worker_cpus=1,
        worker_memory_bytes=2 * 1024**3,
    )


def _pdf_bytes(num_pages: int) -> bytes:
    pikepdf = pytest.importorskip("pikepdf")
    pdf = pikepdf.new()
    for index in range(num_pages):
        pdf.add_blank_page(page_size=(100 + index, 200))
    buf = io.BytesIO()
    pdf.save(buf)
    pdf.close()
    return buf.getvalue()


def _pdf_page_widths(data: bytes) -> list[float]:
    pikepdf = pytest.importorskip("pikepdf")
    pdf = pikepdf.open(io.BytesIO(data))
    widths = [float(page.MediaBox[2]) for page in pdf.pages]
    pdf.close()
    return widths


class _FakeStore:
    def __init__(self, record: TaskRecord | None = None, error: Exception | None = None) -> None:
        self._record = record
        self._error = error
        self.get_calls: list[str] = []

    def get(self, task_id: str) -> TaskRecord:
        self.get_calls.append(task_id)
        if self._error is not None:
            raise self._error
        if self._record is None:
            raise TaskNotFoundError()
        return self._record


class _FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class _FakeReadClient:
    def __init__(self, data: bytes, *, fail: bool = False) -> None:
        self._data = data
        self._fail = fail
        self.get_calls: list[str] = []

    def get_object(self, **kwargs: object) -> dict[str, object]:
        key = kwargs["Key"]
        self.get_calls.append(str(key))
        if self._fail:
            raise RuntimeError("download failed")
        return {"Body": _FakeBody(self._data)}


class _FakeR2:
    def __init__(self) -> None:
        self.bucket_name = "fake-bucket"
        self.uploaded: list[tuple[str, bytes, str | None]] = []
        self.deleted: list[str] = []
        self.fail_delete: bool = False
        self._next_key = 0

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        self._next_key += 1
        suffix = f".{extension}" if extension else ""
        return f"tmp/2026-01-01/output-{self._next_key}{suffix}"

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


def _record(
    *,
    state: JobState = JobState.PROCESSING,
    objects: tuple[str, ...] = ("input-1",),
    options: SplitOptions | None = None,
) -> TaskRecord:
    now = datetime.now(UTC)
    return TaskRecord(
        task_id="task-split-1",
        state=state,
        tool="split-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        queued_at=now,
        objects=objects,
        options=options,
    )


def _executor(
    record: TaskRecord | None = None,
    store_error: Exception | None = None,
    *,
    input_data: bytes = b"%PDF-1.7 input",
    fail_download: bool = False,
    fail_delete: bool = False,
) -> tuple[SplitExecutor, _FakeR2, _FakeStore, _FakeReadClient]:
    executor = SplitExecutor(settings=_settings())
    store = _FakeStore(record=record, error=store_error)
    r2 = _FakeR2()
    r2.fail_delete = fail_delete
    read_client = _FakeReadClient(input_data, fail=fail_download)
    executor._store = store  # type: ignore[assignment]
    executor._r2 = r2  # type: ignore[assignment]
    executor._read_client = read_client
    return executor, r2, store, read_client


# --- strict range parser -------------------------------------------------


def test_parse_range_spec_simple() -> None:
    assert parse_range_spec("1-3") == [(1, 3)]


def test_parse_range_spec_multiple_preserves_order() -> None:
    assert parse_range_spec("1-3,5,7-9") == [(1, 3), (5, 5), (7, 9)]


def test_parse_range_spec_single_page() -> None:
    assert parse_range_spec("5") == [(5, 5)]


def test_parse_range_spec_tolerates_surrounding_whitespace() -> None:
    assert parse_range_spec(" 1-3 , 5 ") == [(1, 3), (5, 5)]


def test_parse_range_spec_inner_whitespace_in_token_rejected() -> None:
    """Space within a token like '1 - 3' is malformed (FR-SPLIT-04)."""
    with pytest.raises(RangeSpecError):
        parse_range_spec(" 1 - 3 ")


def test_parse_range_spec_overlapping_ranges_permitted() -> None:
    assert parse_range_spec("1-3,2-4") == [(1, 3), (2, 4)]


def test_parse_range_spec_empty_raises() -> None:
    with pytest.raises(RangeSpecError):
        parse_range_spec("")


def test_parse_range_spec_whitespace_only_raises() -> None:
    with pytest.raises(RangeSpecError):
        parse_range_spec("   ")


def test_parse_range_spec_malformed_token_raises() -> None:
    with pytest.raises(RangeSpecError):
        parse_range_spec("1-a")


def test_parse_range_spec_reversed_range_raises() -> None:
    with pytest.raises(RangeSpecError):
        parse_range_spec("5-2")


def test_parse_range_spec_zero_page_raises() -> None:
    with pytest.raises(RangeSpecError):
        parse_range_spec("0")


def test_parse_range_spec_trailing_comma_raises() -> None:
    with pytest.raises(RangeSpecError):
        parse_range_spec("1-3,")


def test_canonical_range_spec_round_trip() -> None:
    parsed = parse_range_spec("2-5,7,9-11")
    assert canonical_range_spec(parsed) == "2-5,7,9-11"


# --- SplitEngine contract ------------------------------------------------


def test_engine_default_mode_one_output_per_page() -> None:
    data = _pdf_bytes(4)
    outputs = SplitEngine().split(data, None)
    assert len(outputs) == 4
    for output in outputs:
        assert _pdf_page_widths(output)


def test_engine_default_mode_preserves_page_order() -> None:
    data = _pdf_bytes(3)
    outputs = SplitEngine().split(data, None)
    # page i has width 100+i, so each single-page output carries its width
    assert _pdf_page_widths(outputs[0]) == [100.0]
    assert _pdf_page_widths(outputs[1]) == [101.0]
    assert _pdf_page_widths(outputs[2]) == [102.0]


def test_engine_custom_ranges_pages_2_to_5() -> None:
    data = _pdf_bytes(6)
    outputs = SplitEngine().split(data, [(2, 5)])
    assert len(outputs) == 1
    assert _pdf_page_widths(outputs[0]) == [101.0, 102.0, 103.0, 104.0]


def test_engine_multiple_ranges_independent_outputs_in_order() -> None:
    data = _pdf_bytes(6)
    outputs = SplitEngine().split(data, [(1, 2), (4, 4), (5, 6)])
    assert len(outputs) == 3
    assert _pdf_page_widths(outputs[0]) == [100.0, 101.0]
    assert _pdf_page_widths(outputs[1]) == [103.0]
    assert _pdf_page_widths(outputs[2]) == [104.0, 105.0]


def test_engine_out_of_bounds_range_fails_closed() -> None:
    data = _pdf_bytes(2)
    with pytest.raises(SplitError):
        SplitEngine().split(data, [(1, 5)])


def test_engine_invalid_bytes_raise_split_error() -> None:
    with pytest.raises(SplitError):
        SplitEngine().split(b"not-a-pdf", [(1, 1)])


# --- executor happy-path lifecycle ---------------------------------------


def test_executor_default_mode_uploads_one_output_per_page_and_deletes_input() -> None:
    data = _pdf_bytes(3)
    record = _record(options=None)
    executor, r2, store, read_client = _executor(record=record, input_data=data)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 3
    assert len(r2.uploaded) == 3
    assert read_client.get_calls == ["input-1"]
    assert r2.deleted == ["input-1"]
    assert store.get_calls == ["task-split-1"]
    widths = [_pdf_page_widths(body) for _, body, _ in r2.uploaded]
    assert widths == [[100.0], [101.0], [102.0]]


def test_executor_custom_ranges_2_to_5_uploads_single_output() -> None:
    data = _pdf_bytes(6)
    record = _record(options=SplitOptions(ranges="2-5"))
    executor, r2, _, _ = _executor(record=record, input_data=data)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 1
    assert len(r2.uploaded) == 1
    assert _pdf_page_widths(r2.uploaded[0][1]) == [101.0, 102.0, 103.0, 104.0]
    assert r2.deleted == ["input-1"]


def test_executor_multiple_ranges_upload_all_outputs_in_order() -> None:
    data = _pdf_bytes(6)
    record = _record(options=SplitOptions(ranges="1-2,4,5-6"))
    executor, r2, _, _ = _executor(record=record, input_data=data)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 3
    assert outcome.objects is not None
    assert len(outcome.objects) == 3
    widths = [_pdf_page_widths(body) for _, body, _ in r2.uploaded]
    assert widths == [[100.0, 101.0], [103.0], [104.0, 105.0]]


def test_executor_reports_progress_with_total_outputs() -> None:
    data = _pdf_bytes(3)
    record = _record(options=None)
    executor, _, _, _ = _executor(record=record, input_data=data)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")
    progress: list[Progress] = []

    executor.execute(job, progress.append)

    assert len(progress) >= 1
    assert all(isinstance(p, Progress) for p in progress)
    assert progress[-1].value == 3
    assert progress[-1].total == 3


def test_executor_input_delete_failure_still_returns_success() -> None:
    data = _pdf_bytes(2)
    record = _record(options=None)
    executor, r2, _, _ = _executor(record=record, input_data=data, fail_delete=True)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert len(r2.uploaded) == 2


def test_executor_malformed_persisted_ranges_fail_closed_without_upload() -> None:
    # Simulate a corrupt persisted record (bypass schema validation); the
    # executor must re-validate defensively and fail closed.
    corrupt_options = SplitOptions.model_construct(ranges="1-a")
    record = _record(options=corrupt_options)
    executor, r2, _, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_empty_spec_in_options_falls_back_to_default_mode() -> None:
    data = _pdf_bytes(2)
    record = _record(options=SplitOptions(ranges=""))
    executor, r2, _, _ = _executor(record=record, input_data=data)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert len(r2.uploaded) == 2
    assert r2.deleted == ["input-1"]


def test_executor_download_failure_returns_failure_without_upload() -> None:
    record = _record(options=None)
    executor, r2, _, _ = _executor(record=record, fail_download=True)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_record_not_processing_refused_with_no_effects() -> None:
    record = _record(state=JobState.DONE)
    executor, r2, _, _ = _executor(record=record)
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert r2.uploaded == []
    assert r2.deleted == []


def test_executor_store_unavailable_is_retryable() -> None:
    executor = SplitExecutor(settings=_settings())
    executor._store = _FakeStore(error=StoreUnavailableError())  # type: ignore[assignment]
    job = ClaimedJob(task_id="task-split-1", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert outcome.error.retryable is True
    assert outcome.error.code == "store_unavailable"


def test_executor_task_not_found_returns_failure() -> None:
    executor = SplitExecutor(settings=_settings())
    executor._store = _FakeStore(error=TaskNotFoundError())  # type: ignore[assignment]
    job = ClaimedJob(task_id="missing", tool="split-pdf", route="split-pdf", entry_id=b"e")

    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
