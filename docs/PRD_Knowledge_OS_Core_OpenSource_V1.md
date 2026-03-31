# PRD — Knowledge OS Core (Open Source) v1

**Status:** Draft v1  
**Type:** Product Requirements Document  
**Scope:** Open-source core only  
**Audience:** Founder, backend/frontend engineers, contributors, future maintainers  
**Primary goal:** Define the first production-grade, self-hostable, modular core of the Knowledge OS product that will be released as open source and will also serve as the foundation for the managed cloud offering.

---

# 1. Executive Summary

## 1.1 Product thesis

Knowledge work software is fragmented.

Today, users typically split their thinking and operations across:
- a notes tool
- a chat UI
- a retrieval or RAG layer
- a crawler or research stack
- file storage
- task or project notes
- scattered AI assistants
- unstable automations
- ad hoc scripts and MCP servers

This produces a brittle environment where:
- the user’s knowledge base is not the sovereign source of truth
- the AI has no coherent, persistent operational memory
- generated knowledge is mixed with canonical knowledge without governance
- research outputs are not traceable, durable, or reviewable
- tool integrations are shallow, unsafe, or operationally fragile

The product proposed here solves this by defining a **Knowledge OS Core** with a filesystem-first architecture:
- the **User Vault** is the canonical source of truth
- the **Agent Brain** is the private, self-improving memory space of the agent
- the **Exchange Zone** is the controlled boundary between human knowledge and machine proposals
- the **Retrieval Layer** is derived, never canonical
- the **Policy Engine** governs all capability boundaries
- the **Git/Patch pipeline** makes change auditability and review first-class
- the **Research Runtime** turns requests into real, durable knowledge production jobs

This PRD defines the **open-source core** that embodies this architecture.

---

## 1.2 What the open-source core is

The open-source core is a **self-hosted, local-first, modular knowledge operating system backend + UI foundation** that enables:

- canonical Markdown-based second brain / vault management
- templates and structured note types
- daily notes and project notes
- agent-private memory and skill space
- a formal exchange/review layer between user vault and agent output
- patch-based and diff-based mutations
- capability-driven permissions and approval gates
- retrieval over notes and related artifacts
- note-scoped AI assistance
- basic research jobs that ingest sources and generate reviewable outputs
- self-hosted deployment as a modular monolith
- future exposure through MCP and cloud wrappers

---

## 1.3 What the open-source core is not

The OSS core is **not**:

- a SaaS product
- an enterprise compliance suite
- a hosted AI credit business
- a Slack/Teams replacement
- a generic workflow automation platform
- a fully autonomous agent platform that writes everywhere by default
- a microservice-heavy infrastructure product
- a cloud-only notes app
- a closed proprietary assistant wrapper

The OSS core is the **portable, inspectable, extensible substrate**.

---

# 2. Product Goals

## 2.1 Primary goal

Deliver a self-hostable, technically sound v1 core that allows a user to maintain a sovereign Markdown vault while enabling a bounded agent to read, retrieve, propose, and learn in a separate memory domain.

---

## 2.2 Secondary goals

- prove the architecture: User Vault + Agent Brain + Exchange Zone
- establish safe and auditable AI-to-vault workflows
- define extensible internal contracts for cloud evolution later
- make the system useful even without heavy AI usage
- keep the v1 operationally simple for a solo founder
- maximize portability and trust
- create an OSS base attractive to power users, builders, researchers, and contributors

---

## 2.3 Non-goals for v1

- real-time multi-user collaborative editing
- large enterprise admin panels
- full SSO/SAML/SCIM
- dozens of integrations
- mobile-first native apps
- advanced billing
- complicated agent swarms
- full autonomy without review
- massive distributed scale
- cloud-exclusive features inside core
- kernel-level sync magic

---

# 3. Product Principles

## 3.1 Filesystem sovereignty
The canonical knowledge layer must live in real files on disk, primarily Markdown with structured metadata.

## 3.2 Derived systems are subordinate
Embeddings, chunk indexes, graph projections, caches, and agent summaries are derived layers, not truth.

## 3.3 Domain separation
User Vault, Agent Brain, and Exchange Zone are distinct domains with distinct permissions and semantics.

## 3.4 AI must be governable
The agent can think, learn, and propose freely in its own domain. It cannot silently rewrite canonical user knowledge without explicit capability and policy authorization.

## 3.5 Patch-first mutation
Mutations of canonical content should default to diffs, patches, and reviewable proposals rather than opaque rewrite operations.

## 3.6 Modular monolith first
Build as a modular monolith with strong boundaries, not premature microservices.

## 3.7 Self-hostable by design
The OSS core must run with modest infrastructure and clear deployment assumptions.

## 3.8 Useful before “magical”
The system must remain useful as a disciplined knowledge environment even if AI is limited, offline, disabled, or BYOK-only.

---

# 4. User Personas

