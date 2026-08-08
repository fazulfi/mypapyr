"""Split PDF tool service (TL-04).

Implements the canonical split engine that takes a sanitized PDF and extracts
pages according to user-provided range specifications. Returns multiple
output PDFs in the order the user requested them.

Key contracts:
- Input is ALWAYS sanitized (never trust client classification)
- Range specs like "1-3,5" yield one PDF for each range token in order
- Pages within each range are extracted in the order specified
- Each output is uploaded to R2 with a deterministic name
- Executor is pickle-safe (no live clients at construction)

Engine: pikepdf (same as TL-03 Merge, DEC-199)
"""

from __future__ import annotations

import importlib
import io
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, cast

import pikepdf

from app.config import Settings
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
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


class SplitError(Exception):
    """Raised when split operation fails."""


class RangeSpecError(SplitError):
    """Raised when a range specification is malformed."""


@dataclass(frozen=True)
class SplitResult:
    """Result of a split operation."""

    output_count: int
    total_bytes: int


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

# One token is either a single page ("5") or an inclusive range ("1-3").
_RANGE_TOKEN_RE = re.compile(r"(\d+)(?:-(\d+))?")


def parse_range_spec(spec: str) -> list[tuple[int, int]]:
    """Strictly parse a range specification like ``"1-3,5,7-9"``.

    Returns 1-indexed inclusive ``(start, end)`` tuples preserving user
    order; overlapping ranges are permitted and stay independent outputs
    (FR-SPLIT-02). Raises :class:`RangeSpecError` on an empty spec,
    malformed tokens, non-positive pages, or a reversed range — admission
    rejects such input fail-closed (FR-SPLIT-04).
    """
    ranges: list[tuple[int, int]] = []
    for part in spec.split(","):
        token = part.strip()
        match = _RANGE_TOKEN_RE.fullmatch(token)
        if match is None:
            raise RangeSpecError(f"malformed range token {token!r}")
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) is not None else start
        if start < 1 or end < start:
            raise RangeSpecError(f"invalid range {token!r}")
        ranges.append((start, end))
    if not ranges:
        raise RangeSpecError("range specification is empty")
    return ranges


def canonical_range_spec(ranges: list[tuple[int, int]]) -> str:
    """Serialize parsed ranges to the canonical ``"1-3,5,7-9"`` form."""
    return ",".join(f"{start}-{end}" if start != end else f"{start}" for start, end in ranges)


class S3ReadClient(Protocol):
    def get_object(self, **kwargs: object) -> dict[str, object]: ...


def _build_read_client(settings: Settings) -> S3ReadClient:
    """Build a boto3 S3 client for reading object bytes (r2.py has no read path)."""
    boto3 = cast(Any, importlib.import_module("boto3"))
    botocore_config = cast(Any, importlib.import_module("botocore.config"))
    endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
        config=botocore_config.Config(signature_version="s3v4", retries={"max_attempts": 2}),
    )
    return cast(S3ReadClient, client)


class SplitEngine:
    """Extracts pages from PDFs according to range specifications."""

    def split(self, data: bytes, ranges: list[tuple[int, int]] | None) -> list[bytes]:
        """Split *data* into one PDF per range; ``None`` means one output per page.

        Ranges are 1-indexed inclusive and preserve order. Fails closed with
        :class:`SplitError` on any out-of-bounds range or engine failure.
        Default mode computes ``[(page, page) for page in 1..total]``.
        """
        try:
            with pikepdf.open(io.BytesIO(data)) as pdf:
                total = len(pdf.pages)
                if total == 0:
                    raise SplitError("PDF has zero pages")
                effective = ranges if ranges is not None else [(i, i) for i in range(1, total + 1)]
                outputs = []
                for start, end in effective:
                    if start < 1 or end > total or start > end:
                        raise SplitError("range out of bounds")
                    output_pdf = pikepdf.Pdf.new()
                    for page_num in range(start - 1, end):
                        output_pdf.pages.append(pdf.pages[page_num])

                    buf = io.BytesIO()
                    output_pdf.save(buf)
                    outputs.append(buf.getvalue())

                return outputs

        except SplitError:
            raise
        except Exception as exc:
            logger.error("split engine failure", extra={"fields": {"error": type(exc).__name__}})
            raise SplitError(f"Split operation failed: {type(exc).__name__}") from exc


@dataclass(frozen=True)
class SplitExecutorInput:
    """Input for split executor."""

    task_id: str
    range_spec: str


class SplitExecutor:
    """Executes split jobs for the worker. Pickle-safe."""

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

    def _download_input(self, key: str) -> bytes | ExecutionOutcome:
        try:
            response = self._get_read_client.get_object(Bucket=self._get_r2.bucket_name, Key=key)
        except Exception as exc:
            logger.error(
                "split download failed",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        body = response.get("Body")
        read = getattr(body, "read", None)
        if not callable(read):
            logger.error(
                "split download unreadable",
                extra={"fields": {"error": "UnreadableBody"}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        data = read()
        if isinstance(data, str):
            return data.encode("utf-8")
        if isinstance(data, bytes):
            return data
        return bytes(data)

    def _resolve_ranges(
        self, record: TaskRecord
    ) -> list[tuple[int, int]] | None | ExecutionOutcome:
        spec = record.options.ranges if record.options is not None else ""
        if not spec:
            return None
        try:
            return parse_range_spec(spec)
        except RangeSpecError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

    def _upload_outputs(self, outputs: list[bytes], expires_at: datetime) -> list[str]:
        output_keys: list[str] = []
        for output_data in outputs:
            output_key = self._get_r2.build_object_key(extension="pdf")
            self._get_r2.upload_object(
                output_key, output_data, content_type="application/pdf", expires_at=expires_at
            )
            output_keys.append(output_key)
        return output_keys

    def _delete_inputs(self, keys: tuple[str, ...]) -> None:
        for key in keys:
            try:
                self._get_r2.delete_object(key)
            except Exception as exc:
                logger.error(
                    "split input delete failure",
                    extra={"fields": {"error": type(exc).__name__}},
                )

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        failure = self._resolve_record(job)
        if isinstance(failure, ExecutionOutcome):
            return failure
        record, input_keys = failure
        input_data_or_failure = self._download_input(input_keys[0])
        if isinstance(input_data_or_failure, ExecutionOutcome):
            return input_data_or_failure
        ranges = self._resolve_ranges(record)
        if isinstance(ranges, ExecutionOutcome):
            return ranges
        try:
            outputs = self._engine.split(input_data_or_failure, ranges)
        except SplitError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        if not outputs:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        output_keys = self._upload_outputs(outputs, record.expires_at)
        report(Progress(unit="pages_processed", value=len(outputs), total=len(outputs)))
        self._delete_inputs(input_keys)
        total_bytes = sum(len(o) for o in outputs)
        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=len(outputs), total_bytes=total_bytes),
            objects=tuple(output_keys),
        )
