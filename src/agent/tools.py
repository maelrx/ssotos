"""PydanticAI tool functions for skill invocation — per D-67, D-68.

Provides the bridge between PydanticAI agent tool calls and SkillService invocation.
"""
from typing import Any

from pydantic import BaseModel
from pydanticai import Tool
from pydanticai.common_tools import knowledge

from src.services.skill_service import SkillService
from src.schemas.agent import SkillManifest


class InvokeSkillInput(BaseModel):
    """Input schema for skill invocation tool per D-67."""
    skill_name: str
    input_data: dict[str, Any] = {}


async def invoke_skillTool(
    skill_name: str,
    input_data: dict[str, Any],
    ctx: Any,
) -> dict[str, Any]:
    """PydanticAI tool for invoking a skill per D-68.

    The agent calls this tool when it determines a skill is relevant.
    The skill_service is obtained from the agent's RunContext deps.

    Args:
        skill_name: Name of the skill to invoke
        input_data: Input data to pass to the skill procedure
        ctx: PydanticAI RunContext containing AgentDeps.skill_service

    Returns:
        dict with skill output or error
    """
    skill_service: SkillService = ctx.deps.skill_service
    result = await skill_service.invoke_skill(skill_name, input_data)
    return {
        "skill_name": result.skill_name,
        "output": result.output_data,
        "success": result.success,
        "error": result.error,
    }


def make_skill_tool(skill_name: str, manifest: SkillManifest) -> Tool:
    """Create a PydanticAI Tool from a skill manifest per D-67.

    Args:
        skill_name: Name of the skill
        manifest: SkillManifest loaded from skills/<name>/manifest.yaml

    Returns:
        PydanticAI Tool configured for this skill
    """
    # Build a description from manifest
    description = manifest.description
    if manifest.trigger_patterns:
        triggers = ", ".join(t.pattern for t in manifest.trigger_patterns[:3])
        description = f"{description} (triggers: {triggers})"

    def skill_tool_func(skill_input: dict[str, Any], ctx: Any) -> dict[str, Any]:
        """Wrapper that delegates to invoke_skillTool."""
        return invoke_skillTool(skill_name, skill_input, ctx)

    return Tool(
        name=f"skill_{skill_name}",
        description=description,
        param_model=InvokeSkillInput,
    )(skill_tool_func)


def get_all_skill_tools(skill_service: SkillService) -> list[Tool]:
    """Build PydanticAI Tool list from all registered skills per D-67.

    Args:
        skill_service: SkillService instance with loaded skill manifests

    Returns:
        List of PydanticAI Tool instances, one per skill
    """
    skills_response = skill_service.list_skills()
    tools = []
    for manifest in skills_response.skills:
        tool = make_skill_tool(manifest.name, manifest)
        tools.append(tool)
    return tools