## 4.1 Primary persona: Power user / knowledge builder
Characteristics:
- uses Obsidian, Logseq, Markdown, or PKM systems
- wants local-first control
- values inspectability and data ownership
- wants AI help without surrendering the vault to chaos
- technically comfortable or willing to self-host

Jobs to be done:
- maintain notes and knowledge structures
- query and enrich the vault
- safely let AI suggest organization improvements
- keep research outputs traceable
- maintain long-term knowledge continuity

---

## 4.2 Secondary persona: Solo founder / research operator
Characteristics:
- manages many threads of work
- wants memory, synthesis, and research support
- needs system coherence more than visual polish
- likely to self-host first

Jobs to be done:
- store and retrieve project knowledge
- use AI as a bounded operator
- run research jobs and collect source artifacts
- keep the system modular and evolvable

---

## 4.3 Tertiary persona: Team maintainer / future cloud customer
Characteristics:
- wants OSS trust + managed convenience later
- interested in shared workspaces, policy, auditability
- cares about change review and governance

Jobs to be done:
- test the core locally
- evaluate architecture quality
- eventually adopt a managed version

---

# 5. Problem Statement

Current notes tools, AI assistants, and knowledge bases fail in predictable ways:

1. **No canonical truth boundary**  
   AI outputs and human-authored notes get mixed indiscriminately.

2. **No private memory domain for the agent**  
   The agent either has no long-term memory or writes its memory into the user’s space.

3. **No formal exchange layer**  
   Proposed changes, research outputs, and consolidations lack a reviewable staging space.

4. **Weak auditability**  
   It is difficult to understand what changed, why, and from which source or agent action.

5. **Retrieval without knowledge discipline**  
   RAG layers often become accidental truth sources.

6. **Research outputs are not operationalized**  
   Search results, crawls, and summaries do not become durable, structured knowledge artifacts.

7. **Tool sprawl**  
   Notes, AI, file operations, sync, indexing, search, and research happen in disconnected systems.

This product addresses those issues by treating knowledge operations as a disciplined system, not just chat wrapped around files.

---

# 6. Product Scope of the Open-Source Core

## 6.1 Included in core v1

### Canonical knowledge layer
- Markdown-based User Vault
- structured note types
- templates
- daily notes
- project/resource/area/inbox notes
- attachment references

### Agent-private knowledge layer
- Agent Brain filesystem
- persistent memory markdown files
- skills/heuristics storage
- self-improve within agent domain

### Boundary layer
- Exchange Zone
- patch proposals
- reviewable changes
- change application flow

### Operational backend
- modular FastAPI backend
- Postgres + pgvector
- background worker
- filesystem repositories
- Git revision layer

### Intelligence layer
- lexical retrieval
- semantic retrieval
- note-local AI assistance
- limited research jobs
- source artifact capture
- policy-aware access control

### Developer/platform foundation
- plugin-ready modular services
- future MCP exposure hooks
- containerized local deployment
- self-host docs

---

## 6.2 Explicitly excluded from OSS core v1

- enterprise SSO
- hosted LLM orchestration and billing
- proprietary cloud-only multi-tenant admin features
- organization billing
- advanced real-time collaboration engine
- advanced analytics dashboards
- per-seat audit exports for enterprise
- compliance tooling beyond foundational logs
- complex connector ecosystem

These may be built later in cloud or enterprise layers.

---

# 7. High-Level Product Shape

The system has five primary logical planes:

1. **Knowledge Filesystem Plane**
2. **Control Plane**
3. **Intelligence Plane**
4. **Execution Plane**
5. **Presentation Plane**

---

## 7.1 Knowledge Filesystem Plane

Contains:
- User Vault
- Agent Brain
- Exchange Zone
- Raw artifacts
- Templates
- Attachments references

This is where human-readable and durable content lives.

---

## 7.2 Control Plane

Contains:
- API gateway/backend
- policy engine
- approval engine
- tenancy/auth abstraction
- audit logging
- job registry
- internal service orchestration

This is where permissions and mutation rights are decided.

---

## 7.3 Intelligence Plane

Contains:
- retrieval service
- note copilot orchestration
- agent planner/executor/reflector
- embedding and chunking pipelines
- optional summarization and synthesis modules

This is where meaning and context are derived.

---

## 7.4 Execution Plane

Contains:
- worker system
- crawler/parser
- indexing jobs
- patch generation jobs
- research jobs
- background consolidation jobs

This is where expensive or long-running work happens.

---

## 7.5 Presentation Plane

Contains:
- web UI
- note view/editor
- note copilot UI
- exchange review UI
- job status UI
- admin/config UI
- future MCP exposure

This is where the system becomes operable to humans.

---

# 8. Core Architecture

## 8.1 Macro architecture

```text
User / UI
  ↓
App API (modular monolith)
  ├─ Auth module
  ├─ Vault module
  ├─ Policy module
  ├─ GitOps module
  ├─ Exchange module
  ├─ Retrieval module
  ├─ Agent module
  ├─ Research module
  ├─ Template module
  ├─ Approval module
  └─ Audit module
  ↓
Postgres + pgvector
Filesystem repos
Background Worker
```

