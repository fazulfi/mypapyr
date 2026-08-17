"""Merge PDF tool admission endpoint (TL-03).

Locks the POST /api/v1/tools/merge-pdf/tasks contract: accepts multiple multipart
files, validates each through BE-02 validate_pdf, runs SEC-01/SEC-02 gate on EACH
input unconditionally (never trusts client classification), uploads all SANITIZED
bytes to R2, builds a single queued TaskRecord with all input keys, and admits it
through JobQueue.enqueue via TaskAdmission on HTTP 202.

Encrypted inputs (FR-SHARED-09 / FR-MERGE-04): the client MAY send per-index
``password_<i>`` multipart text fields (``i`` = the file's position in the
``files`` order, 0-based). Each password decrypts ONLY its own file at the
sanitizer stage — the output is always an unencrypted rewrite, so the password
is consumed before any upload and is never persisted, logged, or stored in the
TaskRecord/R2/status. A locked file with a wrong or absent password fails the
whole job with 400 ``error.wrongPassword`` (distinct from corrupt/unsupported,
which stay ``error.badRequest``). Passwords are capped at 1024 UTF-8 bytes and
a ``password_<i>`` whose index has no matching file is malformed.

Fail-closed envelope per file: ValidationRejection -> safe 4xx, sanitizer REFUSED
for any input -> safe 4xx with no task created, capacity rejection -> 429.

Logs carry operation names and exception class names only (DEC-175); no filenames,
object keys, task ids, passwords, or payload details reach telemetry.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import APIRouter, FastAPI, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.datastructures import FormData
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings, load
from app.errors import HttpErrorSpec, build_error_envelope
from app.health import enforce_scan_gate
from app.middleware import REQUEST_ID_HEADER, resolve_request_id
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
from app.security.classification import SanitizerStatus
from app.security.sanitize import PdfSanitizer, SanitizerRefusal
from app.security.validation import ValidationRejection, validate_pdf
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tools/merge-pdf", tags=["merge"])

# FR-SHARED-09: distinct wrong-password key, resolved at the presentation layer.
_WRONG_PASSWORD_KEY = "error.wrongPassword"
# Server-side cap matching the client MAX_PASSWORD_LENGTH (frontend/src/lib/password.ts).
_MAX_PASSWORD_BYTES = 1024
_PASSWORD_FIELD_PREFIX = "password_"


class MergeWrongPasswordError(StarletteHTTPException):
    """400 raised when an encrypted input cannot be opened with its password.

    A dedicated ``HTTPException`` subclass so the app-level exception
    registry (``create_app``) can map precisely this error to the
    ``error.wrongPassword`` messageKey while every other 400 keeps the
    locked global envelope. ``detail`` carries the key only — never the
    submitted value.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            detail={"messageKey": _WRONG_PASSWORD_KEY},  # type: ignore[arg-type]
        )


async def merge_password_handler(request: Request, exc: Exception) -> JSONResponse:
    """Render the 400 envelope with the ``error.wrongPassword`` messageKey.

    Registered in ``create_app`` for the exact ``MergeWrongPasswordError``
    class; mirrors ``errors.http_exception_handler`` but carries the
    FR-SHARED-09-specific message key. Never echoes submitted content.
    """
    del exc
    spec = HttpErrorSpec(
        code="bad_request",
        category="validation",
        message="Bad request",
        message_key=_WRONG_PASSWORD_KEY,
        retryable=False,
    )
    request_id = resolve_request_id(request)
    return JSONResponse(
        status_code=400,
        content=build_error_envelope(spec, request_id=request_id),
        headers={REQUEST_ID_HEADER: request_id},
    )


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


def _delete_orphan_inputs(r2: R2Client, input_keys: list[str]) -> None:
    """Best-effort cleanup of uploaded inputs when enqueue fails (I4)."""
    for input_key in input_keys:
        try:
            r2.delete_object(input_key)
        except Exception as exc:
            logger.error(
                "merge orphan input delete failed",
                extra={"fields": {"error": type(exc).__name__}},
            )


