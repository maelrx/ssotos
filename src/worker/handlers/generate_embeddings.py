"""Handler for generate_embeddings job type — D-94, D-95, D-96.

Generates embeddings for chunks using OpenAI text-embedding-3-small.
Input: {chunk_ids: list[UUID]}
"""
from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import select

from src.db.models import Chunk, Embedding
from src.services.embedding_service import generate_embeddings_batch, get_embeddings_provider

logger = structlog.get_logger(__name__)


async def handle_generate_embeddings(input_data: dict[str, Any]) -> dict[str, Any]:
    """Generate embeddings for a list of chunk IDs."""
    chunk_ids_raw = input_data.get("chunk_ids", [])
    workspace_id = input_data.get("workspace_id")

    # Normalize chunk_ids to strings
    chunk_ids: list[str] = [str(cid) for cid in chunk_ids_raw]

    logger.info(
        "generate_embeddings_start",
        chunk_count=len(chunk_ids),
        workspace_id=workspace_id,
    )

    from src.db.session import async_session_maker

    async with async_session_maker() as db:
        # Fetch chunks from DB
        stmt = select(Chunk).where(Chunk.id.in_(chunk_ids))
        result = await db.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            logger.warning("generate_embeddings_no_chunks_found", chunk_ids=chunk_ids)
            return {
                "chunk_ids": chunk_ids,
                "embeddings_generated": 0,
                "status": "no_chunks_found",
            }

        # Build (chunk_id, content) pairs
        chunk_pairs = [(chunk.id, chunk.content) for chunk in chunks]
        missing_ids = set(chunk_ids) - {str(c.id) for c in chunks}
        if missing_ids:
            logger.warning("generate_embeddings_missing_chunks", missing=list(missing_ids))

        # Generate embeddings
        provider = get_embeddings_provider()
        try:
            results = await generate_embeddings_batch(provider, chunk_pairs)
        except Exception as exc:
            logger.error("generate_embeddings_api_error", error=str(exc))
            return {
                "chunk_ids": chunk_ids,
                "embeddings_generated": 0,
                "status": "error",
                "error": str(exc),
            }

        # Insert embedding records
        for result in results:
            # Check if embedding already exists
            existing = await db.execute(
                select(Embedding).where(Embedding.chunk_id == result.chunk_id)
            )
            existing_emb = existing.scalar_one_or_none()

            if existing_emb:
                # Update existing
                existing_emb.embedding_vector = result.embedding_vector
                existing_emb.embedding_model = result.model
            else:
                # Insert new — look up note_projection_id from chunk
                chunk = next((c for c in chunks if c.id == result.chunk_id), None)
                if chunk:
                    emb = Embedding(
                        chunk_id=result.chunk_id,
                        note_projection_id=chunk.note_projection_id,
                        embedding_vector=result.embedding_vector,
                        embedding_model=result.model,
                    )
                    db.add(emb)

        await db.commit()

        logger.info(
            "generate_embeddings_complete",
            embeddings_generated=len(results),
            chunks_processed=len(chunks),
        )
        return {
            "chunk_ids": chunk_ids,
            "embeddings_generated": len(results),
            "chunks_processed": len(chunks),
            "status": "complete",
        }
