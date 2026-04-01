"""FastMCP server factory with policy-aware HTTP client.

All MCP tools use an internal HTTP client to call REST API endpoints.
This ensures AuditMiddleware and policy checks are always applied —
no MCP path bypasses the API/policy layer.
"""
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

# Internal API base URL — same process, different transport
API_BASE = "http://127.0.0.1:8000/api"


class MCPService:
    """Base class for MCP servers that call the REST API."""

    def __init__(self, server_name: str):
        self.server_name = server_name
        self.mcp = FastMCP(server_name)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=API_BASE, timeout=30.0)
        return self._client

    async def _call_api(
        self,
        method: str,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call an internal API endpoint. Ensures policy is always applied."""
        client = await self._get_client()
        url = f"{API_BASE}{path}"

        if method == "GET":
            response = await client.get(url, params=params)
        elif method == "POST":
            response = await client.post(url, json=json_data)
        elif method == "PUT":
            response = await client.put(url, json=json_data)
        elif method == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError(f"Unknown HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def tool(self, name: str, description: str):
        """Decorator to register a tool on the MCP server."""
        return self.mcp.tool(name=name, description=description)

    def run(self, transport: str = "streamable-http"):
        """Run the MCP server."""
        self.mcp.run(transport=transport)
