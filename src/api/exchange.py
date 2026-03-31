"""Exchange Zone REST API."""
from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from datetime import datetime
import uuid

from schemas.exchange import (
    CreateProposalRequest,
    ApproveProposalRequest,
    RejectProposalRequest,
    ApplyProposalRequest,
    ProposalResponse,
    ProposalListResponse,
    ReviewBundle,
    ApplyPatchRequest,
    ApplyPatchResponse,
    DiffInfo,
)
from services.git_service import GitService
from services.patch_service import PatchService
from services.proposal_service import ProposalService, InvalidStateTransition
from models.proposal import ProposalState, ProposalType, SourceDomain

router = APIRouter(prefix="/exchange", tags=["exchange"])


def get_git_service() -> GitService:
    """Get GitService for the user vault."""
    return GitService(Path("workspace/user-vault"))


def get_patch_service(git: GitService = Depends(get_git_service)) -> PatchService:
    """Get PatchService."""
    return PatchService(git)


def get_proposal_service(
    git: GitService = Depends(get_git_service),
    patch: PatchService = Depends(get_patch_service)
) -> ProposalService:
    """Get ProposalService."""
    return ProposalService(git, patch)


@router.post("/proposals", response_model=ProposalResponse)
async def create_proposal(
    request: CreateProposalRequest,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Create a new proposal.

    Creates a worktree and branch for the proposal.
    If content is provided, writes it to the target path.
    """
    try:
        proposal = svc.create_proposal(
            proposal_id=str(uuid.uuid4())[:8],
            proposal_type=ProposalType(request.proposal_type),
            source_domain=SourceDomain(request.source_domain),
            target_domain=SourceDomain(request.target_domain),
            actor=request.actor,
            target_path=request.target_path,
            source_ref=request.source_ref,
            initial_content=request.content
        )
        return _proposal_to_response(proposal)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposals", response_model=ProposalListResponse)
async def list_proposals(
    state: str | None = None,
    target_domain: str | None = None,
    svc: ProposalService = Depends(get_proposal_service)
):
    """List all proposals, optionally filtered by state or target_domain."""
    state_enum = ProposalState(state) if state else None
    domain_enum = SourceDomain(target_domain) if target_domain else None

    proposals = svc.list_proposals(state=state_enum, target_domain=domain_enum)

    # Count by state
    states = {}
    for p in proposals:
        state_key = p.state.value
        states[state_key] = states.get(state_key, 0) + 1

    return ProposalListResponse(
        proposals=[_proposal_to_response(p) for p in proposals],
        total=len(proposals),
        states=states
    )


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Get a specific proposal by ID."""
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return _proposal_to_response(proposal)


@router.get("/proposals/{proposal_id}/review", response_model=ReviewBundle)
async def get_proposal_review(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service),
    git: GitService = Depends(get_git_service)
):
    """Get review bundle for a proposal with diff and provenance."""
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    patch_svc = PatchService(git)
    bundle = patch_svc.create_review_bundle(proposal, git)
    return bundle


@router.post("/proposals/{proposal_id}/submit", response_model=ProposalResponse)
async def submit_proposal_for_review(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Submit proposal for review.

    Transitions: DRAFT -> GENERATED -> AWAITING_REVIEW
    Generates patch bundle.
    """
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        # First transition to GENERATED if in DRAFT
        if proposal.state == ProposalState.DRAFT:
            proposal.state = ProposalState.GENERATED
        proposal = svc.submit_for_review(proposal)
        return _proposal_to_response(proposal)
    except InvalidStateTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/approve", response_model=ProposalResponse)
async def approve_proposal(
    proposal_id: str,
    request: ApproveProposalRequest,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Approve a proposal.

    Transitions: AWAITING_REVIEW -> APPROVED
    """
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        proposal = svc.approve_proposal(
            proposal,
            reviewer=request.reviewed_by or "user",
            review_note=request.review_note
        )
        return _proposal_to_response(proposal)
    except InvalidStateTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/reject", response_model=ProposalResponse)
async def reject_proposal(
    proposal_id: str,
    request: RejectProposalRequest,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Reject a proposal.

    Transitions: AWAITING_REVIEW -> REJECTED
    """
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        proposal = svc.reject_proposal(
            proposal,
            reason=request.reason,
            reviewer="user"
        )
        return _proposal_to_response(proposal)
    except InvalidStateTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/apply", response_model=ProposalResponse)
async def apply_proposal(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Apply an approved proposal.

    Transitions: APPROVED -> APPLIED
    Merges proposal into main, cleans up worktree.
    """
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        proposal = svc.apply_proposal(proposal)
        return _proposal_to_response(proposal)
    except InvalidStateTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/rollback", response_model=ProposalResponse)
async def rollback_proposal(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Rollback an applied proposal.

    Creates a revert commit.
    """
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        proposal = svc.rollback_proposal(proposal)
        return _proposal_to_response(proposal)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/patches/apply", response_model=ApplyPatchResponse)
async def apply_patch(
    request: ApplyPatchRequest,
    git: GitService = Depends(get_git_service)
):
    """Apply a patch bundle."""
    patch_svc = PatchService(git)

    try:
        result = patch_svc.apply_patch_bundle(
            Path(request.patch_path),
            dry_run=request.dry_run
        )
        return ApplyPatchResponse(
            success=result.success,
            commit_sha=result.commit_sha,
            files_changed=result.files_changed,
            error=result.error
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/domains/{domain}/diff", response_model=DiffInfo)
async def get_domain_diff(
    domain: str,
    ref_a: str = "HEAD~1",
    ref_b: str = "HEAD",
    git: GitService = Depends(get_git_service)
):
    """Get diff for a domain between two refs."""
    patch_svc = PatchService(git)
    try:
        diff = patch_svc.generate_diff(ref_a, ref_b)
        return diff
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Helper functions ---

def _proposal_to_response(proposal) -> ProposalResponse:
    """Convert Proposal model to API response."""
    return ProposalResponse(
        id=proposal.id,
        proposal_type=proposal.proposal_type.value,
        source_domain=proposal.source_domain.value,
        target_domain=proposal.target_domain.value,
        branch_name=proposal.branch_name,
        worktree_path=proposal.worktree_path,
        state=proposal.state.value,
        actor=proposal.actor,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
        target_path=proposal.target_path,
        source_ref=proposal.source_ref,
        reviewed_by=proposal.reviewed_by,
        reviewed_at=proposal.reviewed_at,
        review_note=proposal.review_note,
        patch_path=proposal.patch_path,
        base_commit=proposal.base_commit,
        head_commit=proposal.head_commit,
        error_message=proposal.error_message
    )
