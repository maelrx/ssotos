"""AuditLog model — D-51, D-57, F14-01."""
import uuid as uuid_lib
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class AuditLog(Base):
    """Audit logs table — immutable audit trail for all policy decisions and actions."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid_lib.UUID] = mapped_column(primary_key=True, default=uuid_lib.uuid4)
    workspace_id: Mapped[uuid_lib.UUID | None] = mapped_column(ForeignKey("workspaces.id"), nullable=True, index=True)
    event_id: Mapped[uuid_lib.UUID] = mapped_column(unique=True, nullable=False)  # unique event identifier
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    capability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # success, denied, error
    reason: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    extra: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_logs_workspace_timestamp", "workspace_id", "timestamp"),
        Index("ix_audit_logs_actor_timestamp", "actor", "timestamp"),
        Index("ix_audit_logs_trace_id", "trace_id"),
    )
