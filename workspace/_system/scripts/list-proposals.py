#!/usr/bin/env python3
"""List proposals from CLI.

Usage:
    python list-proposals.py [--state awaiting_review] [--domain user_vault]
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
from models.proposal import ProposalState, SourceDomain


def main():
    parser = argparse.ArgumentParser(description="List proposals")
    parser.add_argument("--state", help="Filter by state")
    parser.add_argument("--domain", help="Filter by target domain")

    args = parser.parse_args()

    git = GitService(Path("workspace/user-vault"))
    patch = PatchService(git)
    proposal_svc = ProposalService(git, patch)

    state = ProposalState(args.state) if args.state else None
    domain = SourceDomain(args.domain) if args.domain else None

    proposals = proposal_svc.list_proposals(state=state, target_domain=domain)

    print(f"Found {len(proposals)} proposal(s)\n")
    for p in proposals:
        print(f"ID: {p.id}")
        print(f"  Type: {p.proposal_type.value}")
        print(f"  State: {p.state.value}")
        print(f"  Actor: {p.actor}")
        print(f"  Branch: {p.branch_name}")
        print(f"  Target: {p.target_path or p.target_domain.value}")
        print(f"  Created: {p.created_at}")
        print()


if __name__ == "__main__":
    main()
