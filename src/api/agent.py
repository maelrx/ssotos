"""Agent Brain REST API — per D-84, D-85, D-86, D-87.

Exposes agent brain, skills, and sessions via REST endpoints.
Brain mutations go through policy check and job enqueue per D-71, D-74, D-82.
"""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.db.models.job import Job
from src.db.models.workspace import Workspace
from src.services.job_service import JobService
from src.schemas.agent import (
    SoulUpdate,
    SoulResponse,
    MemoryUpdate,
    MemoryResponse,
    UserProfileUpdate,
    UserProfileResponse,
    SkillListResponse,
    SkillResponse,
    SkillInvokeRequest,
    SkillInvokeResponse,
    SessionListResponse,
    SessionResponse,
    SessionSummary,
)
from src.services.agent_brain_service import AgentBrainService
from src.services.skill_service import SkillService
from src.core.policy.service import PolicyService
from src.core.policy.models import PolicyRequest
from src.core.policy.enums import CapabilityGroup, CapabilityAction, Domain


router = APIRouter(prefix="/agent", tags=["agent"])


# ==============================================================================
# Service dependency injection
# ==============================================================================


def get_agent_brain_service() -> AgentBrainService:
    """Get AgentBrainService instance."""
    return AgentBrainService()


def get_skill_service() -> SkillService:
    """Get SkillService instance."""
    return SkillService()


def get_policy_service() -> PolicyService:
    """Get PolicyService instance."""
    return PolicyService()


async def _get_default_workspace_id(db: AsyncSession) -> UUID:
    """Get the default workspace ID for job creation."""
    from sqlalchemy import select
    stmt = select(Workspace).limit(1)
    result = await db.execute(stmt)
    workspace = result.scalar_one_or_none()
    if workspace:
        return workspace.id
    return UUID("00000000-0000-0000-0000-000000000000")


def _check_brain_write_policy(policy_service: PolicyService, path: str) -> None:
    """Run policy check for brain write operations per D-74.

    Raises HTTPException 403 if denied.
    """
    policy_request = PolicyRequest(
        actor="agent",
        capability_group=CapabilityGroup.AGENT,
        action=CapabilityAction.WRITE,
        domain=Domain.AGENT_BRAIN,
        path=path,
    )
    policy_result = policy_service.check(policy_request)
    if policy_result.outcome.value != "allow":
        raise HTTPException(status_code=403, detail=f"Policy denied: {policy_result.reason}")


async def _enqueue_reflect_agent_job(
    db: AsyncSession,
    workspace_id: UUID,
    job_data: dict[str, Any],
) -> Job:
    """Create a reflect_agent job in the queue per D-71, D-82."""
    job_service = JobService(db)
    return await job_service.enqueue("reflect_agent", job_data, priority=1, workspace_id=workspace_id)


# ==============================================================================
# Brain endpoints (D-84)
# ==============================================================================


