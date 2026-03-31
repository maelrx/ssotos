# Architecture Patterns

**Domain:** Knowledge OS / Agent-aware knowledge management system
**Researched:** 2026-03-31
**Confidence:** MEDIUM-HIGH

## System Overview

The Knowledge OS Core follows a **plane-based architecture** with five distinct logical layers that separate concerns from filesystem sovereignty through to human presentation.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION PLANE                        │
│         Web UI / Note Editor / Exchange Review               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     CONTROL PLANE                             │
│   API Gateway │ Policy Engine │ Approval │ Auth │ Audit    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTELLIGENCE PLANE                         │
│  Retrieval │ Note Copilot │ Agent │ Embedding Pipeline      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION PLANE                            │
│    Worker System │ Crawler │ Indexing │ Research Jobs       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                KNOWLEDGE FILESYSTEM PLANE                    │
│   User Vault │ Agent Brain │ Exchange Zone │ Raw Artifacts  │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| Planes are logical, not physical | Modular monolith deploys as single unit; planes define boundaries, not services | PRD Section 8 |
| Filesystem is canonical | Markdown files are sovereign; DB is operational projection | PRD Section 3.1, 3.2 |
| Policy precedes mutation | Every meaningful action passes Policy Engine before execution | PRD Section 12.1 |
| Patch-first in user domain | Changes default to diff/patch proposals, not direct overwrite | PRD Section 3.5 |
| Git as revision substrate | Provides diff, patch, rollback, worktrees; NOT policy engine or queue | PRD Section 11.1 |

---

## Component Boundaries

### 1. Knowledge Filesystem Plane

**Responsibility:** Canonical, durable content storage

| Domain | Path | Sovereignty | Notes |
|--------|------|-------------|-------|
| User Vault | `user-vault/` | User owns | Markdown canonical, YAML frontmatter |
| Agent Brain | `agent-brain/` | Agent owns | SOUL.md, MEMORY.md, USER.md, skills/, heuristics/ |
| Exchange Zone | `exchange/` | Shared governance | proposals/, reviews/, research/ |
| Raw Artifacts | `raw/` | System owns | Web crawls, parsed docs, manifests |
| Templates | `user-vault/Templates/` | User curates | Note type schemas |

**Boundary enforcement:**
- Agent Brain is physically separate from User Vault (different directory trees)
- No direct writes from Agent to User Vault without Exchange review
- Raw artifacts are staging, never canonical

### 2. Control Plane

**Responsibility:** Permissions, mutations, audit

```
┌──────────────────────────────────────────────────────┐
│                   API Gateway (FastAPI)               │
│  - Modular routers by domain (vault, exchange, etc.) │
│  - Auth middleware                                   │
│  - Request validation (Pydantic)                     │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                  Policy Engine                        │
│  - evaluate(capability, actor, path, context)        │
│  - returns: allow_direct | allow_patch_only |        │
│             allow_exchange_only | allow_with_approval│
│             | deny                                   │
│  - Deterministic, inspectable, testable              │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                Approval Engine                         │
│  - Creates approval records for gated operations     │
│  - Records reviewer, comment, decision               │
│  - Triggers patch application on approval            │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                 Audit Module                           │
│  - Logs: actor, action, target, decision, metadata   │
│  - Sensitive operations: edits, deletions, policy   │
│  - Proposal lifecycle events                        │
└──────────────────────────────────────────────────────┘
```

### 3. Intelligence Plane

**Responsibility:** Meaning derivation, retrieval, AI assistance

```
┌─────────────────────────────────────────────────────┐
│               Retrieval Service                      │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ Lexical FTS  │  │ pgvector    │  │ Context   │ │
│  │ (Postgres)   │  │ (semantic)  │  │ Pack      │ │
│  └─────────────┘  └─────────────┘  └───────────┘ │
│         │                │                │        │
│         └────────────────┼────────────────┘        │
│                          ▼                          │
│               Hybrid Retrieval                       │
│               (weighted scoring)                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              Note Copilot Service                     │
│  - explain / summarize / suggest-links              │
│  - propose structural changes                       │
│  - generate patch proposals                         │
│  - Always proposes, never directly applies         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 Agent Runtime                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │
│  │ Planner  │ │ Executor  │ │ Reflector │ │Memory │ │
│  │          │ │          │ │          │ │Curator│ │
│  └──────────┘ └──────────┘ └──────────┘ └───────┘ │
│                                                      │
│  Uses PydanticAI tools + RunContext dependency       │
│  Self-improves within Agent Brain only              │
└─────────────────────────────────────────────────────┘
```

