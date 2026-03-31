---
phase: 06-retrieval
plan: "06-01"
subsystem: retrieval
tags: [postgres, pgvector, fastapi, pydantic, hybrid-search, fts, rrf]

# Dependency graph
requires:
  - phase: "04-backend-api-services-jobs"
    provides: "SQLAlchemy 2 async, 12 tables (chunks, embeddings, notes_projection), JobQueue, JobService"
  - phase: "05-agent-brain"
    provides: "pydanticai dependency, Pydantic v2 schemas"
provides:
  - "Alembic migration 002_add_fts_and_pgvector (FTS tsvector + pgvector vector(1536) + HNSW index)"
  - "Embedding model updated to use pgvector Vector(1536) native type"
  - "RetrievalService with fts_search, vector_search, hybrid_search via RRF, build_context_pack"
  - "Pydantic schemas: SearchRequest/Response, ContextPack with neighbors/provenance/metadata"
affects: ["06-02 (ChunkingService, EmbeddingService)", "06-03 (API endpoints, job handlers)"]

# Tech tracking
tech-stack:
  added: [pgvector>=0.3.0, httpx>=0.28.0]
  patterns: [RRF Reciprocal Rank Fusion, hybrid search, context packs, embeddings provider protocol]

key-files:
  created:
    - "alembic/versions/002_add_fts_and_pgvector.py"
    - "src/schemas/retrieval.py"
    - "src/services/retrieval_service.py"
  modified:
    - "src/db/models/embedding.py"
    - "pyproject.toml"

key-decisions:
  - "HNSW index chosen per D-111 (better query performance, build cost acceptable for <100K chunks)"
  - "RRF k=60 per D-97 (standard value for Reciprocal Rank Fusion)"
  - "text-embedding-3-small per D-94 (1536 dims, good quality/cost ratio)"
  - "Sequential neighbors (chunk_index ±1, ±2) per D-106 (simpler than vector neighbors)"

patterns-established:
  - "EmbeddingsProvider protocol for swapable embedding backends"
  - "RetrievalResult internal dataclass before Pydantic serialization"
  - "RRF fusion combining FTS ts_rank_cd and vector cosine_distance ranks"

requirements-completed: [F10-01, F10-02, F10-03, F10-04]

# Metrics
duration: 7 min
completed: 2026-03-31
---

# Phase 6 Plan 06-01: Retrieval Infrastructure Summary

**FTS tsvector + pgvector vector(1536) + RRF hybrid search with context pack schemas and service**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-31T21:36:57Z
- **Completed:** 2026-03-31T21:43:57Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments
- Alembic migration adding `content_tsv tsvector` to chunks table with GIN index and HNSW index on embeddings
- Embedding model updated from JSONB to pgvector `Vector(1536)` native type
- Pydantic v2 schemas for hybrid search requests/responses and full context packs with neighbors
- RetrievalService with FTS search, vector search, RRF hybrid fusion, and context pack builder

## Task Commits

Each task was committed atomically:

1. **Task 1: DB Migration FTS + pgvector** - `7753a60` (feat)
2. **Task 2: Update Embedding Model** - `da97936` (feat)
3. **Task 3: Create Retrieval Schemas** - `8e6b6c1` (feat)
4. **Task 4: Create RetrievalService** - `b5deb2d` (feat)

**Plan metadata:** `7753a60` docs commit

## Files Created/Modified

- `alembic/versions/002_add_fts_and_pgvector.py` - FTS tsvector on chunks, native vector(1536), GIN+HNSW indexes
- `src/db/models/embedding.py` - Changed embedding_vector from JSONB to Vector(1536) from pgvector.sqlalchemy
- `src/schemas/retrieval.py` - SearchRequest/Response, SearchResult with score_breakdown, ContextPack with neighbors/provenance/metadata
- `src/services/retrieval_service.py` - RetrievalService with fts_search, vector_search, hybrid_search (RRF), build_context_pack, OpenAIEmbeddingsProvider
- `pyproject.toml` - Added pgvector>=0.3.0, httpx>=0.28.0, tiktoken>=0.7.0

## Decisions Made

- HNSW index chosen per D-111 (better query performance, build cost acceptable for <100K chunks)
- RRF k=60 per D-97 (standard Reciprocal Rank Fusion value)
- text-embedding-3-small per D-94 (1536 dims, good quality/cost ratio)
- Sequential neighbors (chunk_index ±1, ±2) per D-106 (simpler than vector neighbors)
- FTS indexed at chunk level (not note level) per research §1.4

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

Ready for Phase 06-02 (Wave 2: ChunkingService, EmbeddingService, HybridSearch integration).

---
*Phase: 06-retrieval*
*Completed: 2026-03-31*
