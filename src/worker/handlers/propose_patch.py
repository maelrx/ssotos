"""Handler for propose_patch job type — Phase 7 Wave 3.

Wraps CopilotService.propose_patch logic as an async job.
Input: {note_id: str, instruction: str, workspace_id?: str}
Output: {proposal_id: str, diff: str, note_id: str}
"""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import structlog

from src.services.retrieval_service import RetrievalService
from src.services.proposal_service import ProposalService
from src.services.patch_service import PatchService
from src.services.git_service import GitService
from src.models.proposal import ProposalType, SourceDomain

logger = structlog.get_logger(__name__)


async def handle_propose_patch(input_data: dict[str, Any]) -> dict[str, Any]:
    """Generate a patch proposal for a note and create an Exchange Zone proposal.

    Args:
        input_data: {
            note_id: str,
            instruction: str,
            workspace_id?: str  # optional, resolved from note if not provided
        }

    Returns:
        {proposal_id: str, diff: str, note_id: str}

    Raises:
        ValueError: If note_id is not found.
    """
    note_id_raw = input_data.get("note_id")
    instruction = input_data.get("instruction", "")
    workspace_id_raw = input_data.get("workspace_id")

    if not note_id_raw:
        raise ValueError("note_id is required")
    if not instruction:
        raise ValueError("instruction is required")

    note_id = UUID(str(note_id_raw))
    workspace_id = UUID(str(workspace_id_raw)) if workspace_id_raw else None

    logger.info("propose_patch_start", note_id=str(note_id), instruction=instruction)

    from src.db.session import async_session_maker

    async with async_session_maker() as db:
        # Resolve workspace_id from note if not provided
        if workspace_id is None:
            from sqlalchemy import select
            from src.db.models.note_projection import NoteProjection

            result = await db.execute(
                select(NoteProjection.workspace_id).where(NoteProjection.id == note_id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                raise ValueError(f"NoteProjection not found for note_id={note_id}")
            workspace_id = row

        # Build context via RetrievalService
        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            note_path = context.provenance.note_path if context else f"notes/{note_id}.md"
            snippet = context.snippet if context else ""
        except ValueError:
            note_path = f"notes/{note_id}.md"
            snippet = f"No content found for note {note_id}"

        # Generate unified diff (placeholder for PydanticAI generation)
        diff = f"""--- a/{note_path}
+++ b/{note_path}
@@ -1 +1 @@
-{snippet[:200]}
+[AI-generated patch based on: {instruction}]
"""

        # Create proposal in Exchange Zone
        proposal_id = str(uuid4())

        try:
            git_svc = GitService()
            patch_svc = PatchService(git_svc)
            proposal_svc = ProposalService(git_svc, patch_svc)

            proposal = proposal_svc.create_proposal(
                proposal_id=proposal_id,
                proposal_type=ProposalType.NOTE_EDIT,
                source_domain=SourceDomain.AGENT_BRAIN,
                target_domain=SourceDomain.USER_VAULT,
                actor="copilot",
                target_path=note_path,
                initial_content=diff,
            )
        except Exception as exc:
            logger.error("propose_patch_proposal_create_failed", note_id=str(note_id), error=str(exc))
            raise

        logger.info("propose_patch_complete", note_id=str(note_id), proposal_id=proposal_id)

        return {
            "proposal_id": proposal_id,
            "diff": diff,
            "note_id": str(note_id),
        }