### 4. Execution Plane

**Responsibility:** Async, long-running, or expensive operations

```
┌─────────────────────────────────────────────────────┐
│              Postgres-Backed Job Queue               │
│  - Row-based with FOR UPDATE SKIP LOCKED claiming   │
│  - Job types: index_note, generate_embeddings,      │
│    research_job, apply_patch, reflect_agent        │
│  - Event log per job for observability             │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Worker Process(es)                      │
│  - Polls/claims jobs                               │
│  - Executes: Crawl4AI, Docling, embedding,          │
│    synthesis, indexing                             │
│  - Publishes job events to audit                   │
└─────────────────────────────────────────────────────┘
```

### 5. Presentation Plane

**Responsibility:** Human interaction surfaces

| Surface | Tech | Purpose |
|---------|------|---------|
| Workspace Shell | React + Vite | Navigation, vault tree, search entry |
| Note Editor | CodeMirror 6 | Markdown editing, rendered preview |
| Note Copilot Panel | React + TanStack Query | AI assistance on notes |
| Exchange Review | Diff viewer | Proposal review, approve/reject |
| Research Workspace | React | Job status, artifacts, synthesis |
| Job Status | Polling via TanStack Query | Background job progress |

---

## Data Flow

### Note Creation Flow

```
User UI ──POST /vault/note──▶ API Gateway
                                  │
                                  ▼
                            Policy Engine
                            (vault.create_note)
                                  │
                         ┌────────┴────────┐
                         │  allow_direct   │
                         └────────┬────────┘
                                  │
                                  ▼
                          GitOps Service
                          (create note file)
                                  │
                                  ▼
                          Filesystem Write
                          (user-vault/...)
                                  │
                                  ▼
                          Notes Projection
                          (DB sync)
                                  │
                                  ▼
                          Indexing Job
                          (queued to worker)
```

### Agent Proposal Flow

```
User/Trigger ──▶ Agent Runtime
                      │
                      ▼
              Policy Engine
              (agent.read_memory: allow_direct)
                      │
                      ▼
              Agent reads User Vault context
              (via Retrieval, via policy-gated access)
                      │
                      ▼
              Agent generates proposal
                      │
                      ▼
              Policy Engine
              (vault.propose_patch: allow_exchange_only)
                      │
                      ▼
              GitOps Service
              (creates proposal branch + worktree)
                      │
                      ▼
              Exchange Zone
              (stores proposal metadata + patch)
                      │
                      ▼
              Approval Engine
              (creates approval record if needed)
```

### Patch Application Flow

```
User reviews proposal ──▶ UI: approve
                              │
                              ▼
                        Approval Engine
                        (record: approved)
                              │
                              ▼
                        GitOps Service
                        (merge proposal branch)
                              │
                              ▼
                        Filesystem
                        (main branch updated)
                              │
                              ▼
                        Notes Projection sync
                              │
                              ▼
                        Re-index affected notes
```

### Research Job Flow

```
User creates research brief ──▶ Research Module
                                    │
                                    ▼
                            Job queued: research_job
                                    │
                                    ▼
                            Worker: fetch sources
                            (Crawl4AI + Playwright)
                                    │
                                    ▼
                            Worker: parse artifacts
                            (Docling)
                                    │
                                    ▼
                            Raw Artifacts stored
                            (raw/web/, raw/docs/)
                                    │
                                    ▼
                            Worker: generate synthesis
                            (LLM)
                                    │
                                    ▼
                            Exchange Zone
                            (synthesis + ingest proposal)
                                    │
                                    ▼
                            User reviews in Exchange UI
                            (approve / reject / apply)
```

---

## Suggested Build Order

The mandatory build order from the PRD reflects hard dependencies:

| Phase | Components | Dependency Rationale |
|-------|------------|---------------------|
| **0** | Project structure, Docker Compose, dev environment, workspace init | Foundation only |
| **1** | Canonical filesystem, schemas, note CRUD, templates, daily notes | No dependencies; everything builds on files |
| **2** | Git boundary, Exchange Zone, proposal model, diff/patch, approval flow | Requires filesystem structure to version |
| **3** | Policy engine, capability model, policy checks in all sensitive flows | Requires Exchange Zone to understand what needs gating |
| **4** | Retrieval (chunking, FTS, pgvector, context packs) | Requires notes to exist and be queryable |
| **5** | Agent Brain, Note Copilot, patch-first proposal generation | Requires Policy Engine (agent cannot self-improve without boundaries) |
| **6** | Research Runtime (brief, fetch, parse, synthesis, ingest proposal) | Requires Agent Brain, Exchange Zone, and retrieval |
| **7** | Durability/HITL (LangGraph where needed), HITL approval loops | Requires all above to be stable |
| **8** | MCP exposure, integrations | Requires stable internal contracts |

