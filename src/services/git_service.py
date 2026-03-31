"""GitService — Encapsulates all Git CLI operations per D-21."""
import subprocess
import shutil
from pathlib import Path
from typing import Literal

from src.core.events import emit, EventType
from src.core.policy.service import PolicyService, PolicyDeniedException
from src.core.policy.models import PolicyRequest
from src.core.policy.enums import CapabilityGroup, CapabilityAction, Domain


class GitError(Exception):
    """Raised when a Git command fails."""

    def __init__(self, cmd: list[str], returncode: int, stderr: str):
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"Git command failed: {' '.join(cmd)}\n{stderr}")


class GitService:
    """Encapsulates all Git CLI operations per D-21.

    All Git operations flow through this service — no subprocess calls
    should appear outside this class.
    """

    def __init__(self, repo_path: Path, bare: bool = False):
        self.repo_path = Path(repo_path)
        self.bare = bare
        self.policy = PolicyService()

    def _git_cmd(self, *args: str, capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Execute a git command with proper environment."""
        cmd = ["git"]

        # Add git-dir and work-tree for bare repos
        if self.bare:
            cmd.extend(["--git-dir", str(self.repo_path)])
        else:
            cmd.extend(["--git-dir", str(self.repo_path / ".git") if (self.repo_path / ".git").exists() else str(self.repo_path)])
            cmd.extend(["--work-tree", str(self.repo_path)])

        cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace"
        )

        if check and result.returncode != 0:
            raise GitError(cmd, result.returncode, result.stderr)

        return result

    def _git_cmd_no_check(self, *args: str, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Execute a git command without checking return code."""
        return self._git_cmd(*args, capture_output=capture_output, check=False)

    # --- Repository Lifecycle ---

    def init(self, bare: bool = True) -> None:
        """Initialize a new bare repository.

        For user-vault.git and agent-brain.git: bare=True
        For worktrees: bare=False
        """
        if bare:
            self._git_cmd("init", "--bare")
        else:
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self._git_cmd("init")

        emit(EventType.GIT_REPO_INITIALIZED, domain=str(self.repo_path))

    def clone(self, source: Path, target: Path, bare: bool = False) -> None:
        """Clone a repository to a new location."""
        target_path = Path(target)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if bare:
            subprocess.run(
                ["git", "clone", "--bare", str(source), str(target)],
                capture_output=True,
                text=True,
                check=True
            )
        else:
            subprocess.run(
                ["git", "clone", str(source), str(target)],
                capture_output=True,
                text=True,
                check=True
            )

    def is_repo(self) -> bool:
        """Check if path is a valid git repository."""
        if self.bare:
            result = self._git_cmd_no_check("rev-parse", "--git-dir")
        else:
            result = self._git_cmd_no_check("rev-parse", "--is-inside-work-tree")
        return result.returncode == 0

    # --- Branch Operations (D-25 naming convention) ---

    BRANCH_NAMING_PATTERNS = {
        "proposal": r"^proposal/[^/]+/[^/]+$",
        "research": r"^research/[^/]+$",
        "import": r"^import/[^/]+/[^/]+$",
        "review": r"^review/[^/]+$",
    }

    def get_current_branch(self) -> str:
        """Get current branch name."""
        result = self._git_cmd("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip()

    def list_branches(self, pattern: str | None = None) -> list[str]:
        """List branches, optionally filtered by pattern."""
        args = ["branch", "--format=%(refname:short)"]
        if pattern:
            args.append(pattern)
        result = self._git_cmd(*args)
        branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
        return branches

    def create_branch(self, name: str, start_point: str = "HEAD") -> None:
        """Create a new branch.

        Name must follow D-25 convention:
        - proposal/<actor>/<id>
        - research/<job-id>
        - import/<source>/<ts>
        - review/<id>
        """
        # Policy check before creating branch
        policy_request = PolicyRequest(
            actor=start_point,
            capability_group=CapabilityGroup.EXCHANGE,
            action=CapabilityAction.CREATE,
            domain=Domain.EXCHANGE,
            path=None,
            note_type=None,
            sensitivity=0
        )
        self.policy.check_or_raise(policy_request)

        # Validate naming convention
        if name in ("main", "master"):
            raise GitError(
                ["git", "branch", name],
                1,
                f"Cannot create branch with reserved name: {name}"
            )

        # Check if name matches any allowed pattern
        import re
        valid = any(re.match(pattern, name) for pattern in self.BRANCH_NAMING_PATTERNS.values())
        if not valid:
            raise GitError(
                ["git", "branch", name],
                1,
                f"Branch name '{name}' does not follow D-25 naming convention. "
                f"Expected: proposal/<actor>/<id>, research/<job-id>, "
                f"import/<source>/<ts>, or review/<id>"
            )

        self._git_cmd("branch", name, start_point)
        emit(EventType.GIT_BRANCH_CREATED, actor=start_point, domain=name)

    def delete_branch(self, name: str) -> None:
        """Delete a branch (safe — won't delete main)."""
        # Policy check before deleting branch
        policy_request = PolicyRequest(
            actor="system",
            capability_group=CapabilityGroup.EXCHANGE,
            action=CapabilityAction.DELETE,
            domain=Domain.EXCHANGE,
            path=None,
            note_type=None,
            sensitivity=0
        )
        self.policy.check_or_raise(policy_request)

        if name in ("main", "master"):
            raise GitError(
                ["git", "branch", "-d", name],
                1,
                "Cannot delete protected branch: main"
            )
        self._git_cmd("branch", "-d", name)
        emit(EventType.GIT_BRANCH_DELETED, domain=name)

    def branch_exists(self, name: str) -> bool:
        """Check if branch exists."""
        result = self._git_cmd_no_check("rev-parse", "--verify", f"refs/heads/{name}")
        return result.returncode == 0

    def checkout(self, ref: str) -> None:
        """Checkout a branch or commit."""
        self._git_cmd("checkout", ref)

    # --- Worktree Operations (D-23) ---

    def _find_git_dir(self) -> Path:
        """Find the actual git directory.

        For bare repos: returns self.repo_path
        For worktrees: returns the path stored in .git file
        """
        if self.bare:
            return self.repo_path

        git_file = self.repo_path / ".git"
        if git_file.exists() and git_file.is_file():
            # Worktree: .git is a file pointing to the actual git dir
            content = git_file.read_text().strip()
            if content.startswith("gitdir: "):
                return Path(content[len("gitdir: "):])

        return self.repo_path

    def create_worktree(self, path: Path, branch: str, create_branch: bool = False) -> None:
        """Create a new worktree.

        - path: where the worktree checkout lives
        - branch: branch to check out in this worktree
        - create_branch: if True, create new branch at path

        Worktrees are how proposals edit content — not direct branch checkout.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Get the actual git directory (bare repo for worktrees)
        git_dir = self._find_git_dir()

        if create_branch:
            subprocess.run(
                ["git", "-C", str(git_dir), "worktree", "add", "-b", branch, str(path)],
                capture_output=True,
                text=True,
                check=True
            )
        else:
            subprocess.run(
                ["git", "-C", str(git_dir), "worktree", "add", str(path), branch],
                capture_output=True,
                text=True,
                check=True
            )

        emit(EventType.GIT_WORKTREE_CREATED, domain=branch, metadata={"path": str(path)})

    def list_worktrees(self) -> list[dict]:
        """List all worktrees. Returns list of {path, branch, head}."""
        result = self._git_cmd("worktree", "list", "--porcelain")
        lines = result.stdout.strip().split("\n")

        worktrees = []
        current = {}
        for line in lines:
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line[len("worktree "):].strip()}
            elif line.startswith("branch "):
                current["branch"] = line[len("branch "):].strip()
            elif line.startswith("head "):
                current["head"] = line[len("head "):].strip()

        if current:
            worktrees.append(current)

        return worktrees

    def remove_worktree(self, path: Path, force: bool = False) -> None:
        """Remove a worktree. Must be clean (or force=True)."""
        # Policy check before removing worktree
        policy_request = PolicyRequest(
            actor="system",
            capability_group=CapabilityGroup.EXCHANGE,
            action=CapabilityAction.DELETE,
            domain=Domain.EXCHANGE,
            path=str(path),
            note_type=None,
            sensitivity=0
        )
        self.policy.check_or_raise(policy_request)

        path = Path(path)
        if force:
            self._git_cmd("worktree", "remove", "--force", str(path))
        else:
            self._git_cmd("worktree", "remove", str(path))

        emit(EventType.GIT_WORKTREE_REMOVED, domain=str(path))

    def worktree_path_for_branch(self, branch: str) -> Path | None:
        """Find the worktree path for a given branch."""
        worktrees = self.list_worktrees()
        for wt in worktrees:
            if wt.get("branch") == branch:
                return Path(wt["path"])
        return None

    # --- Diff Operations (D-30) ---

    def diff(self, ref_a: str | None, ref_b: str | None, file: str | None = None) -> str:
        """Generate diff between two refs, or working tree vs staging, or single file.

        Returns readable diff output (unified format).
        ref_a and ref_b can be: branch name, commit SHA, HEAD~1, etc.
        If file is specified, diff only that file.
        """
        args = ["diff", "--unified=3"]
        if ref_a:
            args.append(ref_a)
        if ref_b:
            args.append(ref_b)
        if file:
            args.append("--")
            args.append(file)

        result = self._git_cmd(*args)
        return result.stdout

    def diff_stat(self, ref_a: str | None, ref_b: str | None) -> dict:
        """Return diff statistics: files changed, insertions, deletions."""
        args = ["diff", "--stat"]
        if ref_a:
            args.append(ref_a)
        if ref_b:
            args.append(ref_b)

        result = self._git_cmd(*args)
        stat_output = result.stdout.strip()
        lines = stat_output.split("\n")

        # Parse stat output - can have format like:
        # "  file1.txt | 3 +++\n  1 file changed, 3 insertions(+)"
        # or
        # "  file1.txt | 5 ++--\n  2 files changed, 3 insertions(+), 2 deletions(-)"
        files_changed = 0
        insertions = 0
        deletions = 0

        # Find the summary line (contains "file changed")
        summary_line = ""
        for line in lines:
            if "file changed" in line.lower():
                summary_line = line
                break

        if summary_line:
            # Parse "X file(s) changed, Y insertion(s)(+), Z deletion(s)(-)"
            for part in summary_line.split(","):
                part = part.strip()
                if "file" in part.lower() and "changed" in part.lower():
                    files_changed = int(part.split()[0])
                elif "insertion" in part.lower():
                    insertions = int(part.split()[0])
                elif "deletion" in part.lower():
                    deletions = int(part.split()[0])

        return {
            "files_changed": files_changed,
            "insertions": insertions,
            "deletions": deletions
        }

    # --- Patch Operations (D-29, D-31) ---

    def generate_patch(self, ref_a: str, ref_b: str, output: Path | None = None) -> str:
        """Generate a patch file (unified diff format).

        If output is None, returns patch as string.
        Patch is self-contained per D-31 — applies cleanly to main.
        """
        # Use diff to generate unified patch format
        result = self._git_cmd("diff", "--unified=3", ref_a, ref_b)

        if output:
            Path(output).write_text(result.stdout)

        return result.stdout

    def apply_patch(self, patch_path: Path, dry_run: bool = False) -> bool:
        """Apply a patch file. Returns True on success.

        If dry_run=True, validates patch without applying.
        """
        # Policy check before applying patch
        policy_request = PolicyRequest(
            actor="system",
            capability_group=CapabilityGroup.EXCHANGE,
            action=CapabilityAction.UPDATE,
            domain=Domain.EXCHANGE,
            path=str(patch_path),
            note_type=None,
            sensitivity=0
        )
        self.policy.check_or_raise(policy_request)

        patch_path = Path(patch_path)
        if dry_run:
            result = self._git_cmd_no_check("apply", "--check", str(patch_path))
        else:
            result = self._git_cmd_no_check("apply", str(patch_path))

        if result.returncode == 0:
            emit(EventType.GIT_PATCH_APPLIED, domain=str(patch_path))
        return result.returncode == 0

    def format_patch(self, ref_a: str, ref_b: str, output_dir: Path) -> list[Path]:
        """Generate individual patch files per commit in range.

        Returns list of created patch file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = self._git_cmd(
            "format-patch",
            "--unified=3",
            f"{ref_a}..{ref_b}",
            "-o", str(output_dir)
        )

        patch_files = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                patch_files.append(Path(line.strip()))

        return patch_files

    # --- Commit Operations ---

    def add(self, paths: list[Path] | str = ".") -> None:
        """Stage files for commit."""
        if isinstance(paths, str):
            paths = [Path(paths)]
        paths_str = [str(p) for p in paths]
        self._git_cmd("add", *paths_str)

    def commit(self, message: str, author: str | None = None) -> str:
        """Create a commit. Returns commit SHA."""
        args = ["commit", "-m", message]
        if author:
            args.extend(["--author", author])

        self._git_cmd(*args)
        result = self._git_cmd("rev-parse", "HEAD")
        sha = result.stdout.strip()
        emit(EventType.GIT_COMMIT_CREATED, actor=author or "system", metadata={"sha": sha, "message": message})
        return sha

    def log(self, max_count: int = 10, branch: str | None = None) -> list[dict]:
        """Get commit log. Returns list of {sha, message, author, date}."""
        args = ["log", f"-{max_count}", "--format=%H%n%s%n%an%n%ad%n---", "--date=iso"]
        if branch:
            args.append(branch)

        result = self._git_cmd(*args)
        commits = []
        entries = result.stdout.strip().split("---\n")

        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 4:
                commits.append({
                    "sha": lines[0].strip(),
                    "message": lines[1].strip(),
                    "author": lines[2].strip(),
                    "date": lines[3].strip()
                })

        return commits

    def status(self) -> dict:
        """Get working tree status."""
        result = self._git_cmd("status", "--porcelain")
        lines = result.stdout.strip().split("\n")

        changed = []
        staged = []
        untracked = []

        for line in lines:
            if not line.strip():
                continue
            status = line[:2]
            path = line[3:]

            if status[0] in ("M", "A", "D"):
                staged.append(path)
            if status[1] == "M":
                changed.append(path)
            if status == "??":
                untracked.append(path)

        return {
            "changed": changed,
            "staged": staged,
            "untracked": untracked
        }

    # --- Merge/Cherry-pick (F4-06) ---

    def merge(self, branch: str, no_ff: bool = True) -> bool:
        """Merge branch into current branch.

        Returns True on clean merge, False on conflicts.
        """
        # Policy check before merge
        policy_request = PolicyRequest(
            actor="system",
            capability_group=CapabilityGroup.EXCHANGE,
            action=CapabilityAction.UPDATE,
            domain=Domain.EXCHANGE,
            path=None,
            note_type=None,
            sensitivity=0
        )
        self.policy.check_or_raise(policy_request)

        args = ["merge"]
        if no_ff:
            args.append("--no-ff")
        args.append(branch)

        result = self._git_cmd_no_check(*args)
        if result.returncode == 0:
            emit(EventType.GIT_MERGE_COMPLETED, domain=branch)
        return result.returncode == 0

    def cherry_pick(self, commit: str) -> bool:
        """Cherry-pick a commit onto current branch.

        Returns True on success, False on conflicts.
        """
        result = self._git_cmd_no_check("cherry-pick", commit)
        return result.returncode == 0

    def rebase(self, onto: str) -> bool:
        """Rebase current branch onto onto.

        Returns True on success, False on conflicts.
        """
        result = self._git_cmd_no_check("rebase", onto)
        return result.returncode == 0

    # --- Rollback (F4-07) ---

    def revert(self, ref: str) -> str:
        """Create a new commit that reverts the given ref.

        Returns the new commit SHA.
        """
        self._git_cmd("revert", "--no-edit", ref)
        result = self._git_cmd("rev-parse", "HEAD")
        sha = result.stdout.strip()
        emit(EventType.GIT_COMMIT_CREATED, actor="revert", metadata={"reverted_ref": ref, "sha": sha})
        return sha

    def reset(self, ref: str, hard: bool = False) -> None:
        """Reset HEAD to ref. If hard=True, also reset working tree.

        WARNING: hard reset destroys uncommitted changes.
        """
        args = ["reset"]
        if hard:
            args.append("--hard")
        args.append(ref)

        self._git_cmd(*args)

    def restore(self, paths: list[Path], source: str = "HEAD") -> None:
        """Restore specific files to state at source."""
        paths_str = [str(p) for p in paths]
        self._git_cmd("restore", "--source", source, *paths_str)

    # --- Revision Navigation ---

    def rev_parse(self, ref: str) -> str:
        """Resolve ref to commit SHA."""
        result = self._git_cmd("rev-parse", ref)
        return result.stdout.strip()

    def show(self, ref: str, file: str | None = None) -> str:
        """Show object or file at ref."""
        if file:
            result = self._git_cmd("show", f"{ref}:{file}")
        else:
            result = self._git_cmd("show", ref)
        return result.stdout

    def ls_files(self, ref: str | None = None) -> list[str]:
        """List files in index or at specific ref."""
        if ref:
            result = self._git_cmd("ls-tree", "-r", "--name-only", ref)
        else:
            result = self._git_cmd("ls-files")
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

    def cat_file(self, ref: str, path: str) -> str:
        """Show file content at specific commit."""
        result = self._git_cmd("show", f"{ref}:{path}")
        return result.stdout

    # --- Push ---

    def push(self, remote: str = "origin", branch: str | None = None) -> None:
        """Push branch to remote."""
        args = ["push", remote]
        if branch:
            args.append(branch)
        self._git_cmd(*args)
