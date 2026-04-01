"""Copilot schemas — F11-01 through F11-11."""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

# Base
class CopilotAction(BaseModel):
    note_id: UUID
    instruction: str | None = None

# Explain / Summarize
class NoteExplanationResponse(BaseModel):
    note_id: UUID
    markdown: str = Field(description="Markdown explanation")
    referenced_headings: list[str] = Field(default_factory=list)

class NoteSummaryResponse(BaseModel):
    note_id: UUID
    markdown: str = Field(description="100-300 word summary")
    key_points: list[str] = Field(default_factory=list)

# Suggest Links
class LinkSuggestion(BaseModel):
    target_note_path: str
    target_title: str
    reason: str

class SuggestLinksResponse(BaseModel):
    note_id: UUID
    suggestions: list[LinkSuggestion]

# Suggest Tags
class TagSuggestion(BaseModel):
    tag: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str

class SuggestTagsResponse(BaseModel):
    note_id: UUID
    suggestions: list[TagSuggestion]

# Suggest Structure
class StructureIssue(BaseModel):
    type: Literal["missing_heading", "deeply_nested", "long_paragraph", "logical_gap"]
    location: str = Field(description="Heading path or line range")
    issue: str
    suggestion: str

class SuggestStructureResponse(BaseModel):
    note_id: UUID
    suggestions: list[StructureIssue]

# Propose Patch
class ProposePatchRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=1000)

class ProposePatchResponse(BaseModel):
    note_id: UUID
    proposal_id: UUID
    diff: str = Field(description="Unified diff")


class ProposePatchEnqueueResponse(BaseModel):
    """Response when a propose_patch job is enqueued."""
    job_id: UUID
    status: str = "pending"

# Chat
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    note_id: UUID
    message: str
    history: list[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    note_id: UUID
    message: ChatMessage
