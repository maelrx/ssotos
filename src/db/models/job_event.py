"""JobEvent model — D-51, F14-02."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class JobEvent(Base):
    """Job events table — audit trail for job lifecycle events."""

    __tablename__ = "job_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # created, claimed, started, progress, completed, failed, retried
    message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    extra: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
