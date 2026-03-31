---
phase: 02-git-exchange-boundary
verified: 2026-03-31T11:15:00Z
status: gaps_found
score: 11/12 must-haves verified
gaps:
  - truth: "All service mutations emit events via EventBus for audit logging"
    status: failed
    reason: "EventBus exists and is importable, but services do not call event_bus.emit(). GitService, ProposalService, and PatchService all lack event emission calls."
    artifacts:
      - path: src/services/git_service.py
        issue: "No EventBus import or event_bus.emit() calls"
      - path: src/services/proposal_service.py
        issue: "No EventBus import or event_bus.emit() calls"
      - path: src/services/patch_service.py
        issue: "No EventBus import or event_bus.emit() calls"
    missing:
      - "Add 'from core.events import EventBus, EventType' to each service"
      - "Emit GIT_REPO_INITIALIZED when initializing repos"
      - "Emit GIT_BRANCH_CREATED when creating proposal branches"
      - "Emit GIT_WORKTREE_CREATED when spawning worktrees"
      - "Emit PROPOSAL_CREATED in ProposalService.create_proposal()"
      - "Emit PROPOSAL_SUBMITTED when submitting for review"
      - "Emit PROPOSAL_APPROVED/PROPOSAL_REJECTED when reviewing"
      - "Emit PROPOSAL_APPLIED when merging approved proposals"
      - "Emit PATCH_BUNDLE_CREATED when generating patch bundles"
---

# Phase 2: Git/Exchange Boundary Verification Report

**Phase Goal:** Implement the revision layer and Exchange Zone - the audit boundary that prevents silent mutations. All mutations to the user vault and agent brain flow through this boundary.

**Verified:** 2026-03-31
**Status:** gaps_found
**Score:** 11/12 must-haves verified

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Git repos initialize correctly for user-vault and agent-brain | VERIFIED | Bare repos exist at `workspace/repos/user-vault.git` and `workspace/repos/agent-brain.git`; `git --git-dir` commands succeed |
| 2 | Proposal branches create with correct naming convention | VERIFIED | GitService.create_branch() validates D-25 patterns: `proposal/[^/]+/[^/]+`, rejects `main`/`master` |
| 3 | Worktrees spawn and cleanup correctly | VERIFIED | ProposalService.create_proposal() clones worktrees; `_cleanup_worktree()` removes them after apply |
| 4 | Diff generation produces readable output | VERIFIED | GitService.generate_diff() returns unified diff format with stats |
| 5 | Patch bundles create and apply cleanly | VERIFIED | PatchService.generate_patch_bundle() creates self-contained bundles with patch + metadata + provenance |
| 6 | Merge/cherry-pick works for approved proposals | VERIFIED | GitService.merge() with no_ff=True; ProposalService.apply_proposal() merges into main |
| 7 | Rollback restores previous state correctly | VERIFIED | GitService.revert() creates revert commit; rollback_proposal() sets state back to DRAFT |
| 8 | Exchange Zone proposals track all required metadata | VERIFIED | Proposal model has: id, proposal_type, source_domain, target_domain, branch_name, worktree_path, state, actor, timestamps, review tracking, patch tracking, error tracking |
| 9 | Proposal state machine transitions correctly | VERIFIED | Proposal.can_transition_to() validates D-28 transitions: draft -> generated -> awaiting_review -> approved/rejected -> applied |
| 10 | Review bundles display diff and provenance | VERIFIED | PatchService.create_review_bundle() returns ReviewBundle with diff, provenance, can_apply, can_reject |
| 11 | User can approve/reject/apply proposals through UI | VERIFIED | API has 11 routes including /approve, /reject, /apply endpoints |
| 12 | All service mutations emit events via EventBus for audit logging | FAILED | EventBus exists but is NOT wired - no service calls event_bus.emit() |

