# Requirements — Knowledge OS Core v1

## v1 Requirements

### F1 — Knowledge Filesystem
- [x] **F1-01**: Canonical filesystem structure with `user-vault/`, `agent-brain/`, `exchange/`, `raw/`, `runtime/` directories
- [x] **F1-02**: Note schemas with YAML frontmatter (`id`, `kind`, `status`, `title`, `tags`, `links`, `source`, `policy`)
- [x] **F1-03**: Note types: daily, project, area, resource, archive-item, fleeting, permanent, research-note, source-note, synthesis-note, index-note, template-instance

### F2 — Template System
- [x] **F2-01**: Template profiles (PARA-like, Daily-first, Zettelkasten-like, Research Lab, Project OS)
- [x] **F2-02**: Base templates: daily, project, area, resource, fleeting, permanent, source, synthesis, research brief
- [x] **F2-03**: Template profile selection at workspace creation

### F3 — Daily Notes
- [x] **F3-01**: Daily note creation by date
- [x] **F3-02**: Daily note templates with configurable sections (Inbox, Focus, Notes, Linked Projects, Decisions, Tasks, Review)
- [x] **F3-03**: Daily note linking to projects/areas

### F4 — Git / Revision Boundary
- [ ] **F4-01**: Git repositories: `user-vault.git` and `agent-brain.git`
- [ ] **F4-02**: Branch strategy: `main`, `proposal/<actor>/<id>`, `research/<job-id>`, `import/<source>/<ts>`, `review/<id>`
- [ ] **F4-03**: Worktree creation and management for proposals and jobs
- [ ] **F4-04**: Diff generation for proposals
- [ ] **F4-05**: Patch bundle creation and application
- [ ] **F4-06**: Merge/cherry-pick/apply approved changes
- [ ] **F4-07**: Rollback to previous revisions

### F5 — Exchange Zone
- [ ] **F5-01**: Proposals with metadata (proposal_type, source_domain, target_domain, status, branch_name, worktree_path)
- [ ] **F5-02**: Proposal states: draft, generated, awaiting_review, approved, rejected, applied, superseded, failed
- [ ] **F5-03**: Review bundles with diffs and provenance
- [ ] **F5-04**: Research output staging
- [ ] **F5-05**: Patch pipeline: create → review → approve/reject → apply

### F6 — Policy Engine
- [x] **F6-01**: Capability model for vault.*, agent.*, research.*, exchange.*
- [x] **F6-02**: Policy outcomes: allow_direct, allow_patch_only, allow_in_exchange_only, allow_with_approval, deny
- [x] **F6-03**: Policy rules by actor, domain, capability, path, note_type, sensitivity
- [x] **F6-04**: Policy checks before all sensitive mutations
- [x] **F6-05**: Safe defaults: read broad, create in safe zones, edit patch-first, delete/move/rename gated

### F7 — Backend / API
- [ ] **F7-01**: FastAPI modular backend with internal modules (auth, vault, templates, gitops, exchange, policy, approvals, retrieval, agent, research, jobs, audit)
- [ ] **F7-02**: REST API endpoints: `/vault/*`, `/templates/*`, `/retrieval/*`, `/copilot/*`, `/exchange/*`, `/approvals/*`, `/research/*`, `/jobs/*`, `/policy/*`, `/admin/*`
- [ ] **F7-03**: WebSocket/SSE for job status updates
- [ ] **F7-04**: Postgres operational database with full schema
- [ ] **F7-05**: Background worker for async jobs
- [x] **F7-06**: Audit logging for all sensitive operations

### F8 — Database Schema
- [ ] **F8-01**: Tables: workspaces, actors, notes_projection, policy_rules, approvals, proposals, jobs, job_events, chunks, embeddings, artifacts, audit_logs
- [ ] **F8-02**: Note projection sync with filesystem
- [ ] **F8-03**: Job queue with claim, status, retries

### F9 — Agent Brain
- [ ] **F9-01**: Agent Brain filesystem: SOUL.md, MEMORY.md, USER.md, skills/, heuristics/, reflections/, sessions/, scratchpads/, playbooks/
- [ ] **F9-02**: Agent identity and constitution (SOUL.md)
- [ ] **F9-03**: Persistent curated memory (MEMORY.md)
- [ ] **F9-04**: User operational profile (USER.md)
- [ ] **F9-05**: Skills with manifest.yaml and reusable procedures
- [ ] **F9-06**: Session summaries and traces
- [ ] **F9-07**: Self-improve within agent domain (free) vs user vault (restricted)

### F10 — Retrieval
- [ ] **F10-01**: PostgreSQL FTS for lexical search
- [ ] **F10-02**: pgvector for semantic search
- [ ] **F10-03**: Hybrid retrieval (FTS + vector)
- [ ] **F10-04**: Context packs with note reference, snippet, score, metadata, neighbors, provenance
- [ ] **F10-05**: Chunking guided by headings
- [ ] **F10-06**: Incremental indexing with rebuild capability

