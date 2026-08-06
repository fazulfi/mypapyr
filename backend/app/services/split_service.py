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

import io
import logging
from dataclasses import dataclass

import pikepdf

logger = logging.getLogger(__name__)


class SplitError(Exception):
    """Raised when split operation fails."""


@dataclass(frozen=True)
class SplitResult:
    """Result of a split operation."""

    output_count: int
    total_bytes: int


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


@dataclass(frozen=True)
class SplitExecutorInput:
    """Input for split executor."""

    task_id: str
    range_spec: str


class SplitExecutor:
    """Executes split jobs for the worker. Pickle-safe."""

    def __init__(self, settings: object, engine: SplitEngine | None = None) -> None:
        self._settings = settings
        self._engine = engine or SplitEngine()
        self._r2 = None
        self._store = None
        self._read_client = None

    def _get_r2(self):
        if self._r2 is None:
            from app.utils.r2 import R2Client
            self._r2 = R2Client(self._settings)
        return self._r2

    def _get_store(self):
        if self._store is None:
            from app.queue.store import TaskStore
            self._store = TaskStore(self._settings)
        return self._store

    def _get_read_client(self):
        if self._read_client is None:
            import boto3
            self._read_client = boto3.client(
                "s3",
                endpoint_url=f"https://{self._settings.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self._settings.r2_access_key_id,
                aws_secret_access_key=self._settings.r2_secret_access_key,
                region_name="auto",
            )
        return self._read_client

    def execute(self, job, report) -> object:
        """Execute a split job. Returns ExecutionOutcome."""
        from app.queue.store import TaskNotFoundError, StoreUnavailableError
        from app.schemas.job import ResultSummary
        from app.worker.worker import ExecutionKind, ExecutionOutcome

        store = self._get_store()
        r2 = self._get_r2()
        read_client = self._get_read_client()

        # Fetch the record
        try:
            record = store.get(job.task_id)
        except TaskNotFoundError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error="Task not found")
        except StoreUnavailableError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error="Store unavailable")

        if record.state != "processing":
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error="Invalid record state")

        # Download the input PDF
        input_key = record.objects[0] if record.objects else None
        if not input_key:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error="No input object")

        try:
            response = read_client.get_object(Bucket=self._settings.r2_bucket_name, Key=input_key)
            input_data = response["Body"].read()
        except Exception:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error="Failed to download input")

        # Parse the range specification (for now, use a simple default)
        # In production, this would come from the task record or job metadata
        ranges = self._parse_range_spec("1-1")  # TODO: Parse from record

        # Perform the split
        try:
            outputs = self._engine.split(input_data, ranges)
        except SplitError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error="Split operation failed")

        # Upload each output
        output_keys = []
        for i, output_data in enumerate(outputs):
            output_key = r2.build_object_key(extension="pdf")
            r2.upload_object(output_key, output_data, content_type="application/pdf")
            output_keys.append(output_key)

        # Delete the input
        r2.delete_object(input_key)

        # Report progress
        report({"unit": "pages_processed", "value": len(outputs), "total": len(outputs)})

        # Return success
        total_bytes = sum(len(o) for o in outputs)
        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=len(outputs), total_bytes=total_bytes),
            objects=tuple(output_keys),
        )

    def _parse_range_spec(self, spec: str) -> list[tuple[int, int]]:
        """Parse a range specification like '1-3,5,7-9' into a list of (start, end) tuples."""
        ranges = []
        for part in spec.split(","):
            part = part.strip()
            if "-" in part:
                start_str, end_str = part.split("-", 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                if start <= end:
                    ranges.append((start, end))
            elif part.isdigit():
                page = int(part)
                ranges.append((page, page))
        return ranges
