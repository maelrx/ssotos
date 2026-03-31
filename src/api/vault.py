"""Vault REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

router = APIRouter(prefix="/vault", tags=["vault"])


@router.get("/notes")
async def list_notes():
    """List all notes (placeholder for Phase 1)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.get("/notes/{note_id}")
async def get_note(note_id: UUID):
    """Get note by ID (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.get("/notes/path/{path:path}")
async def get_note_by_path(path: str):
    """Get note by filesystem path (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.post("/notes")
async def create_note():
    """Create note (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.put("/notes/{note_id}")
async def update_note(note_id: UUID):
    """Update note (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.delete("/notes/{note_id}")
async def delete_note(note_id: UUID):
    """Delete note (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.get("/tree")
async def get_vault_tree():
    """Get vault directory tree structure (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.get("/search")
async def search_notes(q: str):
    """Full-text search across notes (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")
