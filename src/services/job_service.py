"""JobService — thin wrapper for job creation per D-71, D-82.

Provides a clean API surface for enqueueing jobs from other services.
Jobs are persisted to Postgres and picked up by the worker process.
"""
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.job import Job
from src.db.models.job_event import JobEvent


class JobService:
    """Thin service for creating jobs in the queue.

    Workers pick up pending jobs from the database using
    SELECT FOR UPDATE SKIP LOCKED (see src/worker/queue.py).
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def enqueue(
        self,
        job_type: str,
        job_data: dict[str, Any],
        priority: int = 0,
        workspace_id: UUID | None = None,
    ) -> Job:
        """Create a new pending job in the queue.

        Args:
            job_type: Type of job (e.g., "reflect_agent", "consolidate_memory")
            job_data: Input data for the job processor
            priority: Higher priority jobs are claimed first (default 0)
            workspace_id: Optional workspace context

        Returns:
            The created Job record
        """
        if workspace_id is None:
            workspace_id = UUID("00000000-0000-0000-0000-000000000000")

        job = Job(
            job_type=job_type,
            priority=priority,
            input_data=job_data,
            workspace_id=workspace_id,
            status="pending",
            attempt_count=0,
            max_attempts=3,
        )
        self._db.add(job)
        await self._db.flush()

        event = JobEvent(
            job_id=job.id,
            event_type="job_created",
            message=f"Job {job_type} created via JobService.enqueue",
            metadata={},
        )
        self._db.add(event)

        return job
