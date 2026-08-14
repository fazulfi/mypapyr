"""Split PDF tool admission endpoint (TL-04).

Locks the POST /api/v1/tools/split-pdf/tasks contract (execution-matrix.md
TL-04 row): accepts multipart form field ``file``, enforces the BE-08 per-tool
input caps through BE-02 ``validate_pdf``, runs the SEC-01/SEC-02 gate
(``classify_payload`` + ``PdfSanitizer``), uploads the SANITIZED bytes only to
R2, builds a full queued :class:`TaskRecord`, and admits it through
``JobQueue.enqueue`` (which creates the record internally — queue.py contract),
returning the typed :class:`TaskAdmission` on HTTP 202.

Range specifications are passed via the optional ``ranges`` form field
(defaults to one PDF per page if omitted).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import NoReturn, cast

from fastapi import APIRouter, FastAPI, Form, HTTPException, Request, UploadFile, status

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
from app.routers import _resolve_origin
from app.routers.capabilities import TOOL_LIMITS, ToolId, ToolLimits
from app.schemas.job import SplitOptions, TaskAdmission
from app.security.sanitize import PdfSanitizer
from app.security.validation import PdfInspection, ValidationRejection, validate_pdf
from app.services.split_service import RangeSpecError, canonical_range_spec, parse_range_spec
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tools/split-pdf", tags=["split"])


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


def _delete_orphan_input(r2: R2Client, input_key: str) -> None:
    """Best-effort cleanup of an uploaded input when enqueue fails (I4)."""
    try:
        r2.delete_object(input_key)
    except Exception as exc:
        logger.error(
            "split orphan input delete failed",
            extra={"fields": {"error": type(exc).__name__}},
        )


def _reject_ranges(reason: str) -> NoReturn:
    logger.error("split ranges rejected", extra={"fields": {"error": reason}})
    raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})


def _validate_split_ranges(
    range_spec: str, inspection: PdfInspection, limit: ToolLimits
) -> SplitOptions | None:
    """Validate the ``ranges`` form field at admission (FR-SPLIT-04).

    Returns normalized options for custom ranges or ``None`` for the default
    one-output-per-page mode. Malformed specs, unverifiable page bounds
    (encrypted input), out-of-bounds pages, and output counts above the
    BE-08 cap all fail closed with HTTP 400.
    """
    spec = range_spec.strip()
    if not spec:
        page_count = inspection.page_count
        if page_count == 0 or (page_count is not None and page_count > limit.max_outputs):
            _reject_ranges("OutputCountExceeded")
        return None
    try:
        parsed = parse_range_spec(spec)
    except RangeSpecError as exc:
        logger.error(
            "split ranges rejected",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"}) from exc
    page_count = inspection.page_count
    if page_count is None:
        _reject_ranges("UnverifiablePageBounds")
    if len(parsed) > limit.max_outputs or any(end > page_count for _, end in parsed):
        _reject_ranges("RangeBoundsExceeded")
    return SplitOptions(ranges=canonical_range_spec(parsed))


@router.post("/tasks", response_model=TaskAdmission, status_code=status.HTTP_202_ACCEPTED)
async def split_pdf_admit(
    request: Request,
    file: UploadFile,
    ranges: str = Form(default=""),
) -> TaskAdmission:
    """Admit a sanitized split-pdf upload; returns 202 TaskAdmission."""
    settings = _resolve_settings(request)
    store = _resolve_task_store(request, settings)
    r2 = _resolve_r2(request, settings)
    queue = _resolve_queue(request, settings, store)

    data = await file.read()
    limit = TOOL_LIMITS[ToolId.SPLIT_PDF]
    max_pages = limit.max_pages if limit.max_pages is not None else 1000
    try:
        inspection = validate_pdf(
            data,
            declared_mime=file.content_type,
            declared_extension=".pdf",
            max_size_bytes=limit.max_file_bytes,
            max_pages=max_pages,
        )
    except ValidationRejection as exc:
        logger.error(
            "split validation rejected",
            extra={"fields": {"error": type(exc).__name__}},
        )
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"}) from exc

    # Range validation (FR-SPLIT-04): fail-closed admission; default mode is
    # one output per page when no ranges are provided.
    options = _validate_split_ranges(ranges, inspection, limit)

    # SEC-01 scanner gate (U-SEC): fail-closed admission
    enforce_scan_gate(request, data)

    sanitizer = PdfSanitizer()
    sanitizer.sanitize(data)
    sanitized = sanitizer.output_bytes
    if sanitized is None:
        logger.error("split sanitization refused", extra={"fields": {"error": "PdfSanitizer"}})
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})

    input_key = r2.build_object_key(extension="pdf")
    r2.upload_object(input_key, sanitized, content_type="application/pdf")

    now = datetime.now(UTC)
    record = TaskRecord(
        task_id=str(uuid.uuid4()),
        state=JobState.QUEUED,
        tool="split-pdf",
        created_at=now,
        accepted_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=settings.retention_seconds),
        queued_at=now,
        objects=(input_key,),
        options=options,
    )
    try:
        enqueued = queue.enqueue(record, origin=_resolve_origin(request), route="split-pdf")
    except (StoreUnavailableError, TaskNotFoundError) as exc:
        logger.error(
            "split enqueue store unavailable",
            extra={"fields": {"error": type(exc).__name__}},
        )
        _delete_orphan_input(r2, input_key)
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc
    except TaskConflictError as exc:
        logger.error(
            "split enqueue conflict",
            extra={"fields": {"error": type(exc).__name__}},
        )
        _delete_orphan_input(r2, input_key)
        raise HTTPException(status_code=409, detail={"messageKey": "error.internalError"}) from exc
    except Exception as exc:
        logger.error(
            "split enqueue failed",
            extra={"fields": {"error": type(exc).__name__}},
        )
        _delete_orphan_input(r2, input_key)
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc

    return TaskAdmission(task_id=enqueued.task_id, expires_at=enqueued.expires_at)
