"""PDF-to-JPG tool admission endpoint (TL-06).

Locks the POST /api/v1/tools/pdf-to-jpg/tasks contract (execution-matrix.md
TL-06 row): accepts multipart form field ``file``, enforces the BE-08 per-tool
input caps through BE-02 ``validate_pdf``, runs the SEC-01/SEC-02 gate
(``classify_payload`` + ``PdfSanitizer``), uploads the SANITIZED bytes only to
R2, builds a full queued :class:`TaskRecord`, and admits it through
``JobQueue.enqueue`` (which creates the record internally — queue.py contract),
returning the typed :class:`TaskAdmission` on HTTP 202.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import APIRouter, FastAPI, HTTPException, Request, UploadFile, status

from app.config import Settings, load
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

router = APIRouter(prefix="/api/v1/tools/pdf-to-jpg", tags=["pdf-to-jpg"])


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


@router.post("/tasks", response_model=TaskAdmission, status_code=status.HTTP_202_ACCEPTED)
async def pdf_to_jpg_admit(request: Request, file: UploadFile) -> TaskAdmission:
    """Admit a sanitized pdf-to-jpg upload; returns 202 TaskAdmission."""
    settings = _resolve_settings(request)
    store = _resolve_task_store(request, settings)
    r2 = _resolve_r2(request, settings)
    queue = _resolve_queue(request, settings, store)

    data = await file.read()
    limit = TOOL_LIMITS[ToolId.PDF_TO_JPG]
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
            "pdf-to-jpg validation rejected",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"}) from exc

    sanitizer = PdfSanitizer()
    sanitizer.sanitize(data)
    sanitized = sanitizer.output_bytes
    if sanitized is None:
        logger.error("pdf-to-jpg sanitization refused", extra={"fields": {"error": "PdfSanitizer"}})
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})

    input_key = r2.build_object_key(extension="pdf")
    r2.upload_object(input_key, sanitized, content_type="application/pdf")

    now = datetime.now(UTC)
    record = TaskRecord(
        task_id=str(uuid.uuid4()),
        state=JobState.QUEUED,
        tool="pdf-to-jpg",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=settings.retention_seconds),
        queued_at=now,
        objects=(input_key,),
    )

    try:
        enqueued = queue.enqueue(record, origin=None, route="pdf-to-jpg")
    except (StoreUnavailableError, TaskNotFoundError) as exc:
        logger.error(
            "pdf-to-jgy enqueue store unavailable",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc
    except TaskConflictError as exc:
        logger.error(
            "pdf-to-jgy enqueue conflict",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=409, detail={"messageKey": "error.internalError"}) from exc
    except Exception as exc:
        logger.error(
            "pdf-to-jgy enqueue failed",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc

    return TaskAdmission(task_id=enqueued.task_id, expires_at=enqueued.expires_at)
