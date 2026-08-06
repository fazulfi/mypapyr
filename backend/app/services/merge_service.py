"""Merge PDF tool service: pikepdf merge engine and job executor.

Owned by TL-03 (execution-matrix.md). The :class: uses pikepdf to
merge multiple PDFs in user-specified order; the :class: downloads
sanitized inputs from R2, merges them under BE-08 per-tool execution cap, uploads
the merged output as a single opaque object, and idempotently deletes consumed
inputs (FOUND-01).

Pickle-safety contract: holds only picklable data (Settings + config), builds
R2 client + TaskStore lazily on first execute() inside child process (live redis/
boto3 are not picklable). Admission router never constructs the executor.

Privacy contract: logs carry operation names and exception class names only.
"""

from __future__ import annotations

import importlib
import logging
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
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import ErrorSummary, ResultSummary
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client
from app.worker.worker import ENGINE_ERROR_FALLBACK, TIMEOUT_ERROR, ClaimedJob, ExecutionKind, ExecutionOutcome, ProgressReporter

logger = logging.getLogger(__name__)

_REFUSED_ERROR = ErrorSummary(
    code='engine_error', category='engine', retryable=False, message_key='error.engineError'
)
_STORE_UNAVAILABLE_ERROR = ErrorSummary(
    code='store_unavailable', category='engine', retryable=True, message_key='error.engineError',
)


class PikepdfError(Exception):
    pass


@dataclass(frozen=True)
class MergeResult:
    """Result of a merge operation."""
    total_pages: int
    total_bytes: int


class S3ReadClient(Protocol):
    """Minimal boto3 get_object interface."""
    def get_object(self, **kwargs: object) -> dict[str, object]: ...


def _build_read_client(settings: Settings) -> S3ReadClient:
    """Build boto3 read client for R2 (r2.py has no read path)."""
    boto3 = cast(Any, importlib.import_module('boto3'))
    botocore_config = cast(Any, importlib.import_module('botocore.config'))
    endpoint = settings.r2_endpoint or f'https://{settings.r2_account_id}.r2.cloudflarestorage.com'
    client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name=settings.r2_region,
        config=botocore_config.Config(signature_version='s3v4', retries={'max_attempts': 2, 'mode': 'standard'}),
    )
    return cast(S3ReadClient, client)


class MergeEngine:
    """Pikepdf-based merge engine."""
    
    def merge(self, sources: list[bytes], *, timeout: timedelta) -> MergeResult:
        """Merge multiple PDFs into one, deterministic page order.
        
        Args:
            sources: List of sanitized PDF bytes (must have same MIME type)
            timeout: Maximum execution time
            
        Returns:
            MergeResult with total_pages and total_bytes
        """
        try:
            import pikepdf
        except ImportError:
            raise PikepdfError('pikepdf not available')
        
        with tempfile.TemporaryDirectory(prefix='papyr-merge-') as tmpdir:
            # Write all inputs to temp files
            input_paths = []
            for i, data in enumerate(sources):
                path = Path(tmpdir) / f'input_{i}.pdf'
                path.write_bytes(data)
                input_paths.append(path)
            
            # Open all PDFs with pikepdf
            pdfs = [pikepdf.open(str(p)) for p in input_paths]
            
            if not pdfs:
                raise PikepdfError('No inputs')
            
            # Merge pages in order (user order preserved)
            merged = pikepdf.new()
            for pdf in pdfs:
                merged.pages.extend(pdf.pages)
                pdf.close()
            
            # Write output
            output_path = Path(tmpdir) / 'output.pdf'
            merged.save(str(output_path))
            merged.close()
            
            # Count total pages
            total_pages = len(merged.pages)
            output_size = output_path.stat().st_size
        
        return MergeResult(total_pages=total_pages, total_bytes=output_size)
