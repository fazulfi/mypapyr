"""Merge PDF tool admission endpoint (TL-03).

Locks the POST /api/v1/tools/merge-pdf/tasks contract: accepts multiple multipart
files, validates each through BE-02 validate_pdf, runs SEC-01/SEC-02 gate on EACH
input unconditionally (never trusts client classification), uploads all SANITIZED
bytes to R2, builds a single queued TaskRecord with all input keys, and admits it
through JobQueue.enqueue via TaskAdmission on HTTP 202.

Fail-closed envelope per file: ValidationRejection -> safe 4xx, sanitizer REFUSED
for any input -> safe 4xx with no task created, capacity rejection -> 429.

Logs carry operation names and exception class names only (DEC-175); no filenames,
object keys, task ids, or payload details reach telemetry.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import APIRouter, FastAPI, HTTPException, Request, UploadFile, status
from pydantic import BaseModel

from app.config import Settings, load
from app.health import enforce_scan_gate
from app.queue.queue import JobQueue
from app.queue.store import (
    StoreUnavailableError,
    TaskConflictError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import TaskAdmission
from app.security.sanitize import PdfSanitizer
from app.security.validation import ValidationRejection, validate_pdf
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tools/merge-pdf", tags=["merge"])


def _resolve_settings(request: Request) -> Settings:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "settings", None)
    if isinstance(preset, Settings):
        return preset
    return load()


def _resolve_task_store(request: Request, settings: Settings) -> TaskStore:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "task_store", None)
    if isinstance(preset, TaskStore):
        return preset
    return TaskStore(settings)


def _resolve_r2(request: Request, settings: Settings) -> R2Client:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "r2_client", None)
    if isinstance(preset, R2Client):
        return preset
    return R2Client(settings)


def _resolve_queue(request: Request, settings: Settings, store: TaskStore) -> JobQueue:
    application = cast(FastAPI, request.app)
    preset = getattr(application.state, "job_queue", None)
    if isinstance(preset, JobQueue):
        return preset
    return JobQueue(settings, store)


class MergeTaskRequest(BaseModel):
    """Schema for multipart merge request."""

    pass


@router.post("/tasks", response_model=TaskAdmission, status_code=status.HTTP_202_ACCEPTED)
async def merge_pdf_admit(request: Request, files: list[UploadFile]) -> TaskAdmission:
    """Admit multiple sanitized PDFs for merging; returns 202 TaskAdmission."""
    # Validate file count
    settings = _resolve_settings(request)
    limit = TOOL_LIMITS[ToolId.MERGE_PDF]

    if len(files) > limit.max_files:
        logger.error(
            "merge too many files",
            extra={"fields": {"error": "ValidationRejection"}},
        )
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})

    # Process each file independently
    sanitized_objects = []
    now = datetime.now(UTC)

    for i, file in enumerate(files):
        data = await file.read()

        # Validate
        max_pages = limit.max_pages if limit.max_pages is not None else 1000
        try:
            validate_pdf(
                data,
                declared_mime=file.content_type,
                declared_extension=".pdf",
                max_size_bytes=limit.max_file_bytes,
                max_pages=max_pages,
            )
        except ValidationRejection as exc:
            logger.error(
                "merge file %d validation rejected",
                i,
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"}) from exc

        # SEC-01 scanner gate (U-SEC): fail-closed admission per-file
        enforce_scan_gate(request, data)

        # Sanitize (NEVER trust client!)
        sanitizer = PdfSanitizer()
        sanitizer.sanitize(data)
        sanitized = sanitizer.output_bytes
        if sanitized is None:
            logger.error(
                "merge file %d sanitization refused",
                i,
                extra={"fields": {"error": "PdfSanitizer"}},
            )
            raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})

        # Upload sanitized bytes only
        r2 = _resolve_r2(request, settings)
        input_key = r2.build_object_key(extension="pdf")
        r2.upload_object(input_key, sanitized, content_type="application/pdf")
        sanitized_objects.append(input_key)

    # Build record with ALL input keys
    store = _resolve_task_store(request, settings)

    record = TaskRecord(
        task_id=str(uuid.uuid4()),
        state=JobState.QUEUED,
        tool="merge-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=settings.retention_seconds),
        queued_at=now,
        objects=tuple(sanitized_objects),
    )

    queue = _resolve_queue(request, settings, store)

    try:
        enqueued = queue.enqueue(record, origin=None, route="merge-pdf")
    except (StoreUnavailableError, TaskNotFoundError) as exc:
        logger.error(
            "merge enqueue store unavailable",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc
    except TaskConflictError as exc:
        logger.error(
            "merge enqueue conflict",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=409, detail={"messageKey": "error.internalError"}) from exc
    except Exception as exc:
        logger.error(
            "merge enqueue failed",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc

    return TaskAdmission(task_id=enqueued.task_id, expires_at=enqueued.expires_at)