def _extract_passwords(form: FormData, *, file_count: int) -> dict[int, str]:
    """Validate and return the per-index password fields for *file_count* files.

    Contract (documented on the router docstring): only ``password_<i>``
    fields for 0 <= i < file_count are accepted; an out-of-bounds index is
    malformed, and any value larger than 1024 UTF-8 bytes is rejected. The
    returned map contains only the non-empty values, so absent and empty
    fields are equivalent (both mean "no password for this file").
    """
    password_fields: dict[int, str] = {}
    prefix_len = len(_PASSWORD_FIELD_PREFIX)
    for field_name, value in form.multi_items():
        if not field_name.startswith(_PASSWORD_FIELD_PREFIX):
            continue
        index = _parse_password_index(field_name, prefix_len)
        if index is None:
            continue
        if index < 0 or index >= file_count:
            raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})
        password_fields[index] = str(value)
    for value in password_fields.values():
        if len(value.encode("utf-8")) > _MAX_PASSWORD_BYTES:
            raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})
    return {index: value for index, value in password_fields.items() if value != ""}


def _parse_password_index(field_name: str, prefix_len: int) -> int | None:
    """Parse the 0-based index from a ``password_<i>`` field name."""
    suffix = field_name[prefix_len:]
    try:
        return int(suffix)
    except ValueError:
        return None


class MergeTaskRequest(BaseModel):
    """Schema for multipart merge request."""

    pass


@router.post("/tasks", response_model=TaskAdmission, status_code=status.HTTP_202_ACCEPTED)
async def merge_pdf_admit(
    request: Request,
    files: list[UploadFile],
) -> TaskAdmission:
    """Admit multiple sanitized PDFs for merging; returns 202 TaskAdmission.

    The optional per-index ``password_<i>`` multipart fields are parsed
    manually from the request form (FastAPI's ``dict[int, str]`` Form
    parameter does not bind ``password_N`` prefix fields, and manual
    parsing keeps submitted values out of validation-error details). Each
    password is validated (cap, index bound) and consumed at the
    sanitizer stage; it is never logged, persisted, or echoed.
    """
    settings = _resolve_settings(request)
    limit = TOOL_LIMITS[ToolId.MERGE_PDF]

    if len(files) > limit.max_files:
        logger.error(
            "merge too many files",
            extra={"fields": {"error": "ValidationRejection"}},
        )
        raise HTTPException(status_code=400, detail={"messageKey": "error.badRequest"})

    form = await request.form()
    password_map = _extract_passwords(form, file_count=len(files))
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

        # Sanitize (NEVER trust client!). The password, when present, opens
        # ONLY this file; the sanitizer rewrites the output unencrypted.
        sanitizer = PdfSanitizer()
        verdict = sanitizer.sanitize(data, password=password_map.get(i, ""))
        sanitized = sanitizer.output_bytes
        if sanitized is None:
            password_refused = (
                verdict.status is SanitizerStatus.REFUSED
                and sanitizer.refusal_reason is SanitizerRefusal.PASSWORD
            )
            if password_refused:
                logger.error(
                    "merge file %d wrong password",
                    i,
                    extra={"fields": {"error": "PasswordError"}},
                )
                raise MergeWrongPasswordError() from None
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
        _delete_orphan_inputs(r2, sanitized_objects)
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc
    except TaskConflictError as exc:
        logger.error(
            "merge enqueue conflict",
            extra={"fields": {"error": type(exc).__name__}},
        )
        _delete_orphan_inputs(r2, sanitized_objects)
        raise HTTPException(status_code=409, detail={"messageKey": "error.internalError"}) from exc
    except Exception as exc:
        logger.error(
            "merge enqueue failed",
            extra={"fields": {"error": type(exc).__name__}},
        )
        _delete_orphan_inputs(r2, sanitized_objects)
        raise HTTPException(status_code=503, detail={"messageKey": "error.internalError"}) from exc

    return TaskAdmission(task_id=enqueued.task_id, expires_at=enqueued.expires_at)
