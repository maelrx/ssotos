"""retrieval-mcp: Search and context packs — per F15-04.

All tools route through REST API to ensure AuditMiddleware applies.
"""
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

API_BASE = "http://127.0.0.1:8000/api"
retrieval_mcp = FastMCP("retrieval")


async def _call(method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
        url = f"{API_BASE}{path}"
        if method == "GET":
            r = await client.get(url, params=params)
        else:
            raise ValueError(f"Unknown method: {method}")
        r.raise_for_status()
        return r.json()


@retrieval_mcp.tool(name="retrieval_search", description="Hybrid search across notes (FTS + vector)")
async def search(
    q: str,
    limit: int = 20,
    mode: str = "hybrid",
    workspace_id: str | None = None,
) -> dict[str, Any]:
    params = {"q": q, "limit": limit, "mode": mode}
    if workspace_id:
        params["workspace_id"] = workspace_id
    return await _call("GET", "/retrieval/search", params=params)


@retrieval_mcp.tool(name="retrieval_get_context", description="Get context pack with neighbors for a note")
async def get_context(note_id: str, limit: int = 20) -> list[dict[str, Any]]:
    return await _call("GET", f"/retrieval/context/{note_id}", params={"limit": limit})


@retrieval_mcp.tool(name="retrieval_get_stats", description="Get retrieval index statistics")
async def get_stats(workspace_id: str) -> dict[str, Any]:
    return await _call("GET", f"/retrieval/stats/{workspace_id}")
