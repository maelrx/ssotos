"""Retrieval REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.get("/search")
async def hybrid_search(q: str):
    """Hybrid search (placeholder for Phase 6)."""
    raise HTTPException(status_code=501, detail="Phase 6 feature - not yet implemented")


@router.get("/context/{note_id}")
async def get_context_pack(note_id: str):
    """Get context pack for a note (Phase 6)."""
    raise HTTPException(status_code=501, detail="Phase 6 feature - not yet implemented")


@router.post("/reindex")
async def trigger_reindex():
    """Trigger reindex job (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 6 feature - not yet implemented")
