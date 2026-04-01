"""Postgres-backed job queue with row claiming — per D-54.

Uses SELECT FOR UPDATE SKIP LOCKED to atomically claim jobs.
Multiple workers can run simultaneously without conflicts.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
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
        Skips jobs that are paused for approval.
        """
        now = datetime.utcnow()

        # Build query for available jobs (skip jobs with next_retry_at in future)
        # Skip jobs that are paused for approval (approval_required=True means awaiting)
        query = (
            select(Job)
            .where(Job.status == "pending")
            .where(Job.claimed_by.is_(None))
            .where((Job.next_retry_at.is_(None)) | (Job.next_retry_at <= now))
            .where(~((Job.approval_required == True) & (Job.approval_id.isnot(None))))
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
        """Mark job as failed. Handles retry logic with exponential backoff."""
        now = datetime.utcnow()
        job.attempt_count += 1
        job.error_message = error

        if job.attempt_count >= job.max_attempts:
            # Max retries reached — mark as permanently failed
            job.status = "failed"
            job.completed_at = now
            job.next_retry_at = None
            event_type = "failed"
            message = f"Job failed after {job.attempt_count} attempts: {error}"
        else:
            # Exponential backoff: base=30s, multiplier=2, cap=3600s
            base_delay = 30
            max_delay = 3600
            delay = min(base_delay * (2 ** (job.attempt_count - 1)), max_delay)
            job.next_retry_at = now + timedelta(seconds=delay)

            # Reset for retry
            job.status = "pending"
            job.claimed_by = None
            job.claimed_at = None
            job.started_at = None
            event_type = "retried"
            message = f"Job will retry (attempt {job.attempt_count}/{job.max_attempts}) in {delay}s"

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

    async def record_checkpoint(
        self,
        db: AsyncSession,
        job: Job,
        checkpoint_id: str,
        checkpoint_data: dict[str, Any],
    ) -> None:
        """Record a named checkpoint for a running job.

        Stores intermediate progress so job can resume from this point
        if interrupted. Checkpoint data is merged into result_data
        under a 'checkpoints' key.

        Args:
            checkpoint_id: Unique identifier for this checkpoint (e.g., 'stage-3-crawl')
            checkpoint_data: Arbitrary dict with intermediate state
        """
        now = datetime.utcnow()

        # Initialize checkpoints structure
        if job.result_data is None:
            job.result_data = {}

        if "checkpoints" not in job.result_data:
            job.result_data["checkpoints"] = {}

        # Store checkpoint with timestamp
        job.result_data["checkpoints"][checkpoint_id] = {
            "data": checkpoint_data,
            "recorded_at": now.isoformat(),
            "attempt": job.attempt_count,
        }
        job.last_checkpoint = checkpoint_id

        event = JobEvent(
            id=uuid4(),
            job_id=job.id,
            event_type="checkpoint",
            message=f"Checkpoint recorded: {checkpoint_id}",
            extra={"checkpoint_id": checkpoint_id, "attempt": job.attempt_count},
            trace_id=job.trace_id,
        )
        db.add(event)
        await db.commit()

        broadcast_job_event({
            "event_type": "job_checkpoint",
            "job_id": str(job.id),
            "checkpoint_id": checkpoint_id,
        }, workspace_id=str(job.workspace_id) if job.workspace_id else None)

        logger.debug("checkpoint_recorded", job_id=str(job.id), checkpoint_id=checkpoint_id)

    def get_checkpoint_data(self, job: Job, checkpoint_id: str) -> dict[str, Any] | None:
        """Extract checkpoint data from job result_data."""
        if job.result_data is None:
            return None
        checkpoints = job.result_data.get("checkpoints", {})
        checkpoint = checkpoints.get(checkpoint_id)
        if checkpoint:
            return checkpoint.get("data")
        return None

    async def pause_for_approval(
        self,
        db: AsyncSession,
        job: Job,
        approval_id: str,
    ) -> None:
        """Pause a running job to wait for human approval.

        Transitions job to awaiting_approval status and records an event.
        The job will not be claimed by workers until approved or rejected.
        """
        now = datetime.utcnow()
        job.status = "awaiting_approval"
        job.approval_required = True
        job.approval_id = UUID(approval_id)

        event = JobEvent(
            id=uuid4(),
            job_id=job.id,
            event_type="awaiting_approval",
            message=f"Job paused for approval: {approval_id}",
            extra={"approval_id": approval_id},
            trace_id=job.trace_id,
        )
        db.add(event)
        await db.commit()

        broadcast_job_event({
            "event_type": "job_awaiting_approval",
            "job_id": str(job.id),
            "approval_id": approval_id,
            "timestamp": now.isoformat(),
        }, workspace_id=str(job.workspace_id) if job.workspace_id else None)

        logger.info(
            "job_paused_for_approval",
            job_id=str(job.id),
            approval_id=approval_id,
        )
