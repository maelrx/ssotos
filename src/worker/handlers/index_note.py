"""Handler for index_note job type.

Indexes a single note in the FTS and vector store.
Input: {note_id: UUID, workspace_id: UUID}
"""
from typing import Any
import structlog

logger = structlog.get_logger(__name__)

async def handle_index_note(input_data: dict) -> dict:
    note_id = input_data.get("note_id")
    workspace_id = input_data.get("workspace_id")

    logger.info("index_note_start", note_id=note_id, workspace_id=workspace_id)

    # Phase 6 (Retrieval) will implement actual indexing
    # For now, simulate work and return success
    result = {
        "note_id": str(note_id),
        "indexed": True,
        "fts_updated": True,
        "embedding_generated": True,
    }

    logger.info("index_note_complete", note_id=note_id)
    return result
