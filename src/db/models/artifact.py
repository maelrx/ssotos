"""Artifact model — D-51."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class Artifact(Base):
    """Artifacts table — research outputs and downloaded content."""

    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id"), nullable=True, index=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # raw_web, raw_document, synthesis, blueprint, manifest
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    extra: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_artifacts_workspace_type", "workspace_id", "artifact_type"),
    )
