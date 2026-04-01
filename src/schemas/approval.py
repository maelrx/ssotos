"""Pydantic schemas for approval flow — F13-07."""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ApprovalRequest(BaseModel):
    """Request approval for a job to pause at a checkpoint."""
    job_id: UUID
    approver_type: str = "user"  # user, role, policy
    approver_id: str | None = None
    reason: str | None = None


class ApprovalResponse(BaseModel):
    """Approval record embedded in job."""
    id: UUID
    job_id: UUID
    status: str  # pending, approved, rejected
    requested_at: datetime
    resolved_at: datetime | None
    resolved_by: str | None
    resolution_note: str | None


class ApprovalActionRequest(BaseModel):
    """Request to approve or reject a paused job."""
    reviewed_by: str = "user"
    note: str | None = None
