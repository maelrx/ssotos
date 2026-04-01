"""Job model — D-51, F13-01, F13-02."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, JSON, ForeignKey, Index, Boolean
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class Job(Base):
    """Jobs table — async job queue for background workers."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)  # index_note, reindex_scope, generate_embeddings, research_job, parse_source, apply_patch_bundle, reflect_agent, consolidate_memory
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed
    priority: Mapped[int] = mapped_column(Integer, default=0)
    input_data: Mapped[dict] = mapped_column(JSON, default=dict)
    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    claimed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)  # worker instance ID
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_checkpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    approval_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_jobs_workspace_status", "workspace_id", "status"),
        Index("ix_jobs_priority_created", "priority", "created_at"),
    )
