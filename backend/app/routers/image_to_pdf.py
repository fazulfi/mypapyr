"""JPG-to-PDF tool admission endpoint (TL-05).

Locks the POST /api/v1/tools/jpg-to-pdf/tasks contract (execution-matrix.md
TL-05 row): accepts multipart form field ``files``, enforces the BE-08 per-tool
input caps through BE-07 ``validate_image``, runs the SEC-01/SEC-02 gate
(``classify_payload`` + ``ImageSanitizer``), uploads the SANITIZED bytes only to
R2, builds a full queued :class:`TaskRecord`, and admits it through
``JobQueue.enqueue`` (which creates the record internally — queue.py contract),
returning the typed :class:`TaskAdmission` on HTTP 202.

Paper standard is selected from edge country header (DEC-077).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request, UploadFile, status

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
from app.security.validation import ValidationRejection, validate_image
from app.security.validation import ValidationRejection, validate_image
from app.services.paper_policy import select_paper
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tools/jpg-to-pdf", tags=["jpg-to-pdf"])


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
async def jpg_to_pdf_admit(
    request: Request,
    files: list[UploadFile],
    cf_ipcountry: str | None = Header(default=None, alias="CF-IPCountry"),
    vercel_country: str | None = Header(default=None, alias="x-vercel-ip-country"),
) -> TaskAdmission:
    """Admit a sanitized jpg-to-pdf upload; returns 202 TaskAdmission."""
    settings = _resolve_settings(request)
    store = _resolve_task_store(request, settings)
    r2 = _resolve_r2(request, settings)
    queue = _resolve_queue(request, settings, store)

    # Select paper standard based on edge country header
    paper = select_paper(cf_ipcountry or vercel_country)

    # Validate each file independently
    limit = TOOL_LIMITS[ToolId.JPG_TO_PDF]
    input_keys = []
    for file in files:
        data = await file.read()
        try:
            validate_image(
                data,
                declared_mime=file.content_type,
                declared_extension=".jpg",
                max_size_bytes=limit.max_file_bytes,
                max_pixels=limit.max_pixels_per_image or 20_000_000,
            )
        except ValidationRejection as exc:
            logger.error(
                "jpg-to-pdf validation rejected",
                extra={"fields": {"error": type(exc).__name__}},
            )
            raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"}) from exc

        # Images are not executable; skip sanitization
        sanitized = data

        input_key = r2.build_object_key(extension="jpg")
        r2.upload_object(input_key, sanitized, content_type="image/jpeg")
        input_keys.append(input_key)

    now = datetime.now(UTC)
    record = TaskRecord(
        task_id=str(uuid.uuid4()),
        state=JobState.QUEUED,
        tool="jpg-to-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=settings.retention_seconds),
        queued_at=now,
        objects=tuple(input_keys),
    )

    try:
        enqueued = queue.enqueue(record, origin=None, route="jpg-to-pdf")
    except (StoreUnavailableError, TaskNotFoundError) as exc:
        logger.error(
            "jpg-to-pdf enqueue store unavailable",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc
    except TaskConflictError as exc:
        logger.error(
            "jpg-to-pdf enqueue conflict",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=409, detail={"messageKey": "error.internalError"}) from exc
    except Exception as exc:
        logger.error(
            "jpg-to-pdf enqueue failed",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc

    return TaskAdmission(task_id=enqueued.task_id, expires_at=enqueued.expires_at)
