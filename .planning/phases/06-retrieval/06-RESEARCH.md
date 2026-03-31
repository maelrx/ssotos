# Phase 6: Retrieval — Research

**Phase:** 06-retrieval
**Status:** Research (pre-planning)
**Date:** 2026-03-31
**Requirements:** F10-01, F10-02, F10-03, F10-04, F10-05, F10-06

---

## 0. Executive Summary

Phase 6 implements the hybrid retrieval layer (FTS + pgvector) with context packs. This is the **derived projection layer** -- canonical truth remains in Markdown files. The layer must never become sovereign per Law 2 (SSOT-Knowledge-OS-V1).

**Key decisions already made (D-90 to D-116):**
- Hybrid search: PostgreSQL FTS + pgvector semantic search
- Embedding model: `text-embedding-3-small` (1536 dimensions)
- Fusion method: Reciprocal Rank Fusion (RRF) with k=60
- Chunking: Heading-guided (H1/H2/H3), max 512 tokens, 50-token overlap
- Index type: HNSW for pgvector (better query performance for <100K chunks)
- Job types: `index_note`, `reindex_scope`, `generate_embeddings` (already defined)

---

## 1. PostgreSQL FTS Setup (F10-01)

### 1.1 Schema Changes Required

The `notes_projection` table needs a `tsvector` column for full-text search:

```sql
-- Add to notes_projection table
ALTER TABLE notes_projection ADD COLUMN content_tsv tsvector;

-- Create GIN index for fast FTS queries
CREATE INDEX ix_notes_projection_fts ON notes_projection USING gin (content_tsv);

-- Trigger-based incremental update (or application-level update)
```

**Note:** The `chunks` table has the actual chunked content. FTS should index the `chunks.content` field, not just the note-level title/tags. The search query joins `chunks` with `notes_projection` and runs FTS on chunk content.

### 1.2 Query Syntax

PostgreSQL FTS uses `tsquery` and `tsvector`:

```python
# Text → tsquery (handles prefix matching, stemming)
from sqlalchemy import func, text

# Example: convert user query to tsquery
# "knowledge os" → 'knowledge' <-> 'os'  (phrase) or 'knowledge' | 'os' (OR)
# Use websearch_to_tsquery for Google-like syntax

# Basic tsquery construction
tsquery_expr = func.plainto_tsquery('english', search_query)
# Or for web-search style:
tsquery_expr = func.websearch_to_tsquery('english', search_query)

# Match
stmt = select(Chunk).join(NoteProjection).where(
    Chunk.note_projection_id == NoteProjection.id,
    NoteProjection.workspace_id == workspace_id,
    NoteProjection.content_tsv.op('@@')(tsquery_expr)
)
```

### 1.3 Ranking Functions

```python
# ts_rank_cd: coverage density ranking (respects term proximity)
from sqlalchemy import func

rank_expr = func.ts_rank_cd(
    NoteProjection.content_tsv,
    func.websearch_to_tsquery('english', q)
)

stmt = (
    select(Chunk, NoteProjection, rank_expr.label('fts_rank'))
    .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
    .where(
        NoteProjection.workspace_id == workspace_id,
        NoteProjection.content_tsv.op('@@')(
            func.websearch_to_tsquery('english', q)
        )
    )
    .order_by(rank_expr.desc())
    .limit(limit)
)
```

### 1.4 Alternative: Chunk-level FTS

Since chunks are the unit of retrieval, FTS should ideally index `chunks.content` directly:

```sql
-- Add tsvector to chunks table
ALTER TABLE chunks ADD COLUMN content_tsv tsvector;
CREATE INDEX ix_chunks_fts ON chunks USING gin (content_tsv);

-- Search at chunk level
SELECT c.*, np.title, np.note_path,
       ts_rank_cd(c.content_tsv, plainto_tsquery('english', :q)) as rank
FROM chunks c
JOIN notes_projection np ON c.note_projection_id = np.id
WHERE c.content_tsv @@ plainto_tsquery('english', :q)
  AND np.workspace_id = :workspace_id
ORDER BY rank DESC
LIMIT :limit;
```

**Decision:** Index FTS at the **chunk level** (`chunks.content_tsv`), not note level. This gives finer-grained results and matches how vector search operates (per-chunk).

### 1.5 FTS Index Maintenance

FTS tsvector can be updated application-level on `index_note` job:

