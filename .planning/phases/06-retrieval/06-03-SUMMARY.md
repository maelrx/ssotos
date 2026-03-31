# Plan 06-03 Summary — Wave 3: API + Job Handlers

**Phase:** 06-retrieval
**Wave:** 3/3
**Status:** COMPLETE
**Executed:** 2026-03-31

## Tasks Executed

| # | Task | Status |
|---|------|--------|
| 8 | API Endpoints — Replace placeholders in `src/api/retrieval.py` | ✅ |
| 9 | Job Handler — `handle_index_note` | ✅ |
| 10 | Job Handler — `handle_generate_embeddings` | ✅ |
| 11 | Job Handler — `handle_reindex_scope` | ✅ |
| 12 | Update pyproject.toml dependencies | ✅ |

## Commits (5)

1. **4fac79a** — `feat(retrieval): implement API endpoints GET /retrieval/search, /context/{note_id}, /stats/{workspace_id}`
   - `src/api/retrieval.py` — full rewrite with 4 endpoints
   - `src/services/retrieval_service.py` — lint fixes
   - `.planning/REQUIREMENTS.md` — F10-01 to F10-06 marked complete

2. **6d054b9** — `feat(retrieval): implement index_note job handler with chunking + FTS + enqueue embeddings`
   - `src/worker/handlers/index_note.py` — 142 lines, handles upsert/delete

3. **a12b05d** — `feat(retrieval): implement generate_embeddings job handler`
   - `src/worker/handlers/generate_embeddings.py` — 96 lines

4. **6b63c24** — `feat(retrieval): implement reindex_scope job handler`
   - `src/worker/handlers/reindex_scope.py` — 67 lines

5. **d5c9ad1** — `chore(retrieval): add B008 ruff ignore for FastAPI Query/Depends pattern`
   - `pyproject.toml` — added B008 to ruff ignore list

## Key Implementation Details

### API Endpoints
- `GET /retrieval/search` — wires to `RetrievalService.search()` with FTS+vector+RRF
- `GET /retrieval/context/{note_id}` — returns ContextPack list with neighbors + provenance
- `POST /retrieval/reindex` — triggers reindex_scope job
- `GET /retrieval/stats/{workspace_id}` — returns chunk/embedding/indexed note counts

### index_note Handler
- `operation="delete"`: removes chunks + embeddings, clears indexed_at
- `operation="upsert"`: reads markdown from filesystem, parses frontmatter, chunks via `markdown_to_chunks()`
- Sets `content_tsv` via raw SQL `to_tsvector('english', content)`
- Enqueues `generate_embeddings` at priority=5

### generate_embeddings Handler
- Fetches Chunk records, calls `generate_embeddings_batch()`
- Inserts/updates Embedding records with vector and model
- Returns count of embeddings generated

### reindex_scope Handler
- Queries all NoteProjection for workspace
- Supports `scope="full"`, `"folder"`, `"tag"` filtering
- Enqueues `index_note` at priority=0 (low)

## Requirements Covered

All F10 requirements (F10-01 through F10-06):
- **F10-01** PostgreSQL FTS — via `Chunk.content_tsv` + `websearch_to_tsquery`
- **F10-02** pgvector — via `Embedding.embedding_vector` (vector(1536))
- **F10-03** Hybrid retrieval — RRF fusion in `RetrievalService`
- **F10-04** Context packs — `build_context_pack()` with neighbors, provenance, metadata
- **F10-05** Heading-guided chunking — `markdown_to_chunks()` in ChunkingService
- **F10-06** Incremental indexing — `index_note` on upsert, `reindex_scope` for full rebuild

## Files Modified (5)

- `src/api/retrieval.py` — 170 lines
- `src/worker/handlers/index_note.py` — 142 lines
- `src/worker/handlers/generate_embeddings.py` — 96 lines
- `src/worker/handlers/reindex_scope.py` — 67 lines
- `pyproject.toml` — B008 ignore added

## Dependencies

Already present in pyproject.toml (added by previous wave):
- `pgvector>=0.3.0` — vector type support
- `httpx>=0.28.0` — async HTTP client for OpenAI embeddings API
- `tiktoken>=0.7.0` — token counting for chunking

---

*Phase 6 Retrieval: all 3 waves complete*