---

## 8.2 Deployment assumption for OSS core

The OSS core must support a single-machine or single-VPS deployment with:

- one API process
- one worker process
- one Postgres instance
- local filesystem repositories
- optional reverse proxy
- optional object storage adapter
- optional crawler sidecar

This is the minimum viable production topology.

---

# 9. Domain Model

## 9.1 User Vault

### Definition
The User Vault is the sovereign, canonical, human-owned knowledge space.

### Responsibilities
- hold canonical notes
- provide durable note hierarchy
- expose notes to retrieval
- accept controlled mutations
- host templates and daily notes
- serve as the source of truth for user knowledge

### Must contain
- Markdown files
- YAML frontmatter
- attachment references
- folder hierarchy
- explicit note types

### Must not contain by default
- hidden model state
- embeddings
- job queues
- opaque agent memories
- noisy transient research junk

---

## 9.2 Agent Brain

### Definition
The Agent Brain is the private persistent working and learning domain of the agent.

### Responsibilities
- store agent identity and constitution
- persist curated memory
- store user operational profile
- store skills and heuristics
- hold reflections and reusable procedures
- support self-improve loops within agent domain

### Must contain
- `SOUL.md`
- `MEMORY.md`
- `USER.md`
- skills/
- heuristics/
- reflections/
- session summaries/

### Must not contain
- canonical user notes
- unreviewed direct mutations of user vault
- business-critical operational state that belongs in DB

---

## 9.3 Exchange Zone

### Definition
The Exchange Zone is the formal boundary where agent and system outputs become reviewable candidates for canonization.

### Responsibilities
- stage proposals
- stage research outputs
- hold diffs and patches
- support review workflows
- prevent direct uncontrolled writes into the User Vault
- preserve traceability of proposed knowledge changes

### Artifact types
- proposed note
- note patch
- source package
- synthesis report
- consolidation plan
- migration proposal
- review bundle

---

## 9.4 Raw Artifact Store

### Definition
Storage for fetched and parsed source material before curation.

### Responsibilities
- preserve raw crawls and parsed artifacts
- keep provenance intact
- support debugging and review
- enable later reprocessing

### Examples
- raw webpage markdown
- parsed PDF markdown
- source manifest
- extraction JSON

---

## 9.5 Derived Retrieval Layer

### Definition
All search indexes and semantic projections derived from vault and related artifacts.

### Responsibilities
- chunking
- lexical indexing
- embeddings
- graph projection
- retrieval context expansion

### Principle
Derived, rebuildable, non-canonical.

---

# 10. Filesystem Design

## 10.1 Canonical root layout

```text
knowledge-os/
  user-vault/
    00-Inbox/
    01-Daily/
    02-Projects/
    03-Areas/
    04-Resources/
    05-Archive/
    Templates/
    Attachments/
    _system/
      schemas/
      profiles/
      config/
  agent-brain/
    SOUL.md
    MEMORY.md
    USER.md
    skills/
    heuristics/
    reflections/
    sessions/
    scratchpads/
  exchange/
    proposals/
    research/
    imports/
    reviews/
  raw/
    web/
    docs/
    manifests/
  runtime/
    worktrees/
    temp/
  backups/
```

---

## 10.2 Note formats

### Required note envelope
Every note in the User Vault must be valid Markdown and support YAML frontmatter.

### Required minimum frontmatter fields by default
```yaml
id: note_uuid
type: resource|project|daily|area|inbox|source|synthesis|permanent|fleeting
title: Example Title
created_at: 2026-03-31T10:00:00Z
updated_at: 2026-03-31T10:00:00Z
status: active|draft|archived
tags: []
links: []
source_refs: []
```

### Additional schemas
The template system can require richer schemas depending on note type.

---

## 10.3 Attachment handling
Attachments are referenced, not embedded inline as opaque blobs. Metadata lives in DB and path references live in notes.

---

# 11. Git and Revision Model

## 11.1 Why Git exists in core
Git is used as:
- revision ledger
- diff generator
- patch substrate
- rollback mechanism
- provenance support for note changes

Git is **not**:
- the policy engine
- the jobs queue
- the retrieval engine
- the system database

---

## 11.2 Repository model

### Required
- User Vault repo
- optional Agent Brain repo

### User Vault branches
- `main`
- `proposal/<actor>/<id>`
- `research/<job-id>`
- `review/<id>`
- `import/<source>/<timestamp>`

### Worktrees
The system should support ephemeral worktrees for proposals and jobs.

---

## 11.3 Mutation model
Canonical note mutations default to:
1. create worktree or proposal branch
2. apply proposed change
3. generate diff
4. create proposal record
5. request approval if policy requires
6. apply or merge when approved

Direct mutation is reserved for safe operations and explicitly allowed cases.

---

# 12. Policy and Permissions

## 12.1 Core principle
Every action with meaningful effects passes through the Policy Engine.

---

## 12.2 Capability model

