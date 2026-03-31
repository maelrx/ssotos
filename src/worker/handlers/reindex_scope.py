"""Handler for reindex_scope job type — D-110.

Reindexes all notes in a workspace by enqueueing index_note jobs.
Input: {workspace_id: UUID, scope: "full"|"folder"|"tag", scope_path?: str}
"""
from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import select

from src.db.models import NoteProjection
from src.services.job_service import JobService

logger = structlog.get_logger(__name__)


async def handle_reindex_scope(input_data: dict[str, Any]) -> dict[str, Any]:
    """Enqueue index_note jobs for all notes in a workspace scope."""
    workspace_id = input_data.get("workspace_id")
    scope = input_data.get("scope", "full")
    scope_path = input_data.get("scope_path")

    logger.info(
        "reindex_scope_start",
        workspace_id=workspace_id,
        scope=scope,
        scope_path=scope_path,
    )

    from src.db.session import async_session_maker

    async with async_session_maker() as db:
        # Query notes for the workspace
        stmt = select(NoteProjection).where(NoteProjection.workspace_id == workspace_id)

        if scope == "folder" and scope_path:
            stmt = stmt.where(NoteProjection.note_path.startswith(scope_path))
        elif scope == "tag" and scope_path:
            # Filter by tag (stored as JSON list)
            stmt = stmt.where(NoteProjection.tags.contains([scope_path]))

        result = await db.execute(stmt)
        notes = result.scalars().all()

        # Enqueue index_note job for each note
        job_service = JobService(db)
        enqueued: list[str] = []

        for note in notes:
            job = await job_service.enqueue(
                "index_note",
                {
                    "note_id": str(note.id),
                    "workspace_id": str(workspace_id),
                    "operation": "upsert",
                },
                priority=0,  # Low priority for reindex (per D-110)
                workspace_id=workspace_id,
            )
            enqueued.append(str(job.id))

        logger.info(
            "reindex_scope_complete",
            workspace_id=workspace_id,
            notes_to_reindex=len(notes),
            jobs_enqueued=len(enqueued),
        )
        return {
            "workspace_id": str(workspace_id),
            "scope": scope,
            "scope_path": scope_path,
            "notes_to_reindex": len(notes),
            "jobs_enqueued": len(enqueued),
            "job_ids": enqueued,
        }
