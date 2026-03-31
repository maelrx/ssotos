"""NoteProjection model — D-51, F8-02."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class NoteProjection(Base):
    """Notes projection table — derived filesystem projection for sync tracking."""

    __tablename__ = "notes_projection"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    note_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    note_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 for change detection
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # NoteType enum value
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    links: Mapped[list] = mapped_column(JSON, default=list)  # outgoing links
    frontmatter: Mapped[dict] = mapped_column(JSON, default=dict)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_state: Mapped[str] = mapped_column(String(20), default="synced")  # synced, pending, error

    __table_args__ = (
        Index("ix_notes_projection_workspace_path", "workspace_id", "note_path", unique=True),
    )