### Critical Path

```
Filesystem/Schemas ──▶ Git/Exchange ──▶ Policy ──▶ Retrieval ──▶ Agent ──▶ Research
     (Phase 0-1)         (Phase 2)      (Phase 3)   (Phase 4)   (Phase 5)  (Phase 6)
```

**Why Policy comes before Agent:**
- Agent must operate within capability boundaries
- Agent self-improvement must be constrained to Agent Brain
- Patch-first mutation requires policy backing before agent can propose

**Why Retrieval comes before Agent:**
- Agent needs context to operate meaningfully
- Context packs require indexing infrastructure
- Agent should query retrieval, not stuff entire vault in prompt

---

## Scaling Considerations

### At 100 Users / 10K Notes

| Concern | Approach |
|---------|----------|
| API latency | FastAPI async, connection pooling |
| Retrieval quality | Postgres FTS + pgvector (sufficient) |
| Indexing | Incremental, job-based |
| Proposal volume | Single Exchange Zone sufficient |
| Agent并发 | Single agent runtime, sequential job processing |

**Expected bottleneck:** Retrieval ranking quality, not throughput

### At 1K Users / 100K Notes

| Concern | Approach |
|---------|----------|
| API | Consider API process horizontal scaling |
| Retrieval | Evaluate Qdrant migration for hybrid search sophistication |
| Proposal management | Archive stale proposals; add Exchange Zone pagination |
| Worker throughput | Multiple worker instances; job queue partitioning |
| Audit log volume | Archive or partition audit tables |

**Expected bottleneck:** Retrieval at scale; Exchange Zone review UX

### At 10K Users / 1M Notes

| Concern | Approach |
|---------|----------|
| Everything above, plus: | Consider read replicas for Postgres |
| Agent isolation | Per-workspace agent runtime isolation |
| Policy evaluation | Cache policy rules; invalidate on change |
| Search relevance | Reranking, BM25 + vector hybrid tuning |

**Expected bottleneck:** Cross-workspace retrieval federation; policy decision latency

### v1 Scaling Constraints

v1 targets **single workspace, thousands to tens of thousands of notes, one or few users**.

- Do not over-engineer for scale that will not arrive in v1
- Design interfaces that could later support sharding/partitioning
- Keep job processing simple until job volume demands sophistication
- pgvector is sufficient until retrieval quality becomes the primary complaint

---

## Architecture Patterns to Follow

### 1. Repository Pattern (Data Access)

Encapsulate all filesystem and database access behind interfaces:

```
IVaultRepository ──▶ FilesystemVaultRepository
                  ──▶ InMemoryVaultRepository (tests)

INotesProjection ──▶ PostgresNotesProjection
```

**Why:** Enables testing, future storage adapters, and clean boundaries between modules.

**Source:** Standard pattern;参见 PydanticAI deps injection model

### 2. Command/Query Separation (API Layer)

Separate mutation commands from read queries:

```
VaultCommands ──▶ create_note, update_note, propose_patch, delete_note
VaultQueries ──▶ get_note, list_notes, search_notes
```

**Why:** Policy Engine only needs to intercept mutations; reads can be more permissive.

### 3. Policy Decision Pattern

Policy decisions are explicit, auditable objects:

```python
@dataclass
class PolicyDecision:
    outcome: PolicyOutcome  # allow_direct, deny, etc.
    reason: str
    triggered_rule: Optional[PolicyRule]
    evaluation_context: dict
```

**Why:** Audit logs need decision records; debugging requires understanding which rule fired.

**Source:** Inspired by capability-based security models

### 4. Context Pack Pattern (Retrieval)

Retrieval returns enriched context, not raw chunks:

```python
@dataclass
class ContextPack:
    note_ref: str
    snippet: str
    score: float
    why_matched: str
    related_notes: list[str]
    provenance: ProvenanceFlags
    access_domain: Domain  # vault, exchange, raw, brain
```

**Why:** Prevents retrieval from becoming an opaque truth source; provenance is critical for trust.

