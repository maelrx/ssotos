# Phase 10: MCP / Integrations — Implementation Steps

**Phase:** 10-mcp-integrations
**Created:** 2026-04-01
**Granularity:** Fine (3 waves)

---

## Wave Structure

| Wave | Plans | Focus | Dependencies |
|------|-------|-------|--------------|
| 1 | 10-01 | MCP infra + vault-user-mcp + agent-brain-mcp | 04-02, 05 |
| 2 | 10-02 | research-mcp + retrieval-mcp | 08, 10-01 |
| 3 | 10-03 | MCP registration, tests, docs | 10-02 |

---

## Plan 10-01: MCP Infrastructure + Vault + Agent

**Wave:** 1 | **Type:** execute

Sets up MCP Python SDK and implements the first two MCP servers.

### Tasks

#### Task 1: Install MCP Python SDK
**Files:** `pyproject.toml`

Add: `mcp[cli]>=1.0`

#### Task 2: Create MCP base server
**Files:** `src/mcp/base.py`

Create `FastMCP` server factory with:
- Internal HTTP client (httpx) for calling API endpoints
- Base URL configured to `http://127.0.0.1:8000`
- Tool naming conventions: `<domain>_<action>`
- Error handling that maps HTTP errors to MCP errors

#### Task 3: Create vault-user-mcp server
**Files:** `src/mcp/vault_server.py`

Tools exposed:
- `vault_list_notes(path?, limit?, page?)` → GET /api/vault/notes
- `vault_get_note(note_id)` → GET /api/vault/notes/{id}
- `vault_create_note(path, content, title, tags?, kind?)` → POST /api/vault/notes
- `vault_update_note(note_id, content?, frontmatter?)` → PUT /api/vault/notes/{id}
- `vault_delete_note(note_id)` → DELETE /api/vault/notes/{id}
- `vault_search_notes(q)` → GET /api/vault/search

#### Task 4: Create agent-brain-mcp server
**Files:** `src/mcp/agent_server.py`

Tools exposed:
- `brain_get_soul()` → GET /api/agent/brain/soul
- `brain_update_soul(content)` → PUT /api/agent/brain/soul
- `brain_get_memory()` → GET /api/agent/brain/memory
- `brain_update_memory(content)` → PUT /api/agent/brain/memory
- `brain_get_user()` → GET /api/agent/brain/user
- `brain_update_user(content)` → PUT /api/agent/brain/user
- `brain_list_skills()` → GET /api/agent/skills
- `brain_invoke_skill(skill_name, params?)` → POST /api/agent/skills/{name}/invoke

---

## Plan 10-02: Research + Retrieval MCP Servers

**Wave:** 2 | **Type:** execute

Implements the remaining two MCP servers.

### Tasks

#### Task 1: Create research-mcp server
**Files:** `src/mcp/research_server.py`

Tools exposed:
- `research_list_jobs(status?, limit?)` → GET /api/research/jobs
- `research_get_job(job_id)` → GET /api/research/jobs/{id}
- `research_create_brief(query, goal, questions?, scope?, depth?, max_sources?)` → POST /api/research/briefs
- `research_cancel_job(job_id)` → POST /api/research/jobs/{id}/cancel
- `research_get_sources(job_id)` → GET /api/research/jobs/{id}/sources
- `research_get_synthesis(job_id)` → GET /api/research/jobs/{id}/synthesis

#### Task 2: Create retrieval-mcp server
**Files:** `src/mcp/retrieval_server.py`

Tools exposed:
- `retrieval_search(q, limit?, mode?, workspace_id?)` → GET /api/retrieval/search
- `retrieval_get_context(note_id, limit?)` → GET /api/retrieval/context/{note_id}
- `retrieval_get_stats(workspace_id)` → GET /api/retrieval/stats/{workspace_id}

---

## Plan 10-03: Registration + Tests + Docs

**Wave:** 3 | **Type:** execute

Wires up MCP servers, adds tests and documentation.

### Tasks

#### Task 1: Register MCP servers in app
**Files:** `src/app.py`

Mount MCP servers as HTTP apps:
```python
from src.mcp.vault_server import vault_mcp
from src.mcp.agent_server import agent_mcp
from src.mcp.research_server import research_mcp
from src.mcp.retrieval_server import retrieval_mcp

app.mount("/mcp/vault", vault_mcp.streamable_http_app())
app.mount("/mcp/agent", agent_mcp.streamable_http_app())
app.mount("/mcp/research", research_mcp.streamable_http_app())
app.mount("/mcp/retrieval", retrieval_mcp.streamable_http_app())
```

#### Task 2: Add MCP endpoint documentation
**Files:** `src/api/mcp.py` (optional OpenAPI schema)

Document MCP server capabilities.

#### Task 3: Add MCP smoke tests
**Files:** `tests/unit/test_mcp_servers.py`

Test: verify MCP servers start, tools are registered, tools call API endpoints.

#### Task 4: Update docs
**Files:** `docs/MCP_INTEGRATION.md`

Document how to connect Claude Desktop, Copilot, etc. to the MCP servers.

---

## Success Criteria

1. vault-user-mcp server exposes note CRUD with policy enforcement
2. agent-brain-mcp server exposes memory and skill operations
3. research-mcp server exposes job creation and status
4. retrieval-mcp server exposes search and context pack retrieval
5. All MCP calls pass through AuditMiddleware (no bypass)
6. No MCP path bypasses API/policy layer

---

*Steps documented: 2026-04-01*
