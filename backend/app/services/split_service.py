"""Split PDF tool service (TL-04).

Implements the canonical split engine that takes a sanitized PDF and extracts
pages according to user-provided range specifications. Returns multiple
output PDFs in the order the user requested them.

Key contracts:
- Input is ALWAYS sanitized (never trust client classification)
- Range specs like "1-3,5" yield one PDF for each range token in order
- Pages within each range are extracted in the order specified
- Each output is uploaded to R2 with a deterministic name
- Executor is pickle-safe: module imports live at top level, but live Redis/
  boto3 clients are only instantiated lazily inside the child process

Engine: pikepdf (same as TL-03 Merge, DEC-199)
"""

from __future__ import annotations

import importlib
import logging
import io
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Protocol, cast

import pikepdf

from app.config import Settings
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskStore,
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import ErrorSummary, ResultSummary
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
    code="engine_error", category="engine", retryable=False, message_key="error.engineError"
)


class SplitError(Exception):
    """Raised when split operation fails."""


@dataclass(frozen=True)
class SplitResult:
    """Result of a split operation."""

    output_count: int
    total_bytes: int


class S3ReadClient(Protocol):
    """Minimal boto3 get_object interface."""

    def get_object(self, **kwargs: object) -> dict[str, object]: ...


class SplitEngine:
    """Extracts pages from PDFs according to range specifications."""

    def split(self, data: bytes, ranges: list[tuple[int, int]]) -> list[bytes]:
        """Split a PDF into multiple PDFs based on page ranges.

        Args:
            data: Source PDF bytes (already sanitized)
            ranges: List of (start, end) page ranges (1-indexed, inclusive)

        Returns:
            List of PDF bytes, one per range, in order
        """
        try:
            with pikepdf.open(io.BytesIO(data)) as pdf:
                outputs = []
                for start, end in ranges:
                    # Create a new PDF with pages from start to end
                    output_pdf = pikepdf.Pdf.new()
                    for page_num in range(start - 1, min(end, len(pdf.pages))):
                        output_pdf.pages.append(pdf.pages[page_num])

                    buf = io.BytesIO()
                    output_pdf.save(buf)
                    outputs.append(buf.getvalue())

                return outputs

        except Exception as exc:
            logger.error("split engine failure", extra={"fields": {"error": type(exc).__name__}})
            raise SplitError(f"Split operation failed: {exc}") from exc

    def _parse_range_spec(self, spec: str) -> list[tuple[int, int]]:
        """Parse a range specification like '1-3,5,7-9' into (start, end) tuples.

        Ranges are 1-indexed and inclusive. Invalid tokens (reversed ranges,
        non-numeric, empty) are silently skipped so a malformed spec never
        aborts a job.
        """
        ranges: list[tuple[int, int]] = []
        for token in spec.split(","):
            stripped = token.strip()
            if "-" in stripped:
                start_str, end_str = stripped.split("-", 1)
                if start_str.strip().isdigit() and end_str.strip().isdigit():
                    start = int(start_str.strip())
                    end = int(end_str.strip())
                    if start <= end:
                        ranges.append((start, end))
            elif stripped.isdigit():
                page = int(stripped)
                ranges.append((page, page))
        return ranges


def _build_read_client(settings: Settings) -> S3ReadClient:
    """Build a boto3 S3 read client for R2 (r2.py has no read path)."""
    boto3 = cast(Any, importlib.import_module("boto3"))
    endpoint = settings.r2_endpoint or f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name=settings.r2_region,
    )
    return cast(S3ReadClient, client)


class SplitExecutor:
    """Executes split jobs for the worker. Pickle-safe.

    Holds only picklable data (Settings + engine) at construction. Live Redis
    and boto3 clients are built lazily on first execute() inside the child
    process, since live clients are not picklable.
    """

    def __init__(self, *, settings: Settings, engine: SplitEngine | None = None) -> None:
        self._settings = settings
        self._engine = engine or SplitEngine()
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

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        """Execute a split job. Returns an ExecutionOutcome (fail-closed)."""
        del report
        try:
            record = self._get_store.get(job.task_id)
        except TaskNotFoundError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        except StoreUnavailableError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=_REFUSED_ERROR)
        if record.state != "processing" or not record.objects:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=_REFUSED_ERROR)

        input_key = record.objects[0]
        response = self._get_read_client.get_object(
            Bucket=self._get_r2.bucket_name, Key=input_key
        )
        body = response.get("Body")
        read = getattr(body, "read", None)
        if not callable(read):
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        input_data = read()
        if isinstance(input_data, str):
            input_data = input_data.encode("utf-8")
        else:
            input_data = bytes(input_data)

        # Parse the range specification from the job input (fall back to a
        # single-page default taken from the executor's configurable input).
        spec = getattr(job, "range_spec", None) or getattr(self, "_spec", "1-1")
        ranges = self._engine._parse_range_spec(spec)
        timeout = timedelta(seconds=TOOL_LIMITS[ToolId.SPLIT_PDF].max_execution_seconds)

        try:
            outputs = self._engine.split(input_data, ranges)
        except SplitError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

        output_keys = []
        for output_data in outputs:
            output_key = self._get_r2.build_object_key(extension="pdf")
            self._get_r2.upload_object(
                output_key,
                output_data,
                content_type="application/pdf",
                expires_at=record.expires_at,
            )
            output_keys.append(output_key)

        self._get_r2.delete_object(input_key)

        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=len(outputs), total_bytes=sum(len(o) for o in outputs)),
            objects=tuple(output_keys),
        )
