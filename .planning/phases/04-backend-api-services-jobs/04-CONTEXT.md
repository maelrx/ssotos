# Phase 4: Backend / API / Services / Jobs - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the FastAPI modular backend with Postgres schema, background worker, observability, and initial UI. This phase exposes the entire system through REST API and enables the web UI.

</domain>

<decisions>
## Implementation Decisions

### Backend Structure (F7)
- **D-47:** FastAPI with modular routers per bounded context
- **D-48:** Internal modules: auth, vault, templates, gitops, exchange, policy, approvals, retrieval, agent, research, jobs, audit
- **D-49:** Pydantic v2 for all DTOs and request/response models

### Database (F8)
- **D-50:** SQLAlchemy 2 with async support via asyncpg
- **D-51:** Tables: workspaces, actors, notes_projection, policy_rules, approvals, proposals, jobs, job_events, chunks, embeddings, artifacts, audit_logs
- **D-52:** Alembic for migrations

### API Endpoints (F7-02)
- **D-53:** REST endpoints: /vault/*, /templates/*, /retrieval/*, /copilot/*, /exchange/*, /approvals/*, /research/*, /jobs/*, /policy/*, /admin/*

### Job Queue (F13)
- **D-54:** Postgres-backed queue with row claiming
- **D-55:** Job types: index_note, reindex_scope, generate_embeddings, research_job, parse_source, apply_patch_bundle, reflect_agent, consolidate_memory

### Observability (F14)
- **D-56:** structlog for structured logging
- **D-57:** Audit logs with event_id, trace_id, actor, capability, domain, target, result, timestamp
- **D-58:** OpenTelemetry light integration

### Frontend (F15)
- **D-59:** React + Vite + TypeScript SPA
- **D-60:** TanStack Query for server state
- **D-61:** Zustand for UI state
- **D-62:** CodeMirror 6 for note editor

### Deployment (F16)
- **D-63:** Docker Compose: app-api, worker-runtime, postgres
- **D-64:** Caddy for reverse proxy with auto-HTTPS

### Claude's Discretion
- WebSocket vs SSE for job status — default to SSE
- Specific UI component library — use shadcn/ui primitives
- Database connection pooling settings — defer to implementation

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `docs/SSOT_Knowledge_OS_V1.md` — Architectural laws
- `docs/STACK_DECISION_RECORD_Knowledge_OS_Core.md` — FastAPI, SQLAlchemy 2, Pydantic v2, structlog, OpenTelemetry

### Phase-Specific
- `.planning/ROADMAP.md` §Phase 4 — Success criteria, key deliverables
- `.planning/REQUIREMENTS.md` §F7, §F8, §F13, §F14, §F15, §F16

### Prior Phases
- `.planning/phases/01-knowledge-filesystem-foundation/01-CONTEXT.md` — filesystem structure
- `.planning/phases/02-git-exchange-boundary/02-CONTEXT.md` — Exchange Zone
- `.planning/phases/03-policy-engine/03-CONTEXT.md` — Policy Engine

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 2 services (GitService, ProposalService, PatchService) — expose via API
- Phase 3 PolicyService — expose via /policy/* endpoints
- Phase 1 workspace structure — sync with filesystem

### Integration Points
- All services must be exposed via API
- Background worker consumes job queue
- UI connects to REST API

</code_context>

<specifics>
## Specific Ideas

No specific external references — decisions derived from STACK_DECISION_RECORD.

</specifics>

<deferred>
## Deferred Ideas

- Real-time collaboration — out of scope for v1
- Mobile app — web app is primary interface

</deferred>

---

*Phase: 04-backend-api-services-jobs*
*Context gathered: 2026-03-31*
*Auto-mode: all gray areas selected with documented defaults*

