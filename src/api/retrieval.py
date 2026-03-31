"""Retrieval REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.db.session import get_db
from src.db.models.note_projection import NoteProjection
from src.db.models.chunk import Chunk
from src.db.models.embedding import Embedding

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.get("/search")
async def hybrid_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """Hybrid search across notes (Phase 6 feature).

    Combines full-text search with semantic vector search.
    For Phase 1-5, returns basic title/path matching.
    """
    # Phase 6 will use pgvector for semantic search
    # For now, use basic FTS-like matching on titles
    try:
        stmt = (
            select(NoteProjection)
            .where(NoteProjection.title.ilike(f"%{q}%"))
            .limit(limit)
        )
        result = await db.execute(stmt)
        notes = result.scalars().all()

        return {
            "query": q,
            "results": [
                {
                    "id": str(note.id),
                    "path": note.note_path,
                    "kind": note.kind,
                    "title": note.title,
                    "tags": note.tags or [],
                    "score": 1.0,  # Placeholder score
                    "match_type": "title",  # Would be 'hybrid' in Phase 6
                }
                for note in notes
            ],
            "total": len(notes),
            "mode": "basic",  # Would be 'hybrid' in Phase 6
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Search not yet available. This feature requires Phase 6 (Retrieval)."
        )


@router.get("/context/{note_id}")
async def get_context_pack(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get context pack for a note (Phase 6 feature).

    Returns related notes, backlinks, and workspace context
    needed for LLM-powered features.
    """
    raise HTTPException(
        status_code=501,
        detail="Context packs require Phase 6 (Retrieval) with pgvector setup"
    )


@router.post("/reindex")
async def trigger_reindex(
    workspace_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a full reindex job for the workspace.

    This creates a high-priority reindex job that will
    re-scan all notes and update embeddings.
    """
    from src.db.models.job import Job
    from src.db.models.workspace import Workspace

    # Get workspace
    if workspace_id:
        ws_stmt = select(Workspace).where(Workspace.id == workspace_id)
    else:
        ws_stmt = select(Workspace).limit(1)
    ws_result = await db.execute(ws_stmt)
    workspace = ws_result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

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
