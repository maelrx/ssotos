"""ProposalService — Proposal lifecycle management per D-26, D-27, D-28."""
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING
import yaml
import shutil

if TYPE_CHECKING:
    from services.git_service import GitService
    from services.patch_service import PatchService
    from models.proposal import Proposal, ProposalState, ProposalType, SourceDomain


class InvalidStateTransition(Exception):
    """Raised when a proposal state transition is invalid."""
    pass


class ProposalService:
    """D-26: Proposal lifecycle management.
    D-27: Proposals track all metadata.
    D-28: State machine transitions."""

    def __init__(
        self,
        git_service: "GitService",
        patch_service: "PatchService",
        exchange_path: Path = Path("workspace/exchange/proposals"),
        worktrees_path: Path = Path("workspace/runtime/worktrees")
    ):
        self.git = git_service
        self.patch = patch_service
        self.exchange_path = exchange_path
        self.worktrees_path = worktrees_path
        self.exchange_path.mkdir(parents=True, exist_ok=True)

    def create_proposal(
        self,
        proposal_id: str,
        proposal_type: "ProposalType",
        source_domain: "SourceDomain",
        target_domain: "SourceDomain",
        actor: str = "system",
        target_path: str | None = None,
        source_ref: str | None = None,
        initial_content: str | None = None
    ) -> "Proposal":
        """D-27: Create a new proposal with metadata.

        - Creates proposal branch (short-lived per D-26)
        - Creates worktree for editing
        - Saves proposal metadata
        """
        from models.proposal import Proposal as ProposalModel, ProposalState

        # Validate actor (reject 'main')
        if actor == "main":
            raise ValueError("Actor 'main' not allowed for proposals")

        # Create branch name following D-25 convention
        branch_name = f"proposal/{actor}/{proposal_id}"

        # Create worktree path
        worktree_name = f"proposal-{actor}-{proposal_id}"
        worktree_path = self.worktrees_path / worktree_name

        # Ensure worktrees directory exists
        self.worktrees_path.mkdir(parents=True, exist_ok=True)

        # Get base ref for the target domain
        base_ref = self._get_base_ref(target_domain)

        # Get the main worktree path
        main_worktree = self._get_main_worktree_path(target_domain)
        main_git = self.git.__class__(main_worktree)

        # Clone to create a separate work directory for the proposal
        # Use git clone to create a full copy that can have its own branch
        import subprocess
        subprocess.run(
            ["git", "clone", str(main_worktree.absolute()), str(worktree_path.absolute())],
            capture_output=True,
            text=True,
            check=True
        )

        # Create the proposal branch in the worktree
        wt_git = self.git.__class__(worktree_path)
        wt_git.create_branch(branch_name)

        # If initial content provided, write it
        if initial_content and target_path:
            note_path = worktree_path / target_path
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(initial_content, encoding="utf-8")
            wt_git.add(target_path)
            wt_git.commit(f"proposal: initial content for {proposal_id}")

        # Get head commit after changes
        head_commit = wt_git.rev_parse("HEAD")

        # Create proposal object
        proposal = ProposalModel(
            id=proposal_id,
            proposal_type=proposal_type,
            source_domain=source_domain,
            target_domain=target_domain,
            branch_name=branch_name,
            worktree_path=str(worktree_path),
            state=ProposalState.DRAFT,
            actor=actor,
            target_path=target_path,
            source_ref=source_ref,
            base_commit=base_ref,
            head_commit=head_commit
        )

        # Save proposal metadata
        self._save_proposal(proposal)

        return proposal

    def generate_proposal_diff(self, proposal: "Proposal") -> "DiffInfo":
        """D-30: Generate diff for a proposal.

        Diff is between the commit before the proposal changes and the current head.
        Uses the worktree's git service to compare against its own history.
        """
        from schemas.exchange import DiffInfo

        worktree_path = Path(proposal.worktree_path)
        wt_git = self.git.__class__(worktree_path)

        # Get the parent of the first commit to compare against
        # The first commit in the worktree is the baseline, HEAD~1 should be the initial state
        log = wt_git.log(max_count=2)
        if len(log) >= 2:
            base_ref = log[1]["sha"]
            head_ref = log[0]["sha"]
        else:
            # Only one commit, use HEAD~1 and HEAD
            base_ref = "HEAD~1"
            head_ref = "HEAD"

        # Use the worktree's patch service
        from services.patch_service import PatchService
        wt_patch = PatchService(wt_git)
        return wt_patch.generate_diff(base_ref, head_ref)

    def submit_for_review(self, proposal: "Proposal") -> "Proposal":
        """Transition: GENERATED -> AWAITING_REVIEW.

        Generates patch bundle and marks proposal ready for human review.
        """
        from models.proposal import ProposalState

        if not proposal.can_transition_to(ProposalState.AWAITING_REVIEW):
            raise InvalidStateTransition(
                f"Cannot transition from {proposal.state} to AWAITING_REVIEW"
            )

        # Use the worktree's git and patch services
        worktree_path = Path(proposal.worktree_path)
        wt_git = self.git.__class__(worktree_path)
        wt_patch = PatchService(wt_git)

        # Get the commit range for the proposal changes
        log = wt_git.log(max_count=2)
        if len(log) >= 2:
            base_ref = log[1]["sha"]
            head_ref = log[0]["sha"]
        else:
            base_ref = "HEAD~1"
            head_ref = "HEAD"

        # Generate patch bundle using worktree's patch service
        bundle = wt_patch.generate_patch_bundle(
            proposal.id,
            base_ref,
            head_ref
        )

        # Update proposal
        proposal.state = ProposalState.AWAITING_REVIEW
        proposal.patch_path = bundle.bundle_path
        proposal.diff_content = bundle.diff.diff_content
        proposal.updated_at = datetime.utcnow()

        self._save_proposal(proposal)
        return proposal

    def approve_proposal(
        self,
        proposal: "Proposal",
        reviewer: str = "user",
        review_note: str | None = None
    ) -> "Proposal":
        """Transition: AWAITING_REVIEW -> APPROVED.

        Marks proposal as approved by reviewer.
        """
        from models.proposal import ProposalState

        if not proposal.can_transition_to(ProposalState.APPROVED):
            raise InvalidStateTransition(
                f"Cannot transition from {proposal.state} to APPROVED"
            )

        proposal.state = ProposalState.APPROVED
        proposal.reviewed_by = reviewer
        proposal.reviewed_at = datetime.utcnow()
        proposal.review_note = review_note
        proposal.updated_at = datetime.utcnow()

        self._save_proposal(proposal)
        return proposal

    def reject_proposal(
        self,
        proposal: "Proposal",
        reason: str,
        reviewer: str = "user",
    ) -> "Proposal":
        """Transition: AWAITING_REVIEW -> REJECTED.

        Marks proposal as rejected with reason.
        """
        from models.proposal import ProposalState

        if not proposal.can_transition_to(ProposalState.REJECTED):
            raise InvalidStateTransition(
                f"Cannot transition from {proposal.state} to REJECTED"
            )

        proposal.state = ProposalState.REJECTED
        proposal.reviewed_by = reviewer
        proposal.reviewed_at = datetime.utcnow()
        proposal.review_note = reason
        proposal.updated_at = datetime.utcnow()

        self._save_proposal(proposal)
        return proposal

    def apply_proposal(self, proposal: "Proposal") -> "Proposal":
        """Transition: APPROVED -> APPLIED.

        Merges proposal branch into main using merge strategy.
        Cleans up worktree after successful merge.
        F4-06: Merge/cherry-pick works for approved proposals.
        """
        from models.proposal import ProposalState, SourceDomain

        if not proposal.can_transition_to(ProposalState.APPLIED):
            raise InvalidStateTransition(
                f"Cannot transition from {proposal.state} to APPLIED"
            )

        worktree_path = Path(proposal.worktree_path)

        # Get the main worktree path for this domain
        main_worktree_path = self._get_main_worktree_path(proposal.target_domain)
        main_git = self.git.__class__(main_worktree_path)

        # Ensure we're on main branch
        main_ref = self._get_main_branch(proposal.target_domain)
        main_git.checkout(main_ref)

        # Merge the proposal branch into main (no_ff to preserve history)
        success = main_git.merge(proposal.branch_name, no_ff=True)

        if not success:
            proposal.state = ProposalState.FAILED
            proposal.error_message = "Merge conflict"
            self._save_proposal(proposal)
            return proposal

        # Get the merge commit
        head_commit = main_git.rev_parse("HEAD")

        # Push changes to bare repo
        main_git.push("origin", main_ref)

        # Cleanup worktree
        self._cleanup_worktree(proposal)

        # Update proposal state
        proposal.state = ProposalState.APPLIED
        proposal.head_commit = head_commit
        proposal.updated_at = datetime.utcnow()

        self._save_proposal(proposal)
        return proposal

    def rollback_proposal(self, proposal: "Proposal") -> "Proposal":
        """F4-07: Rollback to previous state.

        Creates a revert commit on the proposal branch.
        """
        from models.proposal import ProposalState

        if proposal.state != ProposalState.APPLIED:
            raise ValueError("Can only rollback applied proposals")

        worktree_path = Path(proposal.worktree_path)
        worktree_git = self.git.__class__(worktree_path)

        # Create revert commit
        revert_commit = worktree_git.revert(proposal.head_commit)

        # Update proposal
        proposal.head_commit = revert_commit
        proposal.state = ProposalState.DRAFT  # Can be re-proposed
        proposal.updated_at = datetime.utcnow()

        self._save_proposal(proposal)
        return proposal

    def get_proposal(self, proposal_id: str) -> "Proposal | None":
        """Load proposal by ID."""
        proposal_file = self.exchange_path / f"{proposal_id}.yaml"
        if not proposal_file.exists():
            return None

        with open(proposal_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return self._proposal_from_dict(data)

    def list_proposals(
        self,
        state: "ProposalState | None" = None,
        target_domain: "SourceDomain | None" = None
    ) -> list["Proposal"]:
        """List proposals, optionally filtered."""
        from models.proposal import Proposal as ProposalModel

        proposals = []

        for proposal_file in self.exchange_path.glob("*.yaml"):
            with open(proposal_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            proposal = self._proposal_from_dict(data)

            if state and proposal.state != state:
                continue
            if target_domain and proposal.target_domain != target_domain:
                continue

            proposals.append(proposal)

        return sorted(proposals, key=lambda p: p.created_at, reverse=True)

    # --- Private helpers ---

    def _get_base_ref(self, domain: "SourceDomain") -> str:
        """Get the base commit ref for a domain."""
        # For now, use origin/main or main
        return "origin/main" if self.git.branch_exists(f"origin/{domain.value}") else "main"

    def _get_main_branch(self, domain: "SourceDomain") -> str:
        """Get the main branch name for a domain."""
        return "main"

    def _get_main_worktree_path(self, domain: "SourceDomain") -> Path:
        """Get the main worktree path for a domain."""
        from models.proposal import SourceDomain

        if domain == SourceDomain.USER_VAULT:
            return Path("workspace/user-vault")
        elif domain == SourceDomain.AGENT_BRAIN:
            return Path("workspace/agent-brain")
        else:
            return Path("workspace/user-vault")  # Default

    def _save_proposal(self, proposal: "Proposal") -> None:
        """Persist proposal to YAML."""
        proposal_file = self.exchange_path / f"{proposal.id}.yaml"
        with open(proposal_file, "w", encoding="utf-8") as f:
            yaml.dump(self._proposal_to_dict(proposal), f)

    def _proposal_to_dict(self, proposal: "Proposal") -> dict:
        """Serialize proposal to dict for YAML."""
        return {
            "id": proposal.id,
            "proposal_type": proposal.proposal_type.value,
            "source_domain": proposal.source_domain.value,
            "target_domain": proposal.target_domain.value,
            "branch_name": proposal.branch_name,
            "worktree_path": proposal.worktree_path,
            "state": proposal.state.value,
            "actor": proposal.actor,
            "created_at": proposal.created_at.isoformat(),
            "updated_at": proposal.updated_at.isoformat(),
            "target_path": proposal.target_path,
            "source_ref": proposal.source_ref,
            "reviewed_by": proposal.reviewed_by,
            "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
            "review_note": proposal.review_note,
            "patch_path": proposal.patch_path,
            "diff_content": proposal.diff_content,
            "base_commit": proposal.base_commit,
            "head_commit": proposal.head_commit,
            "error_message": proposal.error_message,
            "retry_count": proposal.retry_count,
        }

    def _proposal_from_dict(self, data: dict) -> "Proposal":
        """Deserialize proposal from dict."""
        from models.proposal import (
            Proposal as ProposalModel,
            ProposalType,
            ProposalState,
            SourceDomain,
        )

        return ProposalModel(
            id=data["id"],
            proposal_type=ProposalType(data["proposal_type"]),
            source_domain=SourceDomain(data["source_domain"]),
            target_domain=SourceDomain(data["target_domain"]),
            branch_name=data["branch_name"],
            worktree_path=data["worktree_path"],
            state=ProposalState(data["state"]),
            actor=data["actor"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            target_path=data.get("target_path"),
            source_ref=data.get("source_ref"),
            reviewed_by=data.get("reviewed_by"),
            reviewed_at=datetime.fromisoformat(data["reviewed_at"]) if data.get("reviewed_at") else None,
            review_note=data.get("review_note"),
            patch_path=data.get("patch_path"),
            diff_content=data.get("diff_content"),
            base_commit=data.get("base_commit"),
            head_commit=data.get("head_commit"),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
        )

    def _cleanup_worktree(self, proposal: "Proposal") -> None:
        """Remove worktree after proposal is applied."""
        worktree_path = Path(proposal.worktree_path)
        if worktree_path.exists():
            # Just remove the directory since we're using regular clones, not git worktrees
            shutil.rmtree(worktree_path)
