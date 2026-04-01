"""Approval service for human-in-the-loop job gates — F13-07."""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal
import structlog

from sqlalchemy import select

from src.db.session import async_session_maker
from src.db.models import Job

logger = structlog.get_logger(__name__)


class ApprovalService:
    """Manages approval lifecycle for jobs that need human review."""

    async def request_approval(
        self,
        job_id: UUID,
        approver_type: Literal["user", "role", "policy"] = "user",
        approver_id: str | None = None,
        reason: str | None = None,
    ) -> str:
        """Request approval for a job.

        Pauses the job at current checkpoint and returns approval_id
        that can be used to approve or reject.

        Returns:
            approval_id: str - UUID string for this approval request
        """
        async with async_session_maker() as db:
            result = await db.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"Job {job_id} not found")

            approval_id = str(uuid4())
            job.approval_required = True
            job.approval_id = UUID(approval_id)
            job.status = "awaiting_approval"

            await db.commit()
            logger.info(
                "approval_requested",
                job_id=str(job_id),
                approval_id=approval_id,
                approver_type=approver_type,
            )
            return approval_id

    async def approve(
        self,
        approval_id: str,
        resolved_by: str | None = None,
        resolution_note: str | None = None,
    ) -> None:
        """Approve a job, resuming its execution.

        The job will be picked up by a worker and continue from
        its last checkpoint.
        """
        async with async_session_maker() as db:
            result = await db.execute(
                select(Job).where(Job.approval_id == UUID(approval_id))
            )
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"No job found for approval {approval_id}")

            job.status = "pending"
            job.claimed_by = None  # Allow any worker to claim
            job.approval_required = False
            # approval_id left intact for audit trail

            await db.commit()
            logger.info(
                "approval_approved",
                job_id=str(job.id),
                approval_id=approval_id,
                resolved_by=resolved_by,
            )

    async def reject(
        self,
        approval_id: str,
        resolved_by: str | None = None,
        resolution_note: str | None = None,
    ) -> None:
        """Reject a job, marking it as failed."""
        async with async_session_maker() as db:
            result = await db.execute(
                select(Job).where(Job.approval_id == UUID(approval_id))
            )
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"No job found for approval {approval_id}")

            job.status = "failed"
            job.error_message = f"Rejected: {resolution_note or 'No reason provided'}"
            job.approval_required = False

            await db.commit()
            logger.warning(
                "approval_rejected",
                job_id=str(job.id),
                approval_id=approval_id,
                resolved_by=resolved_by,
                resolution_note=resolution_note,
            )
