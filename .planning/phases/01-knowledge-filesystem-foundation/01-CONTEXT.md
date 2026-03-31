# Phase 1: Knowledge Filesystem Foundation - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the canonical filesystem structure, schemas, templates, and daily notes — the sovereign foundation of the entire system. All subsequent phases depend on this.

</domain>

<decisions>
## Implementation Decisions

### Directory Structure
- **D-01:** Directory hierarchy follows SSOT/PRD specification: `user-vault/`, `agent-brain/`, `exchange/`, `raw/`, `runtime/`, `repos/`
- **D-02:** User Vault uses numbered prefixes: `00-Inbox/`, `01-Daily/`, `02-Projects/`, `03-Areas/`, `04-Resources/`, `05-Archive/`, `Templates/`, `Attachments/`, `_system/`
- **D-03:** Agent Brain structure: `SOUL.md`, `MEMORY.md`, `USER.md`, `skills/`, `heuristics/`, `reflections/`, `sessions/`, `scratchpads/`, `playbooks/`, `traces/`
- **D-04:** Exchange Zone: `proposals/`, `research/`, `imports/`, `reviews/`
- **D-05:** Raw artifacts: `web/`, `documents/`, `parsed/`, `manifests/`, `failed/`
- **D-06:** Runtime: `worktrees/`, `temp/`

### Note Schema
- **D-07:** Required frontmatter fields: `id` (stable UUID), `kind` (note type), `status`, `title`, `tags`, `links`, `source`, `policy`
- **D-08:** Note ID is stable — title can change, id cannot
- **D-09:** Schema validation is strict — invalid frontmatter is rejected at write time (not warned)

### Note Types
- **D-10:** All 11 note types supported: daily, project, area, resource, archive-item, fleeting, permanent, research-note, source-note, synthesis-note, index-note, template-instance

### Template System
- **D-11:** Template profiles are static and selectable at workspace creation
- **D-12:** Minimum 3 profiles required: PARA-like, Daily-first, Zettelkasten-like
- **D-13:** Additional profiles: Research Lab, Project OS
- **D-14:** Base templates for all 9 types: daily, project, area, resource, fleeting, permanent, source, synthesis, research brief

### Daily Notes
- **D-15:** Daily notes auto-created on first access (not on app start — lazy creation)
- **D-16:** Daily note template sections: Inbox, Focus, Notes, Linked Projects, Decisions, Learnings, Tasks, Review
- **D-17:** Daily note naming: `YYYY-MM-DD.md` format
- **D-18:** Daily notes linkable to projects/areas via frontmatter `links.project` and `links.area`

### Workspace Structure
- **D-19:** Each workspace has independent vault, brain, exchange, raw, runtime directories
- **D-20:** `_system/` folder contains vault config, schemas, and template profiles (not user-visible content)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `docs/SSOT_Knowledge_OS_V1.md` — Architectural laws, domain definitions, build order mandate
- `docs/PRD_Knowledge_OS_Core_OSS_V1_REBUILT.md` — Product requirements, Phase 1 scope definition
- `docs/STACK_DECISION_RECORD_Knowledge_OS_Core.md` — Stack decisions, directory structure specs

### Phase-Specific
- `.planning/ROADMAP.md` §Phase 1 — Success criteria, key deliverables
- `.planning/REQUIREMENTS.md` §F1, F2, F3 — Specific requirements F1-01 to F3-03

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet — this is the foundation phase, no existing code

### Established Patterns
- N/A — greenfield foundation

### Integration Points
- Phase 2 (Git/Exchange) depends on directory structure being in place
- Phase 4 (Backend) will expose filesystem operations via API
- All future phases depend on the schema contracts established here

</code_context>

<specifics>
## Specific Ideas

No specific external references — decisions derived from SSOT/PRD requirements.

</specifics>

<deferred>
## Deferred Ideas

None — Phase 1 scope is well-defined.

</deferred>

---

*Phase: 01-knowledge-filesystem-foundation*
*Context gathered: 2026-03-31*
*Auto-mode: all gray areas selected with documented defaults*
