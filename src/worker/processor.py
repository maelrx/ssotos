"""Job processor — dispatches jobs to handlers per D-55."""
from typing import Any
import structlog

from src.db.database import async_session_maker
from src.worker.queue import JobQueue, JobClaim
from src.worker.handlers import HANDLERS

logger = structlog.get_logger(__name__)

class JobProcessor:
    """Processes jobs from the queue by dispatching to handlers."""

    def __init__(self, worker_id: str | None = None):
        self.queue = JobQueue(worker_id=worker_id)
        self.running = False

    async def process_one(self) -> bool:
        """Claim and process one job. Returns True if a job was processed."""
        async with async_session_maker() as db:
            claim = await self.queue.claim(db)
            if claim is None:
                return False

            job = claim.job
            handler = HANDLERS.get(job.job_type)

            if handler is None:
                await self.queue.fail(
                    db, job,
                    f"Unknown job type: {job.job_type}"
                )
                return True

            try:
                logger.info(
                    "job_started",
                    job_id=str(job.id),
                    job_type=job.job_type,
                    worker_id=self.queue.worker_id,
                )

                # Call the handler
                result = await handler(job.input_data)

                await self.queue.complete(db, job, result)
                return True

            except Exception as e:
                logger.exception(
                    "job_handler_error",
                    job_id=str(job.id),
                    job_type=job.job_type,
                    error=str(e),
                )
                await self.queue.fail(db, job, str(e))
                return True

    async def run(self, poll_interval: float = 1.0):
        """Main worker loop. Runs until self.running is set to False."""
        self.running = True
        logger.info("worker_started", worker_id=self.queue.worker_id)

        while self.running:
            try:
                processed = await self.process_one()
                if not processed:
                    # No jobs available — sleep before polling again
                    import asyncio
                    await asyncio.sleep(poll_interval)
            except Exception:
                logger.exception("worker_loop_error")
                import asyncio
                await asyncio.sleep(5)  # Back off on unexpected errors

        logger.info("worker_stopped", worker_id=self.queue.worker_id)
