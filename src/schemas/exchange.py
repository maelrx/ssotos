"""Pydantic schemas for Exchange Zone API."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


# Request schemas

class CreateProposalRequest(BaseModel):
    proposal_type: str  # NOTE_CREATE, NOTE_EDIT, etc.
    source_domain: str   # user_vault, agent_brain, research, import
    target_domain: str
    target_path: str | None = None
    source_ref: str | None = None
    actor: str = "system"

    # For NOTE_CREATE, NOTE_EDIT
    content: str | None = None  # Note content to propose
    title: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "proposal_type": "NOTE_EDIT",
                "source_domain": "agent_brain",
                "target_domain": "user_vault",
                "target_path": "02-Projects/My-Project.md",
                "actor": "agent",
                "content": "# Updated content..."
            }
        }
    }


class ApproveProposalRequest(BaseModel):
    proposal_id: str
    reviewed_by: str | None = "user"
    review_note: str | None = None


class RejectProposalRequest(BaseModel):
    proposal_id: str
    reason: str


class ApplyProposalRequest(BaseModel):
    proposal_id: str


# Response schemas

class DiffInfo(BaseModel):
    """D-30: Readable diff output."""
    files_changed: int
    insertions: int
    deletions: int
    diff_content: str  # Unified diff format


class PatchBundle(BaseModel):
    """D-29, D-31: Self-contained patch for transport."""
    proposal_id: str
    bundle_path: str
    diff: DiffInfo
    created_at: datetime
    self_contained: bool = True  # D-31: applies cleanly to main


class ReviewBundle(BaseModel):
    """D-28: Review package with diff and provenance."""
    proposal_id: str
    proposal_type: str
    state: str
    actor: str
    created_at: datetime
    target_domain: str
    target_path: str | None = None
    source_ref: str | None = None
    diff: DiffInfo
    provenance: dict  # How this proposal was created
    can_apply: bool
    can_reject: bool


class ProposalResponse(BaseModel):
    """Full proposal for API responses."""
    id: str
    proposal_type: str
    source_domain: str
    target_domain: str
    branch_name: str
    worktree_path: str
    state: str
    actor: str
    created_at: datetime
    updated_at: datetime
    target_path: str | None
    source_ref: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    review_note: str | None
    patch_path: str | None
    base_commit: str | None
    head_commit: str | None
    error_message: str | None


class ProposalListResponse(BaseModel):
    proposals: list[ProposalResponse]
    total: int
    states: dict[str, int]  # Count by state


# Patch application

class ApplyPatchRequest(BaseModel):
    patch_path: str
    dry_run: bool = False


class ApplyPatchResponse(BaseModel):
    success: bool
    commit_sha: str | None = None
    files_changed: int = 0
    error: str | None = None
