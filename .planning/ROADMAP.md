# Roadmap — Knowledge OS Core v1

**Project:** Knowledge OS Core
**Phases:** 10 | **Granularity:** Fine
**Created:** 2026-03-31

## Phase Summary

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Knowledge Filesystem Foundation | Establish canonical filesystem structure, schemas, templates, and daily notes | F1, F2, F3 | 6 |
| 2 | Git / Exchange Boundary | Implement revision layer with Git, worktrees, diff, patch, and Exchange Zone | F4, F5 | 11 |
| 3 | Policy Engine | Build capability-based policy system with safe defaults | F6 | 5 |
| 4 | Backend / API / Services / Jobs | Create FastAPI modular backend, Postgres schema, worker, audit | F7, F8, F13, F14, F15, F16 | 6 |
| 5 | Agent Brain | Implement persistent agent memory and skills system | F9 | 7 |
| 6 | Retrieval | Build hybrid search (FTS + vector) with context packs | F10 | 6 |
| 7 | Note Copilot | Create per-note AI assistance with patch proposals | F11 | 8 |
| 8 | Research Runtime | Implement research job pipeline with crawl/parse/synth | F12 | 7 |
| 9 | Durability / HITL | Add retries, checkpoint/resume, approval-aware execution | F13 | 4 |
| 10 | MCP / Integrations | Expose MCP servers for vault, agent, research, retrieval | — | 4 |

---
**
## Phase 1: Knowledge Filesystem Foundation

**Goal:** Establish the canonical filesystem structure, schemas, templates, and daily notes — the sovereign foundation of the entire system.

**Status:** Plan 1/1 COMPLETE (2026-03-31)

**Requirements:** F1-01, F1-02, F1-03, F2-01, F2-02, F2-03, F3-01, F3-02, F3-03

**Success Criteria:**
1. `user-vault/`, `agent-brain/`, `exchange/`, `raw/`, `runtime/` directories exist with correct structure
2. Note frontmatter schema validates `id`, `kind`, `status`, `title`, `tags`, `links`, `source`, `policy` fields
3. All 11 note types are supported with correct schema
4. At least 3 template profiles are selectable (PARA-like, Daily-first, Zettelkasten-like)
5. Base templates render correctly for all 9 template types
6. Daily notes can be created by date with selected template

**Key Deliverables:**
- Directory structure scaffold
- Note schema validation
- Template profile system
- Daily note creation

**Plan 1 Commits:**
- d97c368: create root directory hierarchy
- fedcff0: create agent brain core files
- c4eb96a: create note frontmatter schema
- 06d9b39: create vault configuration
- 6aaacf1: create 5 template profiles
- 320a30f: create 9 base templates
- ffc02b0: create daily note creation script
- 3345e99: create sample notes
- dd3baf9: create workspace materialization script

---

## Phase 2: Git / Exchange Boundary

**Goal:** Implement the revision layer and Exchange Zone — the audit boundary that prevents silent mutations.

**Status:** Plan 2/1 COMPLETE (2026-03-31)

**Requirements:** F4-01, F4-02, F4-03, F4-04, F4-05, F4-06, F4-07, F5-01, F5-02, F5-03, F5-04, F5-05

**Success Criteria:**
1. Git repos initialize correctly for user-vault and agent-brain
2. Proposal branches create with correct naming convention
3. Worktrees spawn and cleanup correctly
4. Diff generation produces readable output for any note change
5. Patch bundles create and apply cleanly to main
6. Merge/cherry-pick works for approved proposals
7. Rollback restores previous state correctly
8. Exchange Zone proposals track all required metadata
9. Proposal state machine transitions correctly (draft → generated → awaiting_review → approved/rejected → applied)
10. Review bundles display diff and provenance clearly
11. User can approve/reject/apply proposals through UI

**Key Deliverables:**
- Git service with full worktree support
- Proposal and branch lifecycle management
- Patch pipeline with diff/view/apply
- Exchange Zone API

**Plan 1:**
- 02-01-PLAN.md — NOT EXECUTED

**Plan 2 (02-02-PLAN.md):**
- Commits: 1605ad3, 7dd67d0, de9d1ad, 8191865, 98eee8a, 60e0305, b6a32a1, 74d4150, 2b3a748
- Status: COMPLETE
- Key files: src/services/git_service.py, src/services/proposal_service.py, src/services/patch_service.py, src/api/exchange.py

