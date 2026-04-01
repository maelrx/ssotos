# Phase 10: MCP / Integrations — Summary

**Phase:** 10-mcp-integrations
**Status:** Planned
**Created:** 2026-04-01

---

## Overview

Expose MCP (Model Context Protocol) servers for vault, agent, research, and retrieval — the standardized integration surface for external AI clients.

**Key constraint:** No MCP path bypasses API/policy layer. MCP tools go through REST API to ensure AuditMiddleware and policy checks are always applied.

---

## Requirements

| ID | Requirement |
|----|-------------|
| F15-01 | vault-user-mcp: note CRUD with policy enforcement |
| F15-02 | agent-brain-mcp: memory and skill operations |
| F15-03 | research-mcp: job creation and status |
| F15-04 | retrieval-mcp: search and context packs |
| F15-05 | All MCP calls pass through policy engine |
| F15-06 | No MCP path bypasses API/policy layer |

---

## Architecture

```
MCP Client → MCP Server → httpx (internal HTTP) → FastAPI → Services → DB
                                        ↑
                                AuditMiddleware (always applied)
```

Each MCP tool maps 1:1 to an API endpoint. No direct service access from MCP.

---

## Key Files to Create

### MCP Servers (src/mcp/)

| File | Purpose |
|------|---------|
| `src/mcp/__init__.py` | Package init |
| `src/mcp/base.py` | FastMCP server factory with policy-aware base |
| `src/mcp/vault_server.py` | vault-user-mcp: note CRUD |
| `src/mcp/agent_server.py` | agent-brain-mcp: brain ops, skills |
| `src/mcp/research_server.py` | research-mcp: job management |
| `src/mcp/retrieval_server.py` | retrieval-mcp: search, context packs |

### Infrastructure

| File | Purpose |
|------|---------|
| `pyproject.toml` | Add `mcp[cli]` dependency |

---

## Wave Plan

| Wave | Plans | Focus |
|------|-------|-------|
| 1 | 10-01 | MCP infrastructure + vault-user-mcp + agent-brain-mcp |
| 2 | 10-02 | research-mcp + retrieval-mcp |
| 3 | 10-03 | MCP registration, tests, docs |

---

## Dependencies

**From Prior Phases:**
- Phase 4: FastAPI app, AuditMiddleware, all API routers
- Phase 5: Agent brain services
- Phase 8: Research pipeline
- Phase 9: Durable jobs

---

## Next Steps

Execute:
```
/gsd:execute-phase 10-01  # MCP infra + vault + agent
# Then
/gsd:execute-phase 10-02  # research + retrieval
# Then
/gsd:execute-phase 10-03  # registration + tests
```

---

*Summary created: 2026-04-01*
