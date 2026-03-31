"""Vault REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from pathlib import Path
from datetime import datetime
from typing import Annotated

from src.db.session import get_db
from src.db.models.note_projection import NoteProjection
from src.db.models.workspace import Workspace
from src.schemas.vault import (
    NoteCreateRequest,
    NoteUpdateRequest,
    NoteResponse,
    NoteListResponse,
)
from src.schemas.common import PaginationParams

router = APIRouter(prefix="/vault", tags=["vault"])

# In-memory filesystem simulation for Phase 1 notes
# In production, this syncs with the actual user-vault filesystem
_notes_store: dict[str, dict] = {}


def _note_to_response(note_dict: dict) -> NoteResponse:
    """Convert a note dict to NoteResponse."""
    return NoteResponse(
        id=note_dict["id"],
        path=note_dict["path"],
        kind=note_dict.get("kind", "permanent"),
        title=note_dict.get("title", ""),
        tags=note_dict.get("tags", []),
        links=note_dict.get("links", []),
        frontmatter=note_dict.get("frontmatter", {}),
        content=note_dict.get("content", ""),
        created_at=note_dict.get("created_at", datetime.utcnow()),
        updated_at=note_dict.get("updated_at", datetime.utcnow()),
    )


@router.get("/notes", response_model=NoteListResponse)
async def list_notes(
    path: str | None = Query(None, description="Filter by note path prefix"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all notes with optional path filter and pagination.

    Returns notes from the database projection if available,
    falling back to in-memory store for Phase 1.
    """
    # Try database first
    try:
        stmt = select(NoteProjection)
        if path:
            stmt = stmt.where(NoteProjection.note_path.startswith(path))
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        result = await db.execute(stmt)
        db_notes = result.scalars().all()

        count_stmt = select(NoteProjection)
        if path:
            count_stmt = count_stmt.where(NoteProjection.note_path.startswith(path))
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        notes = [
            NoteResponse(
                id=note.id,
                path=note.note_path,
                kind=note.kind,
                title=note.title,
                tags=note.tags or [],
                links=note.links or [],
                frontmatter=note.frontmatter or {},
                content="",  # Content not stored in projection
                created_at=note.created_at,
                updated_at=note.updated_at,
            )
            for note in db_notes
        ]
        return NoteListResponse(notes=notes, total=total)
    except Exception:
        # Fall back to in-memory store
        filtered = list(_notes_store.values())
        if path:
            filtered = [n for n in filtered if n["path"].startswith(path)]
        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        notes = [_note_to_response(n) for n in filtered[start:end]]
        return NoteListResponse(notes=notes, total=total)


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a note by its UUID."""
    try:
        stmt = select(NoteProjection).where(NoteProjection.id == note_id)
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return NoteResponse(
            id=note.id,
            path=note.note_path,
            kind=note.kind,
            title=note.title,
            tags=note.tags or [],
            links=note.links or [],
            frontmatter=note.frontmatter or {},
            content="",
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
    except HTTPException:
        raise
    except Exception:
        # Fall back to in-memory store
        for note in _notes_store.values():
            if str(note["id"]) == str(note_id):
                return _note_to_response(note)
        raise HTTPException(status_code=404, detail="Note not found")


@router.get("/notes/path/{path:path}", response_model=NoteResponse)
async def get_note_by_path(
    path: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a note by its filesystem path."""
    try:
        stmt = select(NoteProjection).where(NoteProjection.note_path == path)
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return NoteResponse(
            id=note.id,
            path=note.note_path,
            kind=note.kind,
            title=note.title,
            tags=note.tags or [],
            links=note.links or [],
            frontmatter=note.frontmatter or {},
            content="",
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
    except HTTPException:
        raise
    except Exception:
        # Fall back to in-memory store
        for note in _notes_store.values():
            if note["path"] == path:
                return _note_to_response(note)
        raise HTTPException(status_code=404, detail="Note not found")


@router.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(
    request: NoteCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new note.

    For Phase 1, stores in-memory and creates a database projection.
    In production, writes to the actual user-vault filesystem.
    """
    note_id = UUID(str(uuid.uuid4()))
    now = datetime.utcnow()

    note_dict = {
        "id": note_id,
        "path": request.path,
        "kind": request.frontmatter.kind,
        "title": request.frontmatter.title,
        "tags": request.frontmatter.tags,
        "links": request.frontmatter.links,
        "frontmatter": request.frontmatter.model_dump(),
        "content": request.content,
        "created_at": now,
        "updated_at": now,
    }

    # Store in memory
    _notes_store[str(note_id)] = note_dict

    # Try to create database projection
    try:
        # Get or create default workspace
        ws_stmt = select(Workspace).limit(1)
        ws_result = await db.execute(ws_stmt)
        workspace = ws_result.scalar_one_or_none()

        if workspace:
            projection = NoteProjection(
                id=note_id,
                workspace_id=workspace.id,
                note_path=request.path,
                note_hash="placeholder",
                kind=request.frontmatter.kind,
                title=request.frontmatter.title,
                tags=request.frontmatter.tags,
                links=request.frontmatter.links,
                frontmatter=request.frontmatter.model_dump(),
                content_hash="placeholder",
            )
            db.add(projection)
    except Exception:
        pass  # Phase 1: continue with in-memory only

    return _note_to_response(note_dict)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    request: NoteUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing note."""
    # Try database first
    try:
        stmt = select(NoteProjection).where(NoteProjection.id == note_id)
        result = await db.execute(stmt)
        db_note = result.scalar_one_or_none()
        if db_note:
            if request.content is not None:
                db_note.content_hash = "placeholder"
            if request.frontmatter:
                db_note.tags = request.frontmatter.get("tags", db_note.tags)
                db_note.links = request.frontmatter.get("links", db_note.links)
                db_note.frontmatter = request.frontmatter
            db_note.updated_at = datetime.utcnow()
            return NoteResponse(
                id=db_note.id,
                path=db_note.note_path,
                kind=db_note.kind,
                title=db_note.title,
                tags=db_note.tags or [],
                links=db_note.links or [],
                frontmatter=db_note.frontmatter or {},
                content="",
                created_at=db_note.created_at,
                updated_at=db_note.updated_at,
            )
    except Exception:
        pass

    # Fall back to in-memory store
    note_key = str(note_id)
    if note_key not in _notes_store:
        raise HTTPException(status_code=404, detail="Note not found")

    note = _notes_store[note_key]
    if request.content is not None:
        note["content"] = request.content
    if request.frontmatter:
        note["frontmatter"].update(request.frontmatter)
        note["tags"] = request.frontmatter.get("tags", note["tags"])
        note["links"] = request.frontmatter.get("links", note["links"])
    note["updated_at"] = datetime.utcnow()

    return _note_to_response(note)


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a note by ID."""
    # Try database first
    try:
        stmt = select(NoteProjection).where(NoteProjection.id == note_id)
        result = await db.execute(stmt)
        db_note = result.scalar_one_or_none()
        if db_note:
            await db.delete(db_note)
            return {"success": True, "message": "Note deleted"}
    except Exception:
        pass

    # Fall back to in-memory store
    note_key = str(note_id)
    if note_key in _notes_store:
        del _notes_store[note_key]
        return {"success": True, "message": "Note deleted"}

    raise HTTPException(status_code=404, detail="Note not found")


@router.get("/tree")
async def get_vault_tree(
    db: AsyncSession = Depends(get_db),
):
    """Get vault directory tree structure.

    Returns a nested dict representing the directory structure.
    """
    try:
        stmt = select(NoteProjection.note_path)
        result = await db.execute(stmt)
        paths = [row[0] for row in result.fetchall()]
    except Exception:
        paths = [n["path"] for n in _notes_store.values()]

    # Build tree structure
    tree: dict = {"name": "/", "children": {}}

    for path in paths:
        parts = path.strip("/").split("/")
        node = tree
        for part in parts:
            if part not in node["children"]:
                node["children"][part] = {"name": part, "children": {}}
            node = node["children"][part]

    return tree


@router.get("/search")
async def search_notes(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """Full-text search across notes.

    Searches note titles and paths.
    For Phase 6, this will use hybrid FTS + pgvector search.
    """
    try:
        stmt = select(NoteProjection).where(
            NoteProjection.title.ilike(f"%{q}%") |
            NoteProjection.note_path.ilike(f"%{q}%")
        ).limit(50)
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
                }
                for note in notes
            ],
            "total": len(notes),
        }
    except Exception:
        # Fall back to in-memory search
        q_lower = q.lower()
        results = [
            {
                "id": str(n["id"]),
                "path": n["path"],
                "kind": n.get("kind", "permanent"),
                "title": n.get("title", ""),
                "tags": n.get("tags", []),
            }
            for n in _notes_store.values()
            if q_lower in n.get("title", "").lower() or q_lower in n["path"].lower()
        ]
        return {"query": q, "results": results, "total": len(results)}


# Need uuid for create_note
import uuid