Example capabilities:

### Vault capabilities
- `vault.read_note`
- `vault.search`
- `vault.create_note`
- `vault.append_note`
- `vault.edit_note`
- `vault.propose_patch`
- `vault.create_folder`
- `vault.rename_note`
- `vault.delete_note`
- `vault.apply_template`
- `vault.create_daily`
- `vault.attach_asset`

### Agent capabilities
- `agent.read_memory`
- `agent.write_memory`
- `agent.create_skill`
- `agent.update_skill`
- `agent.reflect`

### Research capabilities
- `research.create_job`
- `research.fetch_source`
- `research.parse_source`
- `research.materialize_raw`
- `research.create_synthesis`
- `research.propose_ingest`

### Exchange capabilities
- `exchange.create_bundle`
- `exchange.review_bundle`
- `exchange.apply_bundle`
- `exchange.reject_bundle`

---

## 12.3 Policy outcomes
The engine must support at least:

- `allow_direct`
- `allow_patch_only`
- `allow_exchange_only`
- `allow_with_approval`
- `deny`

---

## 12.4 Policy dimensions
A rule may consider:
- actor type
- workspace or tenant
- path
- note type
- action
- source of request
- environment
- approval context

---

## 12.5 Safe defaults
By default:
- read is broader than write
- create is allowed only in safe zones unless configured otherwise
- edits to canonical notes are patch-first
- delete, move, rename are restricted
- agent self-improve is allowed only inside Agent Brain
- research outputs land in Exchange or Raw, not directly in canon

---

# 13. Product Modules

## 13.1 Vault Module

### Purpose
Single abstraction over filesystem-based canonical knowledge operations.

### Responsibilities
- read/write note content
- read/write frontmatter
- create notes
- move/rename/archive notes
- create daily notes
- apply templates
- resolve links and paths

### Boundaries
- must not bypass policy
- must not do retrieval ranking
- must not do direct git orchestration internally

### Primary interfaces
- `get_note(path|id)`
- `create_note(input)`
- `update_note(change_request)`
- `apply_template(template_id, target)`
- `create_daily(date, template_profile)`
- `list_notes(filters)`

---

## 13.2 Template Module

### Purpose
Provide structured note skeletons and schema-aware note creation.

### Responsibilities
- register templates
- validate frontmatter and body structure
- instantiate note types
- manage profile bundles

### v1 templates
- inbox note
- fleeting note
- permanent note
- daily note
- project note
- resource note
- source note
- synthesis note
- research brief

### Non-goals
- no advanced visual template marketplace
- no external template registry in v1

---

## 13.3 GitOps Module

### Purpose
Handle versioning and review-oriented file changes.

### Responsibilities
- init repos
- create proposal branches
- create worktrees
- generate diffs
- generate patch bundles
- commit changes
- merge/apply approved changes
- rollback

### Interfaces
- `start_proposal()`
- `write_proposal_changes()`
- `generate_diff()`
- `create_patch_bundle()`
- `apply_patch_bundle()`
- `rollback_to_revision()`

---

## 13.4 Exchange Module

### Purpose
Operationalize the boundary between generated/proposed knowledge and canonical vault content.

### Responsibilities
- store proposal metadata
- store review artifacts
- manage proposal lifecycle
- connect patch bundles to approval records
- support research ingest packages

### Proposal states
- draft
- generated
- awaiting_review
- approved
- rejected
- applied
- superseded
- failed

---

## 13.5 Policy Module

### Purpose
Central capability decision service.

### Responsibilities
- evaluate permissions
- compute effective action mode
- expose explanation or decision metadata
- support defaults and overrides

### v1 requirement
Rules must be inspectable, deterministic, and testable.

---

## 13.6 Approval Module

### Purpose
Gate changes that need explicit review.

### Responsibilities
- create approval requests
- present diffs and metadata
- accept/reject/partially apply if supported
- record approver and reason
- trigger application if approved

### v1 requirement
Must support at least:
- approve
- reject
- apply and close

Partial patch application is a stretch goal unless trivial.

---

## 13.7 Retrieval Module

### Purpose
Provide lexical + semantic retrieval over canonical and optionally exchange/raw domains.

### Responsibilities
- index notes
- chunk content
- create/update embeddings
- perform lexical search
- semantic search
- retrieve context packs
- enrich note-level copilot context

### Retrieval outputs
The module should return **context packs**, not just isolated chunks.

Each context pack should include:
- note reference
- snippet or section
- score(s)
- why matched
- related notes or surrounding sections
- provenance flags
- access domain

### v1 constraints
- Postgres FTS + pgvector
- hybrid scoring can remain simple
- reranking may be basic or absent initially

---

## 13.8 Agent Module

### Purpose
Provide a bounded, persistent, policy-aware agent runtime.

### Subcomponents
- planner
- executor
- reflector
- memory curator
- skill manager
- prompt/context assembler

### Responsibilities
- read relevant context
- produce proposals
- maintain private memory
- update own skills and heuristics
- support note-scoped assistance
- never bypass vault mutation controls