```python
# In index_note handler
async def update_fts_index(db: AsyncSession, note_projection_id: UUID, content: str):
    # Update the tsvector column
    stmt = (
        update(Chunk)
        .where(Chunk.note_projection_id == note_projection_id)
        .values(content_tsv=func.to_tsvector('english', Chunk.content))
    )
    await db.execute(stmt)
```

Or via trigger on the `chunks` table.

---

## 2. pgvector Setup (F10-02)

### 2.1 Current State

The migration already creates the `vector` extension (line 21: `CREATE EXTENSION IF NOT EXISTS vector`). However, the `embeddings` table stores vectors as `JSONB`, which **does not support pgvector's vector operations** (cosine similarity, L2 distance, HNSW indexing).

### 2.2 Required Schema Change

```sql
-- Remove JSONB vector column
ALTER TABLE embeddings DROP COLUMN embedding_vector;

-- Add proper vector column (1536 dims for text-embedding-3-small)
ALTER TABLE embeddings ADD COLUMN embedding_vector vector(1536);

-- Create HNSW index for approximate nearest neighbor search
CREATE INDEX ix_embeddings_vector_hnsw ON embeddings
USING hnsw (embedding_vector vector_cosine_ops);
```

**Alternative: IVFFlat** (faster build, slightly slower queries):
```sql
CREATE INDEX ix_embeddings_vector_ivfflat ON embeddings
USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100);
```

**Decision (D-111):** Use HNSW -- better query performance, build cost acceptable for <100K chunks.

### 2.3 Vector Distance Functions

pgvector supports multiple distance metrics:

```python
# Cosine distance (used per D-99)
# <vec> <=> <vec>  in SQL gives cosine distance
# For cosine similarity: 1 - cosine_distance

from sqlalchemy import func, text

# Vector search query (cosine)
stmt = select(
    Embedding, Chunk, NoteProjection,
    (1 - func.cosine_distance(Embedding.embedding_vector, func.cast(query_vector, Vector(1536)))).label('cosine_sim')
).join(
    Chunk, Embedding.chunk_id == Chunk.id
).join(
    NoteProjection, Embedding.note_projection_id == NoteProjection.id
).where(
    NoteProjection.workspace_id == workspace_id
).order_by(
    text('cosine_sim DESC')
).limit(limit)
```

### 2.4 SQLAlchemy Model Update

The `Embedding` model needs to be updated to use pgvector vector type:

```python
# src/db/models/embedding.py
from pgvector.sqlalchemy import Vector  # from psycopg[binary] or pgvector

class Embedding(Base):
    __tablename__ = "embeddings"
    # ...
    embedding_vector: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    # Note: Vector type stores as list[float] in Python, native vector in Postgres
```

**Package needed:** `pgvector` Python package for the `Vector` type mapping. This comes from `psycopg[binary]` or standalone `pgvector` package.

---

## 3. Embedding Generation (F10-02)

### 3.1 EmbeddingsProvider Interface

Per Stack Decision Record §36 and D-94/D-95:

```python
# src/services/embeddings.py
from typing import Protocol
from abc import ABC, abstractmethod

class EmbeddingsProvider(Protocol):
    """Protocol for embedding generation providers."""
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of text chunks to embed

        Returns:
            List of embedding vectors (1536-dim for text-embedding-3-small)
        """
        ...

class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    """OpenAI text-embedding-3-small provider."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ["OPENAI_API_KEY"]
        self.model = "text-embedding-3-small"
        self.dimensions = 1536

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": texts,
                    "model": self.model,
                    "dimensions": self.dimensions,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
```

### 3.2 Batching Strategy (D-95)

- Batch size: 100 chunks per API call (OpenAI limit is 2048 for batch embedding requests)
- OpenAI rate limits: ~500 requests/minute for embeddings
- Implementation: async with semaphore to control concurrency

```python
async def generate_embeddings_batch(
    provider: EmbeddingsProvider,
    chunks: list[Chunk],
    batch_size: int = 100,
    max_concurrent: int = 5,
) -> list[tuple[UUID, list[float]]]:  # (chunk_id, embedding_vector)
    """Generate embeddings for chunks in batches with concurrency control."""
    import asyncio

    semaphore = asyncio.Semaphore(max_concurrent)

    async def embed_batch(batch: list[tuple[UUID, str]]) -> list[tuple[UUID, list[float]]]:
        async with semaphore:
            chunk_ids, texts = zip(*batch)
            embeddings = await provider.embed_texts(list(texts))
            return list(zip(chunk_ids, embeddings))

    # Prepare (chunk_id, content) pairs
    chunk_pairs = [(chunk.id, chunk.content) for chunk in chunks]

    # Process in batches
    results = []
    for i in range(0, len(chunk_pairs), batch_size):
        batch = chunk_pairs[i:i + batch_size]
        batch_results = await embed_batch(batch)
        results.extend(batch_results)

    return results
```

