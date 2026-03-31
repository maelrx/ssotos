"""PatchService — Diff and patch generation per D-29, D-30, D-31."""
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.events import emit, EventType

if TYPE_CHECKING:
    from src.services.git_service import GitService
    from src.models.proposal import Proposal


@dataclass
class ApplyResult:
    """Result of patch application."""
    success: bool
    commit_sha: str | None = None
    files_changed: int = 0
    error: str | None = None
    dry_run: bool = False


class PatchService:
    """D-29: Patch-first mutation model.
    D-30: Diff generated for any note change with readable output.
    D-31: Patch bundles are self-contained and apply cleanly to main."""

    def __init__(self, git_service: "GitService"):
        self.git = git_service

    def generate_diff(
        self,
        base_ref: str,
        head_ref: str,
        file_filter: str | None = None
    ) -> "DiffInfo":
        """D-30: Generate readable diff between two refs.

        Returns DiffInfo with files_changed, insertions, deletions, diff_content.
        """
        from schemas.exchange import DiffInfo

        diff_output = self.git.diff(base_ref, head_ref, file=file_filter)
        stat = self.git.diff_stat(base_ref, head_ref)

        return DiffInfo(
            files_changed=stat["files_changed"],
            insertions=stat["insertions"],
            deletions=stat["deletions"],
            diff_content=diff_output
        )

    def generate_patch_bundle(
        self,
        proposal_id: str,
        base_ref: str,
        head_ref: str,
        output_dir: Path | None = None
    ) -> "PatchBundle":
        """D-29, D-31: Create a self-contained patch bundle.

        Bundle includes:
        - Unified diff file
        - Metadata YAML
        - Provenance info
        """
        from schemas.exchange import PatchBundle

        if output_dir is None:
            output_dir = Path("workspace/exchange/patches")

        output_dir.mkdir(parents=True, exist_ok=True)
        bundle_dir = output_dir / proposal_id
        bundle_dir.mkdir(parents=True, exist_ok=True)

        # Generate patch file
        patch_content = self.git.generate_patch(base_ref, head_ref) or ""
        patch_path = bundle_dir / "changes.patch"
        patch_path.write_text(patch_content, encoding="utf-8")

        # Generate diff info
        diff_info = self.generate_diff(base_ref, head_ref)

        # Generate metadata
        metadata = {
            "proposal_id": proposal_id,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "created_at": datetime.utcnow().isoformat(),
            "files_changed": diff_info.files_changed,
            "insertions": diff_info.insertions,
            "deletions": diff_info.deletions,
            "self_contained": True
        }
        metadata_path = bundle_dir / "metadata.yaml"
        import yaml
        metadata_path.write_text(yaml.dump(metadata), encoding="utf-8")

        # Generate provenance
        provenance = {
            "generated_by": "PatchService",
            "git_diff": f"{base_ref}..{head_ref}",
            "bundle_path": str(bundle_dir)
        }
        provenance_path = bundle_dir / "provenance.yaml"
        provenance_path.write_text(yaml.dump(provenance), encoding="utf-8")

        bundle = PatchBundle(
            proposal_id=proposal_id,
            bundle_path=str(bundle_dir),
            diff=diff_info,
            created_at=datetime.utcnow(),
            self_contained=True
        )

        emit(EventType.PATCH_BUNDLE_CREATED, domain=proposal_id, metadata={
            "proposal_id": proposal_id,
            "files_changed": diff_info.files_changed,
            "insertions": diff_info.insertions,
            "deletions": diff_info.deletions
        })
        return bundle

    def apply_patch_bundle(
        self,
        bundle_path: Path,
        dry_run: bool = False
    ) -> ApplyResult:
        """Apply a self-contained patch bundle.

        Returns ApplyResult with success, commit_sha, files_changed, error.
        """
        patch_file = bundle_path / "changes.patch"
        if not patch_file.exists():
            return ApplyResult(
                success=False,
                error=f"Patch file not found: {patch_file}"
            )

        # Apply the patch
        if dry_run:
            success = self.git.apply_patch(patch_file, dry_run=True)
            if not success:
                return ApplyResult(success=False, error="Patch would not apply cleanly")
            return ApplyResult(success=True, dry_run=True)

        success = self.git.apply_patch(patch_file, dry_run=False)
        if not success:
            return ApplyResult(success=False, error="Patch did not apply cleanly")

        # Get commit info
        log = self.git.log(max_count=1)
        commit_sha = log[0]["sha"] if log else None

        return ApplyResult(
            success=True,
            commit_sha=commit_sha,
            files_changed=len(self.git.status().get("changed", []))
        )

    def create_review_bundle(
        self,
        proposal: "Proposal",
        git_service: "GitService"
    ) -> "ReviewBundle":
        """D-28: Create a review bundle with diff and provenance.

        This is what the user sees when reviewing a proposal.
        """
        from schemas.exchange import ReviewBundle
        from models.proposal import ProposalState

        # Get diff between main and proposal branch
        main_ref = "main"
        branch_ref = proposal.branch_name

        # Check if origin/main exists, fallback to main
        base_ref = f"origin/{main_ref}" if git_service.branch_exists(f"origin/{main_ref}") else main_ref

        diff_info = self.generate_diff(
            base_ref,
            branch_ref
        )

        # Build provenance
        provenance = {
            "proposal_id": proposal.id,
            "proposal_type": proposal.proposal_type.value,
            "actor": proposal.actor,
            "source_domain": proposal.source_domain.value,
            "target_domain": proposal.target_domain.value,
            "created_at": proposal.created_at.isoformat(),
            "branch": proposal.branch_name,
            "worktree": proposal.worktree_path,
            "base_commit": proposal.base_commit,
            "head_commit": proposal.head_commit
        }

        # Determine what actions are available
        can_apply = proposal.state == ProposalState.APPROVED
        can_reject = proposal.state == ProposalState.AWAITING_REVIEW

        return ReviewBundle(
            proposal_id=proposal.id,
            proposal_type=proposal.proposal_type.value,
            state=proposal.state.value,
            actor=proposal.actor,
            created_at=proposal.created_at,
            target_domain=proposal.target_domain.value,
            target_path=proposal.target_path,
            source_ref=proposal.source_ref,
            diff=diff_info,
            provenance=provenance,
            can_apply=can_apply,
            can_reject=can_reject
        )