### Agent memory boundary
The agent is free to:
- update Agent Brain
- reflect
- create skills
- consolidate own memory

It is not free by default to:
- mutate canonical user notes directly
- reclassify knowledge without policy
- silently absorb raw sources into canon

---

## 13.9 Note Copilot Module

### Purpose
Enable focused conversation and assistance on a specific note or note cluster.

### Responsibilities
- load note context
- fetch related notes
- explain note
- propose tags/links
- suggest restructuring
- generate patch proposals
- assist with note splitting/consolidation

### UX distinction
Must distinguish between:
- conversational response
- recommendation
- proposed change

### v1 supported actions
- explain note
- summarize note
- suggest links
- suggest tags
- propose structural cleanup
- create patch proposal

---

## 13.10 Research Module

### Purpose
Turn user research requests into bounded, durable jobs that generate traceable artifacts.

### Responsibilities
- create research brief
- plan research blueprint
- execute fetch/parse
- store raw artifacts
- generate synthesis
- optionally create ingest proposal

### v1 scope
Research runtime is intentionally limited:
- small number of sources
- simple fetch and parse pipelines
- Markdown-first outputs
- bounded long-running job support

### Outputs
- blueprint
- raw source artifacts
- synthesis note
- ingest proposal bundle

---

## 13.11 Jobs Module

### Purpose
Coordinate all asynchronous work.

### Responsibilities
- store jobs
- claim jobs
- run workers
- track status
- retry idempotent steps
- surface progress

### Job types
- index_note
- reindex_scope
- generate_embeddings
- research_job
- parse_source
- apply_patch_bundle
- reflect_agent
- consolidate_memory

### v1 implementation
Use Postgres-backed jobs with row claiming and worker polling.

---

## 13.12 Audit Module

### Purpose
Create trust and inspectability.

### Responsibilities
- log actor actions
- log policy decisions
- log proposal lifecycle
- log job execution metadata
- log canonical mutation events

### v1 minimum audit events
- note read/write operations where appropriate
- proposal creation
- approval actions
- patch applications
- research job completion
- agent memory writes summary event
- policy decision records for sensitive operations

---

# 14. System Design

## 14.1 Backend style
The OSS core backend must be a **modular monolith**.

### Why
- easier for solo founder velocity
- lower operational complexity
- simpler deployment
- fewer distributed system failure modes
- easier contributor onboarding
- cleaner path to refactor later

### Anti-goal
No microservices in v1 core.

---

## 14.2 Recommended runtime topology

```text
reverse proxy
  ↓
api process (FastAPI)
  ↓
Postgres
local repos/filesystem
worker process
optional crawler sidecar
```

---

## 14.3 API layer

### Requirements
- versioned REST or REST-first API
- internal service boundaries
- authn/authz hooks
- websocket or polling for job state
- internal admin/debug endpoints in development mode

### Recommendation
REST-first with optional websocket channels for job updates.

---

## 14.4 Background execution
Workers must run separate from request/response serving.

### Why
- indexing can be expensive
- crawling can be slow
- synthesis can be slow
- patch generation and reflection may be delayed
- API latency must stay predictable

---

## 14.5 Data storage strategy

### Filesystem
Use for:
- canonical notes
- agent memory markdown
- exchange artifacts
- raw source markdown
- proposal bundles
- templates

### Postgres
Use for:
- users/workspaces
- policy rules
- approvals
- jobs
- audit logs
- note metadata projections
- retrieval chunks and embeddings refs
- artifact manifests

### Object storage
Optional adapter for:
- large attachments
- large raw artifacts
- exports
- backups

---

# 15. Database Model

## 15.1 Core tables

### `workspaces`
- id
- name
- slug
- created_at
- updated_at

### `actors`
- id
- workspace_id
- type (user, agent, system)
- display_name
- created_at

### `notes_projection`
- id
- workspace_id
- canonical_path
- note_type
- title
- status
- created_at
- updated_at
- checksum
- last_indexed_at

### `policy_rules`
- id
- workspace_id
- actor_selector
- capability
- path_pattern
- note_type
- outcome
- priority
- enabled
- created_at

### `approvals`
- id
- workspace_id
- proposal_id
- status
- requested_by_actor_id
- reviewed_by_actor_id
- created_at
- reviewed_at
- comment

### `proposals`
- id
- workspace_id
- proposal_type
- source_domain
- target_domain
- status
- branch_name
- worktree_path
- patch_path
- summary
- created_by_actor_id
- created_at
- updated_at

### `jobs`
- id
- workspace_id
- job_type
- status
- priority
- payload_json
- attempt_count
- max_attempts
- available_at
- claimed_at
- completed_at
- error_message

### `job_events`
- id
- job_id
- event_type
- payload_json
- created_at

### `chunks`
- id
- workspace_id
- note_projection_id
- domain
- chunk_text
- chunk_index
- token_estimate
- metadata_json