### 5. Worktree-Isolated Proposals (Git)

Each proposal gets its own Git worktree:

```
proposal/<actor>/<id>/  ──▶ isolated branch + worktree
                           ──▶ patch bundle
                           ──▶ metadata in Exchange Zone
```

**Why:** Isolation prevents proposal edits from affecting main vault; worktrees enable parallel proposals.

**Source:** Git worktree documentation; PRD Section 11.2

### 6. Job Registry Pattern (Workers)

All async work goes through a typed job registry:

```python
@job_registry.register(type="research_job", max_attempts=3)
async def run_research(job: ResearchJob):
    ...
```

**Why:** Observability (job events), retry logic, claim mechanism, and type safety for job payloads.

### 7. Module Adapter Pattern (Extensibility)

Optional components are adapter-based:

```
IEmbeddingProvider ──▶ OpenAIEmbeddingAdapter
                    ──▶ LocalEmbeddingAdapter

IStorageAdapter ──▶ LocalFilesystemAdapter
                 ──▶ S3CompatibleAdapter
```

**Why:** Allows BYOK flexibility without core dependency on specific providers.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Vault Pollution

**What:** Agent writes directly to User Vault without review, or raw research dumps into canon.

**Why bad:** Collapses the domain separation that is the core value proposition.

**Prevention:**
- Policy Engine blocks direct write capabilities to vault for agent actor
- Research outputs land in Exchange Zone, not vault
- Exchange Zone has mandatory review workflow before canonization

### Anti-Pattern 2: Embedding as Truth

**What:** Retrieval results become the sole source of knowledge; original notes are ignored.

**Why bad:** Embeddings are derived, lossy, and can drift from source.

**Prevention:**
- Context packs always include note references and provenance
- UI shows which note a chunk came from
- System remains usable without embeddings (lexical-only fallback)

### Anti-Pattern 3: Giant Prompt Syndrome

**What:** Stuffing entire vault or Agent Brain into every LLM context.

**Why bad:** Expensive, slow, loses specificity, risks context truncation.

**Prevention:**
- Policy restricts maximum context size
- Agent retrieves relevant context per task (not global memory dump)
- Modular prompt assembly with explicit sections

### Anti-Pattern 4: Exchange Zone Junk Drawer

**What:** Exchange Zone accumulates stale proposals, unprocessed research, and abandoned changes.

**Why bad:** UX friction for review; erodes trust in proposal workflow.

**Prevention:**
- Archive stale proposals after configurable retention
- Clear lifecycle: draft -> generated -> awaiting_review -> approved/rejected/applied
- Periodic cleanup jobs

### Anti-Pattern 5: Policy Magic

**What:** Policy rules become complex, opaque, or magical (inferred rather than explicit).

**Why bad:** Users cannot predict what will happen; audit loses meaning.

**Prevention:**
- Rules are explicit, inspectable, and deterministic
- Test policy decisions as unit tests
- Provide policy simulation/preview tool
- Policy changes are themselves auditable

### Anti-Pattern 6: Synchronous Empire

**What:** Heavy operations (crawling, embedding, synthesis) run synchronously in request path.

**Why bad:** API latency becomes unpredictable; timeouts; user experience suffers.

**Prevention:**
- All expensive operations are async jobs
- API returns job ID immediately; UI polls or websockets for completion
- Background worker processes heavy work

### Anti-Pattern 7: Soft Domain Boundaries

**What:** Modules import freely across domain boundaries, bypassing intended interfaces.

**Why bad:** Monolith becomes a big ball of mud; refactoring becomes impossible.

**Prevention:**
- Explicit module interfaces (not just imports)
- Dependency direction: Presentation -> Control -> Intelligence -> Execution -> Knowledge
- No circular dependencies between planes

### Anti-Pattern 8: Premature Microservices

**What:** Breaking modular monolith into services before operational necessity exists.

**Why bad:** Distributed system failure modes (network, latency, consistency) without benefit.

**Prevention:**
- Modular monolith is the explicit architecture for v1
- Extract services only when: independent deployment need, different scaling characteristics, or team split
- Strong internal boundaries enable later extraction

---

## Scaling Failure Modes and Mitigations