### F11 — Note Copilot
- [ ] **F11-01**: Per-note AI assistance panel
- [ ] **F11-02**: Explain note functionality
- [ ] **F11-03**: Summarize note functionality
- [ ] **F11-04**: Suggest internal links
- [ ] **F11-05**: Suggest tags
- [ ] **F11-06**: Suggest structure improvements
- [ ] **F11-07**: Propose patch for note changes
- [ ] **F11-08**: Clear UX distinction: conversation vs suggestion vs proposal

### F12 — Research Runtime
- [ ] **F12-01**: Research brief and blueprint generation
- [ ] **F12-02**: Research job lifecycle (queued, planning, discovering, crawling, parsing, synthesizing, awaiting_approval, completed, failed)
- [ ] **F12-03**: Source fetch and crawl
- [ ] **F12-04**: Raw artifact materialization
- [ ] **F12-05**: Synthesis generation
- [ ] **F12-06**: Ingest proposal bundle
- [ ] **F12-07**: Research outputs: blueprint.md, raw/, synthesis.md, manifest.yaml, ingest-proposal.patch

### F13 — Jobs System
- [ ] **F13-01**: Postgres-backed job queue with row claiming
- [ ] **F13-02**: Job types: index_note, reindex_scope, generate_embeddings, research_job, parse_source, apply_patch_bundle, reflect_agent, consolidate_memory
- [ ] **F13-03**: Job status tracking with events
- [ ] **F13-04**: Retries for idempotent steps

### F14 — Observability & Audit
- [x] **F14-01**: Structured audit logs with event_id, trace_id, actor, capability, domain, target, result, timestamp
- [x] **F14-02**: Job event timeline
- [x] **F14-03**: Tool call logging
- [x] **F14-04**: File read/write tracking
- [x] **F14-05**: Proposal lifecycle logging

### F15 — Frontend / UI
- [ ] **F15-01**: React + Vite SPA with TypeScript
- [ ] **F15-02**: Workspace shell with sidebar, vault tree, search entry, jobs indicator
- [ ] **F15-03**: Note editor with CodeMirror 6
- [ ] **F15-04**: Note rendered view with metadata panel
- [ ] **F15-05**: Exchange workspace with proposal list, diff view, approval/reject controls
- [ ] **F15-06**: Research workspace with job status, source list, synthesis view
- [ ] **F15-07**: Settings/Policy workspace config UI

### F16 — Deployment
- [ ] **F16-01**: Docker Compose with app-api, worker-runtime, postgres
- [ ] **F16-02**: Caddy for reverse proxy with HTTPS
- [ ] **F16-03**: Self-hosted deployment documentation
- [ ] **F16-04**: Environment-based configuration

## v2 Requirements (Deferred)

- [ ] Multi-user basic support
- [ ] Partial patch application
- [ ] Markdown AST-aware transforms
- [ ] Richer template profiles
- [ ] Better reranking
- [ ] Multiple agent personas
- [ ] OIDC authentication adapter
- [ ] Optional Qdrant for advanced retrieval
- [ ] Optional S3-compatible object storage

## Out of Scope

- **Real-time collaboration** — markdown-first editor focus, not Google Docs
- **Full multi-user/SSO/SAML** — single-user self-hosted is the focus
- **Enterprise controls** — out of OSS core scope
- **Mobile app** — web app is primary interface
- **Complex connector ecosystem** — v1 is minimal integrations
- **Microservices** — modular monolith + workers is sufficient
- **Kubernetes** — Docker Compose is enough for v1
- **LangChain as backbone** — PydanticAI + own abstractions
- **Qdrant/Redis early** — pgvector in Postgres resolves v1
- **MCP internally** — future exposure surface, not internal bus
- **Sync protocol own** — Syncthing as external solution
- **Template marketplace** — static profiles in v1

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| F1-01 to F1-03 | Phase 1 | — |
| F2-01 to F2-03 | Phase 1 | — |
| F3-01 to F3-03 | Phase 1 | — |
| F4-01 to F4-07 | Phase 2 | — |
| F5-01 to F5-05 | Phase 2 | — |
| F6-01 to F6-05 | Phase 3 | — |
| F7-01 to F7-06 | Phase 4 | — |
| F8-01 to F8-03 | Phase 4 | — |
| F9-01 to F9-07 | Phase 5 | — |
| F10-01 to F10-06 | Phase 6 | — |
| F11-01 to F11-08 | Phase 7 | — |
| F12-01 to F12-07 | Phase 8 | — |
| F13-01 to F13-04 | Phase 4/9 | — |
| F14-01 to F14-05 | Phase 4 | — |
| F15-01 to F15-07 | Phase 4/5 | — |
| F16-01 to F16-04 | Phase 4 | — |

---
*Created: 2026-03-31*