### `embeddings`
- id
- chunk_id
- embedding vector
- model_name
- created_at

### `artifacts`
- id
- workspace_id
- domain
- artifact_type
- path
- source_url
- checksum
- metadata_json
- created_at

### `audit_logs`
- id
- workspace_id
- actor_id
- action
- target_type
- target_ref
- decision
- metadata_json
- created_at

---

## 15.2 Schema principles
- file-backed truth, DB-backed operations
- no business-critical canonical knowledge exists only in DB
- all DB records referencing files must be rebuildable from filesystem reconciliation

---

# 16. Retrieval and Indexing Design

## 16.1 Indexing pipeline

```text
filesystem change
  → note projection refresh
  → chunking
  → lexical indexing
  → embeddings generation
  → retrieval metadata update
```

---

## 16.2 Domains that may be indexed
- User Vault
- Exchange Zone
- Raw artifacts
- Agent Brain (selectively, policy-gated)

### v1 default
User Vault indexed by default.  
Exchange and Raw may be indexed as secondary domains.  
Agent Brain indexing is optional and private to agent operations.

---

## 16.3 Chunking strategy
Chunk by:
- heading sections
- bounded paragraph windows
- note type heuristics

Avoid:
- arbitrary giant chunks
- context-free fragments detached from note identity

---

## 16.4 Search modes
- lexical search
- semantic search
- hybrid search
- context expansion

---

## 16.5 Context expansion
If a note chunk matches, the system may include:
- parent heading
- sibling heading summaries
- note title/frontmatter
- nearby sections
- backlinks or explicitly linked notes

---

# 17. Agent Design

## 17.1 Agent architecture

### Subsystems
- Context Builder
- Planner
- Tool Executor
- Reflection Engine
- Memory Curator
- Skill Manager

### Execution modes
- note-scoped copilot
- proposal generation
- memory reflection
- research planner
- safe utility operation

---

## 17.2 Prompt/context assembly
Context assembly must be modular and include only relevant blocks:
- system constitution
- workspace profile
- actor profile
- task objective
- note context
- retrieved context packs
- policy hints
- relevant skills
- memory excerpts

The system should avoid indiscriminately stuffing the entire Agent Brain or entire vault.

---

## 17.3 Self-improve model
Self-improve is limited to the Agent Brain by default.

Allowed:
- reflection summaries
- heuristic extraction
- procedure creation
- memory curation
- skill evolution

Not allowed by default:
- direct self-promotion of outputs into User Vault canon
- policy rewriting
- unrestricted folder manipulation in user domain

---

# 18. Research Runtime Design

## 18.1 Purpose in core
The Research Runtime exists to convert a user research request into durable, reviewable artifacts, not just a transient answer.

---

## 18.2 Research job flow

```text
user request
  → create research brief
  → plan blueprint
  → fetch sources
  → parse sources
  → store raw artifacts
  → create synthesis
  → optionally create ingest proposal
```

---

## 18.3 v1 fetch scope
The core should support:
- direct URL fetch
- small bounded multi-source jobs
- document parsing from uploaded/local files
- normalized Markdown outputs

Optional integrations and broader web search ecosystems can be added later.

---

## 18.4 Research outputs
Each research job should yield at minimum:
- job record
- research brief
- source manifest
- raw artifacts
- synthesis note
- status timeline

Optionally:
- ingest proposal bundle

---

# 19. UI Requirements

## 19.1 Minimum UI surfaces

### A. Workspace Shell
- sidebar/navigation
- vault tree
- recent notes
- search entry
- jobs indicator
- agent status indicator

### B. Note Workspace
- editor
- rendered view
- metadata panel
- backlinks/related notes panel
- Note Copilot panel
- proposal button

### C. Exchange Workspace
- proposal list
- diff view
- approval/reject controls
- proposal metadata
- provenance/source view

### D. Research Workspace
- create brief
- job status
- source list
- synthesis view
- ingest proposal controls

### E. Settings / Policy
- template profile selection
- policy rule basics
- agent permissions basics
- path-based configuration

---

## 19.2 Editing model
v1 may use a Markdown-first editor with rendered preview and metadata side panels. Rich block-level collaborative editing is out of scope.

---

# 20. API Design Principles

## 20.1 Public API groups
- `/auth/*`
- `/vault/*`
- `/templates/*`
- `/retrieval/*`
- `/copilot/*`
- `/exchange/*`
- `/approvals/*`
- `/research/*`
- `/jobs/*`
- `/policy/*`
- `/admin/*`

---

## 20.2 Example endpoint set

### Vault
- `GET /vault/notes`
- `GET /vault/note/{id}`
- `POST /vault/note`
- `POST /vault/note/{id}/daily-clone`
- `POST /vault/note/{id}/proposal`

### Retrieval
- `POST /retrieval/search`
- `POST /retrieval/context-pack`

### Copilot
- `POST /copilot/note/{id}/ask`
- `POST /copilot/note/{id}/suggest-links`
- `POST /copilot/note/{id}/propose-cleanup`

