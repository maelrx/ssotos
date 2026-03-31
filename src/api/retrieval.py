"""Retrieval REST API — per D-112, D-113, D-114."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Chunk, Embedding, NoteProjection, Workspace
from src.db.session import get_db
from src.schemas.retrieval import (
    ContextPack,
    SearchRequest,
    SearchResponse,
)
from src.services.retrieval_service import RetrievalService
from src.services.retrieval_service import search as do_search

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.get("/search", response_model=SearchResponse)
async def hybrid_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    mode: str = Query("hybrid", description="Search mode: fts, vector, or hybrid"),
    workspace_id: UUID | None = Query(None, description="Workspace ID"),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """Hybrid search across notes — FTS + pgvector with RRF fusion (D-90, D-112).

    Returns results with full score breakdowns, FTS/vector ranks, and why_matched.
    Falls back to FTS-only if embeddings are not yet generated.
    """
    # Resolve workspace
    if workspace_id is None:
        ws_result = await db.execute(select(Workspace).limit(1))
    else:
        ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    request = SearchRequest(q=q, limit=limit, mode=mode)
    return await do_search(db=db, workspace_id=workspace.id, request=request)


@router.get("/context/{note_id}", response_model=list[ContextPack])
async def get_context_pack(
    note_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="Max chunks to return"),
    db: AsyncSession = Depends(get_db),
) -> list[ContextPack]:
    """Get context pack for a note — all chunks with neighbors and provenance (D-113)."""
    # Verify note exists
    note = await db.get(NoteProjection, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    svc = RetrievalService(db)
    chunks_stmt = (
        select(Chunk, NoteProjection)
        .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
        .where(NoteProjection.id == note_id)
        .order_by(Chunk.chunk_index)
        .limit(limit)
    )
    rows = (await db.execute(chunks_stmt)).fetchall()

    packs: list[ContextPack] = []
    for chunk, _note_proj in rows:
        pack = await svc.build_context_pack(chunk.id, db)
        # Fill in score info from context
        packs.append(ContextPack(
            chunk_id=pack.chunk_id,
            note_reference=pack.note_reference,
            snippet=pack.snippet,
            heading_path=pack.heading_path,
            score=0.0,
            score_breakdown={},
            fts_rank=0,
            vector_rank=0,
            why_matched="Context pack for note",
            neighbors=pack.neighbors,
            provenance=pack.provenance,
            metadata=pack.metadata,
        ))

    return packs


@router.post("/reindex")
async def trigger_reindex(
    workspace_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a full reindex job for the workspace (D-114).

    Creates a high-priority reindex_scope job.
    """
    from src.db.models.job import Job

    # Get workspace
    if workspace_id:
        ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    else:
        ws_result = await db.execute(select(Workspace).limit(1))
    workspace = ws_result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Create reindex job
    job = Job(
        job_type="reindex_scope",
        priority=100,
        input_data={"workspace_id": str(workspace.id), "scope": "full"},
        workspace_id=workspace.id,
        status="pending",
    )
    db.add(job)
    await db.flush()

    return {
        "success": True,
        "message": "Reindex job created",
        "job_id": str(job.id),
    }


@router.get("/stats/{workspace_id}")
async def get_retrieval_stats(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get retrieval index statistics for a workspace (D-112).

    Returns counts: total_chunks, total_embeddings, indexed_notes.
    """
    # Verify workspace
    ws = await db.get(Workspace, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Count chunks
    chunk_count = await db.scalar(
        select(func.count(Chunk.id))
        .join(NoteProjection, Chunk.note_projection_id == NoteProjection.id)
        .where(NoteProjection.workspace_id == workspace_id)
    )

    # Count embeddings
    embedding_count = await db.scalar(
        select(func.count(Embedding.id))
        .join(NoteProjection, Embedding.note_projection_id == NoteProjection.id)
        .where(NoteProjection.workspace_id == workspace_id)
    )

    # Count indexed notes
    indexed_notes = await db.scalar(
        select(func.count(NoteProjection.id))
        .where(
            NoteProjection.workspace_id == workspace_id,
            NoteProjection.indexed_at.isnot(None),
        )
    )

    return {
        "total_chunks": chunk_count or 0,
        "total_embeddings": embedding_count or 0,
        "indexed_notes": indexed_notes or 0,
    }
