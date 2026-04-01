# MCP Integration Guide

Knowledge OS Core exposes four MCP servers for external AI clients.

## Architecture

All MCP tools route through the internal REST API, ensuring AuditMiddleware and policy checks are always applied.

## Servers

| Server | Path | Tools |
|--------|------|-------|
| vault-user | /mcp/vault | Note CRUD |
| agent-brain | /mcp/agent | Brain, memory, skills |
| research | /mcp/research | Research job management |
| retrieval | /mcp/retrieval | Search and context packs |

## Connecting Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "vault-user": {
      "url": "http://localhost:8000/mcp/vault"
    },
    "agent-brain": {
      "url": "http://localhost:8000/mcp/agent"
    },
    "research": {
      "url": "http://localhost:8000/mcp/research"
    },
    "retrieval": {
      "url": "http://localhost:8000/mcp/retrieval"
    }
  }
}
```

## Policy Enforcement

All MCP calls pass through the same policy engine as REST API calls — no bypass exists.
