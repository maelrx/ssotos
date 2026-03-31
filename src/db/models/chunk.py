"""Chunk model — D-51."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class Chunk(Base):
    """Chunks table — chunked note content for embedding and retrieval."""

    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    note_projection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes_projection.id"), nullable=False, index=True)
    heading_path: Mapped[str] = mapped_column(String(512), nullable=False)  # e.g., "## Introduction"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    char_start: Mapped[int] = mapped_column(Integer, nullable=False)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_chunks_note_projection_index", "note_projection_id", "chunk_index"),
    )