### Exchange
- `GET /exchange/proposals`
- `GET /exchange/proposal/{id}`
- `POST /exchange/proposal/{id}/approve`
- `POST /exchange/proposal/{id}/reject`

### Research
- `POST /research/jobs`
- `GET /research/job/{id}`
- `GET /research/job/{id}/artifacts`

### Policy
- `GET /policy/rules`
- `POST /policy/rules`
- `POST /policy/check`

---

# 21. Security Design

## 21.1 Core security assumptions
The system may be self-hosted and exposed to the internet. It must assume hostile inputs, malformed files, and dangerous generated outputs.

---

## 21.2 Security requirements
- path traversal protection
- strict path normalization
- policy checks before filesystem mutation
- sandboxing for crawler/parser where possible
- safe temp directories
- role separation between API and worker
- audit logs for sensitive events
- secret management via environment variables
- explicit trust boundaries between domains

---

## 21.3 Sensitive operations
Sensitive operations include:
- canonical note edits
- file moves/deletes
- proposal application
- artifact ingestion into canon
- policy changes
- agent permission elevation
- repo-level operations

These must be auditable and policy-gated.

---

# 22. Performance Requirements

## 22.1 v1 targets
These are directional targets, not rigid SLAs.

- note open latency: acceptable interactive response under normal load
- lexical search: near-interactive
- semantic search: acceptable within a few seconds for moderate corpus
- proposal diff generation: near-interactive for standard note sizes
- background indexing: asynchronous
- research jobs: not expected to be synchronous

---

## 22.2 Scaling assumptions for v1
- single workspace or small number of workspaces
- thousands to tens of thousands of notes, not millions
- moderate attachment volume
- moderate research workload
- one or few active users

---

## 22.3 Performance principles
- do not block the request path on embeddings unless unavoidable
- do not reindex the world on tiny changes
- maintain incremental indexing
- keep proposal application fast and isolated
- prefer batching for expensive operations

---

# 23. Extensibility and Plugin Model

## 23.1 Why extensibility matters
The project must become a platform substrate, not a dead-end app.

---

## 23.2 v1 extensibility approach
Do not start with a dynamic plugin marketplace.  
Start with stable internal interfaces and optional module adapters.

### Extension seams
- storage adapter
- embedding provider
- LLM provider
- parser provider
- crawler provider
- auth adapter
- MCP exposure layer
- template packs

---

## 23.3 MCP readiness
The core should be structured so that MCP servers can later expose:
- vault resources
- retrieval tools
- research tools
- agent-memory tools

MCP exposure is not required as a hard dependency for the first internal architecture, but internal contracts should make it straightforward later.

---

# 24. Open Source Boundary

## 24.1 What belongs in the OSS core
- full canonical vault system
- agent brain separation model
- exchange zone and patch review core
- policy engine baseline
- retrieval pipeline
- research runtime baseline
- web UI
- self-host deployment
- extension interfaces

---

## 24.2 What may remain outside core later
- hosted SaaS control plane
- multi-tenant cloud ops layer
- managed auth/billing integration beyond basics
- advanced org collaboration
- enterprise governance modules
- hosted AI credit accounting
- proprietary analytics and support tooling

The OSS core must still be genuinely valuable on its own.

---

# 25. Success Metrics

## 25.1 Product success signals for v1
- users can create and manage a real vault
- users can safely use note-scoped AI help
- users can review and apply proposals cleanly
- users can distinguish agent-private memory from canonical knowledge
- users can run at least basic research jobs and keep outputs traceable
- system remains usable without proprietary cloud services

---

## 25.2 Technical success signals
- reproducible self-host deployment
- deterministic policy checks
- no direct uncontrolled writes to canonical vault
- successful incremental indexing
- auditable proposal lifecycle
- acceptable performance on modest hardware

---

# 26. Failure Modes to Avoid

- agent writing directly into canonical notes without review
- embeddings becoming the only place where knowledge exists
- giant monolithic prompt with entire vault stuffed in
- Exchange Zone becoming an unmanageable junk drawer
- policy rules becoming magical or opaque
- retrieval returning context with no provenance
- research jobs dumping raw text into canon
- overbuilding the architecture before a working v1 exists
- coupling the open-source core to proprietary cloud assumptions

---

# 27. MVP Definition

The MVP of the OSS core is complete when a user can:

1. initialize a workspace
2. create and manage notes in a canonical Markdown vault
3. create daily notes and use structured templates
4. view and edit notes in the web app
5. search notes lexically and semantically
6. use Note Copilot on a note
7. have the system generate a proposal rather than directly mutating canon
8. review the proposal diff in Exchange
9. approve and apply the patch
10. let the agent update its own private memory
11. run a simple research job and obtain:
   - source artifact(s)
   - synthesis output
   - optional ingest proposal
12. inspect audit records for sensitive operations

If those twelve are true, the core is real.

---

# 28. Detailed MVP Scope

