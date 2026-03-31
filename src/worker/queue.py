"""Postgres-backed job queue with row claiming — per D-54.

Uses SELECT FOR UPDATE SKIP LOCKED to atomically claim jobs.
Multiple workers can run simultaneously without conflicts.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4
import structlog

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Job, JobEvent
from src.api.sse import broadcast_job_event

logger = structlog.get_logger(__name__)

@dataclass
class JobClaim:
    """Represents a claimed job ready for processing."""
    job: Job
    db: AsyncSession

class JobQueue:
    """Postgres-backed job queue with row claiming.

    Workers claim jobs atomically using FOR UPDATE SKIP LOCKED.
    This ensures only one worker processes each job even with
    multiple worker instances.
    """

    def __init__(self, worker_id: str | None = None):
        self.worker_id = worker_id or f"worker-{uuid4().hex[:8]}"
        self._claim_ttl_seconds = 300  # 5 minutes — job considered stale if not heartbeat

    async def claim(self, db: AsyncSession, job_type: str | None = None) -> JobClaim | None:
        """Atomically claim an available job.

        Uses SELECT FOR UPDATE SKIP LOCKED to ensure atomic claim.
        Returns None if no jobs available.
        """
        # Build query for available jobs
        query = (
            select(Job)
            .where(Job.status == "pending")
            .where(Job.claimed_by.is_(None))
            .order_by(Job.priority.desc(), Job.created_at)
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        if job_type:
            query = query.where(Job.job_type == job_type)

        result = await db.execute(query)
        job = result.scalar_one_or_none()

        if job is None:
            return None

        # Claim the job
        now = datetime.utcnow()
        job.claimed_by = self.worker_id
        job.claimed_at = now
        job.status = "running"
        job.trace_id = str(uuid4())

        # Record event
        event = JobEvent(
            id=uuid4(),
            job_id=job.id,
            event_type="claimed",
            message=f"Claimed by {self.worker_id}",
            extra={"worker_id": self.worker_id},
            trace_id=job.trace_id,
        )
        db.add(event)

        await db.commit()

        # Broadcast SSE event
        broadcast_job_event({
            "event_type": "job_claimed",
            "job_id": str(job.id),
            "job_type": job.job_type,
            "worker_id": self.worker_id,
            "timestamp": now.isoformat(),
        }, workspace_id=str(job.workspace_id) if job.workspace_id else None)

        logger.info("job_claimed", job_id=str(job.id), job_type=job.job_type, worker_id=self.worker_id)

        return JobClaim(job=job, db=db)

    async def complete(self, db: AsyncSession, job: Job, result_data: dict) -> None:
        """Mark job as completed successfully."""
        now = datetime.utcnow()
        job.status = "completed"
        job.result_data = result_data
        job.completed_at = now

        event = JobEvent(
            id=uuid4(),
            job_id=job.id,
            event_type="completed",
            message="Job completed successfully",
            extra=result_data,
            trace_id=job.trace_id,
        )
        db.add(event)
        await db.commit()

        broadcast_job_event({
            "event_type": "job_completed",
            "job_id": str(job.id),
            "result": result_data,
            "timestamp": now.isoformat(),
        }, workspace_id=str(job.workspace_id) if job.workspace_id else None)

        logger.info("job_completed", job_id=str(job.id), job_type=job.job_type)

    async def fail(self, db: AsyncSession, job: Job, error: str) -> None:
        """Mark job as failed. Handles retry logic."""
        now = datetime.utcnow()
        job.attempt_count += 1
        job.error_message = error

        if job.attempt_count >= job.max_attempts:
            # Max retries reached — mark as permanently failed
            job.status = "failed"
            job.completed_at = now
            event_type = "failed"
            message = f"Job failed after {job.attempt_count} attempts: {error}"
        else:
            # Reset for retry with exponential backoff
            job.status = "pending"
            job.claimed_by = None
            job.claimed_at = None
            job.started_at = None
            event_type = "retried"
            message = f"Job will retry (attempt {job.attempt_count + 1}/{job.max_attempts})"

        event = JobEvent(
            id=uuid4(),
            job_id=job.id,
            event_type=event_type,
            message=message,
            extra={"error": error, "attempt": job.attempt_count},
            trace_id=job.trace_id,
        )
        db.add(event)
        await db.commit()

        broadcast_job_event({
            "event_type": event_type,
            "job_id": str(job.id),
            "error": error,
            "attempt": job.attempt_count,
            "timestamp": now.isoformat(),
        }, workspace_id=str(job.workspace_id) if job.workspace_id else None)

        logger.warning("job_failed", job_id=str(job.id), attempt=job.attempt_count, error=error)

    async def record_progress(self, db: AsyncSession, job: Job, progress: int, message: str) -> None:
        """Record job progress for long-running jobs."""
        event = JobEvent(
            id=uuid4(),
            job_id=job.id,
            event_type="progress",
            message=message,
            extra={"progress": progress},
            trace_id=job.trace_id,
        )
        db.add(event)
        await db.commit()

        broadcast_job_event({
            "event_type": "job_progress",
            "job_id": str(job.id),
            "progress": progress,
            "message": message,
        }, workspace_id=str(job.workspace_id) if job.workspace_id else None)
