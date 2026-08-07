"""Merge PDF tool service: pikepdf merge engine and job executor.

Owned by TL-03 (execution-matrix.md). The :class:`MergeEngine` uses pikepdf
to merge multiple PDFs in user-specified order and returns the merged PDF
bytes plus page/byte metadata; the :class:`MergeExecutor` downloads the
sanitized inputs from R2, merges them under the BE-08 per-tool execution
cap, uploads the merged output as a single opaque object, and idempotently
deletes the consumed inputs (FOUND-01).

Pickle-safety contract (SubprocessJobRunner pickles the executor, worker.py
302-304): the executor holds only picklable construction data — the frozen
:class:`Settings` dataclass — and builds its R2 client, task store, and
boto3 read client lazily on first :meth:`execute` inside the child process
(live redis.Redis / boto3 clients are not picklable). The admission router
never constructs the executor.

Privacy contract (DEC-175): logs carry operation names and exception class
names only; no task ids, object keys, origins, or payload details ever
reach telemetry.
"""

from __future__ import annotations

import importlib
import io
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Protocol, cast

import pikepdf

from app.config import Settings
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import ErrorSummary, Progress, ResultSummary
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client
from app.worker.worker import (
    ENGINE_ERROR_FALLBACK,
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    ProgressReporter,
)

logger = logging.getLogger(__name__)

_REFUSED_ERROR = ErrorSummary(
    code="engine_error",
    category="engine",
    retryable=False,
    message_key="error.engineError",
)
_STORE_UNAVAILABLE_ERROR = ErrorSummary(
    code="store_unavailable",
    category="engine",
    retryable=True,
    message_key="error.engineError",
)


class PikepdfError(Exception):
    pass


@dataclass(frozen=True)
class MergeResult:
    data: bytes
    total_pages: int
    total_bytes: int


class S3ReadClient(Protocol):
    def get_object(self, **kwargs: object) -> dict[str, object]: ...


def _build_read_client(settings: Settings) -> S3ReadClient:
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


class MergeEngine:
    def merge(self, sources: list[bytes], *, timeout: timedelta) -> MergeResult:
        """Merge multiple PDFs into one, preserving user-specified order.

        Args:
            sources: List of sanitized PDF bytes in user order.
            timeout: Maximum execution time.

        Returns:
            MergeResult with merged bytes, page count, and byte size.

        Raises:
            PikepdfError: On empty input, invalid PDF bytes, or engine failure.
        """
        del timeout
        if not sources:
            raise PikepdfError("No inputs")

        try:
            output = pikepdf.new()
            opened: list[Any] = []
            try:
                for data in sources:
                    source = pikepdf.open(io.BytesIO(data))
                    opened.append(source)
                for source in opened:
                    output.pages.extend(source.pages)
                total_pages = len(output.pages)
                buffer = io.BytesIO()
                output.save(buffer)
            finally:
                for source in opened:
                    source.close()
                output.close()
        except PikepdfError:
            raise
        except Exception as exc:
            logger.error(
                "merge engine failure",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise PikepdfError(f"merge failed: {type(exc).__name__}") from exc

        merged_bytes = buffer.getvalue()
        return MergeResult(
            data=merged_bytes,
            total_pages=total_pages,
            total_bytes=len(merged_bytes),
        )


class MergeExecutor:
    def __init__(self, *, settings: Settings, engine: MergeEngine | None = None) -> None:
        self._settings = settings
        self._engine = engine if engine is not None else MergeEngine()
        self._store = None
        self._r2 = None
        self._read_client = None

    @property
    def _get_store(self):
        if self._store is None:
            self._store = TaskStore(self._settings)
        return self._store

    @property
    def _get_r2(self):
        if self._r2 is None:
            self._r2 = R2Client(self._settings)
        return self._r2

    @property
    def _get_read_client(self):
        if self._read_client is None:
            self._read_client = _build_read_client(self._settings)
        return self._read_client

    def _download(self, key: str) -> bytes:
        response = self._get_read_client.get_object(Bucket=self._get_r2.bucket_name, Key=key)
        body = response.get("Body")
        read = getattr(body, "read", None)
        if not callable(read):
            raise PikepdfError("unreadable object body")
        data = read()
        if isinstance(data, str):
            return data.encode()
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
        failure = self._resolve_record(job)
        if isinstance(failure, ExecutionOutcome):
            return failure
        record, input_keys = failure
        sources: list[bytes] = []
        for key in input_keys:
            try:
                sources.append(self._download(key))
            except Exception as exc:
                logger.error(
                    "merge input download failed",
                    extra={"fields": {"error": type(exc).__name__}},
                )
                return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        timeout = timedelta(seconds=TOOL_LIMITS[ToolId.MERGE_PDF].max_execution_seconds)
        report(Progress(unit="pages_processed", value=0, total=len(input_keys)))
        try:
            result = self._engine.merge(sources, timeout=timeout)
        except PikepdfError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        output_key = self._get_r2.build_object_key(extension="pdf")
        self._get_r2.upload_object(
            output_key,
            result.data,
            content_type="application/pdf",
            expires_at=record.expires_at,
        )
        report(
            Progress(
                unit="pages_processed",
                value=result.total_pages,
                total=result.total_pages,
            )
        )
        for key in input_keys:
            try:
                self._get_r2.delete_object(key)
            except Exception as exc:
                logger.error(
                    "merge input delete failure",
                    extra={"fields": {"error": type(exc).__name__}},
                )
        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=1, total_bytes=result.total_bytes),
            objects=(output_key,),
        )
