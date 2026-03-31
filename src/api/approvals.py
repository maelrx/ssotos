"""Approvals REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException
from uuid import UUID

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/")
async def list_pending_approvals():
    """List pending approvals (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/{approval_id}")
async def get_approval(approval_id: UUID):
    """Get approval details (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/{approval_id}/approve")
async def approve_item(approval_id: UUID):
    """Approve (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/{approval_id}/reject")
async def reject_item(approval_id: UUID):
    """Reject (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/")
async def create_approval_request():
    """Create approval request (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")
