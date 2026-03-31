"""Embedding model — D-51, D-94."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from src.db.database import Base


class Embedding(Base):
    """Embeddings table — vector embeddings for chunks."""

    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chunks.id"), nullable=False, index=True)
    note_projection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes_projection.id"), nullable=False, index=True)
    embedding_vector: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)  # 1536-dim native vector
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_embeddings_chunk_id", "chunk_id"),
        Index("ix_embeddings_note_projection_id", "note_projection_id"),
    )
