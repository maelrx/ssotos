# Phase 2: Git / Exchange Boundary - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the revision layer and Exchange Zone — the audit boundary that prevents silent mutations. All mutations to the user vault and agent brain flow through this boundary.

</domain>

<decisions>
## Implementation Decisions

### Git Integration
- **D-21:** Git CLI via GitService — encapsulate all git operations through a well-defined service, not scattered subprocess calls
- **D-22:** Two separate Git repos: `user-vault.git` and `agent-brain.git` (bare repositories at workspace root)
- **D-23:** Worktree-based editing — proposals and research jobs use Git worktrees, not direct branch checkout
- **D-24:** All vault mutations go through Exchange Zone — no direct writes to main branch

### Branch Strategy
- **D-25:** Branch naming: `main`, `proposal/<actor>/<id>`, `research/<job-id>`, `import/<source>/<ts>`, `review/<id>`
- **D-26:** Proposal branches are short-lived — created on draft, merged/rejected on approval

### Exchange Zone
- **D-27:** Proposals track metadata: proposal_type, source_domain, target_domain, status, branch_name, worktree_path
- **D-28:** Proposal state machine: draft → generated → awaiting_review → approved/rejected → applied
- **D-29:** Patch-first mutation model — all changes proposed as patches, reviewed before application

### Diff/Patch
- **D-30:** Diff generated for any note change with readable output
- **D-31:** Patch bundles are self-contained and apply cleanly to main

### Claude's Discretion
- Rollback strategy (full reset vs stepwise revert) — defer to GitService implementation
- Review bundle format — use standard diff + provenance metadata

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `docs/SSOT_Knowledge_OS_V1.md` — Architectural laws, domain definitions, git as ledger
- `docs/STACK_DECISION_RECORD_Knowledge_OS_Core.md` — Git CLI via GitService decision

### Phase-Specific
- `.planning/ROADMAP.md` §Phase 2 — Success criteria, key deliverables
- `.planning/REQUIREMENTS.md` §F4, §F5 — Specific requirements F4-01 to F5-05

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 1 created workspace structure at `workspace/` with user-vault, agent-brain, exchange, raw, runtime directories
- `_system/vault-config.yaml` ready for git settings extension

### Integration Points
- Phase 3 (Policy Engine) will extend Exchange Zone with capability checks
- Phase 4 (Backend) will expose Git operations via API
- Phase 1 `_system/` folder is where git settings will be stored

</code_context>

<specifics>
## Specific Ideas

No specific external references — decisions derived from SSOT/PRD requirements and STACK_DECISION_RECORD.

</specifics>

<deferred>
## Deferred Ideas

None — Phase 2 scope is well-defined.

</deferred>

---

*Phase: 02-git-exchange-boundary*
*Context gathered: 2026-03-31*
*Auto-mode: all gray areas selected with documented defaults*

