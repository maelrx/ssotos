"""Jobs REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException
from uuid import UUID

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/")
async def list_jobs():
    """List all jobs (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/")
async def create_job():
    """Create a job (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/{job_id}")
async def get_job(job_id: UUID):
    """Get job details (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: UUID):
    """Cancel a pending job (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/{job_id}/events")
async def get_job_events(job_id: UUID):
    """Get job event timeline (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/{job_id}/retry")
async def retry_job(job_id: UUID):
    """Retry a failed job (placeholder)."""
    raise HTTPException(status_code=501, detail="Not yet implemented")