---

## Phase 3: Policy Engine

**Goal:** Build the capability-based policy system — the gatekeeper that prevents unauthorized mutations.

**Requirements:** F6-01, F6-02, F6-03, F6-04, F6-05

**Success Criteria:**
1. All 4 capability groups defined (vault.*, agent.*, research.*, exchange.*)
2. Policy evaluator returns correct outcomes for all 5 result types
3. Policy rules can be created by actor, domain, capability, path, note_type, sensitivity
4. Every sensitive mutation call passes through policy check and is logged
5. Safe defaults prevent silent writes: read broad, create in safe zones, edit patch-first, delete gated

**Key Deliverables:**
- Capability model definition
- Policy evaluator service
- Policy rule CRUD
- Policy check integration in all services

---

## Phase 4: Backend / API / Services / Jobs

**Goal:** Create the FastAPI modular backend with Postgres schema, worker, observability, and initial UI.

**Requirements:** F7-01, F7-02, F7-03, F7-04, F7-05, F7-06, F8-01, F8-02, F8-03, F13-01, F13-02, F13-03, F13-04, F14-01, F14-02, F14-03, F14-04, F14-05, F15-01, F15-02, F15-03, F15-04, F15-05, F15-06, F15-07, F16-01, F16-02, F16-03, F16-04

**Success Criteria:**
1. FastAPI app starts with all modules registered
2. All documented REST endpoints respond correctly
3. WebSocket/SSE delivers job status updates in real-time
4. All Postgres tables exist with correct schema
5. Note projection syncs with filesystem changes
6. Background worker claims and processes jobs
7. Audit logs capture all sensitive operations with trace IDs
8. Docker Compose starts full stack (api, worker, postgres)
9. Caddy reverse proxy configured with HTTPS
10. Self-hosted deployment docs are complete and accurate

**Key Deliverables:**
- Modular FastAPI application
- Complete Postgres schema with migrations
- Background worker process
- Audit logging system
- Workspace shell UI
- Note editor (CodeMirror 6)
- Exchange review UI
- Research workspace UI
- Docker Compose setup
- Deployment documentation

---

## Phase 5: Agent Brain

**Goal:** Implement the persistent Agent Brain — the private memory domain where the agent evolves freely.

**Requirements:** F9-01, F9-02, F9-03, F9-04, F9-05, F9-06, F9-07

**Success Criteria:**
1. Agent Brain filesystem exists with all required files (SOUL.md, MEMORY.md, USER.md, skills/, etc.)
2. SOUL.md contains agent identity and constitution
3. MEMORY.md persists curated memories across sessions
4. USER.md captures user operational profile
5. Skills can be created with manifest.yaml and invoked correctly
6. Session summaries persist and are searchable
7. Agent can self-improve freely in own domain but is restricted in user vault

**Key Deliverables:**
- Agent Brain filesystem structure
- SOUL.md, MEMORY.md, USER.md templates
- Skill manifest and invocation system
- Session summary persistence
- Self-improve workflow with restrictions

---

## Phase 6: Retrieval

**Goal:** Build hybrid retrieval (FTS + vector) with context packs — the derived layer that never becomes sovereign.

**Requirements:** F10-01, F10-02, F10-03, F10-04, F10-05, F10-06

**Success Criteria:**
1. PostgreSQL FTS indexes notes and returns relevant results
2. pgvector embeddings generated and stored for all notes
3. Hybrid search combines FTS and vector results intelligently
4. Context packs contain: note reference, snippet, score, why_matched, metadata, neighbors, provenance
5. Heading-guided chunking produces coherent chunks
6. Incremental index updates on note changes; full rebuild completes successfully

**Key Deliverables:**
- FTS index with PostgreSQL
- pgvector embedding pipeline
- Hybrid retrieval algorithm
- Context pack builder
- Chunking strategy
- Index management (incremental + rebuild)

---

## Phase 7: Note Copilot

**Goal:** Create per-note AI assistance with patch proposals — the first "magic" that doesn't break sovereignty.

**Requirements:** F11-01, F11-02, F11-03, F11-04, F11-05, F11-06, F11-07, F11-08

