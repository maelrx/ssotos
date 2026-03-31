"""Retrieval schemas — per D-105, D-90, D-97, D-99."""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Literal


# ─────────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────────


class SearchRequest(BaseModel):
    """Hybrid search request — FTS + vector + RRF fusion."""

    q: str = Field(min_length=1, description="Search query text")
    limit: int = Field(default=20, ge=1, le=100, description="Max results to return")
    mode: Literal["fts", "vector", "hybrid"] = "hybrid"


class SearchResult(BaseModel):
    """A single search result with score breakdown."""

    chunk_id: UUID
    note_id: UUID
    note_path: str
    heading_path: str
    title: str
    tags: list[str]
    content_snippet: str = Field(description="Truncated to 500 chars")
    score: float
    score_breakdown: dict[str, float] = Field(
        description="fts_component, vector_component, recency_boost if applicable"
    )
    fts_rank: int
    vector_rank: int
    why_matched: str


class SearchResponse(BaseModel):
    """Full search response with query metadata."""

    query: str
    mode: str
    results: list[SearchResult]
    total: int


# ─────────────────────────────────────────────────────────────
# Context Pack
# ─────────────────────────────────────────────────────────────


class ContextPackNeighbor(BaseModel):
    """A neighboring chunk from the same note — per D-106."""

    chunk_id: UUID
    heading_path: str
    content_snippet: str = Field(description="Truncated to 200 chars")
    chunk_index: int
    relevance_score: float


class ContextPackProvenance(BaseModel):
    """Where and when this chunk came from — per D-107."""

    note_path: str
    heading_path: str
    workspace_id: UUID
    indexed_at: datetime
    source_file: str


class ContextPackMetadata(BaseModel):
    """Chunk metadata — per D-108."""

    kind: str
    tags: list[str]
    links: list[str]
    frontmatter: dict


class ContextPack(BaseModel):
    """A complete context pack for LLM consumption — per D-105.

    Contains: note reference, snippet, score, why_matched, metadata,
    neighbors (top-3 from same note), provenance.
    """

    chunk_id: UUID
    note_reference: str = Field(
        description="Human-readable: note_path#heading"
    )
    snippet: str = Field(description="The retrieved chunk content (may be truncated)")
    heading_path: str
    score: float
    score_breakdown: dict[str, float]
    fts_rank: int
    vector_rank: int
    why_matched: str = Field(
        description="Human-readable explanation of why this chunk was retrieved"
    )
    neighbors: list[ContextPackNeighbor] = Field(
        default_factory=list,
        description="Top-3 sequential neighbors from same note"
    )
    provenance: ContextPackProvenance
    metadata: ContextPackMetadata