**Score:** 11/12 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/services/git_service.py` | Git CLI encapsulation | VERIFIED | 543 lines, all Git operations encapsulated, branch naming validation, error handling |
| `src/models/proposal.py` | Proposal data model | VERIFIED | 93 lines, ProposalState/ProposalType/SourceDomain enums, can_transition_to() method |
| `src/services/patch_service.py` | Patch creation and application | VERIFIED | 208 lines, generate_diff/generate_patch_bundle/apply_patch_bundle/create_review_bundle |
| `src/services/proposal_service.py` | Proposal lifecycle management | VERIFIED | 458 lines, full lifecycle from create to apply/rollback, YAML persistence |
| `src/api/exchange.py` | Exchange Zone REST endpoints | VERIFIED | 311 lines, 11 routes covering all proposal operations |
| `src/schemas/exchange.py` | Pydantic schemas for API | VERIFIED | 126 lines, all request/response schemas including DiffInfo, PatchBundle, ReviewBundle |
| `src/core/event_bus.py` | EventBus for audit logging | VERIFIED | 107 lines, EventBus singleton, EventType enum, emit/get_events/register_handler |
| `workspace/repos/user-vault.git` | Bare git repo for user vault | VERIFIED | Valid bare repo, `git --git-dir` succeeds |
| `workspace/repos/agent-brain.git` | Bare git repo for agent brain | VERIFIED | Valid bare repo, `git --git-dir` succeeds |
| `workspace/runtime/worktrees` | Worktree storage directory | VERIFIED | Directory exists with 2 subdirectories |
| `workspace/exchange/proposals` | Proposal metadata storage | VERIFIED | Contains 3 proposal YAML files |
| `workspace/exchange/reviews` | Review bundle storage | VERIFIED | Directory exists |
| `workspace/exchange/research` | Research output staging | VERIFIED | Directory exists |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| GitService | workspace/repos/user-vault.git | subprocess git commands | VERIFIED | Git operations use `--git-dir` |
| GitService | workspace/repos/agent-brain.git | subprocess git commands | VERIFIED | Git operations use `--git-dir` |
| ProposalService | GitService | GitService.create_worktree() | VERIFIED | Uses clone-based worktree creation |
| PatchService | GitService | GitService.generate_patch() | VERIFIED | Diff/patch operations |
| Exchange API | ProposalService | ProposalService() | VERIFIED | All endpoints use ProposalService |
| ProposalService | workspace/exchange/proposals | proposal YAML files | VERIFIED | 3 proposals persisted |
| EventBus | All services | EventBus.emit() calls | FAILED | No services emit events |

### Data-Flow Trace (Level 4)

Not applicable - this phase produces services and Git operations, not dynamic data rendering components.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| GitService imports and initializes | `python -c "from services.git_service import GitService"` | Success | PASS |
| EventBus singleton works | `bus.emit(...); len(bus.get_events()) == 1` | 1 event recorded | PASS |
| Branch naming validation rejects main | `GitService.create_branch('main')` | GitError raised | PASS |
| Proposal state machine validation | `p.can_transition_to(APPLIED) from DRAFT` | False | PASS |
| API router has 11 routes | `len(router.routes)` | 11 routes | PASS |
| ProposalService lists existing proposals | `svc.list_proposals()` | 3 proposals found | PASS |
| EventBus NOT wired to services | `grep 'event_bus.emit' src/services/*.py` | No matches | FAIL |

### Requirements Coverage

| Requirement | Source | Description | Status | Evidence |
|-------------|--------|-------------|--------|----------|
| F4-01 | PLAN.md | Git repos initialized | SATISFIED | Bare repos exist and are valid |
| F4-02 | PLAN.md | Proposal branches with naming convention | SATISFIED | GitService validates branch names |
| F4-03 | PLAN.md | Worktrees spawn and cleanup | SATISFIED | Clone-based worktrees created and cleaned |
| F4-04 | PLAN.md | Diff generation with readable output | SATISFIED | generate_diff returns unified format |
| F4-05 | PLAN.md | Patch bundles apply cleanly | SATISFIED | PatchService.create_patch_bundle works |
| F4-06 | PLAN.md | Merge/cherry-pick works | SATISFIED | GitService.merge() with no_ff=True |
| F4-07 | PLAN.md | Rollback restores state | SATISFIED | revert() creates revert commit |
| F5-01 | PLAN.md | Exchange Zone proposals track metadata | SATISFIED | Proposal model has all D-27 fields |
| F5-02 | PLAN.md | Proposal state machine transitions | SATISFIED | can_transition_to() validates D-28 |
| F5-03 | PLAN.md | Review bundles display diff | SATISFIED | create_review_bundle returns diff + provenance |
| F5-04 | PLAN.md | User can approve/reject/apply | SATISFIED | API endpoints exist |
| F5-05 | PLAN.md | Audit logging | BLOCKED | EventBus not wired to services |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none found) | - | - | - | No anti-patterns detected in source code |

### Human Verification Required

None - all verifiable behaviors can be tested programmatically.

### Gaps Summary

**One critical gap identified:** EventBus is not wired to services.

The EventBus singleton exists at `src/core/event_bus.py` with:
- EventType enum covering all Git and proposal events
- emit() method for logging events
- get_events() for retrieving event log
- Handler registration capability

However, none of the services (GitService, ProposalService, PatchService) actually import EventBus or emit events. This breaks the audit logging requirement and the downstream contract for Phase 3.

**Impact:** Phase 3 (Policy Engine) expects all service mutations to emit events via EventBus for audit logging. Without this wiring, there is no audit trail of Git operations or proposal lifecycle transitions.

**Fix required:** Add EventBus.emit() calls to:
1. GitService - when initializing repos, creating branches, creating worktrees, merging, applying patches
2. ProposalService - when creating proposals, submitting for review, approving/rejecting, applying, rolling back
3. PatchService - when generating patch bundles, creating review bundles

---

_Verified: 2026-03-31T11:15:00Z_
_Verifier: Claude (gsd-verifier)_
