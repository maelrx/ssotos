"""Job Pydantic schemas."""
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class JobType(str):
    """Job type constants."""
    INDEX_NOTE = "index_note"
    REINDEX_SCOPE = "reindex_scope"
    GENERATE_EMBEDDINGS = "generate_embeddings"
    RESEARCH_JOB = "research_job"
    PARSE_SOURCE = "parse_source"
    APPLY_PATCH_BUNDLE = "apply_patch_bundle"
    REFLECT_AGENT = "reflect_agent"
    CONSOLIDATE_MEMORY = "consolidate_memory"


class JobStatus(str):
    """Job status constants."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobCreateRequest(BaseModel):
    """Request to create a job."""
    job_type: str
    priority: int = Field(default=0)
    input_data: dict = Field(default_factory=dict)
    workspace_id: UUID | None = None


class JobResponse(BaseModel):
    """Response model for a job."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    job_type: str
    status: str
    priority: int
    input_data: dict
    result_data: dict | None
    error_message: str | None
    attempt_count: int
    max_attempts: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class JobEventResponse(BaseModel):
    """Response model for a job event."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    job_id: UUID
    event_type: str
    message: str | None
    metadata: dict
    created_at: datetime


class JobListResponse(BaseModel):
    """Response model for a list of jobs."""
    jobs: list[JobResponse]
    total: int
