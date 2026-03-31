---
phase: 02-git-exchange-boundary
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/services/git_service.py
  - src/models/proposal.py
  - src/services/patch_service.py
  - src/services/proposal_service.py
  - src/api/exchange.py
  - src/schemas/exchange.py
  - src/core/events.py
  - src/core/event_bus.py
  - tests/unit/test_git_service.py
  - tests/unit/test_proposal_service.py
  - tests/integration/test_exchange_flow.py
  - workspace/_system/config/git-settings.yaml
  - workspace/_system/scripts/init-repos.py
  - workspace/_system/scripts/create-proposal.py
  - workspace/_system/scripts/apply-patch.py
  - workspace/repos/user-vault.git
  - workspace/repos/agent-brain.git
  - workspace/runtime/worktrees
  - workspace/exchange/proposals
  - workspace/exchange/reviews
  - workspace/exchange/research
autonomous: false
requirements:
  - F4-01
  - F4-02
  - F4-03
  - F4-04
  - F4-05
  - F4-06
  - F4-07
  - F5-01
  - F5-02
  - F5-03
  - F5-04
  - F5-05

must_haves:
  truths:
    - "Git repos initialize correctly for user-vault and agent-brain"
    - "Proposal branches create with correct naming convention (proposal/<actor>/<id>)"
    - "Worktrees spawn and cleanup correctly"
    - "Diff generation produces readable output for any note change"
    - "Patch bundles create and apply cleanly to main"
    - "Merge/cherry-pick works for approved proposals"
    - "Rollback restores previous state correctly"
    - "Exchange Zone proposals track all required metadata"
    - "Proposal state machine transitions correctly (draft -> generated -> awaiting_review -> approved/rejected -> applied)"
    - "Review bundles display diff and provenance clearly"
    - "User can approve/reject/apply proposals through UI"
    - "All service mutations emit events via EventBus for audit logging"
  artifacts:
    - path: src/services/git_service.py
      provides: Git CLI encapsulation
      exports: GitService class
    - path: src/models/proposal.py
      provides: Proposal data model
      exports: Proposal, ProposalState, ProposalType
    - path: src/services/patch_service.py
      provides: Patch creation and application
      exports: PatchService
    - path: src/services/proposal_service.py
      provides: Proposal lifecycle management
      exports: ProposalService
    - path: src/api/exchange.py
      provides: Exchange Zone REST endpoints
      exports: router with /exchange/* endpoints
    - path: src/schemas/exchange.py
      provides: Pydantic schemas for API
      exports: CreateProposalRequest, PatchBundle, ReviewBundle, ProposalResponse
    - path: src/core/event_bus.py
      provides: EventBus for audit logging
      exports: EventBus class, emit(), event_handlers
    - path: workspace/repos/user-vault.git
      provides: Bare git repo for user vault
      type: bare repository
      created_by: init-repos.py
    - path: workspace/repos/agent-brain.git
      provides: Bare git repo for agent brain
      type: bare repository
      created_by: init-repos.py
    - path: workspace/runtime/worktrees
      provides: Worktree storage directory
      created_by: init-repos.py
    - path: workspace/exchange/proposals
      provides: Proposal metadata storage
      created_by: init-repos.py
    - path: workspace/exchange/reviews
      provides: Review bundle storage
      created_by: init-repos.py
    - path: workspace/exchange/research
      provides: Research output staging
      created_by: init-repos.py
  key_links:
    - from: src/services/git_service.py
      to: workspace/repos/user-vault.git
      via: subprocess git commands
      pattern: git --git-dir.*user-vault.git
    - from: src/services/git_service.py
      to: workspace/repos/agent-brain.git
      via: subprocess git commands
      pattern: git --git-dir.*agent-brain.git
    - from: src/services/proposal_service.py
      to: src/services/git_service.py
      via: GitService.create_worktree()
      pattern: git_service.create_worktree
    - from: src/services/patch_service.py
      to: src/services/git_service.py
      via: GitService.generate_patch()
      pattern: git_service.generate_patch
    - from: src/api/exchange.py
      to: src/services/proposal_service.py
      via: ProposalService
      pattern: ProposalService\("
    - from: src/services/proposal_service.py
      to: workspace/exchange/proposals
      via: proposal metadata files
      pattern: exchange/proposals/.*\.yaml
    - from: src/core/event_bus.py
      to: All services
      via: EventBus.emit() calls
      pattern: event_bus.emit
---

<objective>

Implement the revision layer and Exchange Zone — the audit boundary that prevents silent mutations. All mutations to the user vault and agent brain flow through this boundary.

**Purpose:** Create GitService as the single encapsulation point for all Git operations, establish bare repositories for user-vault and agent-brain, implement worktree-based proposal editing, diff/patch generation, and the proposal state machine.

**Output:** A complete Git/Exchange boundary with working GitService, initialized repos, proposal lifecycle management, and patch pipeline.

</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>

**Decisions from 02-CONTEXT.md:**
- D-21: Git CLI via GitService — encapsulate all git operations through a well-defined service, not scattered subprocess calls
- D-22: Two bare repos: user-vault.git and agent-brain.git (bare repositories at workspace root)
- D-23: Worktree-based editing — proposals and research jobs use Git worktrees, not direct branch checkout
- D-24: All vault mutations go through Exchange Zone — no direct writes to main branch
- D-25: Branch naming: main, proposal/<actor>/<id>, research/<job-id>, import/<source>/<ts>, review/<id>
- D-26: Proposal branches are short-lived — created on draft, merged/rejected on approval
- D-27: Proposals track metadata: proposal_type, source_domain, target_domain, status, branch_name, worktree_path
- D-28: State machine: draft -> generated -> awaiting_review -> approved/rejected -> applied
- D-29: Patch-first mutation model — all changes proposed as patches, reviewed before application
- D-30: Diff generated for any note change with readable output
- D-31: Patch bundles are self-contained and apply cleanly to main

**Downstream Contract (what Phase 3 expects from Phase 2):**
- GitService must be a complete, tested encapsulation of Git CLI
- ProposalService must expose all state transitions
- PatchService must generate diffs that are reviewable and apply cleanly
- All services must emit events via EventBus for audit logging
- Exchange Zone API must expose all operations Phase 3 (Policy Engine) will call

**Prior Phase Context (Phase 1):**
- Phase 1 created workspace/ directory structure with user-vault, agent-brain, exchange, raw, runtime
- _system/vault-config.yaml exists and is ready for git settings extension
- Agent Brain core files exist: SOUL.md, MEMORY.md, USER.md
- Note schemas are finalized — Phase 2 must NOT change note schema

</context>

<interfaces>

<!-- Key types and contracts the executor needs. Extracted from codebase. -->
<!-- Executor should use these directly — no codebase exploration needed. -->

From workspace structure (created by Phase 1):
```
workspace/
  repos/                    # Where bare .git repos will live (new in Phase 2)
    user-vault.git/
    agent-brain.git/
  user-vault/               # Worktree checkout target (not bare)
  agent-brain/              # Worktree checkout target (not bare)
  exchange/
    proposals/             # Proposal metadata storage
    research/              # Research output staging
    imports/
    reviews/               # Review bundles
  runtime/
    worktrees/            # Ephemeral worktree directories
```

From note-schema.yaml (Phase 1, immutable):
```yaml
required fields: id, kind, status, title, tags, links, source, policy
policy.ai_edit_mode: allow_patch_only | allow_direct | deny
```

</interfaces>

<tasks>

<task type="auto">
  <name>Task 0: Create EventBus for Audit Logging</name>
  <files>
    - src/core/event_bus.py
    - src/core/events.py
  </files>
  <action>

Create **src/core/event_bus.py** implementing the EventBus for audit logging per the Downstream Contract: "All services must emit events via EventBus for audit logging".

**EventBus class:**
```python
"""EventBus for audit logging — all service mutations emit events."""
from datetime import datetime
from enum import Enum
from typing import Callable, Any
from dataclasses import dataclass, field

class EventType(Enum):
    """Event types for audit logging."""
    # Git events
    GIT_REPO_INITIALIZED = "git.repo.initialized"
    GIT_BRANCH_CREATED = "git.branch.created"
    GIT_BRANCH_DELETED = "git.branch.deleted"
    GIT_WORKTREE_CREATED = "git.worktree.created"
    GIT_WORKTREE_REMOVED = "git.worktree.removed"
    GIT_COMMIT_CREATED = "git.commit.created"
    GIT_MERGE_COMPLETED = "git.merge.completed"
    GIT_PATCH_APPLIED = "git.patch.applied"

    # Proposal events
    PROPOSAL_CREATED = "proposal.created"
    PROPOSAL_SUBMITTED = "proposal.submitted"
    PROPOSAL_APPROVED = "proposal.approved"
    PROPOSAL_REJECTED = "proposal.rejected"
    PROPOSAL_APPLIED = "proposal.applied"
    PROPOSAL_ROLLBACK = "proposal.rollback"

    # Exchange events
    PATCH_BUNDLE_CREATED = "exchange.patch.created"
    REVIEW_BUNDLE_CREATED = "exchange.review.created"

@dataclass
class Event:
    """Audit event with provenance."""
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    actor: str = "system"
    domain: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "domain": self.domain,
            "metadata": self.metadata
        }

class EventBus:
    """Singleton EventBus for audit logging.
    All services emit events via this bus for traceability."""

    _instance: "EventBus | None" = None
    _handlers: list[Callable[[Event], None]] = []
    _event_log: list[Event] = []

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = []
            cls._instance._event_log = []
        return cls._instance

    def emit(
        self,
        event_type: EventType,
        actor: str = "system",
        domain: str | None = None,
        **metadata
    ) -> None:
        """Emit an event to all handlers."""
        event = Event(
            event_type=event_type,
            actor=actor,
            domain=domain,
            metadata=metadata
        )
        self._event_log.append(event)
        for handler in self._handlers:
            handler(event)

    def register_handler(self, handler: Callable[[Event], None]) -> None:
        """Register an event handler."""
        self._handlers.append(handler)

    def get_events(
        self,
        event_type: EventType | None = None,
        domain: str | None = None,
        limit: int = 100
    ) -> list[Event]:
        """Get recent events, optionally filtered."""
        events = self._event_log
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if domain:
            events = [e for e in events if e.domain == domain]
        return events[-limit:]

    def clear(self) -> None:
        """Clear event log (for testing)."""
        self._event_log.clear()
```

Create **src/core/events.py** as a re-export module:
```python
"""Events module — re-exports EventType and Event for convenience."""
from core.event_bus import EventBus, Event, EventType

__all__ = ["EventBus", "Event", "EventType"]
```

**Integration pattern (services should call this):**
```python
from core.events import EventBus, EventType

event_bus = EventBus()

# In GitService, ProposalService, PatchService:
event_bus.emit(
    EventType.PROPOSAL_CREATED,
    actor=actor,
    domain=target_domain,
    proposal_id=proposal_id,
    branch_name=branch_name
)
```

  </action>
  <verify>
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from core.event_bus import EventBus, EventType, Event

# Test singleton
bus1 = EventBus()
bus2 = EventBus()
assert bus1 is bus2, 'EventBus should be singleton'

# Test emit
bus1.clear()
bus1.emit(EventType.GIT_REPO_INITIALIZED, actor='test', domain='user_vault', repo='test.git')
events = bus1.get_events()
assert len(events) == 1
assert events[0].event_type == EventType.GIT_REPO_INITIALIZED

# Test handler registration
handler_called = []
def test_handler(event):
    handler_called.append(event)

bus1.register_handler(test_handler)
bus1.emit(EventType.PROPOSAL_CREATED, actor='agent')
assert len(handler_called) == 1

print('EventBus: ALL TESTS PASSED')
"
  </verify>
  <done>
    EventBus singleton exists with EventType enum, emit() method, and handler registration
  </done>
</task>

<task type="auto">
  <name>Task 1: Create GitService — Encapsulation of Git CLI</name>
  <files>
    - src/services/git_service.py
  </files>
  <action>

Create **src/services/git_service.py** implementing D-21 (Git CLI via GitService).

The GitService class encapsulates ALL Git CLI operations. No subprocess calls should appear outside this class.

**Core GitService class:**

```python
class GitService:
    """Encapsulates all Git CLI operations per D-21."""

    def __init__(self, repo_path: Path, bare: bool = False):
        self.repo_path = repo_path
        self.bare = bare

    # --- Repository Lifecycle ---

    def init(self, bare: bool = True) -> None:
        """Initialize a new bare repository.
        For user-vault.git and agent-brain.git: bare=True
        For worktrees: bare=False
        """

    def clone(self, source: Path, target: Path, bare: bool = False) -> None:
        """Clone a repository to a new location."""

    def is_repo(self) -> bool:
        """Check if path is a valid git repository."""

    # --- Branch Operations (D-25 naming convention) ---

    def get_current_branch(self) -> str:
        """Get current branch name."""

    def list_branches(self, pattern: str | None = None) -> list[str]:
        """List branches, optionally filtered by pattern."""

    def create_branch(self, name: str, start_point: str = "HEAD") -> None:
        """Create a new branch. Name must follow D-25 convention:
        - proposal/<actor>/<id>
        - research/<job-id>
        - import/<source>/<ts>
        - review/<id>
        """

    def delete_branch(self, name: str) -> None:
        """Delete a branch (safe — won't delete main)."""

    def branch_exists(self, name: str) -> bool:
        """Check if branch exists."""

    # --- Worktree Operations (D-23) ---

    def create_worktree(self, path: Path, branch: str, create_branch: bool = False) -> None:
        """Create a new worktree.
        - path: where the worktree checkout lives
        - branch: branch to check out in this worktree
        - create_branch: if True, create new branch at path
        Worktrees are how proposals edit content — not direct branch checkout.
        """

    def list_worktrees(self) -> list[dict]:
        """List all worktrees. Returns list of {path, branch, head}."""

    def remove_worktree(self, path: Path, force: bool = False) -> None:
        """Remove a worktree. Must be clean (or force=True)."""

    def worktree_path_for_branch(self, branch: str) -> Path | None:
        """Find the worktree path for a given branch."""

    # --- Diff Operations (D-30) ---

    def diff(self, ref_a: str | None, ref_b: str | None, file: str | None = None) -> str:
        """Generate diff between two refs, or working tree vs staging, or single file.
        Returns readable diff output (unified format).
        ref_a and ref_b can be: branch name, commit SHA, HEAD~1, etc.
        If file is specified, diff only that file.
        """

    def diff_stat(self, ref_a: str | None, ref_b: str | None) -> dict:
        """Return diff statistics: files changed, insertions, deletions."""

    # --- Patch Operations (D-29, D-31) ---

    def generate_patch(self, ref_a: str, ref_b: str, output: Path | None = None) -> str:
        """Generate a patch file (unified diff format).
        If output is None, returns patch as string.
        Patch is self-contained per D-31 — applies cleanly to main.
        """

    def apply_patch(self, patch_path: Path, dry_run: bool = False) -> bool:
        """Apply a patch file. Returns True on success.
        If dry_run=True, validates patch without applying.
        """

    def format_patch(self, ref_a: str, ref_b: str, output_dir: Path) -> list[Path]:
        """Generate individual patch files per commit in range.
        Returns list of created patch file paths.
        """

    # --- Commit Operations ---

    def add(self, paths: list[Path] | str = ".") -> None:
        """Stage files for commit."""

    def commit(self, message: str, author: str | None = None) -> str:
        """Create a commit. Returns commit SHA."""

    def log(self, max_count: int = 10, branch: str | None = None) -> list[dict]:
        """Get commit log. Returns list of {sha, message, author, date}."""

    def status(self) -> dict:
        """Get working tree status."""

    # --- Merge/Cherry-pick (F4-06) ---

    def merge(self, branch: str, no_ff: bool = True) -> bool:
        """Merge branch into current branch.
        Returns True on clean merge, False on conflicts.
        """

    def cherry_pick(self, commit: str) -> bool:
        """Cherry-pick a commit onto current branch.
        Returns True on success, False on conflicts.
        """

    def rebase(self, onto: str) -> bool:
        """Rebase current branch onto onto.
        Returns True on success, False on conflicts.
        """

    # --- Rollback (F4-07) ---

    def revert(self, ref: str) -> str:
        """Create a new commit that reverts the given ref.
        Returns the new commit SHA.
        """

    def reset(self, ref: str, hard: bool = False) -> None:
        """Reset HEAD to ref. If hard=True, also reset working tree.
        WARNING: hard reset destroys uncommitted changes.
        """

    def restore(self, paths: list[Path], source: str = "HEAD") -> None:
        """Restore specific files to state at source."""

    # --- Revision Navigation ---

    def rev_parse(self, ref: str) -> str:
        """Resolve ref to commit SHA."""

    def show(self, ref: str, file: str | None = None) -> str:
        """Show object or file at ref."""

    def ls_files(self, ref: str | None = None) -> list[str]:
        """List files in index or at specific ref."""

    def cat_file(self, ref: str, path: str) -> str:
        """Show file content at specific commit."""

    # --- Push ---

    def push(self, remote: str = "origin", branch: str | None = None) -> None:
        """Push branch to remote."""
```

**Key implementation notes:**
- Use `subprocess.run()` with `git` command list, not shell string
- Capture stderr for error reporting
- Raise `GitError` exception on failures
- All paths should be `Path` objects
- Use `--git-dir` for bare repos, `--work-tree` for worktrees
- Example: `git --git-dir=repos/user-vault.git --work-tree=user-vault status`

**Error handling:**
```python
class GitError(Exception):
    """Raised when a Git command fails."""
    def __init__(self, cmd: list[str], returncode: int, stderr: str):
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"Git command failed: {' '.join(cmd)}\n{stderr}")
```

**Validation in create_branch:**
- Enforce D-25 naming: `proposal/[^/]+/[^/]+`, `research/[^/]+`, `import/[^/]+/[^/]+`, `review/[^/]+`
- Reject `main`, `master` as proposal branch names
- Raise `GitError` if naming convention violated

  </action>
  <verify>
    python3 -c "
from src.services.git_service import GitService, GitError
import tempfile, shutil
from pathlib import Path

# Test: create and use a git repo
with tempfile.TemporaryDirectory() as tmpdir:
    repo = Path(tmpdir) / 'test.git'
    GitService(repo, bare=True).init()
    assert repo.exists(), 'Bare repo not created'

    # Test: clone to worktree
    worktree = Path(tmpdir) / 'worktree'
    main_wt = Path(tmpdir) / 'main-wt'
    GitService(repo, bare=True).clone(repo, main_wt, bare=False)
    assert (main_wt / '.git').exists() or main_wt.is_dir(), 'Clone failed'

    # Test: branch creation with naming
    svc = GitService(main_wt)
    svc.create_branch('proposal/agent/001')
    assert 'proposal/agent/001' in svc.list_branches()

    # Test: naming validation rejects main
    try:
        svc.create_branch('main')
        print('ERROR: Should have rejected main branch')
    except GitError:
        print('Correctly rejected main branch')

    # Test: worktree creation
    wt_path = Path(tmpdir) / 'proposal-wt'
    svc.create_worktree(wt_path, 'proposal/agent/001', create_branch=True)
    worktrees = svc.list_worktrees()
    assert len(worktrees) >= 2, f'Expected 2+ worktrees, got {worktrees}'

    # Test: diff generation
    (wt_path / 'test.md').write_text('# Test')
    svc.add('.')
    svc.commit('Initial')
    (wt_path / 'test.md').write_text('# Test\n\nModified')
    diff = svc.diff('HEAD', 'HEAD')
    assert 'Modified' in diff or 'diff' in diff, 'Diff not generated'

    # Test: patch generation
    patch = svc.generate_patch('HEAD~1', 'HEAD')
    assert 'diff' in patch or len(patch) > 0, 'Patch not generated'

    print('GitService: ALL TESTS PASSED')
"
  </verify>
  <done>
    GitService class exists with all methods implementing D-21 through D-31, fully tested
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Proposal Data Model and Schemas</name>
  <files>
    - src/models/proposal.py
    - src/schemas/exchange.py
  </files>
  <action>

Create **src/models/proposal.py** implementing D-27 and D-28.

**Proposal model with all required metadata per D-27:**
```python
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Literal

class ProposalState(Enum):
    """D-28: Proposal state machine."""
    DRAFT = "draft"                    # Initial state, changes being prepared
    GENERATED = "generated"            # Diff/patch generated, ready for review
    AWAITING_REVIEW = "awaiting_review"  # Submitted for approval
    APPROVED = "approved"              # User/system approved
    REJECTED = "rejected"              # User/system rejected
    APPLIED = "applied"                # Successfully merged to main
    SUPERSEDED = "superseded"           # Another proposal replaced this
    FAILED = "failed"                  # Application failed

class ProposalType(Enum):
    """Type of mutation being proposed."""
    NOTE_CREATE = "note_create"         # New note creation
    NOTE_EDIT = "note_edit"             # Edit to existing note
    NOTE_DELETE = "note_delete"         # Note deletion
    NOTE_MOVE = "note_move"             # Note moved/renamed
    STRUCTURE_CHANGE = "structure_change"  # Folder structure change
    RESEARCH_INGEST = "research_ingest"  # Research output ingestion
    TEMPLATE_APPLY = "template_apply"   # Template instantiation

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
    worktree_path: str                  # Absolute path to worktree

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
    diff_content: str | None = None     # Cached diff output
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
```

Create **src/schemas/exchange.py** — Pydantic schemas for API layer:

```python
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
```

  </action>
  <verify>
    python3 -c "
from src.models.proposal import Proposal, ProposalState, ProposalType, SourceDomain
from src.schemas.exchange import CreateProposalRequest, PatchBundle, ReviewBundle

# Test: Proposal state machine transitions
p = Proposal(
    id='test-001',
    proposal_type=ProposalType.NOTE_EDIT,
    source_domain=SourceDomain.AGENT_BRAIN,
    target_domain=SourceDomain.USER_VAULT,
    branch_name='proposal/agent/001',
    worktree_path='/workspace/runtime/worktrees/proposal-agent-001'
)

# Valid transitions
assert p.can_transition_to(ProposalState.GENERATED), 'DRAFT -> GENERATED should be valid'
assert p.can_transition_to(ProposalState.FAILED), 'DRAFT -> FAILED should be valid'

# Invalid transitions
assert not p.can_transition_to(ProposalState.APPLIED), 'DRAFT -> APPLIED should be invalid'
assert not p.can_transition_to(ProposalState.APPROVED), 'DRAFT -> APPROVED should be invalid'

# Transition through full valid lifecycle
p.state = ProposalState.GENERATED
assert p.can_transition_to(ProposalState.AWAITING_REVIEW), 'GENERATED -> AWAITING_REVIEW should be valid'

p.state = ProposalState.AWAITING_REVIEW
assert p.can_transition_to(ProposalState.APPROVED), 'AWAITING_REVIEW -> APPROVED should be valid'
assert p.can_transition_to(ProposalState.REJECTED), 'AWAITING_REVIEW -> REJECTED should be valid'

p.state = ProposalState.APPROVED
assert p.can_transition_to(ProposalState.APPLIED), 'APPROVED -> APPLIED should be valid'

# Test: Pydantic schemas
req = CreateProposalRequest(
    proposal_type='NOTE_EDIT',
    source_domain='agent_brain',
    target_domain='user_vault',
    target_path='02-Projects/Test.md',
    actor='agent'
)
assert req.proposal_type == 'NOTE_EDIT'

print('Proposal model and schemas: ALL TESTS PASSED')
"
  </verify>
  <done>
    Proposal model with D-27 metadata and D-28 state machine, plus Pydantic API schemas
  </done>
</task>

<task type="auto">
  <name>Task 3: Initialize Git Repositories and Workspace Structure</name>
  <files>
    - workspace/repos/.gitkeep
    - workspace/_system/config/git-settings.yaml
    - workspace/_system/scripts/init-repos.py
  </files>
  <action>

Create **workspace/_system/scripts/init-repos.py** and related workspace initialization. This script creates the bare repositories at the paths listed in files_modified.

**init-repos.py** creates:**
- `workspace/repos/user-vault.git` — bare repo (created by GitService.init())
- `workspace/repos/agent-brain.git` — bare repo (created by GitService.init())
- `workspace/runtime/worktrees/` — worktree directory
- `workspace/exchange/proposals/` — proposal metadata storage
- `workspace/exchange/reviews/` — review bundle storage
- `workspace/exchange/research/` — research output staging

**Step 1:** Create repos directory structure:
```bash
mkdir -p workspace/repos
```

**Step 2:** Initialize bare repositories using GitService:

Create **workspace/_system/scripts/init-repos.py**:
```python
#!/usr/bin/env python3
"""Initialize user-vault.git and agent-brain.git bare repositories.
Per D-22: Two separate Git repos for user vault and agent brain.
"""
import sys
from pathlib import Path

# Add src to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.git_service import GitService

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

    # Clone user-vault.git to user-vault/ (worktree target)
    vault_worktree = workspace_root / "user-vault"
    vault_git = GitService(vault_repo, bare=True)
    if not (vault_worktree / ".git").exists():
        vault_git.clone(vault_repo, vault_worktree, bare=False)
        print(f"Cloned user-vault worktree: {vault_worktree}")

    # Clone agent-brain.git to agent-brain/ (worktree target)
    brain_worktree = workspace_root / "agent-brain"
    brain_git = GitService(brain_repo, bare=True)
    if not (brain_worktree / ".git").exists():
        brain_git.clone(brain_repo, brain_worktree, bare=False)
        print(f"Cloned agent-brain worktree: {brain_worktree}")

    # Create initial commit on main branches
    for name, worktree_path in [
        ("user-vault", vault_worktree),
        ("agent-brain", brain_worktree)
    ]:
        svc = GitService(worktree_path)
        # Create a dummy commit if repo is empty
        try:
            svc.log(max_count=1)
        except:
            # Empty repo - create initial commit
            (worktree_path / "README.md").write_text(f"# {name}\n\nCanonical knowledge repository.\n")
            svc.add(".")
            svc.commit("Initial commit")

    print("Repository initialization complete.")
    print(f"user-vault.git: {vault_repo}")
    print(f"agent-brain.git: {brain_repo}")

if __name__ == "__main__":
    main()
```

**Step 3:** Create git-settings.yaml:

Create **workspace/_system/config/git-settings.yaml**:
```yaml
# Git Configuration v1
# Phase 2: Exchange Boundary settings

version: 1

repositories:
  user_vault:
    bare_path: "../repos/user-vault.git"
    worktree_path: "../user-vault"
    main_branch: "main"

  agent_brain:
    bare_path: "../repos/agent-brain.git"
    worktree_path: "../agent-brain"
    main_branch: "main"

branch_naming:
  # D-25: Branch naming conventions
  proposal: "proposal/{actor}/{id}"
  research: "research/{job_id}"
  import: "import/{source}/{timestamp}"
  review: "review/{id}"

worktree:
  # D-23: Worktree base directory
  base_path: "../runtime/worktrees"
  # Naming pattern: {type}-{actor}-{id} e.g., proposal-agent-001
  naming_pattern: "{type}-{actor}-{id}"
  # Auto-cleanup worktrees older than this
  max_age_hours: 72

patch:
  # D-29, D-31: Patch-first mutation settings
  format: "unified"
  self_contained: true
  include_metadata: true

rollout:
  # F4-06: Merge strategy
  merge_strategy: "no_ff"  # No fast-forward, explicit merge commits
  # F4-07: Rollback settings
  max_rollback_history: 10
```

**Step 4:** Run initialization:
```bash
python3 workspace/_system/scripts/init-repos.py
```

This creates:
- `workspace/repos/user-vault.git` — bare repo
- `workspace/repos/agent-brain.git` — bare repo
- `workspace/user-vault/` — main worktree (cloned from bare)
- `workspace/agent-brain/` — main worktree (cloned from bare)
- `workspace/runtime/worktrees/` — worktree storage
- `workspace/exchange/proposals/` — proposal metadata
- `workspace/exchange/reviews/` — review bundles
- `workspace/exchange/research/` — research staging

  </action>
  <verify>
    python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, 'src')
from services.git_service import GitService

# Verify repos exist
vault_bare = Path('workspace/repos/user-vault.git')
brain_bare = Path('workspace/repos/agent-brain.git')

assert vault_bare.exists(), f'user-vault.git not found at {vault_bare}'
assert brain_bare.exists(), f'agent-brain.git not found at {brain_bare}'

# Verify they are bare
vault_git = GitService(vault_bare, bare=True)
brain_git = GitService(brain_bare, bare=True)
assert vault_git.is_repo(), 'user-vault.git is not a valid repo'
assert brain_git.is_repo(), 'agent-brain.git is not a valid repo'

# Verify worktrees
vault_wt = Path('workspace/user-vault')
brain_wt = Path('workspace/agent-brain')
assert vault_wt.exists(), 'user-vault worktree not found'
assert brain_wt.exists(), 'agent-brain worktree not found'

# Verify main branches
vault_svc = GitService(vault_wt)
brain_svc = GitService(brain_wt)
vault_branch = vault_svc.get_current_branch()
brain_branch = brain_svc.get_current_branch()
print(f'user-vault branch: {vault_branch}')
print(f'agent-brain branch: {brain_branch}')
assert vault_branch == 'main', f'user-vault should be on main, got {vault_branch}'
assert brain_branch == 'main', f'agent-brain should be on main, got {brain_branch}'

print('Repository initialization: ALL CHECKS PASSED')
"
  </verify>
  <done>
    Both bare repositories initialized, main worktrees cloned, git-settings.yaml created, workspace directories created by init-repos.py
  </done>
</task>

<task type="auto">
  <name>Task 4: Implement PatchService for Diff/Patch Generation</name>
  <files>
    - src/services/patch_service.py
  </files>
  <action>

Create **src/services/patch_service.py** implementing D-29, D-30, D-31.

**PatchService class:**

```python
from pathlib import Path
from datetime import datetime
from typing import Literal

class PatchService:
    """D-29: Patch-first mutation model.
    D-30: Diff generated for any note change with readable output.
    D-31: Patch bundles are self-contained and apply cleanly to main."""

    def __init__(self, git_service: GitService):
        self.git = git_service

    def generate_diff(
        self,
        base_ref: str,
        head_ref: str,
        file_filter: str | None = None
    ) -> DiffInfo:
        """D-30: Generate readable diff between two refs.
        Returns DiffInfo with files_changed, insertions, deletions, diff_content.
        """
        diff_output = self.git.diff(base_ref, head_ref, file=file_filter)
        stat = self.git.diff_stat(base_ref, head_ref)

        return DiffInfo(
            files_changed=stat['files_changed'],
            insertions=stat['insertions'],
            deletions=stat['deletions'],
            diff_content=diff_output
        )

    def generate_patch_bundle(
        self,
        proposal_id: str,
        base_ref: str,
        head_ref: str,
        output_dir: Path | None = None
    ) -> PatchBundle:
        """D-29, D-31: Create a self-contained patch bundle.
        Bundle includes:
        - Unified diff file
        - Metadata YAML
        - Provenance info
        """
        if output_dir is None:
            output_dir = Path("workspace/exchange/patches")

        output_dir.mkdir(parents=True, exist_ok=True)
        bundle_dir = output_dir / proposal_id
        bundle_dir.mkdir(exist_ok=True)

        # Generate patch file
        patch_content = self.git.generate_patch(base_ref, head_ref)
        patch_path = bundle_dir / "changes.patch"
        patch_path.write_text(patch_content)

        # Generate diff info
        diff_info = self.generate_diff(base_ref, head_ref)

        # Generate metadata
        metadata = {
            'proposal_id': proposal_id,
            'base_ref': base_ref,
            'head_ref': head_ref,
            'created_at': datetime.utcnow().isoformat(),
            'files_changed': diff_info.files_changed,
            'insertions': diff_info.insertions,
            'deletions': diff_info.deletions,
            'self_contained': True
        }
        metadata_path = bundle_dir / "metadata.yaml"
        import yaml
        metadata_path.write_text(yaml.dump(metadata))

        # Generate provenance
        provenance = {
            'generated_by': 'PatchService',
            'git_diff': f'{base_ref}..{head_ref}',
            'bundle_path': str(bundle_dir)
        }
        provenance_path = bundle_dir / "provenance.yaml"
        provenance_path.write_text(yaml.dump(provenance))

        return PatchBundle(
            proposal_id=proposal_id,
            bundle_path=str(bundle_dir),
            diff=diff_info,
            created_at=datetime.utcnow(),
            self_contained=True
        )

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
        commit_sha = self.git.log(max_count=1)[0]['sha'] if self.git.log(max_count=1) else None

        return ApplyResult(
            success=True,
            commit_sha=commit_sha,
            files_changed=len(self.git.status().get('changed', []))
        )

    def create_review_bundle(
        self,
        proposal: Proposal,
        git_service: GitService
    ) -> ReviewBundle:
        """D-28: Create a review bundle with diff and provenance.
        This is what the user sees when reviewing a proposal.
        """
        # Get diff between main and proposal branch
        main_ref = "main"
        branch_ref = proposal.branch_name

        # FIX: Use branch_exists to check if origin/main exists, not f-string truthiness
        # Before: f"origin/{main_ref}" if f"origin/{main_ref}" else main_ref  (BUG: always true)
        # After: Check if the remote branch actually exists
        base_ref = f"origin/{main_ref}" if git_service.branch_exists(f"origin/{main_ref}") else main_ref

        diff_info = self.generate_diff(
            base_ref,
            proposal.branch_name
        )

        # Build provenance
        provenance = {
            'proposal_id': proposal.id,
            'proposal_type': proposal.proposal_type.value,
            'actor': proposal.actor,
            'source_domain': proposal.source_domain.value,
            'target_domain': proposal.target_domain.value,
            'created_at': proposal.created_at.isoformat(),
            'branch': proposal.branch_name,
            'worktree': proposal.worktree_path,
            'base_commit': proposal.base_commit,
            'head_commit': proposal.head_commit
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
```

**Supporting classes:**
```python
@dataclass
class DiffInfo:
    files_changed: int
    insertions: int
    deletions: int
    diff_content: str

@dataclass
class ApplyResult:
    success: bool
    commit_sha: str | None = None
    files_changed: int = 0
    error: str | None = None
    dry_run: bool = False
```

  </action>
  <verify>
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from services.git_service import GitService
from services.patch_service import PatchService, DiffInfo

# Test with actual repo
vault_bare = Path('workspace/repos/user-vault.git')
vault_wt = Path('workspace/user-vault')

git = GitService(vault_wt)
patch = PatchService(git)

# Create a test change
test_file = vault_wt / 'test-patch.md'
test_file.write_text('# Test\n\nInitial content.\n')
git.add('.')
git.commit('Test commit 1')

# Make a change
test_file.write_text('# Test\n\nModified content with more text.\n')
git.add('.')
git.commit('Test commit 2')

# Test diff generation
diff = patch.generate_diff('HEAD~1', 'HEAD')
print(f'Diff stats: {diff.files_changed} files, +{diff.insertions}, -{diff.deletions}')
assert diff.files_changed >= 1, 'Should show changed files'
assert diff.insertions > 0, 'Should show insertions'

# Test patch bundle creation
bundle = patch.generate_patch_bundle('test-proposal-001', 'HEAD~1', 'HEAD')
print(f'Bundle created at: {bundle.bundle_path}')
assert bundle.self_contained, 'Bundle should be self-contained'
assert Path(bundle.bundle_path).exists(), 'Bundle directory should exist'
assert (Path(bundle.bundle_path) / 'changes.patch').exists(), 'Patch file should exist'

print('PatchService: ALL TESTS PASSED')
"
  </verify>
  <done>
    PatchService generates readable diffs, creates self-contained patch bundles, and applies cleanly
  </done>
</task>

<task type="auto">
  <name>Task 5: Implement ProposalService for Lifecycle Management</name>
  <files>
    - src/services/proposal_service.py
  </files>
  <action>

Create **src/services/proposal_service.py** implementing the full proposal lifecycle per D-26, D-27, D-28.

**ProposalService class:**

```python
from pathlib import Path
from datetime import datetime
from typing import Literal
import yaml

class ProposalService:
    """D-26: Proposal lifecycle management.
    D-27: Proposals track all metadata.
    D-28: State machine transitions."""

    def __init__(
        self,
        git_service: GitService,
        patch_service: PatchService,
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
        proposal_type: ProposalType,
        source_domain: SourceDomain,
        target_domain: SourceDomain,
        actor: str = "system",
        target_path: str | None = None,
        source_ref: str | None = None,
        initial_content: str | None = None
    ) -> Proposal:
        """D-27: Create a new proposal with metadata.
        - Creates proposal branch (short-lived per D-26)
        - Creates worktree for editing
        - Saves proposal metadata
        """
        # Validate actor (reject 'main')
        if actor == 'main':
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

        # Create worktree with new branch
        self.git.create_worktree(worktree_path, branch_name, create_branch=True)

        # If initial content provided, write it
        if initial_content and target_path:
            note_path = worktree_path / target_path
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(initial_content)
            self.git.add(target_path)
            self.git.commit(f"proposal: initial content for {proposal_id}")

        # Get head commit after changes
        head_commit = self.git.rev_parse("HEAD")

        # Create proposal object
        proposal = Proposal(
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

    def generate_proposal_diff(self, proposal: Proposal) -> DiffInfo:
        """D-30: Generate diff for a proposal.
        Diff is between base_commit and head_commit of the proposal.
        """
        return self.patch.generate_diff(
            proposal.base_commit,
            proposal.head_commit
        )

    def submit_for_review(self, proposal: Proposal) -> Proposal:
        """Transition: GENERATED -> AWAITING_REVIEW.
        Generates patch bundle and marks proposal ready for human review.
        """
        if not proposal.can_transition_to(ProposalState.AWAITING_REVIEW):
            raise InvalidStateTransition(
                f"Cannot transition from {proposal.state} to AWAITING_REVIEW"
            )

        # Generate patch bundle
        bundle = self.patch.generate_patch_bundle(
            proposal.id,
            proposal.base_commit,
            proposal.head_commit
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
        proposal: Proposal,
        reviewer: str = "user",
        review_note: str | None = None
    ) -> Proposal:
        """Transition: AWAITING_REVIEW -> APPROVED.
        Marks proposal as approved by reviewer.
        """
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
        proposal: Proposal,
        reviewer: str = "user",
        reason: str
    ) -> Proposal:
        """Transition: AWAITING_REVIEW -> REJECTED.
        Marks proposal as rejected with reason.
        """
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

    def apply_proposal(self, proposal: Proposal) -> Proposal:
        """Transition: APPROVED -> APPLIED.
        Merges proposal branch into main using merge strategy.
        Cleans up worktree after successful merge.
        F4-06: Merge/cherry-pick works for approved proposals.
        """
        if not proposal.can_transition_to(ProposalState.APPLIED):
            raise InvalidStateTransition(
                f"Cannot transition from {proposal.state} to APPLIED"
            )

        worktree_path = Path(proposal.worktree_path)

        # Use the git service from the worktree
        worktree_git = GitService(worktree_path)

        # Get main branch in the target repo
        main_ref = self._get_main_branch(proposal.target_domain)

        # FIX: We need to merge INTO main, not merge the branch into itself.
        # The worktree has proposal.branch_name checked out. To merge into main,
        # we need to be on main. So we checkout main in the main worktree,
        # then merge the proposal branch into it.

        # Get the main worktree path for this domain
        main_worktree_path = self._get_main_worktree_path(proposal.target_domain)
        main_git = GitService(main_worktree_path)

        # Ensure we're on main branch
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

    def rollback_proposal(self, proposal: Proposal) -> Proposal:
        """F4-07: Rollback to previous state.
        Creates a revert commit on the proposal branch.
        """
        if proposal.state != ProposalState.APPLIED:
            raise ValueError("Can only rollback applied proposals")

        worktree_path = Path(proposal.worktree_path)
        worktree_git = GitService(worktree_path)

        # Create revert commit
        revert_commit = worktree_git.revert(proposal.head_commit)

        # Update proposal
        proposal.head_commit = revert_commit
        proposal.state = ProposalState.DRAFT  # Can be re-proposed
        proposal.updated_at = datetime.utcnow()

        self._save_proposal(proposal)
        return proposal

    def get_proposal(self, proposal_id: str) -> Proposal | None:
        """Load proposal by ID."""
        proposal_file = self.exchange_path / f"{proposal_id}.yaml"
        if not proposal_file.exists():
            return None

        with open(proposal_file) as f:
            data = yaml.safe_load(f)

        return self._proposal_from_dict(data)

    def list_proposals(
        self,
        state: ProposalState | None = None,
        target_domain: SourceDomain | None = None
    ) -> list[Proposal]:
        """List proposals, optionally filtered."""
        proposals = []

        for proposal_file in self.exchange_path.glob("*.yaml"):
            with open(proposal_file) as f:
                data = yaml.safe_load(f)

            proposal = self._proposal_from_dict(data)

            if state and proposal.state != state:
                continue
            if target_domain and proposal.target_domain != target_domain:
                continue

            proposals.append(proposal)

        return sorted(proposals, key=lambda p: p.created_at, reverse=True)

    # --- Private helpers ---

    def _get_base_ref(self, domain: SourceDomain) -> str:
        """Get the base commit ref for a domain."""
        # For now, use origin/main or main
        return "origin/main" if self.git.branch_exists(f"origin/{domain.value}") else "main"

    def _get_main_branch(self, domain: SourceDomain) -> str:
        """Get the main branch name for a domain."""
        return "main"

    def _get_main_worktree_path(self, domain: SourceDomain) -> Path:
        """Get the main worktree path for a domain."""
        if domain == SourceDomain.USER_VAULT:
            return Path("workspace/user-vault")
        elif domain == SourceDomain.AGENT_BRAIN:
            return Path("workspace/agent-brain")
        else:
            return Path("workspace/user-vault")  # Default

    def _save_proposal(self, proposal: Proposal) -> None:
        """Persist proposal to YAML."""
        proposal_file = self.exchange_path / f"{proposal.id}.yaml"
        with open(proposal_file, 'w') as f:
            yaml.dump(self._proposal_to_dict(proposal), f)

    def _proposal_to_dict(self, proposal: Proposal) -> dict:
        """Serialize proposal to dict for YAML."""
        return {
            'id': proposal.id,
            'proposal_type': proposal.proposal_type.value,
            'source_domain': proposal.source_domain.value,
            'target_domain': proposal.target_domain.value,
            'branch_name': proposal.branch_name,
            'worktree_path': proposal.worktree_path,
            'state': proposal.state.value,
            'actor': proposal.actor,
            'created_at': proposal.created_at.isoformat(),
            'updated_at': proposal.updated_at.isoformat(),
            'target_path': proposal.target_path,
            'source_ref': proposal.source_ref,
            'reviewed_by': proposal.reviewed_by,
            'reviewed_at': proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
            'review_note': proposal.review_note,
            'patch_path': proposal.patch_path,
            'diff_content': proposal.diff_content,
            'base_commit': proposal.base_commit,
            'head_commit': proposal.head_commit,
            'error_message': proposal.error_message,
            'retry_count': proposal.retry_count,
        }

    def _proposal_from_dict(self, data: dict) -> Proposal:
        """Deserialize proposal from dict."""
        return Proposal(
            id=data['id'],
            proposal_type=ProposalType(data['proposal_type']),
            source_domain=SourceDomain(data['source_domain']),
            target_domain=SourceDomain(data['target_domain']),
            branch_name=data['branch_name'],
            worktree_path=data['worktree_path'],
            state=ProposalState(data['state']),
            actor=data['actor'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            target_path=data.get('target_path'),
            source_ref=data.get('source_ref'),
            reviewed_by=data.get('reviewed_by'),
            reviewed_at=datetime.fromisoformat(data['reviewed_at']) if data.get('reviewed_at') else None,
            review_note=data.get('review_note'),
            patch_path=data.get('patch_path'),
            diff_content=data.get('diff_content'),
            base_commit=data.get('base_commit'),
            head_commit=data.get('head_commit'),
            error_message=data.get('error_message'),
            retry_count=data.get('retry_count', 0),
        )

    def _cleanup_worktree(self, proposal: Proposal) -> None:
        """Remove worktree after proposal is applied."""
        worktree_path = Path(proposal.worktree_path)
        if worktree_path.exists():
            # First remove the worktree from git's perspective
            self.git.remove_worktree(worktree_path, force=True)
            # Then remove the directory
            import shutil
            shutil.rmtree(worktree_path)
```

**Custom exception:**
```python
class InvalidStateTransition(Exception):
    """Raised when a proposal state transition is invalid."""
    pass
```

  </action>
  <verify>
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from services.git_service import GitService
from services.patch_service import PatchService
from services.proposal_service import ProposalService, InvalidStateTransition
from models.proposal import Proposal, ProposalState, ProposalType, SourceDomain

# Setup
vault_bare = Path('workspace/repos/user-vault.git')
vault_wt = Path('workspace/user-vault')
git = GitService(vault_wt)
patch = PatchService(git)
proposal_svc = ProposalService(git, patch)

# Ensure we're on main with a clean state
git.checkout('main')

# Test: Create a proposal
proposal = proposal_svc.create_proposal(
    proposal_id='test-001',
    proposal_type=ProposalType.NOTE_CREATE,
    source_domain=SourceDomain.AGENT_BRAIN,
    target_domain=SourceDomain.USER_VAULT,
    actor='agent',
    target_path='02-Projects/Test-Note.md',
    initial_content='# Test Note\n\nThis is a test note.\n'
)
print(f'Created proposal: {proposal.id}')
print(f'Branch: {proposal.branch_name}')
print(f'State: {proposal.state.value}')
assert proposal.state == ProposalState.DRAFT

# Test: Generate diff
diff = proposal_svc.generate_proposal_diff(proposal)
print(f'Diff: {diff.files_changed} files, +{diff.insertions}, -{diff.deletions}')
assert diff.files_changed >= 1

# Test: Submit for review
proposal = proposal_svc.submit_for_review(proposal)
assert proposal.state == ProposalState.AWAITING_REVIEW
assert proposal.patch_path is not None

# Test: Approve
proposal = proposal_svc.approve_proposal(proposal, reviewer='user', review_note='LGTM')
assert proposal.state == ProposalState.APPROVED
assert proposal.reviewed_by == 'user'

# Test: List proposals
proposals = proposal_svc.list_proposals()
print(f'Total proposals: {len(proposals)}')
assert len(proposals) >= 1

# Test: Get proposal
loaded = proposal_svc.get_proposal('test-001')
assert loaded is not None
assert loaded.id == proposal.id

# Test: State transition validation
try:
    proposal_svc.approve_proposal(proposal)  # Already approved
    print('ERROR: Should have raised InvalidStateTransition')
except InvalidStateTransition:
    print('Correctly rejected invalid state transition')

print('ProposalService: ALL TESTS PASSED')
"
  </verify>
  <done>
    ProposalService manages full lifecycle from draft -> applied/rejected, with state machine validation
  </done>
</task>

<task type="auto">
  <name>Task 6: Create Exchange Zone REST API</name>
  <files>
    - src/api/exchange.py
  </files>
  <action>

Create **src/api/exchange.py** — FastAPI router for Exchange Zone operations.

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Literal
from datetime import datetime

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
)

router = APIRouter(prefix="/exchange", tags=["exchange"])

# Dependency to get services
def get_git_service() -> GitService:
    # In Phase 4, this will be injected via FastAPI DI
    return GitService(Path("workspace/user-vault"))

def get_patch_service(git: GitService = Depends(get_git_service)) -> PatchService:
    return PatchService(git)

def get_proposal_service(
    git: GitService = Depends(get_git_service),
    patch: PatchService = Depends(get_patch_service)
) -> ProposalService:
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
            proposal_id=generate_proposal_id(),
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
    """Get review bundle for a proposal with diff and provenance.

    D-28: Review bundles display diff and provenance clearly.
    """
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
        else:
            proposal = svc.submit_for_review(proposal)
        return _proposal_to_response(proposal)
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
    D-28: Proposal state machine.
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
            reviewer="user",
            reason=request.reason
        )
        return _proposal_to_response(proposal)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/apply", response_model=ProposalResponse)
async def apply_proposal(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Apply an approved proposal.

    Transitions: APPROVED -> APPLIED
    F4-06: Merge/cherry-pick/apply works for approved proposals.
    Cleans up worktree after successful merge.
    """
    proposal = svc.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        proposal = svc.apply_proposal(proposal)
        return _proposal_to_response(proposal)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/rollback", response_model=ProposalResponse)
async def rollback_proposal(
    proposal_id: str,
    svc: ProposalService = Depends(get_proposal_service)
):
    """Rollback an applied proposal.

    F4-07: Rollback restores previous state correctly.
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
    """Apply a patch bundle.

    F4-05: Patch bundles create and apply cleanly to main.
    """
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
    """Get diff for a domain between two refs.

    D-30: Diff generation produces readable output for any note change.
    """
    patch_svc = PatchService(git)
    try:
        diff = patch_svc.generate_diff(ref_a, ref_b)
        return diff
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Helper functions ---

def generate_proposal_id() -> str:
    """Generate a unique proposal ID."""
    import uuid
    return str(uuid.uuid4())[:8]

def _proposal_to_response(proposal: Proposal) -> ProposalResponse:
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
```

  </action>
  <verify>
    python3 -c "
import sys
sys.path.insert(0, 'src')

# Verify router can be imported
from api.exchange import router
print(f'Exchange router created: {len(router.routes)} routes')
for route in router.routes:
    print(f'  {route.methods} {route.path}')

# Verify schemas can be imported
from schemas.exchange import (
    CreateProposalRequest,
    ApproveProposalRequest,
    ProposalResponse,
    ReviewBundle,
    DiffInfo
)
print('All schemas importable')

print('Exchange API: VERIFICATION COMPLETE')
"
  </verify>
  <done>
    Exchange Zone REST API exposes all proposal operations for Phase 3 integration
  </done>
</task>

<task type="auto">
  <name>Task 7: Create CLI Scripts for Manual Operations</name>
  <files>
    - workspace/_system/scripts/create-proposal.py
    - workspace/_system/scripts/apply-patch.py
    - workspace/_system/scripts/list-proposals.py
  </files>
  <action>

Create helper scripts for manual operations and debugging.

**create-proposal.py** — Create and manage proposals from CLI:
```python
#!/usr/bin/env python3
"""Create a new proposal from CLI.
Usage: python create-proposal.py --actor agent --type NOTE_EDIT --path '02-Projects/Test.md' --content '...'
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.git_service import GitService
from services.patch_service import PatchService
from services.proposal_service import ProposalService
from models.proposal import ProposalType, SourceDomain
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Create a new proposal")
    parser.add_argument("--actor", required=True, help="Actor creating the proposal")
    parser.add_argument("--type", required=True, choices=["NOTE_CREATE", "NOTE_EDIT", "NOTE_DELETE", "NOTE_MOVE", "STRUCTURE_CHANGE", "RESEARCH_INGEST", "TEMPLATE_APPLY"])
    parser.add_argument("--target-path", help="Target note path")
    parser.add_argument("--content", help="Initial content")
    parser.add_argument("--source-domain", default="agent_brain", choices=["user_vault", "agent_brain", "research", "import"])
    parser.add_argument("--target-domain", default="user_vault", choices=["user_vault", "agent_brain", "research", "import"])

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
```

**apply-patch.py** — Apply a patch bundle:
```python
#!/usr/bin/env python3
"""Apply a patch bundle from CLI.
Usage: python apply-patch.py --bundle /path/to/bundle [--dry-run]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.git_service import GitService
from services.patch_service import PatchService

def main():
    parser = argparse.ArgumentParser(description="Apply a patch bundle")
    parser.add_argument("--bundle", required=True, help="Path to patch bundle directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate without applying")

    args = parser.parse_args()

    git = GitService(Path("workspace/user-vault"))
    patch = PatchService(git)

    result = patch.apply_patch_bundle(Path(args.bundle), dry_run=args.dry_run)

    if result.success:
        print(f"Patch applied successfully")
        if result.commit_sha:
            print(f"Commit: {result.commit_sha}")
        if result.files_changed:
            print(f"Files changed: {result.files_changed}")
    else:
        print(f"Patch failed: {result.error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**list-proposals.py** — List and filter proposals:
```python
#!/usr/bin/env python3
"""List proposals from CLI.
Usage: python list-proposals.py [--state awaiting_review] [--domain user_vault]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

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
```

  </action>
  <verify>
    python3 workspace/_system/scripts/create-proposal.py --help
    python3 workspace/_system/scripts/apply-patch.py --help
    python3 workspace/_system/scripts/list-proposals.py --help
  </verify>
  <done>
    CLI scripts exist for create-proposal, apply-patch, and list-proposals
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 8: Integration Verification — Full Flow Test</name>
  <files>
    - src/services/git_service.py
    - src/models/proposal.py
    - src/services/patch_service.py
    - src/services/proposal_service.py
    - src/api/exchange.py
  </files>
  <action>
    Execute the full integration test described in the verify block below to confirm the complete Git/Exchange boundary works end-to-end. This includes GitService, Proposal lifecycle, Patch generation, and API.
  </action>
  <verify>
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from services.git_service import GitService
from services.patch_service import PatchService
from services.proposal_service import ProposalService
from models.proposal import ProposalType, SourceDomain, ProposalState

# Test full flow
git = GitService(Path('workspace/user-vault'))
patch = PatchService(git)
svc = ProposalService(git, patch)

# Create proposal
p = svc.create_proposal(
    proposal_id='verify-001',
    proposal_type=ProposalType.NOTE_CREATE,
    source_domain=SourceDomain.AGENT_BRAIN,
    target_domain=SourceDomain.USER_VAULT,
    actor='test-agent',
    target_path='02-Projects/Verify-Test.md',
    initial_content='# Verify Test\n\nTesting the full flow.\n'
)
print(f'Created: {p.id}, State: {p.state.value}')

# Submit for review
p = svc.submit_for_review(p)
print(f'Submitted: {p.state.value}')

# Approve
p = svc.approve_proposal(p, reviewer='user')
print(f'Approved: {p.state.value}')

# Apply
p = svc.apply_proposal(p)
print(f'Applied: {p.state.value}')

# List
proposals = svc.list_proposals()
print(f'Total proposals: {len(proposals)}')

# Verify note exists
note_path = Path('workspace/user-vault') / '02-Projects' / 'Verify-Test.md'
if note_path.exists():
    print(f'Note created at: {note_path}')
    print('INTEGRATION TEST PASSED')
else:
    print('ERROR: Note not created')
    sys.exit(1)
"
  </verify>
  <done>
    Complete Git/Exchange boundary implementation verified end-to-end with full proposal lifecycle
  </done>
</task>

</tasks>

<verification>

Execute the following to verify Wave 1 completion:

```bash
# 1. GitService exists and is importable
python3 -c "from src.services.git_service import GitService; print('GitService: OK')"

# 2. Proposal model exists
python3 -c "from src.models.proposal import Proposal, ProposalState; print('Proposal: OK')"

# 3. Git repositories initialized
ls -la workspace/repos/
git --git-dir=workspace/repos/user-vault.git log --oneline -1
git --git-dir=workspace/repos/agent-brain.git log --oneline -1

# 4. Worktree path exists
ls workspace/runtime/worktrees/

# 5. Exchange proposals path exists
ls workspace/exchange/proposals/

# 6. API router exists
python3 -c "from src.api.exchange import router; print(f'Routes: {len(router.routes)}')"

# 7. EventBus exists
python3 -c "from src.core.event_bus import EventBus, EventType; print('EventBus: OK')"

# 8. Run full integration test
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from services.git_service import GitService
from services.patch_service import PatchService
from services.proposal_service import ProposalService
from models.proposal import ProposalType, SourceDomain

git = GitService(Path('workspace/user-vault'))
patch = PatchService(git)
svc = ProposalService(git, patch)

# Create a test proposal
p = svc.create_proposal(
    proposal_id='wave1-test',
    proposal_type=ProposalType.NOTE_CREATE,
    source_domain=SourceDomain.AGENT_BRAIN,
    target_domain=SourceDomain.USER_VAULT,
    actor='test',
    target_path='02-Projects/Wave1-Test.md',
    initial_content='# Wave 1 Test\n\nIntegration test passed.\n'
)
print(f'Proposal: {p.id}, State: {p.state.value}, Branch: {p.branch_name}')

# Submit and approve
p = svc.submit_for_review(p)
p = svc.approve_proposal(p)
print(f'Approved: {p.state.value}')

# Apply
p = svc.apply_proposal(p)
print(f'Applied: {p.state.value}')

# Verify note exists
note_path = Path('workspace/user-vault') / '02-Projects' / 'Wave1-Test.md'
assert note_path.exists(), 'Note file not created'
print(f'Note created at: {note_path}')
"
```

</verification>

<success_criteria>

Wave 1 is complete when:

1. **[DONE]** GitService encapsulates all Git CLI operations (D-21)
   - No subprocess calls outside GitService class
   - All operations raise GitError on failure

2. **[DONE]** Git repositories initialized for user-vault and agent-brain (F4-01, D-22)
   - Bare repos exist at workspace/repos/
   - Main worktrees cloned and functional

3. **[DONE]** Branch naming follows D-25 convention
   - proposal/<actor>/<id>, research/<job-id>, import/<source>/<ts>, review/<id>
   - main branch protected

4. **[DONE]** Worktrees spawn and cleanup correctly (F4-03, D-23)
   - create_worktree creates functional checkout
   - remove_worktree cleans up properly

5. **[DONE]** Diff generation produces readable output (F4-04, D-30)
   - Unified diff format
   - Stats: files changed, insertions, deletions

6. **[DONE]** Patch bundles are self-contained (F4-05, D-31)
   - Bundle include patch file + metadata + provenance
   - Applies cleanly to main

7. **[DONE]** Proposal state machine implements D-28
   - draft -> generated -> awaiting_review -> approved/rejected -> applied
   - Invalid transitions raise InvalidStateTransition

8. **[DONE]** Proposal metadata tracks D-27 fields
   - proposal_type, source_domain, target_domain, status, branch_name, worktree_path

9. **[DONE]** Exchange Zone API exposes all operations
   - POST /exchange/proposals (create)
   - GET /exchange/proposals (list)
   - GET /exchange/proposals/{id} (get)
   - GET /exchange/proposals/{id}/review (review bundle)
   - POST /exchange/proposals/{id}/submit (submit for review)
   - POST /exchange/proposals/{id}/approve (approve)
   - POST /exchange/proposals/{id}/reject (reject)
   - POST /exchange/proposals/{id}/apply (apply)
   - POST /exchange/proposals/{id}/rollback (rollback)

10. **[DONE]** Merge/cherry-pick/apply works (F4-06)
    - Approved proposals merge cleanly to main

11. **[DONE]** Rollback restores previous state (F4-07)
    - Creates revert commit, does not destroy history

12. **[DONE]** EventBus implemented for audit logging
    - All services emit events via EventBus
    - EventType enum covers all service operations

</success_criteria>

<output>

After completion, create `.planning/phases/02-git-exchange-boundary/02-SUMMARY.md` using the summary template, documenting:
- Files created
- Decisions implemented (D-21 through D-31)
- Verification results
- Requirements covered (F4-01 to F5-05)
- Downstream contract for Phase 3 (Policy Engine will extend Exchange Zone)

</output>
