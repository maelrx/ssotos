#!/usr/bin/env python3
"""Create a new proposal from CLI.

Usage:
    python create-proposal.py --actor agent --type NOTE_CREATE --path '02-Projects/Test.md' --content '...'
"""
import argparse
import sys
from pathlib import Path

# Navigate from workspace/_system/scripts/ to project root
# 3 levels up gets us to project root, then add src
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from services.git_service import GitService
from services.patch_service import PatchService
from services.proposal_service import ProposalService
from models.proposal import ProposalType, SourceDomain


def main():
    parser = argparse.ArgumentParser(description="Create a new proposal")
    parser.add_argument("--actor", required=True, help="Actor creating the proposal")
    parser.add_argument(
        "--type",
        required=True,
        choices=["NOTE_CREATE", "NOTE_EDIT", "NOTE_DELETE", "NOTE_MOVE", "STRUCTURE_CHANGE", "RESEARCH_INGEST", "TEMPLATE_APPLY"]
    )
    parser.add_argument("--target-path", help="Target note path")
    parser.add_argument("--content", help="Initial content")
    parser.add_argument(
        "--source-domain",
        default="agent_brain",
        choices=["user_vault", "agent_brain", "research", "import"]
    )
    parser.add_argument(
        "--target-domain",
        default="user_vault",
        choices=["user_vault", "agent_brain", "research", "import"]
    )

    args = parser.parse_args()

    # Setup services
    git = GitService(Path("workspace/user-vault"))
    patch = PatchService(git)
    proposal_svc = ProposalService(git, patch)

    # Create proposal
    import uuid
    proposal_id = str(uuid.uuid4())[:8]

    proposal = proposal_svc.create_proposal(
        proposal_id=proposal_id,
        proposal_type=ProposalType(args.type),
        source_domain=SourceDomain(args.source_domain),
        target_domain=SourceDomain(args.target_domain),
        actor=args.actor,
        target_path=args.target_path,
        initial_content=args.content
    )

    print(f"Created proposal: {proposal.id}")
    print(f"Branch: {proposal.branch_name}")
    print(f"Worktree: {proposal.worktree_path}")
    print(f"State: {proposal.state.value}")
    print(f"\nTo edit the proposal, work in: {proposal.worktree_path}")


if __name__ == "__main__":
    main()
