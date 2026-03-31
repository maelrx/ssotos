# Phase 4: Backend / API / Services / Jobs - Implementation Plan

**Status:** Ready for execution
**Phase:** 04-backend-api-services-jobs
**Scope:** F7 (Backend), F8 (Database), F13 (Jobs), F14 (Observability), F15 (Frontend), F16 (Deployment)
**Granularity:** Fine (6 sub-plans, 3 waves)

---

## Phase Overview

This phase creates the FastAPI modular backend, Postgres schema, background worker, observability, initial UI, and Docker deployment. It is the largest phase in the project.

**Requirements covered:** F7-01 to F7-06, F8-01 to F8-03, F13-01 to F13-04, F14-01 to F14-05, F15-01 to F15-07, F16-01 to F16-04

**Downstream contract (Phase 5 - Agent Brain):**
- Agent Brain operations exposed via `/agent/*` API endpoints
- Skill manifest format: `skills/<skill-name>/manifest.yaml`
- Session summaries persisted to `agent-brain/sessions/<session-id>.md`
- SOUL.md, MEMORY.md, USER.md accessible via `/agent/brain/*` endpoints

---

## Wave Structure

| Wave | Plans | Focus | Dependencies |
|------|-------|-------|--------------|
| 1 | 04-01 | Database foundation (schema + migrations) | None |
| 1 | 04-02 | FastAPI app shell + all API routers | 04-01 |
| 2 | 04-03 | Background worker + job queue | 04-01, 04-02 |
| 2 | 04-04 | Observability (structlog + audit + OTel) | 04-01, 04-02 |
| 3 | 04-05 | React SPA + workspace shell UI | 04-02 |
| 3 | 04-06 | Docker Compose + Caddy + deployment docs | 04-03, 04-04, 04-05 |

---

## Plan 04-01: Database Foundation

**File:** `.planning/phases/04-backend-api-services-jobs/04-01-PLAN.md`
**Wave:** 1 | **Type:** execute | **Autonomous:** true

Creates SQLAlchemy 2 async models for all tables, Alembic migration setup, and initial migration.

**Requirements:** F8-01 (tables), F8-02 (note projection sync)

**Tables to create (per D-51):**
- `workspaces` — workspace configuration
- `actors` — users and agents
- `notes_projection` — materialized note index synced with filesystem
- `policy_rules` — policy rule definitions
- `approvals` — pending approval requests
- `proposals` — exchange zone proposals
- `jobs` — background job queue
- `job_events` — job status event log
- `chunks` — heading-guided text chunks
- `embeddings` — vector embeddings for notes
- `artifacts` — research raw artifacts
- `audit_logs` — structured audit log entries

**Must-haves:**
- All 12 tables defined with SQLAlchemy 2 async models
- Alembic initialized with migration environment
- Initial migration creates all tables
- Alembic migration runs successfully against fresh Postgres
- notes_projection has filesystem watcher sync capability

---

## Plan 04-02: FastAPI App Shell + API Routers

**File:** `.planning/phases/04-backend-api-services-jobs/04-02-PLAN.md`
**Wave:** 1 | **Type:** execute | **Autonomous:** true | **Depends:** 04-01

Creates FastAPI app with modular routers, SSE for job status, and all REST endpoints per D-53.

**Requirements:** F7-01 (modular backend), F7-02 (REST endpoints), F7-03 (SSE/WebSocket), F7-04 (Postgres operational DB)

**Internal modules (per D-48):**
- `auth` — authentication endpoints
- `vault` — note CRUD, vault operations
- `templates` — template listing and creation
- `gitops` — git operations exposure
- `exchange` — proposal lifecycle management
- `policy` — policy rule CRUD and evaluation
- `approvals` — approval request management
- `retrieval` — search and context pack retrieval
- `agent` — agent brain operations
- `research` — research job creation and status
- `jobs` — job queue management
- `audit` — audit log query endpoints

