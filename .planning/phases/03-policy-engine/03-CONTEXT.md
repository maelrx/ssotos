# Phase 3: Policy Engine - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the capability-based policy system — the gatekeeper that prevents unauthorized mutations. All sensitive operations pass through policy checks before execution.

</domain>

<decisions>
## Implementation Decisions

### Capability Model
- **D-32:** Four capability groups: vault.*, agent.*, research.*, exchange.*
- **D-33:** Each group has fine-grained capabilities (read, create, update, delete, move, rename)

### Policy Outcomes (F6-02)
- **D-34:** allow_direct — operation allowed immediately
- **D-35:** allow_patch_only — requires Exchange Zone patch flow
- **D-36:** allow_in_exchange_only — only via Exchange Zone
- **D-37:** allow_with_approval — requires human approval
- **D-38:** deny — operation blocked

### Policy Rules (F6-03)
- **D-39:** Rules can be created by: actor, domain, capability, path, note_type, sensitivity
- **D-40:** Rule priority: most specific wins (path > note_type > sensitivity > domain > actor)

### Safe Defaults (F6-05)
- **D-41:** Read is broad by default
- **D-42:** Create only in safe zones (inbox, designated areas)
- **D-43:** Edit requires patch-first flow
- **D-44:** Delete/move/rename gated (require approval or denied)

### Policy Check Integration (F6-04)
- **D-45:** Every sensitive mutation call passes through policy check
- **D-46:** Policy checks are logged via EventBus

### Claude's Discretion
- Rule storage format (YAML/JSON in _system/policy/) — defer to implementation
- Policy admin UI details — defer to Phase 4 (Backend)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `docs/SSOT_Knowledge_OS_V1.md` — Architectural laws, policy-first principle
- `docs/STACK_DECISION_RECORD_Knowledge_OS_Core.md` — Stack decisions

### Phase-Specific
- `.planning/ROADMAP.md` §Phase 3 — Success criteria, key deliverables
- `.planning/REQUIREMENTS.md` §F6 — F6-01 to F6-05

### Prior Phases
- `.planning/phases/01-knowledge-filesystem-foundation/01-CONTEXT.md` — filesystem structure
- `.planning/phases/02-git-exchange-boundary/02-CONTEXT.md` — Exchange Zone

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 2 EventBus at src/core/event_bus.py — policy checks emit audit events
- Phase 2 services (GitService, ProposalService, PatchService) — must integrate policy checks
- Phase 1 workspace structure with _system/ folder for config

### Integration Points
- Phase 4 (Backend) will expose policy API
- Exchange Zone proposal flow requires policy approval
- All services must call policy.check() before mutations

</code_context>

<specifics>
## Specific Ideas

No specific external references — decisions derived from SSOT/PRD requirements.

</specifics>

<deferred>
## Deferred Ideas

- Policy admin UI — Phase 4 (Backend)
- Rule storage format — implementation detail

</deferred>

---

*Phase: 03-policy-engine*
*Context gathered: 2026-03-31*
*Auto-mode: all gray areas selected with documented defaults*

