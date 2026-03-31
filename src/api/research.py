"""Research REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from typing import Any

from src.db.session import get_db
from src.db.models.job import Job
from src.db.models.artifact import Artifact
from src.db.models.workspace import Workspace

router = APIRouter(prefix="/research", tags=["research"])


class CreateResearchJobRequest(BaseModel):
    """Request to create a research job."""
    query: str
    sources: list[str] = []
    workspace_id: UUID | None = None
    metadata: dict[str, Any] = {}


@router.get("/jobs")
async def list_research_jobs(
    status: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List research jobs (job_type='research_job')."""
    stmt = (
        select(Job)
        .where(Job.job_type == "research_job")
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    if status:
        stmt = stmt.where(Job.status == status)

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return {
        "jobs": [
            {
                "id": str(job.id),
                "query": job.input_data.get("query", ""),
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }
            for job in jobs
        ],
        "total": len(jobs),
    }


@router.post("/jobs")
async def create_research_job(
    request: CreateResearchJobRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new research job.

    Research jobs follow the pipeline:
    blueprint -> job -> raw -> synthesis -> ingest proposal
    """
    workspace_id = request.workspace_id

    if not workspace_id:
        ws_stmt = select(Workspace).limit(1)
        ws_result = await db.execute(ws_stmt)
        workspace = ws_result.scalar_one_or_none()
        if workspace:
            workspace_id = workspace.id

    job = Job(
        job_type="research_job",
        priority=50,
        input_data={
            "query": request.query,
            "sources": request.sources,
            "metadata": request.metadata,
        },
        workspace_id=workspace_id or UUID("00000000-0000-0000-0000-000000000000"),
        status="pending",
    )
    db.add(job)
    await db.flush()

    return {
        "success": True,
        "message": "Research job created",
        "job_id": str(job.id),
    }


@router.get("/jobs/{job_id}")
async def get_research_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get research job status and results."""
    stmt = select(Job).where(Job.id == job_id, Job.job_type == "research_job")
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")

    return {
        "id": str(job.id),
        "query": job.input_data.get("query", ""),
        "sources": job.input_data.get("sources", []),
        "status": job.status,
        "result_data": job.result_data,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


@router.get("/jobs/{job_id}/artifacts")
async def list_artifacts(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List artifacts produced by a research job."""
    stmt = (
        select(Artifact)
        .where(Artifact.job_id == job_id)
        .order_by(Artifact.created_at.desc())
    )
    result = await db.execute(stmt)
    artifacts = result.scalars().all()

    return {
        "job_id": str(job_id),
        "artifacts": [
            {
                "id": str(a.id),
                "artifact_type": a.artifact_type,
                "name": a.name,
                "path": a.path,
                "mime_type": a.mime_type,
                "size_bytes": a.size_bytes,
                "created_at": a.created_at.isoformat(),
            }
            for a in artifacts
        ],
        "total": len(artifacts),
    }
