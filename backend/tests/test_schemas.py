"""Contract tests for metadata-only schemas.

Locked surfaces:
- Job states are the closed set ``queued / processing / done / failed /
  cancelled``; expiry is not a state.
- Metadata models structurally reject content bytes, previews, passwords,
  signed URLs, object keys, and original filenames.
- Status and admission schemas carry state,
  authoritative timestamps, the authoritative expiry, measurable progress
  only, and safe error categories.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi import APIRouter
from pydantic import BaseModel, ValidationError

from app import routers
from app.schemas import (
    ErrorSummary,
    FileMetadata,
    FileObjectMetadata,
    JobState,
    Progress,
    ResultSummary,
    TaskAdmission,
    TaskStatus,
)
from app.tasks import state_machine

NOW = datetime.now(UTC)

PROHIBITED_FIELD_NAMES = {
    "filename",
    "filenames",
    "content",
    "contents",
    "preview",
    "previews",
    "password",
    "passwords",
    "signed_url",
    "signed_urls",
    "url",
    "object_key",
    "object_keys",
}

ALL_METADATA_MODELS = (
    FileMetadata,
    FileObjectMetadata,
    Progress,
    ResultSummary,
    ErrorSummary,
    TaskAdmission,
    TaskStatus,
)


_VALID_KWARGS: dict[type[BaseModel], dict[str, object]] = {
    FileMetadata: {"size_bytes": 1024, "expires_at": NOW},
    FileObjectMetadata: {"expires_at": NOW},
    Progress: {"unit": "pages_processed", "value": 1},
    ResultSummary: {"output_count": 1, "total_bytes": 10},
    ErrorSummary: {
        "code": "processing_failed",
        "category": "engine",
        "retryable": False,
        "message_key": "error.processingFailed",
    },
    TaskAdmission: {"task_id": "a" * 32, "expires_at": NOW},
    TaskStatus: {
        "task_id": "a" * 32,
        "tool": "compress",
        "state": JobState.QUEUED,
        "created_at": NOW,
        "accepted_at": NOW,
        "updated_at": NOW,
        "expires_at": NOW,
    },
}


def _valid_kwargs(model: type[BaseModel]) -> dict[str, object]:
    try:
        return _VALID_KWARGS[model]
    except KeyError:
        raise AssertionError(f"no valid-kwargs fixture for {model.__name__}") from None


def _make_status(**overrides: object) -> TaskStatus:
    kwargs = {
        "task_id": "a" * 32,
        "tool": "compress",
        "state": JobState.QUEUED,
        "created_at": NOW,
        "accepted_at": NOW,
        "updated_at": NOW,
        "expires_at": NOW,
    }
    kwargs.update(overrides)
    # model_validate keeps the deliberately heterogeneous kwargs (valid values
    # plus invalid-literal overrides) outside the typed constructor boundary;
    # validation semantics are identical to ``TaskStatus(**kwargs)``.
    return TaskStatus.model_validate(kwargs)


def _dump_keys(obj: object) -> set[str]:
    if isinstance(obj, dict):
        keys: set[str] = set(obj)
        for value in obj.values():
            keys |= _dump_keys(value)
        return keys
    if isinstance(obj, list):
        keys = set()
        for value in obj:
            keys |= _dump_keys(value)
        return keys
    return set()


# --- closed job-state set ---------------------------------------------------


def test_job_state_is_the_closed_five_state_set() -> None:
    assert {state.value for state in JobState} == {
        "queued",
        "processing",
        "done",
        "failed",
        "cancelled",
    }


def test_job_state_is_the_canonical_task_definition() -> None:
    assert JobState is state_machine.JobState


def test_expiry_is_not_a_job_state() -> None:
    assert "expired" not in {state.value for state in JobState}
    with pytest.raises(ValueError):
        JobState("expired")


def test_task_status_accepts_each_closed_state() -> None:
    for state in JobState:
        overrides: dict[str, object] = {}
        if state is JobState.DONE:
            overrides["result"] = ResultSummary(output_count=1, total_bytes=10)
        if state is JobState.FAILED:
            overrides["error"] = ErrorSummary(
                code="processing_failed",
                category="engine",
                retryable=False,
                message_key="error.processingFailed",
            )
        if state is JobState.QUEUED:
            overrides["cancellable"] = True
        status = _make_status(state=state, **overrides)
        assert status.state is state


def test_task_status_rejects_expired_as_a_state() -> None:
    with pytest.raises(ValidationError):
        _make_status(state="expired")


# --- state-consistency invariants ---


def test_task_status_requires_result_when_done() -> None:
    with pytest.raises(ValidationError):
        _make_status(state=JobState.DONE)


def test_task_status_forbids_result_unless_done() -> None:
    with pytest.raises(ValidationError):
        _make_status(
            state=JobState.QUEUED,
            result=ResultSummary(output_count=1, total_bytes=10),
        )


def test_task_status_requires_error_when_failed() -> None:
    with pytest.raises(ValidationError):
        _make_status(state=JobState.FAILED)


def test_task_status_forbids_error_unless_failed() -> None:
    with pytest.raises(ValidationError):
        _make_status(
            state=JobState.DONE,
            result=ResultSummary(output_count=1, total_bytes=10),
            error=ErrorSummary(
                code="processing_failed",
                category="engine",
                retryable=False,
                message_key="error.processingFailed",
            ),
        )


def test_cancellable_only_while_queued() -> None:
    status = _make_status(state=JobState.QUEUED, cancellable=True)
    assert status.cancellable is True
    with pytest.raises(ValidationError):
        _make_status(state=JobState.PROCESSING, cancellable=True)


# --- measurable progress ---------------------------------------------------


def test_progress_accepts_measurable_units() -> None:
    for unit in ("bytes_uploaded", "pages_processed", "engine_progress"):
        # model_validate keeps the deliberately untyped loop variable outside
        # the typed constructor boundary; validation semantics are identical
        # to ``Progress(unit=unit, value=10)``.
        progress = Progress.model_validate({"unit": unit, "value": 10})
        assert progress.value == 10
        assert progress.total is None
    assert Progress(unit="pages_processed", value=3, total=10).total == 10


def test_progress_rejects_unknown_unit_and_negatives() -> None:
    with pytest.raises(ValidationError):
        Progress.model_validate({"unit": "percent", "value": 10})
    with pytest.raises(ValidationError):
        Progress(unit="pages_processed", value=-1)
    with pytest.raises(ValidationError):
        Progress(unit="pages_processed", value=1, total=-2)


def test_result_summary_rejects_negative_counts() -> None:
    with pytest.raises(ValidationError):
        ResultSummary(output_count=-1, total_bytes=10)
    with pytest.raises(ValidationError):
        ResultSummary(output_count=1, total_bytes=-1)


# --- typed file metadata -----------------------------------------------------


def test_file_metadata_accepts_size_and_expiry() -> None:
    metadata = FileMetadata(size_bytes=1024, expires_at=NOW)
    assert metadata.size_bytes == 1024
    assert metadata.expires_at == NOW
    with pytest.raises(ValidationError):
        FileMetadata(size_bytes=-1, expires_at=NOW)


def test_file_object_metadata_is_expires_at_only() -> None:
    metadata = FileObjectMetadata(expires_at=NOW)
    assert set(FileObjectMetadata.model_fields) == {"expires_at"}
    assert metadata.expires_at == NOW


# --- upload admission schema ---


def test_admission_always_reports_queued() -> None:
    admission = TaskAdmission(task_id="b" * 32, expires_at=NOW)
    assert admission.state is JobState.QUEUED
    with pytest.raises(ValidationError):
        TaskAdmission.model_validate(
            {"task_id": "b" * 32, "state": "processing", "expires_at": NOW}
        )


# --- metadata-only invariants -----------------------------------------------


@pytest.mark.parametrize("model", ALL_METADATA_MODELS)
def test_metadata_models_declare_no_prohibited_fields(model: type[BaseModel]) -> None:
    declared = set(model.model_fields)
    assert declared.isdisjoint(PROHIBITED_FIELD_NAMES), (
        f"{model.__name__} declares prohibited field(s): "
        f"{sorted(declared & PROHIBITED_FIELD_NAMES)}"
    )


@pytest.mark.parametrize("model", ALL_METADATA_MODELS)
def test_metadata_models_reject_prohibited_fields(model: type[BaseModel]) -> None:
    valid = _valid_kwargs(model)
    for name in (
        "filename",
        "content",
        "preview",
        "password",
        "signed_url",
        "object_key",
    ):
        with pytest.raises(ValidationError):
            model(**valid, **{name: "x"})


def test_task_status_exposes_the_proposed_seam_fields() -> None:
    _make_status(state=JobState.QUEUED)
    assert set(TaskStatus.model_fields) == {
        "task_id",
        "tool",
        "state",
        "created_at",
        "accepted_at",
        "updated_at",
        "expires_at",
        "progress",
        "result",
        "error",
        "queued_at",
        "started_at",
        "completed_at",
        "cancellable",
    }


def test_status_dump_carries_no_prohibited_keys() -> None:
    status = _make_status(
        state=JobState.DONE,
        result=ResultSummary(output_count=1, total_bytes=42),
        progress=Progress(unit="pages_processed", value=1, total=2),
    )
    dumped = status.model_dump(mode="json")
    assert "expires_at" in dumped
    assert _dump_keys(dumped).isdisjoint(PROHIBITED_FIELD_NAMES)


# --- empty routers package marker -------------------------------------------


def test_routers_package_defines_no_routes() -> None:
    assert getattr(routers, "__path__", None)
    assert not any(isinstance(value, APIRouter) for value in vars(routers).values())
