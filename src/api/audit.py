"""Audit log query endpoints — per F14-01."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from uuid import UUID

from src.db.session import get_db
from src.db.models import AuditLog

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-logs")
async def query_audit_logs(
    db: AsyncSession = Depends(get_db),
    actor: str | None = Query(None, description="Filter by actor"),
    domain: str | None = Query(None, description="Filter by domain"),
    capability: str | None = Query(None, description="Filter by capability"),
    result: str | None = Query(None, description="Filter by result (success, denied, error)"),
    start_time: datetime | None = Query(None, description="Filter from timestamp"),
    end_time: datetime | None = Query(None, description="Filter to timestamp"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """Query audit logs with filters — per F14-01.

    Returns paginated audit log entries matching the filters.
    """
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())

    if actor:
        query = query.where(AuditLog.actor == actor)
    if domain:
        query = query.where(AuditLog.domain == domain)
    if capability:
        query = query.where(AuditLog.capability == capability)
    if result:
        query = query.where(AuditLog.result == result)
    if start_time:
        query = query.where(AuditLog.timestamp >= start_time)
    if end_time:
        query = query.where(AuditLog.timestamp <= end_time)

    # Count total
    count_query = select(func.count()).select_from(AuditLog)
    if actor:
        count_query = count_query.where(AuditLog.actor == actor)
    if domain:
        count_query = count_query.where(AuditLog.domain == domain)
    if capability:
        count_query = count_query.where(AuditLog.capability == capability)
    if result:
        count_query = count_query.where(AuditLog.result == result)
    if start_time:
        count_query = count_query.where(AuditLog.timestamp >= start_time)
    if end_time:
        count_query = count_query.where(AuditLog.timestamp <= end_time)

    total = await db.scalar(count_query)

    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    result_proxy = await db.execute(query)
    logs = result_proxy.scalars().all()

    return {
        "total": total or 0,
        "page": page,
        "limit": limit,
        "items": [
            {
                "id": str(log.id),
                "event_id": str(log.event_id),
                "trace_id": log.trace_id,
                "actor": log.actor,
                "capability": log.capability,
                "domain": log.domain,
                "target": log.target,
                "action": log.action,
                "result": log.result,
                "reason": log.reason,
                "metadata": log.extra or {},
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }
