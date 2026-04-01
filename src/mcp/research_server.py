"""research-mcp: Job management — per F15-03.

All tools route through REST API to ensure AuditMiddleware applies.
"""
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

API_BASE = "http://127.0.0.1:8000/api"
research_mcp = FastMCP("research")


async def _call(method: str, path: str, json_data: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60.0) as client:
        url = f"{API_BASE}{path}"
        if method == "GET":
            r = await client.get(url, params=params)
        elif method == "POST":
            r = await client.post(url, json=json_data)
        else:
            raise ValueError(f"Unknown method: {method}")
        r.raise_for_status()
        return r.json()


@research_mcp.tool(name="research_list_jobs", description="List research jobs")
async def list_jobs(status: str | None = None, limit: int = 50) -> dict[str, Any]:
    params = {"status": status, "limit": limit} if status else {"limit": limit}
    return await _call("GET", "/research/jobs", params=params)


@research_mcp.tool(name="research_get_job", description="Get research job status and result")
async def get_job(job_id: str) -> dict[str, Any]:
    return await _call("GET", f"/research/jobs/{job_id}")


@research_mcp.tool(name="research_create_brief", description="Create a research brief and enqueue job")
async def create_brief(
    query: str,
    goal: str,
    questions: list[str] | None = None,
    scope: str = "web",
    depth: str = "surface",
    max_sources: int = 10,
) -> dict[str, Any]:
    return await _call("POST", "/research/briefs", json_data={
        "query": query,
        "goal": goal,
        "questions": questions or [],
        "scope": scope,
        "depth": depth,
        "max_sources": max_sources,
    })


@research_mcp.tool(name="research_cancel_job", description="Cancel a running research job")
async def cancel_job(job_id: str) -> dict[str, Any]:
    return await _call("POST", f"/research/jobs/{job_id}/cancel")


@research_mcp.tool(name="research_get_sources", description="Get sources for a research job")
async def get_sources(job_id: str) -> dict[str, Any]:
    return await _call("GET", f"/research/jobs/{job_id}/sources")


@research_mcp.tool(name="research_get_synthesis", description="Get synthesis output for a completed job")
async def get_synthesis(job_id: str) -> dict[str, Any]:
    return await _call("GET", f"/research/jobs/{job_id}/synthesis")