### 3.3 Token Counting for Chunking

Need to count tokens before embedding to enforce the 512-token limit (D-102):

```python
import tiktoken  # OpenAI's tokenizer

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using the model's tokenizer."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Or approximate: 1 token ≈ 4 chars in English
def approximate_tokens(text: str) -> int:
    return len(text) // 4
```

---

## 4. Heading-Guided Chunking (F10-05)

### 4.1 Chunking Algorithm (D-101, D-102, D-103)

```python
import re
from dataclasses import dataclass

@dataclass
class ChunkResult:
    content: str
    heading_path: str  # e.g., "## Introduction"
    chunk_index: int
    char_start: int
    char_end: int

def chunk_by_headings(
    markdown: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[ChunkResult]:
    """Split markdown into chunks at heading boundaries.

    Rules (D-101, D-102, D-103):
    - Split on H1 (#), H2 (##), H3 (###) boundaries
    - Max chunk size: 512 tokens
    - Overlap: 50 tokens between consecutive chunks
    """
    # Split by heading lines
    heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)

    sections: list[tuple[int, int, str]] = []  # (char_start, char_start_of_next, heading_path)
    last_pos = 0
    last_heading = ""

    for match in heading_pattern.finditer(markdown):
        heading_level = len(match.group(1))
        heading_text = match.group(2).strip()
        heading_path = f"{'#' * heading_level} {heading_text}"

        # The section runs from last_pos to match.start()
        if last_pos < match.start():
            sections.append((last_pos, match.start(), last_heading))

        last_pos = match.start()
        last_heading = heading_path

    # Last section goes to end of file
    sections.append((last_pos, len(markdown), last_heading))

    # Now split sections larger than max_tokens
    chunks: list[ChunkResult] = []
    chunk_index = 0
    overlap_chars = overlap_tokens * 4  # approximate chars for 50 tokens

    for start, end, heading_path in sections:
        section_text = markdown[start:end]
        section_tokens = approximate_tokens(section_text)

        if section_tokens <= max_tokens:
            chunks.append(ChunkResult(
                content=section_text,
                heading_path=heading_path,
                chunk_index=chunk_index,
                char_start=start,
                char_end=end,
            ))
            chunk_index += 1
        else:
            # Split this section into smaller chunks with overlap
            char_limit = max_tokens * 4  # approximate chars
            pos = start
            while pos < end:
                chunk_end = min(pos + char_limit, end)

                # Try to break at a paragraph or sentence boundary
                if chunk_end < end:
                    break_point = find_break_point(markdown, pos, chunk_end)
                    chunk_end = break_point if break_point > pos else chunk_end

                # Include overlap from previous chunk
                chunk_start = max(pos - overlap_chars, start) if chunks else pos
                chunk_text = markdown[chunk_start:chunk_end]

                chunks.append(ChunkResult(
                    content=chunk_text,
                    heading_path=heading_path,
                    chunk_index=chunk_index,
                    char_start=chunk_start,
                    char_end=chunk_end,
                ))
                chunk_index += 1
                pos = chunk_end - overlap_chars  # Back up for overlap

    return chunks

def find_break_point(text: str, start: int, end: int) -> int:
    """Find a good break point near 'end' (paragraph, sentence, or word boundary)."""
    # Try to find paragraph break (\n\n) before end
    paragraph_break = text.rfind('\n\n', start, end)
    if paragraph_break > start:
        return paragraph_break

    # Try sentence break (. or ! or ? followed by space)
    sentence_break = max(
        text.rfind('. ', start, end),
        text.rfind('! ', start, end),
        text.rfind('? ', start, end),
    )
    if sentence_break > start:
        return sentence_break + 2

    # Fall back to word boundary
    word_break = text.rfind(' ', start, end)
    return word_break if word_break > start else end
```

### 4.2 Integration with NoteProjection

When `index_note` job runs:
1. Read markdown file from filesystem
2. Parse frontmatter (extract metadata)
3. Run `chunk_by_headings()` on body content
4. Store chunks in `chunks` table with `heading_path`, `chunk_index`, `char_start`, `char_end`
5. Store FTS tsvector for each chunk
6. Enqueue `generate_embeddings` job for the new chunks

---

## 5. Hybrid Fusion (F10-03)

