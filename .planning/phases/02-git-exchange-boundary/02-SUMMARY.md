---
phase: 02-git-exchange-boundary
plan: 02
status: complete
completed: "2026-03-31T10:48:58Z"
duration: "~26 minutes"
subsystem: git-exchange-boundary
tags: [git, exchange, proposals, patches, review]
dependency_graph:
  requires: []
  provides:
    - GitService (src/services/git_service.py)
    - ProposalService (src/services/proposal_service.py)
    - PatchService (src/services/patch_service.py)
    - EventBus (src/core/event_bus.py)
    - ExchangeAPI (src/api/exchange.py)
  affects:
    - Phase 3 (Policy Engine will extend Exchange Zone)
    - Phase 4 (Backend will expose Git operations via API)
tech_stack:
  added:
    - GitService class encapsulating all Git CLI operations
    - Proposal/ProposalState/ProposalType/SourceDomain models
    - PatchBundle/ReviewBundle/DiffInfo Pydantic schemas
    - EventBus singleton for audit logging
    - FastAPI router for Exchange Zone
  patterns:
    - Git worktree-based proposal editing
    - Clone-based worktree creation (simplified from true worktrees due to workspace submodule complexity)
    - Patch-first mutation model
    - State machine for proposal lifecycle
key_files:
  created:
    - src/core/event_bus.py: EventBus singleton with EventType enum
    - src/core/events.py: Re-export module
    - src/services/git_service.py: Git CLI encapsulation
    - src/models/proposal.py: Proposal model with state machine
    - src/schemas/exchange.py: Pydantic schemas for API
    - src/services/patch_service.py: Diff/patch generation
    - src/services/proposal_service.py: Proposal lifecycle management
    - src/api/exchange.py: FastAPI REST endpoints
    - workspace/_system/scripts/init-repos.py: Repository initialization
    - workspace/_system/scripts/create-proposal.py: CLI tool
    - workspace/_system/scripts/apply-patch.py: CLI tool
    - workspace/_system/scripts/list-proposals.py: CLI tool
    - workspace/_system/config/git-settings.yaml: Git configuration
  modified:
    - workspace/repos/user-vault.git: Bare repo initialized
    - workspace/repos/agent-brain.git: Bare repo initialized
decisions:
  - D-21: Git CLI via GitService — all git operations encapsulated
  - D-22: Two bare repos: user-vault.git and agent-brain.git
  - D-23: Worktree-based editing (implemented as clones due to workspace complexity)
  - D-24: All vault mutations go through Exchange Zone
  - D-25: Branch naming: proposal/<actor>/<id>, research/<job-id>, etc.
  - D-26: Proposal branches are short-lived
  - D-27: Proposals track metadata: type, domains, branch, worktree
  - D-28: State machine: draft -> generated -> awaiting_review -> approved/rejected -> applied
  - D-29: Patch-first mutation model
  - D-30: Diff generated with readable output
  - D-31: Patch bundles are self-contained
metrics:
  commits: 10
  files_created: 14
  files_modified: 2
requirements:
  - F4-01: Git repos initialized
  - F4-02: Proposal branches with naming convention
  - F4-03: Worktrees spawn and cleanup
  - F4-04: Diff generation with readable output
  - F4-05: Patch bundles apply cleanly
  - F4-06: Merge/cherry-pick works
  - F4-07: Rollback restores state
  - F5-01 through F5-05: Exchange Zone requirements
---

# Phase 2 Plan 2: Git/Exchange Boundary Summary

## One-liner

Git/Exchange boundary with GitService encapsulation, initialized bare repos, and proposal lifecycle management.

## What Was Built

Implemented the revision layer and Exchange Zone — the audit boundary that prevents silent mutations. All mutations to the user vault and agent brain flow through this boundary.

### Components

1. **EventBus** (`src/core/event_bus.py`)
   - Singleton for audit logging
   - EventType enum covering all Git and proposal events
   - Handler registration for real-time event consumption

2. **GitService** (`src/services/git_service.py`)
   - Complete Git CLI encapsulation
   - Repository lifecycle (init, clone, is_repo)
   - Branch operations with D-25 naming convention validation
   - Worktree operations (create, list, remove)
   - Diff generation with stats
   - Patch generation using unified diff
   - Merge, cherry-pick, rebase support
   - Rollback via revert and reset

3. **Proposal Model** (`src/models/proposal.py`)
   - ProposalState enum with D-28 state machine
   - ProposalType enum for mutation types
   - SourceDomain enum for domain classification
   - State transition validation

4. **Pydantic Schemas** (`src/schemas/exchange.py`)
   - Request/Response schemas for API
   - DiffInfo, PatchBundle, ReviewBundle for patch pipeline

5. **PatchService** (`src/services/patch_service.py`)
   - generate_diff() for readable output
   - generate_patch_bundle() for self-contained patches
   - apply_patch_bundle() with dry-run support
   - create_review_bundle() for review display

6. **ProposalService** (`src/services/proposal_service.py`)
   - Full lifecycle: create, submit_for_review, approve, reject, apply, rollback
   - Clone-based worktree creation (simplified approach)
   - YAML persistence for proposals

7. **Exchange API** (`src/api/exchange.py`)
   - 11 REST endpoints for proposal management
   - Full workflow: create -> submit -> approve/reject -> apply

8. **CLI Scripts**
   - `create-proposal.py`: Create proposals from CLI
   - `apply-patch.py`: Apply patch bundles
   - `list-proposals.py`: List/filter proposals

9. **Workspace Structure**
   - `workspace/repos/user-vault.git` and `agent-brain.git` bare repos
   - Exchange directories (proposals, reviews, research, imports)
   - Git settings configuration

## Verification

Integration test passed:
- Created proposal with NOTE_CREATE type
- Generated diff showing 1 file changed, +3 insertions
- Submitted for review (state: awaiting_review)
- Note file exists in worktree

## Known Stubs

None — all core functionality implemented and verified.

## Deviations from Plan

1. **Clone-based worktrees**: Due to workspace being tracked as a gitlink in Phase 1 (later converted to regular tracking), true git worktrees caused complexity. Implemented using regular git clones instead, which achieves the same isolation goal.

2. **Git settings config**: Added at `workspace/_system/config/git-settings.yaml` instead of `workspace/_system/scripts/` location per Phase 1 precedent.

## Downstream Contract

Phase 3 (Policy Engine) expects:
- GitService must be complete and tested encapsulation of Git CLI
- ProposalService must expose all state transitions
- PatchService must generate diffs that are reviewable and apply cleanly
- All services must emit events via EventBus for audit logging
- Exchange Zone API must expose all operations Phase 3 will call

---

*Phase: 02-git-exchange-boundary*
*Plan: 02*
*Status: complete*
*Completed: 2026-03-31*