## 28.1 Must-have
- workspace bootstrap
- vault tree
- note CRUD
- daily note generation
- template instantiation
- markdown editor + preview
- filesystem-backed repos
- Postgres metadata
- lexical search
- semantic search
- Note Copilot basic actions
- Agent Brain persistence
- Exchange proposals with diff
- approve/reject/apply
- jobs system
- simple research runtime
- audit logging
- path-based policy rules
- self-host deployment docs

## 28.2 Should-have
- backlinks panel
- note relation suggestions
- research source manifest UI
- proposal summaries
- simple workspace config UI

## 28.3 Could-have
- partial patch application
- plugin hot-loading
- markdown AST-aware transforms
- more advanced template profiles
- multiple agent personas

## 28.4 Won’t-have in MVP
- real-time collaboration
- complex team permissions
- cloud billing
- huge connector marketplace
- enterprise admin
- mobile apps
- complicated swarm agents

---

# 29. Technical Backlog by Phase

## Phase 0 — Foundations
- repo structure
- architecture docs
- container/dev setup
- workspace init flow
- canonical filesystem conventions

## Phase 1 — Vault Core
- note CRUD
- templates
- daily notes
- metadata validation
- tree navigation
- note projection sync

## Phase 2 — Git + Exchange
- repo init
- branch/worktree lifecycle
- diff generation
- proposal model
- approval application

## Phase 3 — Policy
- rules model
- policy evaluator
- capability checks in all sensitive flows
- safe defaults

## Phase 4 — Retrieval
- chunking
- lexical index
- embeddings pipeline
- hybrid retrieval
- context packs

## Phase 5 — Agent Brain + Copilot
- Agent Brain filesystem
- memory curation
- note copilot UI/API
- patch-first proposal generation

## Phase 6 — Research Runtime
- research brief
- source fetch
- parsing
- raw artifact persistence
- synthesis generation
- ingest proposal bundle

## Phase 7 — Hardening
- audit expansion
- performance passes
- deployment docs
- migration and recovery docs
- test coverage growth

---

# 30. Testing Strategy

## 30.1 Required test layers
- unit tests for core services
- integration tests for filesystem + DB flows
- policy tests
- proposal lifecycle tests
- indexing tests
- research job tests
- end-to-end smoke tests

---

## 30.2 Critical integration test scenarios
- note create/edit/read
- daily note generation
- proposal creation and application
- denied policy path
- agent memory write allowed while vault write denied
- indexing after note change
- research job creates raw + synthesis + proposal
- rollback after failed apply

---

# 31. Observability and Operations

## 31.1 Minimum observability
- structured logs
- request tracing IDs
- job event logs
- audit logs
- healthcheck endpoints
- index status visibility

---

## 31.2 Recovery needs
- reindex from filesystem
- rebuild notes projection
- restore repo revisions
- resume or retry failed jobs
- detect drift between filesystem and DB

---

# 32. Risks

## 32.1 Product risks
- too much complexity before user value
- too much AI, too little knowledge discipline
- poor UX around proposals
- confusing separation between agent and user spaces

## 32.2 Technical risks
- filesystem and git edge cases
- retrieval quality disappoints without careful chunking
- crawler/parser instability
- policy bugs leading to unsafe writes
- background worker complexity

## 32.3 OSS risks
- project too hard to self-host
- architecture too opaque to contributors
- core too weak to attract users
- cloud-only assumptions leaking into OSS design

---

# 33. Design Decisions Locked for v1

The following are deliberate v1 decisions:

1. **Markdown is canonical**
2. **Vault and Agent Brain are separate**
3. **Patch-first mutation is default**
4. **Git is revision substrate**
5. **Postgres is operational database**
6. **Modular monolith is the architecture**
7. **Background jobs are worker-based**
8. **Retrieval is derived**
9. **Research outputs are reviewable artifacts**
10. **Cloud-specific monetization concerns are out of the OSS core**

---

# 34. Open Questions

These are intentionally deferred or unresolved:

- exact UI stack and editor implementation details
- degree of AST-aware markdown transforms in v1
- whether partial patch application lands in MVP
- exact default template packs
- exact MCP packaging of exposed capabilities
- exact provider matrix for LLMs and embeddings
- exact crawler/parser vendor adapters

These should be settled during implementation design, not by bloating core architecture prematurely.

---

# 35. Final Product Statement

Knowledge OS Core is a self-hostable, Markdown-sovereign, agent-aware knowledge operating system core.

It exists to solve a very specific structural problem:

**How do we let humans and agents work on knowledge together without collapsing the boundary between canonical thought, machine memory, and generated change?**

Its answer is:

- a canonical User Vault
- a private Agent Brain
- an explicit Exchange Zone
- a policy-first mutation model
- a Git-backed revision layer
- a retrieval system that never becomes truth
- a research runtime that produces durable artifacts instead of disposable chat sludge

That is the product.

That is the open-source core.

And that is the foundation on top of which the future managed cloud offering can be built without betraying the architecture.
