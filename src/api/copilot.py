"""Copilot REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/explain/{note_id}")
async def explain_note(note_id: str):
    """Explain note (Phase 7)."""
    return {"message": "Phase 7 feature - not yet implemented"}


@router.post("/summarize/{note_id}")
async def summarize_note(note_id: str):
    """Summarize note (Phase 7)."""
    return {"message": "Phase 7 feature - not yet implemented"}


@router.post("/suggest-links/{note_id}")
async def suggest_links(note_id: str):
    """Suggest links (Phase 7)."""
    return {"message": "Phase 7 feature - not yet implemented"}


@router.post("/propose-patch/{note_id}")
async def propose_patch(note_id: str):
    """Propose patch (Phase 7)."""
    return {"message": "Phase 7 feature - not yet implemented"}
