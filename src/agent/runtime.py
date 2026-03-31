"""PydanticAI Agent runtime builder — per D-67.

Constructs a PydanticAI Agent with skills as tools and SOUL.md as system prompt.
"""
import asyncio
from typing import Any

from pydantic import BaseModel
from pydanticai import Agent
from pydanticai.common_tools import knowledge

from src.services.skill_service import SkillService


class AgentDeps(BaseModel):
    """Dependencies injected into the PydanticAI agent per D-67."""
    skill_service: SkillService


def _build_system_prompt(soul_content: dict[str, Any]) -> str:
    """Build system prompt from SOUL.md sections per D-73.

    Constructs a coherent identity prompt from the parsed SOUL.md sections.
    """
    sections = []

    if soul_content.get("identity_statement"):
        sections.append(f"# Identity\n{soul_content['identity_statement']}")

    if soul_content.get("operating_principles"):
        principles = "\n".join(f"- {p}" for p in soul_content["operating_principles"])
        sections.append(f"# Operating Principles\n{principles}")

    if soul_content.get("communication_style"):
        sections.append(f"# Communication Style\n{soul_content['communication_style']}")

    if soul_content.get("constraints"):
        constraints = "\n".join(f"- {c}" for c in soul_content["constraints"])
        sections.append(f"# Constraints\n{constraints}")

    if soul_content.get("self_improvement_guidelines"):
        guidelines = "\n".join(f"- {g}" for g in soul_content["self_improvement_guidelines"])
        sections.append(f"# Self-Improvement\n{guidelines}")

    return "\n\n".join(sections) if sections else "You are a helpful AI assistant."


def build_agent(skill_service: SkillService) -> Agent[AgentDeps]:
    """Build a PydanticAI Agent with skills as tools per D-67.

    Args:
        skill_service: SkillService instance for loading skill manifests

    Returns:
        Configured PydanticAI Agent instance

    The agent uses:
    - model: anthropic:claude-3-5-sonnet
    - tools: all skills from skill_service.list_skills() as PydanticAI Tool
    - deps_type: AgentDeps (injects skill_service)
    - system_prompt: constructed from SOUL.md sections

    Note: asyncio.run() is used for one-time initialization at agent build time
    (startup, not per-request).
    """
    # Load skills to get their manifests (async call from sync context)
    skills_response = asyncio.run(skill_service.list_skills())
    skill_names = [s.name for s in skills_response.skills]

    # Load SOUL.md for system prompt (async call from sync context)
    from src.services.agent_brain_service import AgentBrainService
    brain_svc = AgentBrainService()
    soul_response = asyncio.run(brain_svc.read_soul())

    # Build system prompt from SOUL.md sections
    soul_dict = soul_response.content.model_dump() if hasattr(soul_response.content, "model_dump") else soul_response.content
    system_prompt = _build_system_prompt(soul_dict)

    # Create agent with skills as tools
    # Note: tools are added via get_all_skill_tools which is called separately
    agent = Agent(
        model="anthropic:claude-3-5-sonnet",
        deps_type=AgentDeps,
        system_prompt=system_prompt,
    )

    return agent
