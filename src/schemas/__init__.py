"""Pydantic schemas — per D-49 (Pydantic v2 for all DTOs)."""
from src.schemas.common import (
    TimestampMixin,
    WorkspaceMixin,
    PaginationParams,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.schemas.vault import (
    NoteFrontmatter,
    NoteCreateRequest,
    NoteUpdateRequest,
    NoteResponse,
    NoteListResponse,
)
from src.schemas.jobs import (
    JobType,
    JobStatus,
    JobCreateRequest,
    JobResponse,
    JobEventResponse,
    JobListResponse,
)

__all__ = [
    # common
    "TimestampMixin",
    "WorkspaceMixin",
    "PaginationParams",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    # vault
    "NoteFrontmatter",
    "NoteCreateRequest",
    "NoteUpdateRequest",
    "NoteResponse",
    "NoteListResponse",
    # jobs
    "JobType",
    "JobStatus",
    "JobCreateRequest",
    "JobResponse",
    "JobEventResponse",
    "JobListResponse",
]