### 5.1 Reciprocal Rank Fusion (RRF) Algorithm (D-97, D-100)

```python
from dataclasses import dataclass
from typing import NamedTuple

@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: UUID
    note_projection_id: UUID
    fts_rank: int
    vector_rank: int
    fts_score: float
    vector_score: float
    rrf_score: float  # Final combined score
    note_path: str
    heading_path: str
    content: str
    title: str
    tags: list[str]
    metadata: dict

def reciprocal_rank_fusion(
    fts_results: list[tuple[UUID, float, int]],  # (chunk_id, score, rank)
    vector_results: list[tuple[UUID, float, int]],  # (chunk_id, score, rank)
    k: int = 60,  # D-97: k=60 is standard
) -> dict[UUID, float]:
    """Combine FTS and vector rankings using RRF.

    RRF formula: score(d) = sum(1 / (k + rank(d))) for each ranker
    """
    rrf_scores: dict[UUID, float] = {}

    # FTS contributions
    for rank, (chunk_id, score, _) in enumerate(fts_results, start=1):
        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = 0.0
        rrf_scores[chunk_id] += 1 / (k + rank)

    # Vector contributions
    for rank, (chunk_id, score, _) in enumerate(vector_results, start=1):
        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = 0.0
        rrf_scores[chunk_id] += 1 / (k + rank)

    return rrf_scores
```

### 5.2 Hybrid Search Flow

```python
async def hybrid_search(
    db: AsyncSession,
    workspace_id: UUID,
    query: str,
    query_vector: list[float],  # Pre-computed query embedding
    limit: int = 20,
    fts_weight: float = 0.5,
    vector_weight: float = 0.5,
) -> list[RetrievalResult]:
    """Execute hybrid search combining FTS and vector results.

    Steps:
    1. Run FTS query (ts_rank_cd) → get ranked chunk list
    2. Run vector search (cosine similarity) → get ranked chunk list
    3. Apply RRF to combine ranks
    4. Fetch full chunk data for top results
    5. Build context packs
    """
    # Step 1: FTS search
    fts_stmt = (
        select(
            Chunk.id,
            Chunk.note_projection_id,
            func.ts_rank_cd(Chunk.content_tsv, func.websearch_to_tsquery('english', query)).label('fts_score')
        )
        .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
        .where(
            NoteProjection.workspace_id == workspace_id,
            Chunk.content_tsv.op('@@')(func.websearch_to_tsquery('english', query))
        )
        .order_by(text('fts_score DESC'))
        .limit(limit * 2)  # Fetch extra for fusion
    )
    fts_results = (await db.execute(fts_stmt)).fetchall()
    fts_ranked = [(row[0], row[2], i+1) for i, row in enumerate(fts_results)]

    # Step 2: Vector search
    vector_stmt = (
        select(
            Embedding.chunk_id,
            Embedding.note_projection_id,
            (1 - func.cosine_distance(
                Embedding.embedding_vector,
                func.cast(query_vector, Vector(1536))
            )).label('cosine_sim')
        )
        .join(Chunk, Embedding.chunk_id == Chunk.id)
        .join(NoteProjection, Embedding.note_projection_id == NoteProjection.id)
        .where(NoteProjection.workspace_id == workspace_id)
        .order_by(text('cosine_sim DESC'))
        .limit(limit * 2)
    )
    vector_results = (await db.execute(vector_stmt)).fetchall()
    vector_ranked = [(row[0], row[2], i+1) for i, row in enumerate(vector_results)]

    # Step 3: RRF fusion
    rrf_scores = reciprocal_rank_fusion(fts_ranked, vector_ranked, k=60)

    # Step 4: Sort by RRF score and take top N
    sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:limit]

    # Step 5: Fetch full chunk data
    chunks_stmt = (
        select(Chunk, NoteProjection)
        .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
        .where(Chunk.id.in_(sorted_chunk_ids))
    )
    chunk_data = {row[0].id: row for row in (await db.execute(chunks_stmt)).fetchall()}

    # Step 6: Build results
    results = []
    for chunk_id in sorted_chunk_ids:
        if chunk_id not in chunk_data:
            continue
        chunk, note_proj = chunk_data[chunk_id]
        fts_info = next((x for x in fts_results if x[0] == chunk_id), (None, None, 0))
        vec_info = next((x for x in vector_results if x[0] == chunk_id), (None, None, 0))

        results.append(RetrievalResult(
            chunk_id=chunk_id,
            note_projection_id=note_proj.id,
            fts_rank=fts_info[2] if fts_info else 0,
            vector_rank=vec_info[2] if vec_info else 0,
            fts_score=fts_info[1] if fts_info else 0.0,
            vector_score=vec_info[1] if vec_info else 0.0,
            rrf_score=rrf_scores[chunk_id],
            note_path=note_proj.note_path,
            heading_path=chunk.heading_path,
            content=chunk.content,
            title=note_proj.title,
            tags=note_proj.tags or [],
            metadata={"kind": note_proj.kind, "frontmatter": note_proj.frontmatter},
        ))

    return results
```

