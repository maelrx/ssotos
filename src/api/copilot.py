"""Copilot REST API — per F11-01 through F11-11."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from src.db.database import get_db
from src.schemas.copilot import (
    NoteExplanationResponse,
    NoteSummaryResponse,
    SuggestLinksResponse,
    SuggestTagsResponse,
    SuggestStructureResponse,
    ProposePatchRequest,
    ProposePatchResponse,
    ChatRequest,
    ChatResponse,
)
from src.services.copilot_service import CopilotService

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/explain/{note_id}", response_model=NoteExplanationResponse)
async def explain_note(
    note_id: UUID,
    db=Depends(get_db),
) -> NoteExplanationResponse:
    """Generate explanation of a note (F11-02)."""
    svc = CopilotService()
    return await svc.explain(note_id, db)


@router.post("/summarize/{note_id}", response_model=NoteSummaryResponse)
async def summarize_note(
    note_id: UUID,
    db=Depends(get_db),
) -> NoteSummaryResponse:
    """Generate summary of a note (F11-03)."""
    svc = CopilotService()
    return await svc.summarize(note_id, db)


@router.post("/suggest-links/{note_id}", response_model=SuggestLinksResponse)
async def suggest_links(
    note_id: UUID,
    db=Depends(get_db),
) -> SuggestLinksResponse:
    """Suggest internal links for a note (F11-04)."""
    svc = CopilotService()
    return await svc.suggest_links(note_id, db)


@router.post("/suggest-tags/{note_id}", response_model=SuggestTagsResponse)
async def suggest_tags(
    note_id: UUID,
    db=Depends(get_db),
) -> SuggestTagsResponse:
    """Suggest tags for a note (F11-05)."""
    svc = CopilotService()
    return await svc.suggest_tags(note_id, db)


@router.post("/suggest-structure/{note_id}", response_model=SuggestStructureResponse)
async def suggest_structure(
    note_id: UUID,
    db=Depends(get_db),
) -> SuggestStructureResponse:
    """Suggest structure improvements for a note (F11-06)."""
    svc = CopilotService()
    return await svc.suggest_structure(note_id, db)


@router.post("/propose-patch/{note_id}", response_model=ProposePatchResponse)
async def propose_patch(
    note_id: UUID,
    body: ProposePatchRequest,
    db=Depends(get_db),
) -> ProposePatchResponse:
    """Generate patch proposal for a note (F11-07)."""
    svc = CopilotService()
    try:
        return await svc.propose_patch(note_id, body.instruction, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create proposal: {e}")


@router.post("/chat/{note_id}", response_model=ChatResponse)
async def chat(
    note_id: UUID,
    body: ChatRequest,
    db=Depends(get_db),
) -> ChatResponse:
    """Stateless chat about a note (F11-09)."""
    svc = CopilotService()
    return await svc.chat(note_id, body.message, body.history, db)
