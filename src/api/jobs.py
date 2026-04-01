"""Jobs REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from src.db.session import get_db
from src.db.models.job import Job
from src.db.models.job_event import JobEvent
from src.schemas.jobs import (
    JobCreateRequest,
    JobResponse,
    JobEventResponse,
    JobListResponse,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _job_to_response(job: Job) -> JobResponse:
    """Convert a Job model to JobResponse."""
    return JobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        input_data=job.input_data or {},
        result_data=job.result_data,
        error_message=job.error_message,
        attempt_count=job.attempt_count,
        max_attempts=job.max_attempts,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    status: str | None = Query(None, description="Filter by job status"),
    job_type: str | None = Query(None, description="Filter by job type"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all jobs with optional status/type filters."""
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(Job.status == status)
    if job_type:
        stmt = stmt.where(Job.job_type == job_type)

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    count_stmt = select(Job)
    if status:
        count_stmt = count_stmt.where(Job.status == status)
    if job_type:
        count_stmt = count_stmt.where(Job.job_type == job_type)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    return JobListResponse(
        jobs=[_job_to_response(job) for job in jobs],
        total=total,
    )


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    request: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new job.

    Jobs are added to the queue for worker processing.
    The job starts in 'pending' status.

    If an idempotency_key is provided and a job with the same key and job_type
    already exists, returns the existing job with idempotent=True.
    """
    from src.db.models.workspace import Workspace
    from sqlalchemy import select

    workspace_id = request.workspace_id

    # If no workspace_id provided, get the default workspace
    if not workspace_id:
        ws_stmt = select(Workspace).limit(1)
        ws_result = await db.execute(ws_stmt)
        workspace = ws_result.scalar_one_or_none()
        if workspace:
            workspace_id = workspace.id

    # Check for existing job with same idempotency_key and job_type
    if request.idempotency_key:
        existing_stmt = select(Job).where(
            Job.idempotency_key == request.idempotency_key,
            Job.job_type == request.job_type,
        )
        existing_result = await db.execute(existing_stmt)
        existing_job = existing_result.scalar_one_or_none()
        if existing_job:
            return JobResponse(
                id=existing_job.id,
                job_type=existing_job.job_type,
                status=existing_job.status,
                priority=existing_job.priority,
                input_data=existing_job.input_data or {},
                result_data=existing_job.result_data,
                error_message=existing_job.error_message,
                attempt_count=existing_job.attempt_count,
                max_attempts=existing_job.max_attempts,
                created_at=existing_job.created_at,
                started_at=existing_job.started_at,
                completed_at=existing_job.completed_at,
                idempotent=True,
            )

    job = Job(
        job_type=request.job_type,
        priority=request.priority,
        input_data=request.input_data,
        workspace_id=workspace_id or UUID("00000000-0000-0000-0000-000000000000"),
        status="pending",
        attempt_count=0,
        max_attempts=3,
        idempotency_key=request.idempotency_key,
    )
    db.add(job)
    await db.flush()

    # Record job created event
    event = JobEvent(
        job_id=job.id,
        event_type="job_created",
        message=f"Job {job.job_type} created",
        metadata={},
    )
    db.add(event)

    return JobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        input_data=job.input_data or {},
        result_data=job.result_data,
        error_message=job.error_message,
        attempt_count=job.attempt_count,
        max_attempts=job.max_attempts,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        idempotent=False,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get job details by ID."""
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return _job_to_response(job)


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a pending job.

    Only jobs in 'pending' status can be cancelled.
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in '{job.status}' status. Only 'pending' jobs can be cancelled."
        )

    job.status = "failed"
    job.error_message = "Cancelled by user"
    job.completed_at = datetime.utcnow()

    # Record cancellation event
    event = JobEvent(
        job_id=job.id,
        event_type="job_cancelled",
        message="Job cancelled by user",
        metadata={},
    )
    db.add(event)

    return {"success": True, "message": "Job cancelled"}


@router.get("/{job_id}/events")
async def get_job_events(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the event timeline for a job (F14-02)."""
    # Verify job exists
    job_stmt = select(Job).where(Job.id == job_id)
    job_result = await db.execute(job_stmt)
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get events
    events_stmt = (
        select(JobEvent)
        .where(JobEvent.job_id == job_id)
        .order_by(JobEvent.created_at.asc())
    )
    events_result = await db.execute(events_stmt)
    events = events_result.scalars().all()

    return {
        "job_id": str(job_id),
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "message": e.message,
                "metadata": e.extra or {},
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed job.

    Resets the job to 'pending' status and increments attempt count.
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ("failed",):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry job in '{job.status}' status. Only failed jobs can be retried."
        )

    if job.attempt_count >= job.max_attempts:
        raise HTTPException(
            status_code=400,
            detail=f"Job has reached max attempts ({job.max_attempts})"
        )

    job.status = "pending"
    job.attempt_count += 1
    job.error_message = None
    job.completed_at = None
    job.started_at = None

    # Record retry event
    event = JobEvent(
        job_id=job.id,
        event_type="job_retried",
        message=f"Job retry attempt {job.attempt_count}",
        metadata={},
    )
    db.add(event)

    return {"success": True, "message": f"Job retry scheduled (attempt {job.attempt_count})"}
