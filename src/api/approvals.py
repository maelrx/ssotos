"""Approvals REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from src.db.session import get_db
from src.db.models.approval import Approval
from src.db.models.workspace import Workspace

router = APIRouter(prefix="/approvals", tags=["approvals"])


class CreateApprovalRequest(BaseModel):
    """Request to create an approval."""
    title: str
    description: str | None = None
    approval_type: str
    target_domain: str
    target_path: str | None = None
    requested_by: str = "user"
    metadata: dict = {}


class ApprovalActionRequest(BaseModel):
    """Request to approve or reject."""
    reviewed_by: str = "user"
    note: str | None = None


@router.get("/")
async def list_pending_approvals(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List pending approvals."""
    stmt = select(Approval).order_by(Approval.created_at.desc())
    if status:
        stmt = stmt.where(Approval.status == status)
    else:
        stmt = stmt.where(Approval.status == "pending")

    result = await db.execute(stmt)
    approvals = result.scalars().all()

    return {
        "approvals": [
            {
                "id": str(a.id),
                "title": a.title,
                "approval_type": a.approval_type,
                "target_domain": a.target_domain,
                "target_path": a.target_path,
                "status": a.status,
                "requested_by": a.requested_by,
                "created_at": a.created_at.isoformat(),
            }
            for a in approvals
        ],
        "total": len(approvals),
    }


@router.get("/{approval_id}")
async def get_approval(
    approval_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get approval details."""
    stmt = select(Approval).where(Approval.id == approval_id)
    result = await db.execute(stmt)
    approval = result.scalar_one_or_none()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    return {
        "id": str(approval.id),
        "title": approval.title,
        "description": approval.description,
        "approval_type": approval.approval_type,
        "target_domain": approval.target_domain,
        "target_path": approval.target_path,
        "status": approval.status,
        "requested_by": approval.requested_by,
        "reviewed_by": approval.reviewed_by,
        "reviewed_at": approval.reviewed_at.isoformat() if approval.reviewed_at else None,
        "review_note": approval.review_note,
        "metadata": approval.metadata or {},
        "created_at": approval.created_at.isoformat(),
    }


@router.post("/{approval_id}/approve")
async def approve_item(
    approval_id: UUID,
    request: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending item."""
    stmt = select(Approval).where(Approval.id == approval_id)
    result = await db.execute(stmt)
    approval = result.scalar_one_or_none()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Approval is '{approval.status}', not 'pending'"
        )

    approval.status = "approved"
    approval.reviewed_by = request.reviewed_by
    approval.reviewed_at = datetime.utcnow()
    approval.review_note = request.note

    return {
        "success": True,
        "message": "Approval granted",
        "approval_id": str(approval_id),
    }


@router.post("/{approval_id}/reject")
async def reject_item(
    approval_id: UUID,
    request: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending item."""
    stmt = select(Approval).where(Approval.id == approval_id)
    result = await db.execute(stmt)
    approval = result.scalar_one_or_none()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Approval is '{approval.status}', not 'pending'"
        )

    approval.status = "rejected"
    approval.reviewed_by = request.reviewed_by
    approval.reviewed_at = datetime.utcnow()
    approval.review_note = request.note

    return {
        "success": True,
        "message": "Approval rejected",
        "approval_id": str(approval_id),
    }


@router.post("/")
async def create_approval_request(
    request: CreateApprovalRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new approval request."""
    # Get default workspace
    ws_stmt = select(Workspace).limit(1)
    ws_result = await db.execute(ws_stmt)
    workspace = ws_result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=400,
            detail="No workspace available"
        )

    approval = Approval(
        workspace_id=workspace.id,
        title=request.title,
        description=request.description,
        approval_type=request.approval_type,
        target_domain=request.target_domain,
        target_path=request.target_path,
        requested_by=request.requested_by,
        metadata=request.metadata,
        status="pending",
    )
    db.add(approval)
    await db.flush()

    return {
        "success": True,
        "message": "Approval request created",
        "approval_id": str(approval.id),
    }
