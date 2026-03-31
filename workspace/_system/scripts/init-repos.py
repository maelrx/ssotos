#!/usr/bin/env python3
"""Initialize user-vault.git and agent-brain.git bare repositories.

Per D-22: Two separate Git repos for user vault and agent brain.

This script handles both new repositories and existing workspace directories
that need to be connected to their bare repositories.
"""
import sys
import subprocess
from pathlib import Path

# Add src to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.git_service import GitService


def init_git_repo(worktree_path: Path, bare_repo: Path, readme_content: str | None = None) -> None:
    """Initialize a worktree directory with git and connect to bare repo."""
    if (worktree_path / ".git").exists():
        print(f"  {worktree_path} already has .git, skipping")
        return

    svc = GitService(worktree_path)
    svc.init(bare=False)
    print(f"  Initialized git in {worktree_path}")

    if readme_content:
        readme = worktree_path / "README.md"
        if not readme.exists():
            readme.write_text(readme_content)
            svc.add("README.md")
            svc.commit("Initial commit")

    # Add all existing files and commit
    subprocess.run(["git", "-C", str(worktree_path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(worktree_path), "commit", "-m", "Initial commit"], check=True)

    # Push to bare repo
    subprocess.run(["git", "-C", str(worktree_path), "remote", "add", "origin", str(bare_repo)], check=False)
    subprocess.run(["git", "-C", str(worktree_path), "branch", "-m", "master", "main"], check=True)
    subprocess.run(["git", "-C", str(worktree_path), "push", "-u", "origin", "main"], check=True)
    subprocess.run(["git", "-C", str(bare_repo), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
    print(f"  Connected {worktree_path} to {bare_repo}")


def main():
    workspace_root = Path(__file__).parent.parent.parent / "workspace"
    repos_dir = workspace_root / "repos"
    repos_dir.mkdir(exist_ok=True)

    # Create exchange directories
    (workspace_root / "exchange" / "proposals").mkdir(parents=True, exist_ok=True)
    (workspace_root / "exchange" / "reviews").mkdir(parents=True, exist_ok=True)
    (workspace_root / "exchange" / "research").mkdir(parents=True, exist_ok=True)
    (workspace_root / "runtime" / "worktrees").mkdir(parents=True, exist_ok=True)

    # Initialize user-vault.git
    vault_repo = repos_dir / "user-vault.git"
    if not vault_repo.exists():
        GitService(vault_repo, bare=True).init()
        print(f"Initialized: {vault_repo}")
    else:
        print(f"Already exists: {vault_repo}")

    # Initialize agent-brain.git
    brain_repo = repos_dir / "agent-brain.git"
    if not brain_repo.exists():
        GitService(brain_repo, bare=True).init()
        print(f"Initialized: {brain_repo}")
    else:
        print(f"Already exists: {brain_repo}")

    # Handle existing user-vault directory
    vault_worktree = workspace_root / "user-vault"
    print(f"Setting up user-vault...")
    init_git_repo(
        vault_worktree,
        vault_repo,
        "# User Vault\n\nCanonical user knowledge repository.\n"
    )

    # Handle existing agent-brain directory
    brain_worktree = workspace_root / "agent-brain"
    print(f"Setting up agent-brain...")
    init_git_repo(
        brain_worktree,
        brain_repo,
        "# Agent Brain\n\nAgent operational memory.\n"
    )

    print("Repository initialization complete.")
    print(f"user-vault.git: {vault_repo}")
    print(f"agent-brain.git: {brain_repo}")


if __name__ == "__main__":
    main()
