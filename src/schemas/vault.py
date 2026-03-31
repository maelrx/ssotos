"""Vault Pydantic schemas."""
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class NoteFrontmatter(BaseModel):
    """Frontmatter for a note."""
    id: str
    kind: str
    status: str = "active"
    title: str
    tags: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    source: str | None = None
    policy: dict | None = None


class NoteCreateRequest(BaseModel):
    """Request to create a note."""
    path: str
    content: str
    frontmatter: NoteFrontmatter
    actor: str = "user"


class NoteUpdateRequest(BaseModel):
    """Request to update a note."""
    content: str | None = None
    frontmatter: dict | None = None
    actor: str = "user"


class NoteResponse(BaseModel):
    """Response model for a note."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    path: str
    kind: str
    title: str
    tags: list[str]
    links: list[str]
    frontmatter: dict
    content: str
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    """Response model for a list of notes."""
    notes: list[NoteResponse]
    total: int
