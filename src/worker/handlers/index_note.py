"""Handler for index_note job type — D-101, D-102, D-103, D-109.

Indexes a single note: reads markdown, chunks it, stores chunks with FTS vectors,
and enqueues embedding generation.
Input: {note_id: UUID, workspace_id: UUID, operation: "upsert"|"delete"}
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Chunk, Embedding, NoteProjection
from src.services.chunking_service import markdown_to_chunks, parse_frontmatter
from src.services.job_service import JobService

logger = structlog.get_logger(__name__)


async def handle_index_note(input_data: dict[str, Any]) -> dict[str, Any]:
    """Index a single note: chunk it, store FTS vectors, enqueue embeddings."""
    note_id = input_data.get("note_id")
    workspace_id = input_data.get("workspace_id")
    operation = input_data.get("operation", "upsert")

    logger.info("index_note_start", note_id=note_id, workspace_id=workspace_id, operation=operation)

    from src.db.session import async_session_maker

    async with async_session_maker() as db:
        note_proj: NoteProjection | None = await db.get(NoteProjection, note_id)

        # ── Delete operation ────────────────────────────────────
        if operation == "delete":
            if note_proj is None:
                logger.warning("index_note_delete_not_found", note_id=note_id)
                return {"note_id": str(note_id), "deleted": False, "reason": "note_not_found"}

            # Get chunk IDs for this note
            chunk_ids_stmt = select(Chunk.id).where(Chunk.note_projection_id == note_id)
            chunk_ids = (await db.execute(chunk_ids_stmt)).scalars().all()

            # Delete embeddings first (FK dependency)
            if chunk_ids:
                await db.execute(delete(Embedding).where(Embedding.chunk_id.in_(chunk_ids)))

            # Delete chunks
            await db.execute(delete(Chunk).where(Chunk.note_projection_id == note_id))

            # Mark note as not indexed
            await db.execute(
                update(NoteProjection)
                .where(NoteProjection.id == note_id)
                .values(indexed_at=None)
            )
            await db.commit()

            logger.info("index_note_delete_complete", note_id=note_id, chunks_deleted=len(chunk_ids))
            return {"note_id": str(note_id), "deleted": True, "chunks_deleted": len(chunk_ids)}

        # ── Upsert operation ─────────────────────────────────────
        if note_proj is None:
            logger.error("index_note_note_not_found", note_id=note_id)
            return {"note_id": str(note_id), "error": "NoteProjection not found"}

        # Read markdown from filesystem
        workspace_root = await _get_workspace_root(db, workspace_id)
        note_path = os.path.join(workspace_root, note_proj.note_path)

        try:
            markdown = Path(note_path).read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.error("index_note_file_not_found", path=note_path, note_id=note_id)
            return {"note_id": str(note_id), "error": f"File not found: {note_path}"}
        except Exception as exc:
            logger.error("index_note_read_error", path=note_path, error=str(exc))
            return {"note_id": str(note_id), "error": f"Failed to read file: {exc}"}

        # Parse frontmatter
        frontmatter, body = parse_frontmatter(markdown)

        # Delete old chunks + embeddings for this note
        old_chunk_ids_stmt = select(Chunk.id).where(Chunk.note_projection_id == note_id)
        old_chunk_ids = (await db.execute(old_chunk_ids_stmt)).scalars().all()
        if old_chunk_ids:
            await db.execute(delete(Embedding).where(Embedding.chunk_id.in_(old_chunk_ids)))
            await db.execute(delete(Chunk).where(Chunk.note_projection_id == note_id))

        # Chunk the content
        chunks = markdown_to_chunks(body, note_id)

        # Insert new chunks with FTS tsvector
        for chunk_result in chunks:
            chunk = Chunk(
                note_projection_id=note_id,
                heading_path=chunk_result.heading_path,
                content=chunk_result.content,
                chunk_index=chunk_result.chunk_index,
                char_start=chunk_result.char_start,
                char_end=chunk_result.char_end,
            )
            db.add(chunk)
            await db.flush()

            # Set content_tsv via raw SQL
            await db.execute(
                text("UPDATE chunks SET content_tsv = to_tsvector('english', content) WHERE id = :cid"),
                {"cid": str(chunk.id)},
            )

        # Update NoteProjection.indexed_at
        await db.execute(
            update(NoteProjection)
            .where(NoteProjection.id == note_id)
            .values(indexed_at=datetime.utcnow())
        )
        await db.commit()

        # Enqueue generate_embeddings job for new chunks
        new_chunk_ids = [str(c.id) for c in chunks]
        job_service = JobService(db)
        await job_service.enqueue(
            "generate_embeddings",
            {"chunk_ids": new_chunk_ids},
            priority=5,
            workspace_id=workspace_id,
        )

        logger.info(
            "index_note_complete",
            note_id=note_id,
            chunks_created=len(chunks),
            enqueued_embeddings=len(new_chunk_ids),
        )
        return {
            "note_id": str(note_id),
            "chunks_created": len(chunks),
            "enqueued_embeddings": len(new_chunk_ids),
        }


async def _get_workspace_root(db: AsyncSession, workspace_id: str) -> str:
    """Get the root_path for a workspace."""
    from src.db.models import Workspace

    ws = await db.get(Workspace, workspace_id)
    if ws is None:
        raise ValueError(f"Workspace {workspace_id} not found")
    return ws.root_path