@router.get("/brain/soul", response_model=SoulResponse)
async def get_soul(
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> SoulResponse:
    """Read SOUL.md content per D-73."""
    return await brain_svc.read_soul()


@router.put("/brain/soul", response_model=SoulResponse)
async def update_soul(
    update: SoulUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
    policy_service: PolicyService = Depends(get_policy_service),
) -> SoulResponse:
    """Update SOUL.md per D-74.

    Policy check and job enqueue per D-71, D-74, D-82.
    """
    _check_brain_write_policy(policy_service, "agent-brain/SOUL.md")

    workspace_id = await _get_default_workspace_id(db)
    job_data = {
        "operation": "update_soul",
        "update": update.model_dump(exclude_none=True),
    }
    await _enqueue_reflect_agent_job(db, workspace_id, job_data)
    await db.commit()

    return await brain_svc.update_soul(update)


@router.get("/brain/memory", response_model=MemoryResponse)
async def get_memory(
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> MemoryResponse:
    """Read MEMORY.md content per D-75."""
    return await brain_svc.read_memory()


@router.put("/brain/memory", response_model=MemoryResponse)
async def update_memory(
    update: MemoryUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
    policy_service: PolicyService = Depends(get_policy_service),
) -> MemoryResponse:
    """Update MEMORY.md per D-76.

    Policy check and job enqueue per D-71, D-74, D-82.
    """
    _check_brain_write_policy(policy_service, "agent-brain/MEMORY.md")

    workspace_id = await _get_default_workspace_id(db)
    job_data = {
        "operation": "update_memory",
        "update": update.model_dump(exclude_none=True),
    }
    await _enqueue_reflect_agent_job(db, workspace_id, job_data)
    await db.commit()

    return await brain_svc.update_memory(update)


@router.get("/brain/user", response_model=UserProfileResponse)
async def get_user_profile(
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> UserProfileResponse:
    """Read USER.md content per D-78."""
    return await brain_svc.read_user_profile()


@router.put("/brain/user", response_model=UserProfileResponse)
async def update_user_profile(
    update: UserProfileUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
    policy_service: PolicyService = Depends(get_policy_service),
) -> UserProfileResponse:
    """Update USER.md per D-79.

    Policy check and job enqueue per D-71, D-74, D-82.
    """
    _check_brain_write_policy(policy_service, "agent-brain/USER.md")

    workspace_id = await _get_default_workspace_id(db)
    job_data = {
        "operation": "update_user_profile",
        "update": update.model_dump(exclude_none=True),
    }
    await _enqueue_reflect_agent_job(db, workspace_id, job_data)
    await db.commit()

    return await brain_svc.update_user_profile(update)


class BrainStructureResponse(BaseModel):
    """Response for brain structure validation."""
    valid: bool
    files: dict[str, bool]
    missing: list[str]


@router.get("/brain/structure", response_model=BrainStructureResponse)
async def validate_brain_structure(
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> BrainStructureResponse:
    """Validate brain filesystem structure per D-65."""
    result = await brain_svc.validate_brain_structure()
    return BrainStructureResponse(**result)


# ==============================================================================
# Skills endpoints (D-85, D-87)
# ==============================================================================


@router.get("/skills", response_model=SkillListResponse)
async def list_skills(
    skill_svc: SkillService = Depends(get_skill_service),
) -> SkillListResponse:
    """List all available skills per D-67."""
    return await skill_svc.list_skills()


@router.get("/skills/{skill_name}", response_model=SkillResponse)
async def get_skill(
    skill_name: str,
    skill_svc: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    """Get a specific skill by name per D-67."""
    result = await skill_svc.get_skill(skill_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    return result


@router.post("/skills/{skill_name}/invoke", response_model=SkillInvokeResponse)
async def invoke_skill(
    skill_name: str,
    request: SkillInvokeRequest,
    skill_svc: SkillService = Depends(get_skill_service),
) -> SkillInvokeResponse:
    """Invoke a skill per D-87.

    Executes the skill procedure with given input data.
    """
    return await skill_svc.invoke_skill(skill_name, request.input_data)


class CreateSkillRequest(BaseModel):
    """Request to create a new skill per D-67."""
    name: str
    description: str
    procedure: str
    triggers: list[str] | None = None
    inputs_schema: dict[str, Any] | None = None
    outputs_schema: dict[str, Any] | None = None


@router.post("/skills", response_model=SkillResponse, status_code=201)
async def create_skill(
    request: CreateSkillRequest,
    skill_svc: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    """Create a new skill per D-67."""
    from src.schemas.agent import SkillTrigger

    triggers = None
    if request.triggers:
        triggers = [SkillTrigger(pattern=p) for p in request.triggers]

    return await skill_svc.create_skill(
        skill_name=request.name,
        description=request.description,
        procedure=request.procedure,
        triggers=triggers,
        inputs_schema=request.inputs_schema,
        outputs_schema=request.outputs_schema,
    )


# ==============================================================================
# Sessions endpoints (D-86)
# ==============================================================================


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> SessionListResponse:
    """List all session summaries per D-70."""
    return await brain_svc.list_sessions()


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> SessionResponse:
    """Get a specific session summary per D-70."""
    return await brain_svc.get_session(str(session_id))


@router.post("/sessions/{session_id}", response_model=SessionResponse)
async def create_session_summary(
    session_id: UUID,
    summary: SessionSummary,
    brain_svc: AgentBrainService = Depends(get_agent_brain_service),
) -> SessionResponse:
    """Create a session summary per D-72.

    Session summaries are written by the reflect_agent job after sessions.
    """
    return await brain_svc.write_session_summary(str(session_id), summary)


# ==============================================================================
# Self-improve endpoint (D-81, D-83, F9-07)
# ==============================================================================


class SelfImproveRequest(BaseModel):
    """Request to self-improve brain files per D-81, D-83, F9-07.

    Enables the agent to freely modify brain files through the async job queue.
    The job handler will process the mutations without gating (D-82).
    """
    soul_update: dict[str, Any] | None = None
    memory_update: dict[str, Any] | None = None
    user_update: dict[str, Any] | None = None


class SelfImproveResponse(BaseModel):
    """Response for self-improve endpoint."""
    status: str
    job_id: str
    message: str


@router.post("/self-improve", response_model=SelfImproveResponse)
async def self_improve(
    request: SelfImproveRequest,
    db: AsyncSession = Depends(get_db),
    policy_service: PolicyService = Depends(get_policy_service),
) -> SelfImproveResponse:
    """Self-improve endpoint per D-81, D-83, F9-07.

    Enables the agent to freely modify brain files (per F9-07, D-81, D-83)
    through the async job queue. The job handler will process the mutations
    without gating (D-82).

    Policy check for agent.brain.write capability per D-74.
    """
    # Policy check per D-74
    _check_brain_write_policy(policy_service, "agent-brain")

    # Build brain_mutations payload per D-82
    brain_mutations = {}
    if request.soul_update:
        brain_mutations["soul_update"] = request.soul_update
    if request.memory_update:
        brain_mutations["memory_update"] = request.memory_update
    if request.user_update:
        brain_mutations["user_update"] = request.user_update

    if not brain_mutations:
        raise HTTPException(status_code=400, detail="At least one brain mutation (soul_update, memory_update, user_update) is required")

    workspace_id = await _get_default_workspace_id(db)

    # Enqueue reflect_agent job with brain_mutations payload per D-82
    job_data = {"brain_mutations": brain_mutations}
    job = await _enqueue_reflect_agent_job(db, workspace_id, job_data)
    await db.commit()

    logger.info("self_improve_enqueued", job_id=str(job.id), mutations=list(brain_mutations.keys()))

    return SelfImproveResponse(
        status="enqueued",
        job_id=str(job.id),
        message="Self-improvement job enqueued. Brain mutations will be processed asynchronously.",
    )
