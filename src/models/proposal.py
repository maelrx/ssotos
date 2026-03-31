"""Proposal data model per D-27 and D-28."""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


class ProposalState(Enum):
    """D-28: Proposal state machine."""
    DRAFT = "draft"                     # Initial state, changes being prepared
    GENERATED = "generated"             # Diff/patch generated, ready for review
    AWAITING_REVIEW = "awaiting_review" # Submitted for approval
    APPROVED = "approved"               # User/system approved
    REJECTED = "rejected"               # User/system rejected
    APPLIED = "applied"                 # Successfully merged to main
    SUPERSEDED = "superseded"           # Another proposal replaced this
    FAILED = "failed"                   # Application failed


class ProposalType(Enum):
    """Type of mutation being proposed."""
    NOTE_CREATE = "note_create"          # New note creation
    NOTE_EDIT = "note_edit"              # Edit to existing note
    NOTE_DELETE = "note_delete"          # Note deletion
    NOTE_MOVE = "note_move"              # Note moved/renamed
    STRUCTURE_CHANGE = "structure_change"  # Folder structure change
    RESEARCH_INGEST = "research_ingest"  # Research output ingestion
    TEMPLATE_APPLY = "template_apply"     # Template instantiation


class SourceDomain(Enum):
    """D-27: Source and target domain classification."""
    USER_VAULT = "user_vault"
    AGENT_BRAIN = "agent_brain"
    RESEARCH = "research"
    IMPORT = "import"


@dataclass
class Proposal:
    """D-27: Proposal with full metadata tracking."""

    # Identity
    id: str                              # Stable UUID
    proposal_type: ProposalType
    source_domain: SourceDomain
    target_domain: SourceDomain          # Where change will be applied

    # Git tracking (D-27)
    branch_name: str                    # e.g., "proposal/agent/001"
    worktree_path: str                   # Absolute path to worktree

    # State machine (D-28)
    state: ProposalState = ProposalState.DRAFT

    # Provenance
    actor: str = "system"               # Who/what created this proposal
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Content tracking
    target_path: str | None = None      # Note path being changed
    source_ref: str | None = None       # For research/import proposals

    # Review tracking
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None

    # Patch tracking
    patch_path: str | None = None       # Path to patch bundle
    diff_content: str | None = None      # Cached diff output
    base_commit: str | None = None       # Commit before proposal changes
    head_commit: str | None = None      # Commit with proposal changes

    # Error tracking
    error_message: str | None = None
    retry_count: int = 0

    def can_transition_to(self, new_state: ProposalState) -> bool:
        """D-28: Validate state transitions."""
        valid_transitions = {
            ProposalState.DRAFT: [ProposalState.GENERATED, ProposalState.FAILED],
            ProposalState.GENERATED: [ProposalState.AWAITING_REVIEW, ProposalState.FAILED],
            ProposalState.AWAITING_REVIEW: [ProposalState.APPROVED, ProposalState.REJECTED, ProposalState.FAILED],
            ProposalState.APPROVED: [ProposalState.APPLIED, ProposalState.SUPERSEDED, ProposalState.FAILED],
            ProposalState.REJECTED: [ProposalState.DRAFT],  # Can resubmit
            ProposalState.APPLIED: [],
            ProposalState.SUPERSEDED: [],
            ProposalState.FAILED: [ProposalState.DRAFT],  # Can retry
        }
        return new_state in valid_transitions.get(self.state, [])
