"""Proposal model — D-51, F14-05."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class Proposal(Base):
    """Proposals table — exchange zone change proposals with review workflow."""

    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    proposal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_domain: Mapped[str] = mapped_column(String(50), nullable=False)
    target_domain: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft, generated, awaiting_review, approved, rejected, applied, superseded, failed
    branch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    worktree_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    target_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    patch_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    base_commit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    head_commit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_proposals_workspace_status", "workspace_id", "status"),
    )
