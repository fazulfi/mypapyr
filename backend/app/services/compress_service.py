"""Compress PDF tool service: Ghostscript engine wrapper and job executor.

Owned by TL-02 (execution-matrix.md). The :class:`GhostscriptEngine` runs
the pinned Ghostscript binary through :func:`subprocess.run` with the
R-04-approved pdfwrite profile (DEC-066) and reports honest sizes
(DEC-080); the :class:`CompressExecutor` is the :class:`JobExecutor`
implementation that downloads the sanitized input from R2, runs the engine
under the BE-08 per-tool execution cap, uploads the compressed output as a
new opaque object, and idempotently deletes the consumed inputs (FOUND-01).

Pickle-safety contract (SubprocessJobRunner pickles the executor, worker.py
302-304): the executor holds only picklable construction data — the frozen
:class:`Settings` dataclass and the engine's plain configuration — and
builds its R2 client, task store, and boto3 read client lazily on first
:meth:`execute` inside the child process (live redis.Redis / boto3 clients
are not picklable). The admission router never constructs the executor.

Privacy contract (DEC-175): logs carry operation names and exception class
names only; no task ids, object keys, origins, or payload details ever
reach telemetry.
"""

from __future__ import annotations

import importlib
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Protocol, cast

from app.config import Settings
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import ErrorSummary, ResultSummary
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client
from app.worker.worker import (
    ENGINE_ERROR_FALLBACK,
    TIMEOUT_ERROR,
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    ProgressReporter,
)

logger = logging.getLogger(__name__)

_REFUSED_ERROR = ErrorSummary(
    code="engine_error", category="engine", retryable=False, message_key="error.engineError"
)
_STORE_UNAVAILABLE_ERROR = ErrorSummary(
    code="store_unavailable",
    category="engine",
    retryable=True,
    message_key="error.engineError",
)
_R04_PREFIX = (
    "-dSAFER",
    "-dBATCH",
    "-dNOPAUSE",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.7",
    "-dDetectDuplicateImages=true",
)
_FONT_FLAGS = (
    "-dEmbedAllFonts=true",
    "-dSubsetFonts=true",
    "-dCompressFonts=true",
)
_DOWNSAMPLE_COLOR = (
    "-dDownsampleColorImages=true",
    "-dColorImageDownsampleType=/Bicubic",
    "-dColorImageDownsampleThreshold=1.5",
    "-dColorImageResolution=150",
)
_DOWNSAMPLE_GRAY = (
    "-dDownsampleGrayImages=true",
    "-dGrayImageDownsampleType=/Bicubic",
    "-dGrayImageDownsampleThreshold=1.5",
    "-dGrayImageResolution=150",
)
_COLOR_IMAGE_DICT = "-dColorImageDict={/QFactor 0.76 /HSample [2 2 2 2] /VSample [2 2 2 2]}"
_GRAY_IMAGE_DICT = "-dGrayImageDict={/QFactor 0.76 /HSample [2 2 2 2] /VSample [2 2 2 2]}"


class GhostscriptError(RuntimeError):
    pass


class GhostscriptTimeoutError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompressResult:
    original_size: int
    result_size: int
    saved_percent: float


class S3ReadClient(Protocol):
    def get_object(self, **kwargs: object) -> dict[str, object]: ...


