"""agent-brain-mcp: Brain and skill operations — per F15-02.

All tools route through REST API, ensuring AuditMiddleware applies.
"""
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

API_BASE = "http://127.0.0.1:8000/api"
agent_mcp = FastMCP("agent-brain")


async def _call(method: str, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
        url = f"{API_BASE}{path}"
        if method == "GET":
            r = await client.get(url)
        elif method == "POST":
            r = await client.post(url, json=json_data)
        elif method == "PUT":
            r = await client.put(url, json=json_data)
        else:
            raise ValueError(f"Unknown method: {method}")
        r.raise_for_status()
        return r.json()


@agent_mcp.tool(name="brain_get_soul", description="Get the agent's SOUL.md content")
async def get_soul() -> dict[str, Any]:
    return await _call("GET", "/agent/brain/soul")


@agent_mcp.tool(name="brain_update_soul", description="Update the agent's SOUL.md")
async def update_soul(content: str) -> dict[str, Any]:
    return await _call("PUT", "/agent/brain/soul", json_data={"content": content})


@agent_mcp.tool(name="brain_get_memory", description="Get the agent's MEMORY.md content")
async def get_memory() -> dict[str, Any]:
    return await _call("GET", "/agent/brain/memory")


@agent_mcp.tool(name="brain_update_memory", description="Update the agent's MEMORY.md")
async def update_memory(content: str) -> dict[str, Any]:
    return await _call("PUT", "/agent/brain/memory", json_data={"content": content})


@agent_mcp.tool(name="brain_get_user", description="Get the user profile")
async def get_user() -> dict[str, Any]:
    return await _call("GET", "/agent/brain/user")


@agent_mcp.tool(name="brain_update_user", description="Update the user profile")
async def update_user(content: str) -> dict[str, Any]:
    return await _call("PUT", "/agent/brain/user", json_data={"content": content})


@agent_mcp.tool(name="brain_list_skills", description="List all available skills")
async def list_skills() -> dict[str, Any]:
    return await _call("GET", "/agent/skills")


@agent_mcp.tool(name="brain_invoke_skill", description="Invoke a named skill with parameters")
async def invoke_skill(skill_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    return await _call("POST", f"/agent/skills/{skill_name}/invoke", json_data=params or {})
