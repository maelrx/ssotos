"""Pydantic schemas for research pipeline — per F12-01."""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

class ResearchBriefRequest(BaseModel):
    """Request to create a research brief."""
    query: str = Field(min_length=1, description="Research question or topic")
    goal: str = Field(description="What the research aims to achieve")
    questions: list[str] = Field(default_factory=list, description="Specific questions to answer")
    scope: Literal["web", "documents", "all"] = "web"
    depth: Literal["surface", "moderate", "deep"] = "surface"
    max_sources: int = Field(default=10, ge=1, le=100)

class BlueprintResponse(BaseModel):
    """Response after creating a research blueprint."""
    job_id: UUID
    blueprint_path: str
    planned_sources: list[str]

class SourceStatus(BaseModel):
    """Status of a research source."""
    source_id: str
    url: str | None = None
    source_path: str | None = None
    status: Literal["pending", "crawled", "parsed", "failed"] = "pending"
    content_hash: str | None = None
    error: str | None = None

class ResearchJobStatus(BaseModel):
    """Status of a research job."""
    job_id: UUID
    query: str
    state: str = Field(description="Current pipeline state")
    progress: int = Field(ge=0, le=100)
    sources: list[SourceStatus] = Field(default_factory=list)
    synthesis_path: str | None = None
    blueprint_path: str | None = None

class CreateBriefResponse(BaseModel):
    """Response when creating a research brief."""
    job_id: UUID
    message: str
