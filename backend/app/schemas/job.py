"""Job metadata and status contracts.

The canonical ``JobState`` closed set is defined once in
``app.tasks.state_machine`` and re-exported here; expiry is not a state.
Status responses contain authoritative timestamps, measurable progress, and
safe error categories—never filenames, signed URLs, passwords, content,
or object keys. JSON keys use snake_case.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.tasks.state_machine import JobState

__all__ = [
    "ErrorSummary",
    "JobState",
    "Progress",
    "ResultSummary",
    "TaskAdmission",
    "TaskStatus",
]


class Progress(BaseModel):
    """Measurable progress only; never fabricated percentages.

    ``total`` set to None means progress is indeterminate.
    """

    model_config = ConfigDict(extra="forbid")

    unit: Literal["bytes_uploaded", "pages_processed", "engine_progress"]
    value: int = Field(ge=0)
    total: int | None = Field(default=None, ge=0)


class ResultSummary(BaseModel):
    """Result metadata present when a task reaches ``done``.

    Byte counts are metadata; content bytes, previews, signed URLs, passwords,
    and object keys are structurally excluded.
    """

    model_config = ConfigDict(extra="forbid")

    output_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)


class ErrorSummary(BaseModel):
    """Safe error category only; no engine internals.

    ``code`` and ``category`` remain plain strings until concrete processing
    endpoints define their closed vocabulary. Message keys localize at the
    presentation layer.
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    category: str
    retryable: bool
    message_key: str


class TaskAdmission(BaseModel):
    """Upload-admission response.

    Admission always reports state ``queued``. ``task_id`` is opaque and
    high-entropy; format enforcement belongs to the endpoint layer.
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str
    state: Literal[JobState.QUEUED] = JobState.QUEUED
    expires_at: datetime


class TaskStatus(BaseModel):
    """Task status response.

    ``tool`` remains a string until concrete endpoints define the closed
    tool identifier set.
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str
    tool: str
    state: JobState
    created_at: datetime
    accepted_at: datetime
    updated_at: datetime
    expires_at: datetime
    progress: Progress | None = None
    result: ResultSummary | None = None
    error: ErrorSummary | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancellable: bool = False

    @model_validator(mode="after")
    def _state_consistency(self) -> TaskStatus:
        if self.state is JobState.DONE and self.result is None:
            raise ValueError("result is required when state is done")
        if self.state is not JobState.DONE and self.result is not None:
            raise ValueError("result is only allowed when state is done")
        if self.state is JobState.FAILED and self.error is None:
            raise ValueError("error is required when state is failed")
        if self.state is not JobState.FAILED and self.error is not None:
            raise ValueError("error is only allowed when state is failed")
        if self.cancellable and self.state is not JobState.QUEUED:
            raise ValueError("cancellable is only allowed while queued")
        return self