def _build_read_client(settings: Settings) -> S3ReadClient:
    """Build a boto3 S3 client for reading object bytes (r2.py has no read path)."""
    boto3 = cast(Any, importlib.import_module("boto3"))
    botocore_config = cast(Any, importlib.import_module("botocore.config"))
    endpoint = settings.r2_endpoint or (
        f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    )
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name=settings.r2_region,
        config=botocore_config.Config(
            signature_version="s3v4",
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    return cast(S3ReadClient, client)


class GhostscriptEngine:
    def __init__(self, *, gs_path: str = "gs", runner: Any | None = None) -> None:
        self._gs_path = gs_path
        self._runner = runner if runner is not None else subprocess.run

    def build_args(self, input_path: str, output_path: str) -> list[str]:
        return [
            self._gs_path,
            *_R04_PREFIX,
            *_FONT_FLAGS,
            *_DOWNSAMPLE_COLOR,
            *_DOWNSAMPLE_GRAY,
            _COLOR_IMAGE_DICT,
            _GRAY_IMAGE_DICT,
            f"-sOutputFile={output_path}",
            input_path,
        ]

    def compress(self, data: bytes, *, timeout: timedelta) -> CompressResult:
        original_size = len(data)
        with tempfile.TemporaryDirectory(prefix="papyr-gs-") as tmpdir:
            input_path = os.path.join(tmpdir, "input.pdf")
            output_path = os.path.join(tmpdir, "output.pdf")
            Path(input_path).write_bytes(data)
            args = self.build_args(input_path, output_path)
            try:
                proc = self._runner(args, capture_output=True, timeout=timeout.total_seconds())
            except subprocess.TimeoutExpired as exc:
                logger.error(
                    "ghostscript timeout",
                    extra={"fields": {"error": type(exc).__name__}},
                )
                raise GhostscriptTimeoutError() from exc
            if proc.returncode != 0:
                logger.error(
                    "ghostscript failed",
                    extra={"fields": {"error": "GhostscriptError"}},
                )
                raise GhostscriptError()
            result_path = Path(output_path)
            if not result_path.is_file():
                logger.error(
                    "ghostscript failed",
                    extra={"fields": {"error": "GhostscriptError"}},
                )
                raise GhostscriptError()
            result_size = result_path.stat().st_size
        saved_percent = (
            0.0
            if result_size >= original_size
            else round((original_size - result_size) / original_size * 100, 2)
        )
        return CompressResult(
            original_size=original_size,
            result_size=result_size,
            saved_percent=saved_percent,
        )


class CompressExecutor:
    def __init__(self, *, settings: Settings, engine: GhostscriptEngine) -> None:
        self._settings = settings
        self._engine = engine
        self._store: TaskStore | None = None
        self._r2: R2Client | None = None
        self._read_client: S3ReadClient | None = None

    @property
    def _get_store(self) -> TaskStore:
        if self._store is None:
            self._store = TaskStore(self._settings)
        return self._store

    @property
    def _get_r2(self) -> R2Client:
        if self._r2 is None:
            self._r2 = R2Client(self._settings)
        return self._r2

    @property
    def _get_read_client(self) -> S3ReadClient:
        if self._read_client is None:
            self._read_client = _build_read_client(self._settings)
        return self._read_client

    def _download(self, key: str) -> bytes:
        response = self._get_read_client.get_object(Bucket=self._get_r2.bucket_name, Key=key)
        body = response.get("Body")
        read = getattr(body, "read", None)
        if not callable(read):
            raise GhostscriptError()
        data = read()
        if isinstance(data, str):
            return data.encode("utf-8")
        return bytes(data)

    def _resolve_record(
        self, job: ClaimedJob
    ) -> ExecutionOutcome | tuple[TaskRecord, tuple[str, ...]]:
        try:
            record = self._get_store.get(job.task_id)
        except TaskNotFoundError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        except StoreUnavailableError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=_STORE_UNAVAILABLE_ERROR)
        if record.state is not JobState.PROCESSING or not record.objects:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=_REFUSED_ERROR)
        return record, record.objects

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        del report
        failure = self._resolve_record(job)
        if isinstance(failure, ExecutionOutcome):
            return failure
        record, input_keys = failure
        data = self._download(input_keys[0])
        timeout = timedelta(seconds=TOOL_LIMITS[ToolId.COMPRESS_PDF].max_execution_seconds)
        try:
            result = self._engine.compress(data, timeout=timeout)
        except GhostscriptTimeoutError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=TIMEOUT_ERROR)
        except GhostscriptError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        output_key = self._get_r2.build_object_key(extension="pdf")
        self._get_r2.upload_object(
            output_key,
            data,
            content_type="application/pdf",
            expires_at=record.expires_at,
        )
        for key in input_keys:
            try:
                self._get_r2.delete_object(key)
            except Exception as exc:
                logger.error(
                    "compress input delete failure",
                    extra={"fields": {"error": type(exc).__name__}},
                )
        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=1, total_bytes=result.result_size),
            objects=(output_key,),
        )
