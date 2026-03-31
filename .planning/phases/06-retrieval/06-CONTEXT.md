# Phase 6: Retrieval - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Build hybrid retrieval (FTS + vector) with context packs — the derived layer that never becomes sovereign. This serves as the projection layer for agent brain, note copilot, and research runtime without overriding canonical Markdown files.

</domain>

<decisions>
## Implementation Decisions

### Retrieval Architecture (F10)
- **D-90:** Hybrid search combines PostgreSQL FTS (tsvector/tsquery) with pgvector semantic search
- **D-91:** Chunk model already exists in `src/db/models/chunk.py` with heading_path, content, chunk_index, char_start, char_end
- **D-92:** Embedding model already exists in `src/db/models/embedding.py` with embedding_vector (JSONB), embedding_model
- **D-93:** Retrieval is a derived projection — canonical truth remains in Markdown files, not vectors

### Embedding Strategy (F10-02)
- **D-94:** Embedding model: `text-embedding-3-small` (OpenAI) — 1536 dimensions, good quality/cost ratio
- **D-95:** Embedding generation via job queue (`generate_embeddings` job type already defined in D-55)
- **D-96:** Batch embedding generation for efficiency — process chunks in batches of 100

### Hybrid Fusion Algorithm (F10-03)
- **D-97:** Fusion method: Reciprocal Rank Fusion (RRF) with k=60 — standard approach combining multiple rankers
- **D-98:** FTS uses PostgreSQL `ts_rank_cd` for relevance scoring
- **D-99:** Vector search uses pgvector cosine similarity
- **D-100:** Final ranking = RRF(FTS_rank, vector_rank)

### Chunking Strategy (F10-05)
- **D-101:** Heading-guided chunking — split on H1, H2, H3 boundaries
- **D-102:** Max chunk size: 512 tokens (configurable per note kind)
- **D-103:** Overlap: 50 tokens between chunks for context continuity
- **D-104:** Chunk index job runs on note create/update via `index_note` job type

### Context Pack Structure (F10-04)
- **D-105:** Context pack contains: note reference, snippet, score, why_matched, metadata, neighbors, provenance
- **D-106:** Neighbors: top-3 related chunks from same note
- **D-107:** Provenance: note_path, heading_path, workspace_id, indexed_at
- **D-108:** Score breakdown: FTS component + vector component + recency boost (optional)

### Index Management (F10-06)
- **D-109:** Incremental updates via `index_note` job on note change
- **D-110:** Full rebuild via `reindex_scope` job with FOR UPDATE SKIP LOCKED claiming
- **D-111:** pgvector index type: HNSW (better query performance, build cost acceptable for <100K chunks)

### API Endpoints (F10)
- **D-112:** `GET /retrieval/search` — hybrid search with query, limit, mode (fts|vector|hybrid)
- **D-113:** `GET /retrieval/context/{note_id}` — context pack for a note
- **D-114:** `POST /retrieval/reindex` — trigger full reindex job

### Work Boundary
- **D-115:** Retrieval never writes back to canonical Markdown — it only reads and projects
- **D-116:** Index jobs run as background workers, not blocking note operations

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `docs/SSOT_Knowledge_OS_V1.md` §12 — Retrieval layer mission (never sovereign)
- `docs/STACK_DECISION_RECORD_Knowledge_OS_Core.md` — Postgres + pgvector stack decision

### Phase-Specific
- `.planning/ROADMAP.md` §Phase 6 — Success criteria, key deliverables
- `.planning/REQUIREMENTS.md` §F10 — F10-01 to F10-06

### Prior Phases
- `.planning/phases/04-backend-api-services-jobs/04-CONTEXT.md` — D-50: SQLAlchemy 2 async, D-51: tables, D-53: REST endpoints, D-55: job types
- `.planning/phases/05-agent-brain/05-CONTEXT.md` — D-67-D-87: skill system, D-88-D-89: job handlers

</canonical_refs>

<codebase_context>
## Existing Code Insights

### Reusable Assets
- `src/api/retrieval.py` — skeleton API with placeholder hybrid_search (returns title-only matching)
- `src/db/models/chunk.py` — Chunk model already defined with heading_path, content, chunk_index, char_start, char_end
- `src/db/models/embedding.py` — Embedding model with JSONB vector storage (1536-dim)
- `src/db/models/note_projection.py` — NoteProjection with note_path, kind, title, tags, links, frontmatter
- Phase 4 job types: `index_note`, `reindex_scope`, `generate_embeddings` already defined

### Integration Points
- `/retrieval/search` endpoint → uses chunks, embeddings, notes_projection tables
- `/retrieval/context/{note_id}` → needs NoteProjection lookup + chunk retrieval
- Worker handlers → `index_note`, `reindex_scope`, `generate_embeddings` job types
- NoteProjection sync (Phase 4 F8-02) triggers index jobs on note changes

</codebase_context>

<specifics>
## Specific Ideas

No external references beyond SSOT/PRD and existing database models.

</specifics>

<deferred>
## Deferred Ideas

- BGE or local embedding models — deferred to v2 if privacy needs arise
- Query expansion or rewriting — deferred to v2 if retrieval quality insufficient
- Reranking with cross-encoder — deferred to v2

</deferred>

---

*Phase: 06-retrieval*
*Context gathered: 2026-03-31*
*Auto-mode: all gray areas auto-selected with documented defaults*