---

## 6. Context Pack Construction (F10-04)

### 6.1 ContextPack Schema (D-105)

```python
# src/api/schemas/retrieval.py
from pydantic import BaseModel, Field
from uuid import UUID

class ContextPackNeighbor(BaseModel):
    """A neighboring chunk from the same note."""
    chunk_id: UUID
    heading_path: str
    content_snippet: str  # Truncated to ~200 chars
    chunk_index: int
    relevance_score: float

class ContextPackProvenance(BaseModel):
    """Where and when this chunk came from."""
    note_path: str
    heading_path: str
    workspace_id: UUID
    indexed_at: str  # ISO timestamp
    source_file: str  # Original markdown file path

class ContextPackMetadata(BaseModel):
    """Chunk metadata."""
    kind: str  # NoteType
    tags: list[str]
    links: list[str]
    frontmatter: dict

class ContextPack(BaseModel):
    """A complete context pack for LLM consumption.

    Per D-105, D-106, D-107, D-108:
    - note reference
    - snippet (the retrieved chunk content)
    - score (RRF score with breakdown)
    - why_matched (explanation of why this chunk was retrieved)
    - metadata (note kind, tags, links, frontmatter)
    - neighbors (top-3 related chunks from same note)
    - provenance (note_path, heading_path, workspace_id, indexed_at)
    """
    chunk_id: UUID
    note_reference: str  # Human-readable: "note_path#heading"

    # Core content
    snippet: str = Field(description="The retrieved chunk content (may be truncated)")
    heading_path: str = Field(description="Full heading path, e.g. '## Introduction'")

    # Scoring
    score: float = Field(description="RRF combined score")
    score_breakdown: dict[str, float] = Field(
        description="FTS component, vector component, recency boost if any"
    )
    fts_rank: int
    vector_rank: int

    # Why matched
    why_matched: str = Field(
        description="Human-readable explanation of why this chunk was retrieved"
    )

    # Neighbors
    neighbors: list[ContextPackNeighbor] = Field(
        default_factory=list,
        description="Top-3 related chunks from same note"
    )

    # Provenance
    provenance: ContextPackProvenance

    # Metadata
    metadata: ContextPackMetadata
```

### 6.2 Building Neighbors

"Neighbors" = other chunks from the same note that are topically related. Options:

1. **Sequential neighbors**: chunk_index ± 1, ± 2 (D-106 says top-3 related chunks)
2. **Vector neighbors**: Find chunks with similar embeddings in same note
3. **Heading-based neighbors**: All chunks under the same H1/H2 parent heading

**Decision (D-106):** Top-3 **sequential neighbors** (chunk_index proximity) -- simpler, coherent context, good UX. Vector neighbors deferred to v2.

```python
async def get_chunk_neighbors(
    db: AsyncSession,
    chunk: Chunk,
    limit: int = 3,
) -> list[ContextPackNeighbor]:
    """Get sequential neighbors of a chunk within the same note."""
    stmt = (
        select(Chunk)
        .where(
            Chunk.note_projection_id == chunk.note_projection_id,
            Chunk.chunk_index.in_([
                chunk.chunk_index - 1,
                chunk.chunk_index - 2,
                chunk.chunk_index + 1,
                chunk.chunk_index + 2,
            ])
        )
        .order_by(Chunk.chunk_index)
    )
    neighbors = (await db.execute(stmt)).scalars().all()

    return [
        ContextPackNeighbor(
            chunk_id=n.id,
            heading_path=n.heading_path,
            content_snippet=n.content[:200] + "..." if len(n.content) > 200 else n.content,
            chunk_index=n.chunk_index,
            relevance_score=1.0 / abs(n.chunk_index - chunk.chunk_index),  # Proximity weight
        )
        for n in neighbors[:limit]
    ]
```

### 6.3 Score Breakdown (D-108)

