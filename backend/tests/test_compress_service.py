"""Tests for the compress PDF executor and Ghostscript engine."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from app.config import Settings
from app.queue.store import StoreUnavailableError, TaskNotFoundError, TaskRecord
from app.services.compress_service import (
    CompressExecutor,
    GhostscriptEngine,
    GhostscriptError,
    GhostscriptTimeoutError,
)
from app.tasks.state_machine import JobState
from app.worker.worker import ClaimedJob, ExecutionKind

R04_TOKENS = (
    "-dSAFER",
    "-dBATCH",
    "-dNOPAUSE",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.7",
    "-dDetectDuplicateImages=true",
    "-dEmbedAllFonts=true",
    "-dSubsetFonts=true",
    "-dCompressFonts=true",
    "-dDownsampleColorImages=true",
    "-dColorImageDownsampleType=/Bicubic",
    "-dColorImageDownsampleThreshold=1.5",
    "-dColorImageResolution=150",
    "-dDownsampleGrayImages=true",
    "-dGrayImageDownsampleType=/Bicubic",
    "-dGrayImageDownsampleThreshold=1.5",
    "-dGrayImageResolution=150",
)


@dataclass(frozen=True)
class FakeJob:
    task_id: str
    tool: str
    route: str
    entry_id: bytes = b"fake-entry"
    origin_fingerprint: str | None = None


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


@pytest.fixture
def sample_task_record() -> TaskRecord:
    now = datetime.now(UTC)
    return TaskRecord(
        task_id="task-abc123",
        state=JobState.PROCESSING,
        tool="compress-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        queued_at=now,
        objects=("input-key-123",),
    )


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeReadClient:
    def __init__(self, data_by_key: dict[str, bytes]) -> None:
        self._data_by_key = data_by_key

    def get_object(self, **kwargs: object) -> dict[str, object]:
        key = kwargs["Key"]
        return {"Body": FakeBody(self._data_by_key[key])}


class FakeR2:
    def __init__(self, input_key: str, input_bytes: bytes) -> None:
        self.bucket_name = "fake-bucket"
        self._objects: dict[str, bytes] = {input_key: input_bytes}
        self.uploaded: list[tuple[str, bytes]] = []
        self.deleted: list[str] = []
        self.fail_delete: bool = False

    def build_object_key(self, *, extension: str | None = None, now: datetime | None = None) -> str:
        return "tmp/2026-01-01/output-key"

    def upload_object(
        self,
        key: str,
        body: bytes,
        *,
        content_type: str | None = None,
        expires_at: datetime | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.uploaded.append((key, body))

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


class FakeRunner:
    def __init__(self, *, returncode: int = 0, output: bytes = b"%PDF-1.7 output") -> None:
        self._returncode = returncode
        self._output = output
        self.calls: list[tuple[list[str], dict[str, Any]]] = []

    def __call__(self, args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        self.calls.append((list(args), dict(kwargs)))
        output_arg = next((a for a in args if a.startswith("-sOutputFile=")), None)
        if output_arg is not None:
            Path(output_arg.split("=", 1)[1]).write_bytes(self._output)
        return subprocess.CompletedProcess(args, self._returncode, b"", b"")


def _executor(
    record: TaskRecord | None = None,
    store_error: Exception | None = None,
    *,
    engine: GhostscriptEngine | None = None,
    fail_delete: bool = False,
) -> tuple[CompressExecutor, FakeR2, FakeStore]:
    engine = engine or GhostscriptEngine(gs_path="fake-gs", runner=FakeRunner())
    executor = CompressExecutor(settings=_SETTINGS_MOCK, engine=engine)
    input_key = record.objects[0] if record is not None else "input-key-123"
    r2 = FakeR2(input_key, b"%PDF-1.7 sample pdf content")
    r2.fail_delete = fail_delete
    store = FakeStore(record=record, error=store_error)
    executor._store = store  # type: ignore[assignment]
    executor._r2 = r2  # type: ignore[assignment]
    executor._read_client = FakeReadClient({input_key: b"%PDF-1.7 sample pdf content"})
    return executor, r2, store


def test_engine_args_contain_all_r04_tokens() -> None:
    engine = GhostscriptEngine(gs_path="fake-gs")
    args = engine.build_args("/tmp/in.pdf", "/tmp/out.pdf")
    for token in R04_TOKENS:
        assert any(token in arg for arg in args), f"missing R-04 token: {token}"
    assert args.index("-dSAFER") < args.index("-dBATCH")


def test_engine_calls_subprocess_with_capture_output_and_timeout() -> None:
    runner = FakeRunner(output=b"%PDF-1.7 compressed")
    engine = GhostscriptEngine(gs_path="fake-gs", runner=runner)
    result = engine.compress(b"%PDF-1.7 input", timeout=timedelta(seconds=180))
    assert result.result_size == len(b"%PDF-1.7 compressed")
    assert runner.calls[0][1]["capture_output"] is True
    assert runner.calls[0][1]["timeout"] == 180.0


def test_engine_timeout_maps_to_timeout_error() -> None:
    def runner(args: list[str], **kwargs: Any) -> None:
        raise subprocess.TimeoutExpired(cmd=args, timeout=kwargs["timeout"])

    engine = GhostscriptEngine(gs_path="fake-gs", runner=runner)
    with pytest.raises(GhostscriptTimeoutError):
        engine.compress(b"%PDF-1.7 input", timeout=timedelta(milliseconds=1))


def test_engine_nonzero_exit_maps_to_generic_error() -> None:
    engine = GhostscriptEngine(gs_path="fake-gs", runner=FakeRunner(returncode=1))
    with pytest.raises(GhostscriptError):
        engine.compress(b"%PDF-1.7 input", timeout=timedelta(seconds=1))


def test_engine_honest_saved_percent_zero_when_not_smaller() -> None:
    runner = FakeRunner(output=b"x" * 20)
    engine = GhostscriptEngine(gs_path="fake-gs", runner=runner)
    result = engine.compress(b"y" * 20, timeout=timedelta(seconds=1))
    assert result.saved_percent == 0.0


def test_executor_happy_path(sample_task_record: TaskRecord) -> None:
    executor, r2, store = _executor(record=sample_task_record)
    job = ClaimedJob(
        task_id="task-abc123", tool="compress-pdf", route="compress-pdf", entry_id=b"entry-0"
    )
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.result.output_count == 1
    assert outcome.result.total_bytes == len(b"%PDF-1.7 output")
    assert outcome.objects == ("tmp/2026-01-01/output-key",)
    assert store.get_calls == ["task-abc123"]
    assert len(r2.uploaded) == 1
    assert r2.deleted == ["input-key-123"]


def test_executor_input_delete_failure_still_returns_success(
    sample_task_record: TaskRecord,
) -> None:
    executor, r2, _ = _executor(record=sample_task_record, fail_delete=True)
    job = ClaimedJob(
        task_id="task-abc123", tool="compress-pdf", route="compress-pdf", entry_id=b"entry-0"
    )
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.SUCCESS
    assert outcome.result is not None
    assert outcome.error is None
    assert len(r2.uploaded) == 1


def test_executor_record_not_processing_refusal() -> None:
    now = datetime.now(UTC)
    record = TaskRecord(
        task_id="task-abc123",
        state=JobState.DONE,
        tool="compress-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=3600),
        queued_at=now,
        objects=("input-key",),
    )
    executor, r2, _ = _executor(record=record)
    job = ClaimedJob(
        task_id="task-abc123", tool="compress-pdf", route="compress-pdf", entry_id=b"entry-0"
    )
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_task_not_found_returns_failure() -> None:
    executor, r2, _ = _executor(record=None, store_error=TaskNotFoundError())
    job = ClaimedJob(
        task_id="missing-task", tool="compress-pdf", route="compress-pdf", entry_id=b"entry-0"
    )
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert r2.uploaded == []


def test_executor_store_unavailable_retryable() -> None:
    executor, r2, _ = _executor(record=None, store_error=StoreUnavailableError())
    job = ClaimedJob(
        task_id="task-abc123", tool="compress-pdf", route="compress-pdf", entry_id=b"entry-0"
    )
    outcome = executor.execute(job, lambda p: None)

    assert outcome.kind == ExecutionKind.FAILURE
    assert outcome.error is not None
    assert outcome.error.retryable is True
    assert r2.uploaded == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
