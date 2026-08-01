"""Public metadata-only schema contracts.

Shapes only: typed file metadata and job metadata/state models with the
metadata-only invariants. This package defines no endpoints, capability
values, or Redis record shapes.
"""

from __future__ import annotations

from app.schemas.file import FileMetadata, FileObjectMetadata
from app.schemas.job import (
    ErrorSummary,
    JobState,
    Progress,
    ResultSummary,
    TaskAdmission,
    TaskStatus,
)

__all__ = [
    "ErrorSummary",
    "FileMetadata",
    "FileObjectMetadata",
    "JobState",
    "Progress",
    "ResultSummary",
    "TaskAdmission",
    "TaskStatus",
]