```python
def build_score_breakdown(
    fts_score: float,
    vector_score: float,
    note_updated_at: datetime | None,
    weights: tuple[float, float] = (0.5, 0.5),
) -> dict[str, float]:
    """Build score breakdown per D-108.

    Optional recency boost: newer notes get a small boost.
    """
    breakdown = {
        "fts_component": fts_score * weights[0],
        "vector_component": vector_score * weights[1],
        "fts_raw": fts_score,
        "vector_raw": vector_score,
    }

    # Optional recency boost (last 7 days get +5%)
    if note_updated_at:
        days_old = (datetime.utcnow() - note_updated_at).days
        if days_old <= 7:
            recency_boost = 0.05
            breakdown["recency_boost"] = recency_boost

    return breakdown
```

---

## 7. Incremental Index Updates (F10-06)

### 7.1 Event-Driven Update Flow

Per D-109: Incremental updates via `index_note` job on note change.

When a note is created/updated/deleted:
1. `NoteProjection` sync job (Phase 4 F8-02) detects the change
2. Enqueues `index_note` job with `{note_id, workspace_id, operation: "upsert"|"delete"}`
3. `handle_index_note` worker handler runs:
   - If delete: remove chunks + embeddings for that note
   - If upsert: re-chunk the note, update FTS, enqueue `generate_embeddings`

```python
async def handle_index_note(input_data: dict) -> dict:
    """Per-file: src/worker/handlers/index_note.py (replace placeholder)."""
    note_id = input_data.get("note_id")
    workspace_id = input_data.get("workspace_id")
    operation = input_data.get("operation", "upsert")

    from src.db.session import async_session_maker
    from src.db.models.note_projection import NoteProjection
    from src.db.models.chunk import Chunk
    from sqlalchemy import delete, select

    async with async_session_maker() as db:
        if operation == "delete":
            # Remove chunks and their embeddings
            chunks_stmt = select(Chunk.id).where(Chunk.note_projection_id == note_id)
            chunk_ids = (await db.execute(chunks_stmt)).scalars().all()

            # Delete embeddings first (foreign key)
            for cid in chunk_ids:
                await db.execute(delete(Embedding).where(Embedding.chunk_id == cid))

            # Delete chunks
            await db.execute(delete(Chunk).where(Chunk.note_projection_id == note_id))

            # Mark note_projection as not indexed
            await db.execute(
                update(NoteProjection)
                .where(NoteProjection.id == note_id)
                .values(indexed_at=None)
            )

            return {"note_id": str(note_id), "deleted": True}

        # upsert: read note from filesystem
        note_proj = await db.get(NoteProjection, note_id)
        if not note_proj:
            return {"error": f"NoteProjection {note_id} not found"}

        # Read markdown file
        note_path = os.path.join(note_proj.workspace.root_path, note_proj.note_path)
        with open(note_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Parse frontmatter and body
        frontmatter, body = parse_frontmatter(markdown_content)

        # Chunk the content
        chunks = chunk_by_headings(body)

        # Delete old chunks
        await db.execute(delete(Chunk).where(Chunk.note_projection_id == note_id))

        # Insert new chunks with FTS vectors
        for i, chunk_data in enumerate(chunks):
            chunk = Chunk(
                note_projection_id=note_id,
                heading_path=chunk_data.heading_path,
                content=chunk_data.content,
                chunk_index=chunk_data.chunk_index,
                char_start=chunk_data.char_start,
                char_end=chunk_data.char_end,
            )
            db.add(chunk)
            await db.flush()

            # Set tsvector for FTS
            await db.execute(
                update(Chunk)
                .where(Chunk.id == chunk.id)
                .values(content_tsv=func.to_tsvector('english', chunk_data.content))
            )

        # Mark indexed
        await db.execute(
            update(NoteProjection)
            .where(NoteProjection.id == note_id)
            .values(indexed_at=datetime.utcnow())
        )

        await db.commit()

        # Enqueue embedding generation
        from src.services.job_service import JobService
        job_service = JobService(db)
        new_chunk_ids = [c.id for c in chunks]
        await job_service.enqueue(
            "generate_embeddings",
            {"note_id": str(note_id), "chunk_ids": [str(cid) for cid in new_chunk_ids]},
            priority=5,
            workspace_id=workspace_id,
        )

        return {
            "note_id": str(note_id),
            "chunks_created": len(chunks),
            "enqueued_embeddings": len(new_chunk_ids),
        }
```

### 7.2 Full Rebuild (D-110)

`handle_reindex_scope` iterates all `NoteProjection` records for a workspace and enqueues `index_note` for each:

