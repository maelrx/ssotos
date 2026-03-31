"""Agent brain schemas — F9-02, F9-03, F9-04, F9-05, F9-06."""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# Soul schemas (F9-02)
# ==============================================================================


class SoulSection(BaseModel):
    """Parsed sections from SOUL.md per D-73."""
    model_config = ConfigDict(extra="forbid")

    identity_statement: str | None = None
    operating_principles: list[str] = Field(default_factory=list)
    communication_style: str | None = None
    constraints: list[str] = Field(default_factory=list)
    self_improvement_guidelines: list[str] = Field(default_factory=list)
    raw_content: str = ""


class SoulUpdate(BaseModel):
    """Request to update SOUL.md per D-74."""
    model_config = ConfigDict(extra="forbid")

    identity_statement: str | None = None
    operating_principles: list[str] | None = None
    communication_style: str | None = None
    constraints: list[str] | None = None
    self_improvement_guidelines: list[str] | None = None


class SoulResponse(BaseModel):
    """Response containing SOUL.md content."""
    success: bool = True
    content: SoulSection
    updated_at: datetime | None = None


# ==============================================================================
# Memory schemas (F9-03)
# ==============================================================================


class MemorySection(BaseModel):
    """Parsed sections from MEMORY.md per D-75."""
    model_config = ConfigDict(extra="forbid")

    high_value_learnings: list[str] = Field(default_factory=list)
    patterns_established: list[str] = Field(default_factory=list)
    operational_heuristics: list[str] = Field(default_factory=list)
    raw_content: str = ""
    updated_at: datetime | None = None


class MemoryUpdate(BaseModel):
    """Request to update MEMORY.md per D-77."""
    model_config = ConfigDict(extra="forbid")

    high_value_learnings: list[str] | None = None
    patterns_established: list[str] | None = None
    operational_heuristics: list[str] | None = None


class MemoryResponse(BaseModel):
    """Response containing MEMORY.md content."""
    success: bool = True
    content: MemorySection
    updated_at: datetime | None = None


# ==============================================================================
# User Profile schemas (F9-04)
# ==============================================================================


class UserProfileSection(BaseModel):
    """Parsed sections from USER.md per D-78."""
    model_config = ConfigDict(extra="forbid")

    user_preferences: list[str] = Field(default_factory=list)
    work_patterns: list[str] = Field(default_factory=list)
    context_notes: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)
    communication_style: str | None = None
    raw_content: str = ""
    updated_at: datetime | None = None


class UserProfileUpdate(BaseModel):
    """Request to update USER.md per D-79."""
    model_config = ConfigDict(extra="forbid")

    user_preferences: list[str] | None = None
    work_patterns: list[str] | None = None
    context_notes: list[str] | None = None
    restrictions: list[str] | None = None
    communication_style: str | None = None


class UserProfileResponse(BaseModel):
    """Response containing USER.md content."""
    success: bool = True
    content: UserProfileSection
    updated_at: datetime | None = None


# ==============================================================================
# Skill schemas (F9-05)
# ==============================================================================


class SkillTrigger(BaseModel):
    """Skill trigger pattern per D-67."""
    model_config = ConfigDict(extra="forbid")

    pattern: str  # regex pattern
    description: str | None = None


class SkillInputsSchema(BaseModel):
    """JSON Schema for skill inputs per D-67."""
    model_config = ConfigDict(extra="forbid")

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class SkillOutputsSchema(BaseModel):
    """JSON Schema for skill outputs per D-67."""
    model_config = ConfigDict(extra="forbid")

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)


class SkillManifest(BaseModel):
    """Skill manifest per D-67: skills/<skill-name>/manifest.yaml."""
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    trigger_patterns: list[SkillTrigger] = Field(default_factory=list)
    inputs_schema: SkillInputsSchema | None = None
    outputs_schema: SkillOutputsSchema | None = None
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None


class SkillResponse(BaseModel):
    """Response containing a single skill."""
    success: bool = True
    manifest: SkillManifest
    procedure_body: str = ""


class SkillListResponse(BaseModel):
    """Response listing all available skills."""
    success: bool = True
    skills: list[SkillManifest] = Field(default_factory=list)
    total: int = 0


class SkillInvokeRequest(BaseModel):
    """Request to invoke a skill per D-87."""
    model_config = ConfigDict(extra="forbid")

    skill_name: str
    input_data: dict[str, Any] = Field(default_factory=dict)


class SkillInvokeResponse(BaseModel):
    """Response from skill invocation per D-68."""
    success: bool = True
    skill_name: str
    output_data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: int | None = None
    error: str | None = None


# ==============================================================================
# Session schemas (F9-06)
# ==============================================================================


class SessionSummary(BaseModel):
    """Session summary format per D-72."""
    model_config = ConfigDict(extra="forbid")

    session_id: UUID = Field(default_factory=uuid4)
    date: str = ""  # YYYY-MM-DD of the session
    duration_minutes: int = 0  # Session duration
    what_happened: str = ""
    key_decisions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionResponse(BaseModel):
    """Response containing a single session summary."""
    success: bool = True
    session_id: UUID
    content: str = ""  # Raw markdown content
    summary: SessionSummary | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SessionListResponse(BaseModel):
    """Response listing all session summaries."""
    success: bool = True
    sessions: list[SessionResponse] = Field(default_factory=list)
    total: int = 0
