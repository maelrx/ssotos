"""Audit logger — per D-57 (F14-01 to F14-05).

Writes structured audit log entries to the audit_logs table
with trace_id for distributed tracing across async boundaries.
"""
from datetime import datetime
from typing import Any
from uuid import uuid4, UUID
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import AuditLog
from src.core.audit_events import AuditEventType

logger = structlog.get_logger(__name__)


class AuditLogger:
    """Audit logger that writes structured entries to audit_logs table.

    Trace ID is propagated through contextvars for async safety.
    """

    def __init__(self):
        self._context: dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """Set audit context for subsequent calls (actor, workspace_id, etc)."""
        self._context.update(kwargs)

    def clear_context(self) -> None:
        """Clear audit context."""
        self._context.clear()

    async def log(
        self,
        db: AsyncSession,
        event_type: AuditEventType | str,
        actor: str,
        result: str = "success",
        capability: str | None = None,
        domain: str | None = None,
        target: str | None = None,
        action: str | None = None,
        reason: str | None = None,
        trace_id: str | None = None,
        metadata: dict | None = None,
        **extra
    ) -> UUID:
        """Write an audit log entry.

        Args:
            db: Database session
            event_type: Type of event (AuditEventType or string)
            actor: Who performed the action
            result: success, denied, error
            capability: Which capability was exercised
            domain: Which domain (vault, agent, exchange, research)
            target: What was targeted
            action: What action was performed
            reason: Why (for denied/error results)
            trace_id: Distributed trace ID
            metadata: Additional structured data

        Returns:
            event_id: UUID of the created audit log entry
        """
        event_id = uuid4()
        timestamp = datetime.utcnow()

        # Merge context with provided values
        merged = {**self._context, **extra}
        merged_metadata = {**(metadata or {}), **merged}

        audit_entry = AuditLog(
            id=uuid4(),
            event_id=event_id,
            trace_id=trace_id,
            actor=actor,
            capability=capability,
            domain=domain,
            target=target,
            action=action,
            result=result,
            reason=reason,
            extra=merged_metadata,
            timestamp=timestamp,
        )

        if db is not None:
            db.add(audit_entry)
            await db.commit()

        # Also emit to structlog for log-based observability
        log_data = {
            "event_id": str(event_id),
            "trace_id": trace_id,
            "audit_event_type": str(event_type),
            "actor": actor,
            "capability": capability,
            "domain": domain,
            "target": target,
            "result": result,
        }
        if reason:
            log_data["reason"] = reason

        if result == "success":
            logger.info("audit_event", **log_data)
        elif result == "denied":
            logger.warning("audit_event_denied", **log_data)
        else:
            logger.error("audit_event_error", **log_data)

        return event_id


# Global audit logger instance
audit_logger = AuditLogger()


async def audit_log(
    db: AsyncSession,
    event_type: AuditEventType | str,
    actor: str,
    **kwargs
) -> UUID:
    """Module-level audit logging function."""
    return await audit_logger.log(db, event_type, actor, **kwargs)
