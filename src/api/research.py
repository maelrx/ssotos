"""Research REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException
from uuid import UUID

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/jobs")
async def list_research_jobs():
    """List research jobs (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 8 feature - not yet implemented")


@router.post("/jobs")
async def create_research_job():
    """Create research job (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 8 feature - not yet implemented")


@router.get("/jobs/{job_id}")
async def get_research_job(job_id: UUID):
    """Get research job status (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 8 feature - not yet implemented")


@router.get("/jobs/{job_id}/artifacts")
async def list_artifacts(job_id: UUID):
    """List artifacts (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 8 feature - not yet implemented")