| Failure Mode | Symptom | Mitigation |
|--------------|---------|------------|
| **Retrieval quality degrades** | Users find search useless | Invest in chunking strategy early; hybrid scoring tuning; user feedback loop |
| **Exchange Zone overload** | Too many proposals; stale items | Archive policy; retention rules; pagination; clear lifecycle |
| **Policy evaluation bottleneck** | Latency on every mutation | Cache compiled policy rules; async policy evaluation for batch |
| **Worker backlog** | Jobs pile up; research takes hours | Worker autoscaling; job prioritization; timeout limits |
| **Vault divergence** | DB projection drifts from filesystem | Periodic reconciliation job; event-driven sync on write |
| **Agent context collapse** | Agent loses track of recent context | Explicit context management; session summaries; memory curation |
| **Git worktree leak** | Orphaned worktrees on failures | Cleanup job; worktree lifecycle tied to proposal lifecycle |
| **Embedding staleness** | Notes updated but search returns old chunks | Incremental re-indexing on note update; version/checksum tracking |

---

## Technology-Specific Patterns

### FastAPI Modular Monolith

```
app/
  api/
    routers/
      vault.py      # /vault/* endpoints
      exchange.py   # /exchange/* endpoints
      policy.py     # /policy/* endpoints
      retrieval.py # /retrieval/* endpoints
      copilot.py    # /copilot/* endpoints
      research.py   # /research/* endpoints
      jobs.py       # /jobs/* endpoints
  services/
    vault_service.py
    git_service.py
    policy_service.py
    retrieval_service.py
    agent_service.py
    research_service.py
  domain/
    models/         # Pydantic models for domain
    entities/      # Core domain entities
  infrastructure/
    repositories/  # Data access implementations
    workers/       # Job workers
```

**Key patterns:**
- APIRouter per domain module
- Dependency injection via Depends() for cross-cutting concerns
- Pydantic models as contracts between layers
- No cross-import between routers

### PydanticAI Agent Pattern

```python
agent = Agent(
    model="openai:gpt-4",
    deps_type=AgentDeps,
    tools=[vault_tools, exchange_tools, retrieval_tools],
)

@agent.tool
async def propose_note_patch(ctx: RunContext[AgentDeps], note_id: str, change: str):
    # Policy check first
    decision = await policy_service.evaluate(
        capability="vault.propose_patch",
        actor=ctx.deps.actor,
        path=note_id,
    )
    if decision.outcome == PolicyOutcome.DENY:
        raise PolicyDeniedError(decision.reason)
    # Proceed with proposal...
```

### Postgres + pgvector Pattern

```python
class NoteChunk(Base):
    __tablename__ = "chunks"
    id = Column(UUID, primary_key=True)
    note_id = Column(UUID, ForeignKey("notes.id"))
    chunk_text = Column(Text)
    embedding = Column(Vector(1536))  # pgvector
    token_estimate = Column(Integer)

class NoteSearchResult:
    note_ref: str
    chunk: str
    score: float
    why: str
    provenance: dict
```

### Crawl4AI Research Pattern

```python
async def run_research(job: ResearchJob):
    # Two-phase: discover URLs then extract
    urls = await crawler.discover_urls(job.seed_urls, max_urls=10)

    artifacts = []
    for url in urls:
        result = await crawler.crawl(url, strategy="markdown")
        artifacts.append(result.markdown)

    # Store raw
    raw_artifacts = [store_raw(a) for a in artifacts]

    # Synthesize
    synthesis = await llm.synthesize(raw_artifacts, brief=job.brief)

    # Propose to Exchange
    await exchange.create_ingest_proposal(synthesis, raw_artifacts)
```

---

## Sources

- FastAPI modular architecture patterns: https://fastapi.tiangolo.com/features/
- PydanticAI agent and tool patterns: https://ai.pydantic.dev/
- PydanticAI tool registration: https://ai.pydantic.dev/tools/
- LangGraph durable execution: https://docs.langchain.com/oss/python/langgraph/overview
- MCP protocol architecture: https://modelcontextprotocol.io/specification/2025-11-25
- pgvector features: https://github.com/pgvector/pgvector
- Crawl4AI architecture: https://docs.crawl4ai.com/blog/
- Docling document parsing: https://docling-project.github.io/docling/
- OpenTelemetry Python: https://opentelemetry.io/docs/languages/python/
- Alembic migration patterns: https://alembic.sqlalchemy.org/
- Structured logging (structlog): https://www.structlog.org/
- PRD Knowledge OS Core: docs/PRD_Knowledge_OS_Core_OpenSource_V1.md
- Stack Decision Record: docs/STACK_DECISION_RECORD_Knowledge_OS_Core.md