```python
async def handle_reindex_scope(input_data: dict) -> dict:
    """Per-file: src/worker/handlers/reindex_scope.py (replace placeholder)."""
    workspace_id = input_data.get("workspace_id")
    scope_type = input_data.get("scope_type", "full")  # or "folder", "tag"
    scope_path = input_data.get("scope_path")

    from src.db.session import async_session_maker
    from src.db.models.note_projection import NoteProjection
    from sqlalchemy import select

    async with async_session_maker() as db:
        stmt = select(NoteProjection).where(NoteProjection.workspace_id == workspace_id)
        if scope_type == "folder" and scope_path:
            stmt = stmt.where(NoteProjection.note_path.like(f"{scope_path}%"))

        notes = (await db.execute(stmt)).scalars().all()

        from src.services.job_service import JobService
        job_service = JobService(db)

        enqueued = []
        for note in notes:
            job = await job_service.enqueue(
                "index_note",
                {"note_id": str(note.id), "workspace_id": str(workspace_id), "operation": "upsert"},
                priority=0,  # Lower priority than user-triggered jobs
                workspace_id=workspace_id,
            )
            enqueued.append(str(job.id))

        return {
            "workspace_id": str(workspace_id),
            "notes_to_reindex": len(notes),
            "jobs_enqueued": len(enqueued),
            "job_ids": enqueued,
        }
```

### 7.3 Change Detection

`NoteProjection` already has `note_hash` and `content_hash` (D-51). When these change, the sync job should trigger reindexing. The Phase 4 `index_note` job type already exists as a trigger point.

---

## 8. API Endpoints (D-112, D-113, D-114)

### 8.1 Existing Endpoint: `GET /retrieval/search`

Currently placeholder (per `src/api/retrieval.py`). Needs to be replaced with actual hybrid search:

```python
# Replace src/api/retrieval.py hybrid_search function

@router.get("/search")
async def hybrid_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    mode: Literal["fts", "vector", "hybrid"] = Query("hybrid"),
    workspace_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Hybrid search across notes.

    Combines PostgreSQL FTS with pgvector semantic search using RRF.
    """
    from src.services.embeddings import get_embeddings_provider
    from src.services.retrieval import hybrid_search as do_hybrid_search

    # Get workspace
    if workspace_id is None:
        ws_stmt = select(Workspace).limit(1)
    else:
        ws_stmt = select(Workspace).where(Workspace.id == workspace_id)
    ws_result = await db.execute(ws_stmt)
    workspace = ws_result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get query embedding
    provider = get_embeddings_provider()
    query_vector = (await provider.embed_texts([q]))[0]

    # Execute search
    results = await do_hybrid_search(
        db=db,
        workspace_id=workspace.id,
        query=q,
        query_vector=query_vector,
        limit=limit,
        mode=mode,
    )

    # Build context packs
    context_packs = [build_context_pack(r, db) for r in results]

    return {
        "query": q,
        "mode": mode,
        "results": [cp.model_dump() for cp in context_packs],
        "total": len(context_packs),
    }
```

### 8.2 `GET /retrieval/context/{note_id}`

```python
@router.get("/context/{note_id}")
async def get_context_pack(
    note_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get context pack for a specific note.

    Returns the note's chunks with neighbors and provenance.
    """
    from src.services.retrieval import build_note_context_pack

    note = await db.get(NoteProjection, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    context = await build_note_context_pack(db, note, limit=limit)

    return context.model_dump()
```

### 8.3 `POST /retrieval/reindex`

Already implemented in current `src/api/retrieval.py` (lines 77-119). Minor fix: the job type should be `reindex_scope` per the handler.

---

## 9. New Dependencies

The following packages need to be added to `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing ...

    # Embeddings
    "openai>=1.0.0",  # For OpenAI embeddings API (or use httpx directly)

    # pgvector Python support
    "pgvector>=0.3.0",  # For Vector type in SQLAlchemy models

    # Token counting for chunking
    "tiktoken>=0.7.0",  # OpenAI's tokenizer
]
```

**Note:** `openai` package is needed for the embeddings API. Alternative: use `httpx` directly with the REST API (no SDK dependency). Per Stack Decision Record §14.4, avoid heavy dependencies like `LiteLLM`. Using `httpx` directly is lighter.

---

## 10. Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `src/services/embeddings.py` | EmbeddingsProvider interface + OpenAI implementation |
| `src/services/retrieval.py` | Hybrid search, context pack builder |
| `src/services/chunking.py` | Heading-guided chunking logic |
| `src/api/schemas/retrieval.py` | Pydantic schemas (ContextPack, etc.) |
| `alembic/versions/002_add_fts_and_pgvector.py` | Migration for FTS columns, vector type, indexes |

