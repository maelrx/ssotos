"""Audit event types — per D-57 (F14-01 to F14-05)."""
from enum import Enum


class AuditEventType(str, Enum):
    # Vault operations (F14-04: file tracking)
    FILE_READ = "file.read"
    FILE_CREATED = "file.created"
    FILE_UPDATED = "file.updated"
    FILE_DELETED = "file.deleted"
    FILE_MOVED = "file.moved"

    # Proposal lifecycle (F14-05: proposal logging)
    PROPOSAL_CREATED = "proposal.created"
    PROPOSAL_SUBMITTED = "proposal.submitted"
    PROPOSAL_APPROVED = "proposal.approved"
    PROPOSAL_REJECTED = "proposal.rejected"
    PROPOSAL_APPLIED = "proposal.applied"
    PROPOSAL_ROLLBACK = "proposal.rollback"

    # Tool call logging (F14-03)
    TOOL_CALLED = "tool.called"
    TOOL_ERROR = "tool.error"

    # Job events (F14-02: job event timeline)
    JOB_CREATED = "job.created"
    JOB_CLAIMED = "job.claimed"
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"

    # Policy (F14-01)
    POLICY_EVALUATED = "policy.evaluated"
    POLICY_DENIED = "policy.denied"

    # Auth
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"