**API routers (per D-53):**
- `/vault/*` — note operations
- `/templates/*` — template operations
- `/retrieval/*` — search operations
- `/copilot/*` — note copilot operations
- `/exchange/*` — proposal management
- `/approvals/*` — approval workflow
- `/research/*` — research job management
- `/jobs/*` — job queue operations
- `/policy/*` — policy management
- `/admin/*` — admin operations

**Must-haves:**
- FastAPI app starts with all routers registered
- All documented REST endpoints return valid responses
- SSE endpoint `/jobs/events` streams job status updates
- CORS configured for frontend SPA
- Health check endpoint at `/health`

---

## Plan 04-03: Background Worker + Job Queue

**File:** `.planning/phases/04-backend-api-services-jobs/04-03-PLAN.md`
**Wave:** 2 | **Type:** execute | **Autonomous:** true | **Depends:** 04-01, 04-02

Creates Postgres-backed job queue with row claiming and background worker that processes jobs.

**Requirements:** F13-01 (job queue), F13-02 (job types), F13-03 (status tracking), F13-04 (retries)

**Job types (per D-55):**
- `index_note` — index a single note in FTS/vector
- `reindex_scope` — reindex a folder or tag
- `generate_embeddings` — generate embeddings for notes
- `research_job` — full research pipeline execution
- `parse_source` — parse a raw source document
- `apply_patch_bundle` — apply an approved patch
- `reflect_agent` — agent reflection/summarization
- `consolidate_memory` — consolidate agent memory

**Must-haves:**
- Job queue uses Postgres row claiming (per D-54)
- Worker claims available jobs and processes them
- Job status transitions correctly: pending -> running -> completed/failed
- Failed jobs retry with exponential backoff (max 3 retries)
- Job events are recorded in job_events table
- Worker can be scaled horizontally (multiple instances safe)

---

## Plan 04-04: Observability

**File:** `.planning/phases/04-backend-api-services-jobs/04-04-PLAN.md`
**Wave:** 2 | **Type:** execute | **Autonomous:** true | **Depends:** 04-01, 04-02

Creates structured logging, audit logging, and OpenTelemetry light integration.

**Requirements:** F7-06 (audit logging), F14-01 (structured audit logs), F14-02 (job event timeline), F14-03 (tool call logging), F14-04 (file tracking), F14-05 (proposal logging)

**Audit log schema (per D-57):**
- `event_id` — unique event identifier (UUID)
- `trace_id` — distributed trace identifier
- `actor` — who performed the action
- `capability` — which capability was exercised
- `domain` — which domain (vault, agent, exchange, research)
- `target` — what was targeted
- `result` — outcome (success, denied, error)
- `timestamp` — when it happened
- `metadata` — additional context (JSONB)

**Must-haves:**
- structlog configured with JSON output for production
- All sensitive operations emit audit log entries with trace_id
- Job event timeline queryable via `/jobs/{job_id}/events`
- File read/write tracked in audit_logs
- Proposal lifecycle logged with all state transitions
- OpenTelemetry spans created for HTTP requests and job processing
- Trace context propagated through async job processing

---

## Plan 04-05: React SPA + Workspace Shell

**File:** `.planning/phases/04-backend-api-services-jobs/04-05-PLAN.md`
**Wave:** 3 | **Type:** execute | **Autonomous:** true | **Depends:** 04-02

Creates the React + Vite + TypeScript SPA with workspace shell, note editor, and all workspace views.

**Requirements:** F15-01 (React + Vite + TypeScript), F15-02 (workspace shell), F15-03 (note editor), F15-04 (note view), F15-05 (exchange workspace), F15-06 (research workspace), F15-07 (settings UI)

**Frontend stack (per D-59 to D-62):**
- React 18 + Vite + TypeScript SPA
- TanStack Query for server state
- Zustand for UI state
- CodeMirror 6 for note editor
- shadcn/ui primitives for UI components

