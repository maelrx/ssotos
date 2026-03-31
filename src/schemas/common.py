"""Common Pydantic schemas — per D-49 (Pydantic v2 for all DTOs)."""
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for created_at/updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None


class WorkspaceMixin(BaseModel):
    """Mixin for workspace-scoped entities."""
    workspace_id: UUID


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    total: int
    page: int
    limit: int
    items: list[dict]


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str | None = None


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
    detail: str | None = None
