"""vault-user-mcp: Note CRUD with policy enforcement — per F15-01.

All tools route through REST API, ensuring AuditMiddleware applies.
"""
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

API_BASE = "http://127.0.0.1:8000/api"
vault_mcp = FastMCP("vault-user")


async def _call(method: str, path: str, json_data: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
        url = f"{API_BASE}{path}"
        if method == "GET":
            r = await client.get(url, params=params)
        elif method == "POST":
            r = await client.post(url, json=json_data)
        elif method == "PUT":
            r = await client.put(url, json=json_data)
        elif method == "DELETE":
            r = await client.delete(url)
        else:
            raise ValueError(f"Unknown method: {method}")
        r.raise_for_status()
        return r.json()


@vault_mcp.tool(name="vault_list_notes", description="List notes with optional path filter")
async def list_notes(
    path: str | None = None,
    limit: int = 50,
    page: int = 1,
) -> list[dict[str, Any]]:
    """List notes from the vault."""
    params = {"path": path, "limit": limit, "page": page} if path else {"limit": limit, "page": page}
    data = await _call("GET", "/vault/notes", params=params)
    return data.get("notes", [])


@vault_mcp.tool(name="vault_get_note", description="Get a note by ID")
async def get_note(note_id: str) -> dict[str, Any]:
    """Get a single note by its UUID."""
    return await _call("GET", f"/vault/notes/{note_id}")


@vault_mcp.tool(name="vault_create_note", description="Create a new note")
async def create_note(
    path: str,
    content: str = "",
    title: str = "",
    tags: list[str] | None = None,
    kind: str = "permanent",
) -> dict[str, Any]:
    """Create a new note in the vault."""
    frontmatter = {
        "title": title,
        "kind": kind,
        "tags": tags or [],
        "links": [],
    }
    return await _call("POST", "/vault/notes", json_data={
        "path": path,
        "content": content,
        "frontmatter": frontmatter,
    })


@vault_mcp.tool(name="vault_update_note", description="Update an existing note")
async def update_note(
    note_id: str,
    content: str | None = None,
    frontmatter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update a note's content or frontmatter."""
    payload = {}
    if content is not None:
        payload["content"] = content
    if frontmatter is not None:
        payload["frontmatter"] = frontmatter
    return await _call("PUT", f"/vault/notes/{note_id}", json_data=payload)


@vault_mcp.tool(name="vault_delete_note", description="Delete a note by ID")
async def delete_note(note_id: str) -> dict[str, Any]:
    """Delete a note from the vault."""
    return await _call("DELETE", f"/vault/notes/{note_id}")


@vault_mcp.tool(name="vault_search_notes", description="Search notes by query")
async def search_notes(q: str) -> dict[str, Any]:
    """Full-text search across vault notes."""
    return await _call("GET", "/vault/search", params={"q": q})
