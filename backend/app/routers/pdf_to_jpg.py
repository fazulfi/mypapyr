from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.schemas.job import TaskAdmission

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


@router.post("/pdf-to-jpg/tasks", response_model=TaskAdmission, status_code=202)
async def admit_pdf_to_jpg_task(file: UploadFile = File(...)) -> TaskAdmission:
    if file.content_type != "application/pdf":
        from fastapi import HTTPException

        raise HTTPException(status_code=415, detail="unsupported PDF")
    data = await file.read()
    if not data.startswith(b"%PDF"):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="invalid PDF")
    now = datetime.now(UTC)
    return TaskAdmission(task_id=str(uuid4()), expires_at=now + timedelta(hours=1))
