"""Retrieval service — hybrid search with FTS + pgvector + RRF fusion.

Per D-90, D-97, D-99, D-105.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Any

import httpx
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, joinedload

from src.db.models.chunk import Chunk
from src.db.models.embedding import Embedding
from src.db.models.note_projection import NoteProjection
from src.schemas.retrieval import (
    SearchRequest,
    SearchResult,
    SearchResponse,
    ContextPack,
    ContextPackNeighbor,
    ContextPackProvenance,
    ContextPackMetadata,
)


# ─────────────────────────────────────────────────────────────
# Embeddings Provider
# ─────────────────────────────────────────────────────────────


class EmbeddingsProvider(Protocol):
    """Protocol for embedding generation providers — per D-94."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of text chunks to embed.

        Returns:
            List of embedding vectors (1536-dim for text-embedding-3-small).
        """
        ...


class OpenAIEmbeddingsProvider:
    """OpenAI text-embedding-3-small provider — per D-94, research §3.1."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ["OPENAI_API_KEY"]
        self.model = "text-embedding-3-small"
        self.dimensions = 1536
        self.base_url = "https://api.openai.com/v1/embeddings"

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via OpenAI embeddings API."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": texts,
                    "model": self.model,
                    "dimensions": self.dimensions,
                },
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]


# ─────────────────────────────────────────────────────────────
# Internal result types
# ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RetrievalResult:
    """Internal retrieval result before schema serialization."""

    chunk_id: Any
    note_projection_id: Any
    fts_rank: int
    vector_rank: int
    fts_score: float
    vector_score: float
    rrf_score: float
    note_path: str
    heading_path: str
    content: str
    title: str
    tags: list[str]
    metadata: dict[str, Any]


# ─────────────────────────────────────────────────────────────
# RRF Fusion
# ─────────────────────────────────────────────────────────────


def reciprocal_rank_fusion(
    fts_results: list[tuple[Any, float, int]],
    vector_results: list[tuple[Any, float, int]],
    k: int = 60,
) -> dict[Any, float]:
    """Combine FTS and vector rankings using Reciprocal Rank Fusion — per D-97.

    RRF formula: score(d) = sum(1 / (k + rank(d))) for each ranker.
    k=60 is the standard value per D-97.
    """
    rrf_scores: dict[Any, float] = {}

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


# ─────────────────────────────────────────────────────────────
# Retrieval Service
# ─────────────────────────────────────────────────────────────