### Existing Files to Modify

| File | Change |
|------|--------|
| `src/db/models/embedding.py` | Change `embedding_vector` from `JSON` to `Vector(1536)` |
| `src/worker/handlers/index_note.py` | Replace placeholder with real implementation |
| `src/worker/handlers/reindex_scope.py` | Replace placeholder with real implementation |
| `src/worker/handlers/generate_embeddings.py` | Replace placeholder with real implementation |
| `src/api/retrieval.py` | Replace placeholder implementations with real ones |
| `pyproject.toml` | Add openai, pgvector, tiktoken dependencies |

---

## 11. Critical Technical Decisions

### 11.1 FTS at Chunk Level vs Note Level

**Decision:** Index at **chunk level** (`chunks.content_tsv`). Reasoning:
- Vector search operates per-chunk (each chunk has its own embedding)
- FTS at chunk level gives finer-grained, more relevant results
- Both rankers operate on the same unit (chunk), making RRF fusion cleaner

### 11.2 Vector Type vs JSONB for Embeddings

**Decision:** Use pgvector's native `vector(1536)` type, not JSONB. Reasoning:
- JSONB does not support vector operations (cosine distance, L2)
- Cannot create HNSW index on JSONB column
- pgvector's Vector type is natively supported and indexed

### 11.3 HNSW vs IVFFlat for pgvector Index

**Decision (D-111):** HNSW. Reasoning:
- Better query performance (the critical path)
- Build cost acceptable for <100K chunks
- IVFFlat: faster build, less memory, but worse query performance and requires exact `lists` parameter tuning

### 11.4 OpenAI Embeddings vs Local Models

**Decision (D-94):** `text-embedding-3-small` via OpenAI API. Reasoning:
- Good quality/cost ratio (1536 dims, low cost)
- Local models (BGE, etc.) deferred to v2 per D-108
- BYOK-friendly: can swap provider later via EmbeddingsProvider interface

---

## 12. Open Questions (Pre-Planning)

1. **FTS index update strategy**: Application-level update on each `index_note` (simpler) vs PostgreSQL triggers on `chunks` table (more robust but complex)? Recommendation: application-level for v1.

2. **Query embedding caching**: Should query embeddings be cached? Cost: memory. Benefit: avoid repeated API calls for same query in a session. Recommendation: cache in-memory with TTL for session duration.

3. **Minimum chunk size**: What if a heading section is smaller than the 512-token limit? Should short sections be merged with the next? Recommendation: merge sections under ~100 tokens with next section.

4. **Context pack size limit**: Max chunks to return per search? Max neighbors per chunk? Recommendation: max 20 results, max 3 neighbors.

5. **Empty FTS or empty vector results**: If one ranker returns no results, should we fall back to the other ranker alone? Recommendation: yes, RRF handles this naturally (zero contributions from empty ranker).

---

## 13. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| pgvector HNSW index build time for large vaults | Medium | High | Use `reindex_scope` with low priority; do incremental builds |
| OpenAI API rate limits on bulk embedding | Medium | Medium | Semaphore + batch size of 100; graceful backoff |
| Chunking produces poor splits at boundaries | Medium | Medium | Multiple break strategies (paragraph → sentence → word); fallback to char limit |
| FTS stemming doesn't match user intent | Low | Low | `websearch_to_tsquery` handles natural language better than `plainto_tsquery` |
| Embedding drift (same text different vector) | Low | Low | text-embedding-3-small is deterministic; if not, cache by content hash |

---

## 14. Sequence to Implement

Recommended order to minimize cross-cutting changes:

1. **Migration** (`002_add_fts_and_pgvector`): Add `content_tsv` to `chunks`, change `embedding_vector` to `vector(1536)`, create GIN and HNSW indexes
2. **Chunking service** (`chunking.py`): Pure logic, no DB deps
3. **Embeddings service** (`embeddings.py`): Pure logic, no DB deps
4. **Retrieval service** (`retrieval.py`): Uses chunking + embeddings + DB
5. **Job handlers** (index_note, generate_embeddings, reindex_scope): Wired to retrieval service
6. **API endpoints** (`retrieval.py`): Wired to retrieval service
7. **Tests**: Unit tests for chunking, embeddings batching; integration tests for hybrid search

---

*Research completed: 2026-03-31*
*Key references: pgvector GitHub, PostgreSQL FTS docs, OpenAI embeddings API docs*