**Must-haves:**
- Vite dev server starts and SPA loads
- Workspace shell with sidebar, vault tree, search entry, jobs indicator
- Note editor with CodeMirror 6 (Markdown syntax highlighting)
- Note rendered view with metadata panel
- Exchange workspace: proposal list, diff view, approve/reject controls
- Research workspace: job status, source list, synthesis view
- Settings/policy workspace config UI
- All views connect to backend API via TanStack Query
- TanStack Query mutation hooks for all write operations

---

## Plan 04-06: Docker Compose + Caddy + Deployment Docs

**File:** `.planning/phases/04-backend-api-services-jobs/04-06-PLAN.md`
**Wave:** 3 | **Type:** execute | **Autonomous:** true | **Depends:** 04-03, 04-04, 04-05

Creates Docker Compose setup, Caddy reverse proxy configuration, and self-hosted deployment documentation.

**Requirements:** F16-01 (Docker Compose), F16-02 (Caddy), F16-03 (deployment docs), F16-04 (env config)

**Docker Compose services (per D-63):**
- `postgres` — PostgreSQL 16 with pgvector extension
- `app-api` — FastAPI application
- `worker-runtime` — background job worker
- `caddy` — reverse proxy with auto-HTTPS

**Must-haves:**
- `docker-compose.yml` starts full stack (postgres, api, worker)
- `Dockerfile` for app-api builds successfully
- `Dockerfile` for worker-runtime builds successfully
- Caddyfile configures HTTPS and routes to api/worker
- `.env.example` documents all required environment variables
- `DEPLOYMENT.md` explains self-hosted setup step-by-step
- Docker Compose health checks configured for all services
- Volume mounts for workspace data persistence

---

## Requirement Coverage Matrix

| Requirement | Plan |
|-------------|------|
| F7-01 FastAPI modular backend | 04-02 |
| F7-02 REST endpoints | 04-02 |
| F7-03 WebSocket/SSE | 04-02 |
| F7-04 Postgres operational DB | 04-01, 04-02 |
| F7-05 Background worker | 04-03 |
| F7-06 Audit logging | 04-04 |
| F8-01 Tables | 04-01 |
| F8-02 Note projection sync | 04-01 |
| F8-03 Job queue | 04-03 |
| F13-01 Postgres-backed job queue | 04-03 |
| F13-02 Job types | 04-03 |
| F13-03 Job status tracking | 04-03 |
| F13-04 Retries | 04-03 |
| F14-01 Structured audit logs | 04-04 |
| F14-02 Job event timeline | 04-04 |
| F14-03 Tool call logging | 04-04 |
| F14-04 File tracking | 04-04 |
| F14-05 Proposal logging | 04-04 |
| F15-01 React + Vite + TS | 04-05 |
| F15-02 Workspace shell | 04-05 |
| F15-03 Note editor | 04-05 |
| F15-04 Note view | 04-05 |
| F15-05 Exchange workspace | 04-05 |
| F15-06 Research workspace | 04-05 |
| F15-07 Settings UI | 04-05 |
| F16-01 Docker Compose | 04-06 |
| F16-02 Caddy | 04-06 |
| F16-03 Deployment docs | 04-06 |
| F16-04 Env config | 04-06 |

---

## Success Criteria

1. FastAPI app starts with all modules registered
2. All documented REST endpoints respond correctly
3. SSE delivers job status updates in real-time
4. All Postgres tables exist with correct schema
5. Note projection syncs with filesystem changes
6. Background worker claims and processes jobs
7. Audit logs capture all sensitive operations with trace IDs
8. Docker Compose starts full stack (api, worker, postgres)
9. Caddy reverse proxy configured with HTTPS
10. Self-hosted deployment docs are complete

---

## Next Steps

Execute the plans in wave order:

```bash
# Wave 1 (parallel)
Execute: /gsd:execute-phase 04-01
Execute: /gsd:execute-phase 04-02

# Wave 2 (after wave 1)
/gsd:execute-phase 04-03
/gsd:execute-phase 04-04

# Wave 3 (after wave 2)
/gsd:execute-phase 04-05
/gsd:execute-phase 04-06
```