**Success Criteria:**
1. User can open copilot panel on any note
2. "Explain" returns accurate note summary in context
3. "Summarize" produces concise recap
4. "Suggest links" proposes relevant internal links with reasoning
5. "Suggest tags" proposes appropriate tags
6. "Suggest structure" identifies improvement opportunities
7. "Propose patch" generates diff/patch instead of direct edit
8. UX clearly distinguishes: conversation (chat), suggestion (recommendation), proposal (patch-to-approve)

**Key Deliverables:**
- Note copilot panel UI
- Explain/summarize actions
- Link/tag/structure suggestions
- Patch proposal generation
- Clear UX distinction between response types

---

## Phase 8: Research Runtime

**Goal:** Implement the research job pipeline — turning ephemeral chat into durable, traceable knowledge production.

**Requirements:** F12-01, F12-02, F12-03, F12-04, F12-05, F12-06, F12-07

**Success Criteria:**
1. User can create research brief with goal, questions, scope, depth, max_sources
2. Research job transitions through all states correctly
3. Crawler fetches sources and produces raw markdown
4. Raw artifacts persist with provenance metadata
5. Synthesis generates coherent summary from multiple sources
6. Ingest proposal bundle creates correctly for Exchange Zone
7. Research outputs traceable: blueprint.md, raw/, normalized/, synthesis.md, manifest.yaml, ingest-proposal.patch

**Key Deliverables:**
- Research brief UI
- Job lifecycle management
- Crawl4AI integration
- Raw artifact materialization
- Synthesis generation
- Ingest proposal bundle
- Research workspace UI

---

## Phase 9: Durability / HITL

**Goal:** Add retries, checkpoint/resume, approval-aware execution — making the system robust for real workloads.

**Requirements:** F13-01, F13-02, F13-03, F13-04 (refinements)

**Success Criteria:**
1. Failed jobs retry with exponential backoff up to max_attempts
2. Long-running jobs can checkpoint and resume after interrupt
3. Approval-required jobs pause and resume after approval
4. Job idempotency verified — re-running same job produces same result

**Key Deliverables:**
- Retry logic with backoff
- Checkpoint/resume infrastructure
- Approval-aware job execution
- Idempotency verification

---

## Phase 10: MCP / Integrations

**Goal:** Expose MCP servers for vault, agent, research, retrieval — the standardized integration surface.

**Success Criteria:**
1. `vault-user-mcp` server exposes note CRUD with policy enforcement
2. `agent-brain-mcp` server exposes memory and skill operations
3. `research-mcp` server exposes job creation and status
4. `retrieval-mcp` server exposes search and context pack retrieval
5. All MCP calls pass through internal policy engine
6. No MCP path bypasses API/policy layer

**Key Deliverables:**
- MCP server implementations
- Policy enforcement on MCP calls
- MCP exposure documentation

---

## Phase Ordering Rationale

The build order is not arbitrary — each phase builds on the previous:

1. **Filesystem first** — establishes the sovereign foundation before anything else
2. **Git/Exchange second** — builds the audit boundary before any automated mutation is possible
3. **Policy third** — the gatekeeper that protects the boundary established in phase 2
4. **Backend fourth** — exposes everything through API; audit/logging here covers all future work
5. **Agent Brain fifth** — plugs in the agentic layer without risk of vault pollution (policy protects)
6. **Retrieval sixth** — builds the derived layer that serves the agent and copilot
7. **Note Copilot seventh** — uses retrieval + agent + policy to assist without invading
8. **Research eighth** — the most complex workflow, now with full system support
9. **Durability ninth** — hardening after all workflows exist
10. **MCP last** — external exposure only after internal contracts are solid

---

## Research Flags

- **Phase 4 (Backend):** WebSocket vs SSE decision — verify best practice for job status
- **Phase 6 (Retrieval):** Chunking strategy — may need tuning based on actual note sizes
- **Phase 8 (Research):** Crawl4AI version compatibility — verify with latest release

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Already decided in STACK_DECISION_RECORD |
| Features | HIGH | Well-defined in SSOT/PRD |
| Architecture | HIGH | 3 major docs define architecture clearly |
| Build Order | HIGH | Mandated by product laws, not arbitrary |

**Overall confidence:** HIGH — extensive existing documentation provides strong foundation.

---

*Roadmap created: 2026-03-31*
*Phase 2 plan created: 2026-03-31*
*Ready for execution: yes*