class RetrievalService:
    """Hybrid retrieval combining PostgreSQL FTS with pgvector — per D-90, D-99."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── FTS Search ────────────────────────────────────────────

    async def fts_search(
        self,
        workspace_id: Any,
        query: str,
        limit: int = 20,
    ) -> list[tuple[Any, float, int]]:
        """Full-text search using PostgreSQL tsvector/tsquery — per D-98.

        Returns list of (chunk_id, fts_score, rank) ordered by ts_rank_cd.
        """
        tsquery = func.websearch_to_tsquery("english", query)
        stmt = (
            select(
                Chunk.id,
                func.ts_rank_cd(Chunk.content_tsv, tsquery).label("fts_score"),
            )
            .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
            .where(
                NoteProjection.workspace_id == workspace_id,
                Chunk.content_tsv.op("@@")(tsquery),
            )
            .order_by(text("fts_score DESC"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        return [(row[0], float(row[1]), i + 1) for i, row in enumerate(rows)]

    # ── Vector Search ─────────────────────────────────────────

    async def vector_search(
        self,
        workspace_id: Any,
        query_vector: list[float],
        limit: int = 20,
    ) -> list[tuple[Any, float, int]]:
        """Vector search using pgvector cosine similarity — per D-99.

        Returns list of (chunk_id, cosine_sim, rank) ordered by similarity.
        """
        from pgvector.sqlalchemy import Vector

        # Cast query vector to vector type
        query_vec = func.cast(query_vector, Vector(1536))
        # Cosine similarity = 1 - cosine_distance
        cosine_sim = 1 - func.cosine_distance(Embedding.embedding_vector, query_vec)

        stmt = (
            select(
                Embedding.chunk_id,
                cosine_sim.label("cosine_sim"),
            )
            .join(Chunk, Embedding.chunk_id == Chunk.id)
            .join(NoteProjection, Embedding.note_projection_id == NoteProjection.id)
            .where(NoteProjection.workspace_id == workspace_id)
            .order_by(text("cosine_sim DESC"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        return [(row[0], float(row[1]), i + 1) for i, row in enumerate(rows)]

    # ── Hybrid Search ────────────────────────────────────────

    async def hybrid_search(
        self,
        workspace_id: Any,
        query: str,
        query_vector: list[float],
        limit: int = 20,
        mode: str = "hybrid",
    ) -> list[RetrievalResult]:
        """Hybrid search combining FTS + vector via RRF — per D-90, D-97.

        Args:
            workspace_id: Workspace to search within.
            query: Raw query string for FTS.
            query_vector: Pre-computed query embedding.
            limit: Max results.
            mode: 'fts', 'vector', or 'hybrid'.

        Returns:
            List of RetrievalResult sorted by RRF score.
        """
        # Run rankers
        fts_limit = limit * 2 if mode in ("fts", "hybrid") else 0
        vec_limit = limit * 2 if mode in ("vector", "hybrid") else 0

        fts_results: list[tuple[Any, float, int]] = []
        vector_results: list[tuple[Any, float, int]] = []

        if mode in ("fts", "hybrid") and fts_limit > 0:
            fts_results = await self.fts_search(workspace_id, query, fts_limit)

        if mode in ("vector", "hybrid") and vec_limit > 0:
            vector_results = await self.vector_search(workspace_id, query_vector, vec_limit)

        # Apply RRF fusion
        if mode == "hybrid":
            rrf_scores = reciprocal_rank_fusion(fts_results, vector_results, k=60)
        elif mode == "fts":
            rrf_scores = {cid: 1 / (60 + rank) for cid, score, rank in fts_results}
        else:  # vector
            rrf_scores = {cid: 1 / (60 + rank) for cid, score, rank in vector_results}

        # Sort by RRF score and take top N
        sorted_chunk_ids = sorted(
            rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True
        )[:limit]

        if not sorted_chunk_ids:
            return []

        # Fetch full chunk data for top results
        chunks_stmt = (
            select(Chunk, NoteProjection)
            .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
            .where(Chunk.id.in_(sorted_chunk_ids))
        )
        chunk_rows = (await self.db.execute(chunks_stmt)).fetchall()
        chunk_data = {row[0].id: row for row in chunk_rows}

        # Build index lookups for ranks
        fts_rank_map = {cid: rank for cid, _, rank in fts_results}
        vec_rank_map = {cid: rank for cid, _, rank in vector_results}

        # Build results
        results: list[RetrievalResult] = []
        for chunk_id in sorted_chunk_ids:
            if chunk_id not in chunk_data:
                continue
            chunk, note_proj = chunk_data[chunk_id]

            fts_info = next(
                ((s, r) for c, s, r in fts_results if c == chunk_id),
                (0.0, 0),
            )
            vec_info = next(
                ((s, r) for c, s, r in vector_results if c == chunk_id),
                (0.0, 0),
            )

            results.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    note_projection_id=note_proj.id,
                    fts_rank=fts_rank_map.get(chunk_id, 0),
                    vector_rank=vec_rank_map.get(chunk_id, 0),
                    fts_score=fts_info[0],
                    vector_score=vec_info[0],
                    rrf_score=rrf_scores[chunk_id],
                    note_path=note_proj.note_path,
                    heading_path=chunk.heading_path,
                    content=chunk.content,
                    title=note_proj.title,
                    tags=note_proj.tags or [],
                    metadata={
                        "kind": note_proj.kind,
                        "frontmatter": note_proj.frontmatter or {},
                    },
                )
            )

        return results

    # ── Context Pack Builder ─────────────────────────────────

    async def build_context_pack(
        self,
        chunk_id: Any,
        db: AsyncSession,
    ) -> ContextPack:
        """Build a complete ContextPack for a chunk — per D-105.

        Includes neighbors (sequential, top-3), provenance, and metadata.
        """
        # Fetch chunk and note projection
        chunk_stmt = (
            select(Chunk, NoteProjection)
            .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
            .where(Chunk.id == chunk_id)
        )
        row = (await db.execute(chunk_stmt)).fetchone()
        if not row:
            raise ValueError(f"Chunk {chunk_id} not found")
        chunk, note_proj = row

        # Fetch sequential neighbors (chunk_index ±1, ±2)
        neighbor_stmt = (
            select(Chunk)
            .where(
                Chunk.note_projection_id == chunk.note_projection_id,
                Chunk.chunk_index.in_([
                    chunk.chunk_index - 2,
                    chunk.chunk_index - 1,
                    chunk.chunk_index + 1,
                    chunk.chunk_index + 2,
                ]),
            )
            .order_by(Chunk.chunk_index)
        )
        neighbor_rows = (await db.execute(neighbor_stmt)).fetchall()
        neighbors = [
            ContextPackNeighbor(
                chunk_id=n.id,
                heading_path=n.heading_path,
                content_snippet=n.content[:200] + "..." if len(n.content) > 200 else n.content,
                chunk_index=n.chunk_index,
                relevance_score=1.0 / (abs(n.chunk_index - chunk.chunk_index) or 1),
            )
            for n in neighbor_rows[:3]
        ]

        # Build provenance
        provenance = ContextPackProvenance(
            note_path=note_proj.note_path,
            heading_path=chunk.heading_path,
            workspace_id=note_proj.workspace_id,
            indexed_at=note_proj.indexed_at or note_proj.updated_at,
            source_file=note_proj.note_path,
        )

        # Build metadata
        metadata = ContextPackMetadata(
            kind=note_proj.kind,
            tags=note_proj.tags or [],
            links=note_proj.links or [],
            frontmatter=note_proj.frontmatter or {},
        )

        # Build note reference
        note_reference = f"{note_proj.note_path}#{chunk.heading_path}"

        return ContextPack(
            chunk_id=chunk.id,
            note_reference=note_reference,
            snippet=chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
            heading_path=chunk.heading_path,
            score=0.0,  # Set by caller from RRF score
            score_breakdown={},  # Set by caller
            fts_rank=0,  # Set by caller
            vector_rank=0,  # Set by caller
            why_matched="",  # Set by caller
            neighbors=neighbors,
            provenance=provenance,
            metadata=metadata,
        )


# ─────────────────────────────────────────────────────────────
# Convenience functions
# ─────────────────────────────────────────────────────────────


async def search(
    db: AsyncSession,
    workspace_id: Any,
    request: SearchRequest,
    provider: EmbeddingsProvider | None = None,
) -> SearchResponse:
    """High-level search function for use in API handlers."""
    if request.mode == "basic":
        # Fallback for when embeddings are not yet generated
        svc = RetrievalService(db)
        fts_results = await svc.fts_search(workspace_id, request.q, request.limit)
        results: list[SearchResult] = []

        if fts_results:
            chunk_ids = [cid for cid, _, _ in fts_results]
            chunks_stmt = (
                select(Chunk, NoteProjection)
                .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
                .where(Chunk.id.in_(chunk_ids))
            )
            chunk_rows = (await db.execute(chunks_stmt)).fetchall()
            chunk_data = {row[0].id: row for row in chunk_rows}

            for rank, (chunk_id, fts_score, _) in enumerate(fts_results, start=1):
                if chunk_id not in chunk_data:
                    continue
                chunk, note_proj = chunk_data[chunk_id]
                results.append(
                    SearchResult(
                        chunk_id=chunk_id,
                        note_id=note_proj.id,
                        note_path=note_proj.note_path,
                        heading_path=chunk.heading_path,
                        title=note_proj.title,
                        tags=note_proj.tags or [],
                        content_snippet=chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
                        score=float(fts_score),
                        score_breakdown={"fts_raw": float(fts_score)},
                        fts_rank=rank,
                        vector_rank=0,
                        why_matched=f"FTS match (rank {rank})",
                    )
                )

        return SearchResponse(
            query=request.q,
            mode="fts",
            results=results,
            total=len(results),
        )

    # Full hybrid search
    if provider is None:
        provider = OpenAIEmbeddingsProvider()

    query_vector = (await provider.embed_texts([request.q]))[0]
    svc = RetrievalService(db)
    retrieval_results = await svc.hybrid_search(
        workspace_id=workspace_id,
        query=request.q,
        query_vector=query_vector,
        limit=request.limit,
        mode=request.mode,
    )

    search_results: list[SearchResult] = []
    for r in retrieval_results:
        score_breakdown = {
            "fts_component": r.fts_score * 0.5,
            "vector_component": r.vector_score * 0.5,
            "fts_raw": r.fts_score,
            "vector_raw": r.vector_score,
        }
        search_results.append(
            SearchResult(
                chunk_id=r.chunk_id,
                note_id=r.note_projection_id,
                note_path=r.note_path,
                heading_path=r.heading_path,
                title=r.title,
                tags=r.tags,
                content_snippet=r.content[:500] + "..." if len(r.content) > 500 else r.content,
                score=r.rrf_score,
                score_breakdown=score_breakdown,
                fts_rank=r.fts_rank,
                vector_rank=r.vector_rank,
                why_matched=_build_why_matched(r),
            )
        )

    return SearchResponse(
        query=request.q,
        mode=request.mode,
        results=search_results,
        total=len(search_results),
    )


def _build_why_matched(r: RetrievalResult) -> str:
    """Build a human-readable explanation of why a chunk was retrieved."""
    parts = []
    if r.fts_rank > 0:
        parts.append(f"FTS rank {r.fts_rank}")
    if r.vector_rank > 0:
        parts.append(f"vector rank {r.vector_rank}")
    if not parts:
        return "Matched by query"
    return f"Matched by: {', '.join(parts)}"
