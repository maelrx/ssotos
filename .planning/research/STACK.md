# Technology Stack Research

**Project:** Knowledge OS Core OSS v1
**Researched:** 2026-03-31
**Confidence:** HIGH (based on official docs, Context7 where available, and verified web sources)

---

## Executive Summary

The stack decisions documented in the SSOT and STACK_DECISION_RECORD are well-aligned with current 2025/2026 ecosystem practices. This research validates the core choices and provides additional context for implementation. The Python ecosystem for agentic knowledge management is mature and well-supported.

---

## 1. Backend Framework

### FastAPI
**Decision:** CONFIRMED
**Version:** Current (check via `pip show fastapi`)
**Confidence:** HIGH

**Why FastAPI:**
- Native async support essential for job polling and WebSocket updates
- Automatic OpenAPI/Swagger for API discovery
- Pydantic v2 integration is seamless
- BackgroundTasks for lightweight operations, workers for heavy lifting
- WebSocket support for real-time job status updates

**Best Practices:**
- Use `BackgroundTasks` sparingly; prefer workers for anything beyond trivial
- Modular app structure with APIRouters per bounded context
- Dependency injection for services and database sessions

**Sources:**
- https://fastapi.tiangolo.com/

---

## 2. Schema and Validation

### Pydantic v2
**Decision:** CONFIRMED
**Confidence:** HIGH

**Key Features for This Project:**
- `BaseModel` for all DTOs, API schemas, tool inputs/outputs
- `Field` for validation with clear error messages
- `computed_field` for derived metadata
- `validator`/`field_validator` for complex domain rules
- `Settings` management via `pydantic-settings`
- JSON Schema generation for tool calling compatibility

**Rust-powered core** provides 10-50x validation performance improvement over v1.

**Why NOT Pydantic v1:** Deprecated, security fixes only. V2 is the standard.

**Sources:**
- https://docs.pydantic.dev/latest/

---

## 3. Database Layer

### PostgreSQL + pgvector
**Decision:** CONFIRMED
**Confidence:** HIGH

**PostgreSQL 16+ recommended for:**
- pgvector 0.8+ support (HNSW, IVFFlat, iterative index scans)
- JSONB for flexible metadata storage
- Full-text search (tsvector/tsquery)
- Advisory locks for job queue
- pg_trgm for fuzzy matching on titles/paths

**pgvector Architecture:**
```
pgvector 0.8+ supports:
- HNSW index: Better query performance, slower builds
- IVFFlat index: Faster builds, less memory
- Iterative index scans: Automatic expansion for filtered searches
- Multiple distance metrics: L2, cosine, inner product, Hamming, Jaccard
```

**Hybrid Search Pattern:**
```sql
-- Combine FTS and vector in single query
SELECT
  title,
  ts_rank(search_vector, query) AS text_rank,
  1 - (embedding <=> $1) AS vector_similarity
FROM notes, to_tsquery('english', $2) query
WHERE search_vector @@ query
ORDER BY text_rank * 0.3 + vector_similarity * 0.7 DESC;
```

**Why NOT Dedicated Vector DB (Qdrant) for v1:**
- Adds operational complexity (separate service)
- pgvector is "good enough" for <100K chunks
- Hybrid search simpler with single database
- Point-in-time recovery, ACID compliance maintained
- No JOIN complexity across systems

**Defer Qdrant When:**
- >100K chunks with latency requirements <50ms
- Sophisticated hybrid scoring needed
- Distributed vector search required

**Sources:**
- https://github.com/pgvector/pgvector
- https://www.postgresql.org/docs/current/textsearch.html

---

## 4. ORM and Migrations

### SQLAlchemy 2
**Decision:** CONFIRMED
**Confidence:** HIGH

**Key SQLAlchemy 2 Features:**
- First-class async support via `asyncpg` and `AsyncSession`
- Unified tutorial for Core + ORM
- `select()` statements by default (vs `query()`)
- Type annotation hints throughout
- `Mapped` column mapping with automatic type coercion

**Async Pattern for This Project:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

async with async_session() as session:
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
```

**Why NOT SQLModel:**
- Simpler for basic CRUD, limiting for complex domain
- Less flexibility when relational model gets serious
- Adds another dependency with marginal benefit

### Alembic
**Decision:** CONFIRMED
**Confidence:** HIGH

**Best Practices:**
1. Use `autogenerate` for routine schema changes
2. Explicit constraint naming for clarity
3. Batch operations for SQLite (not primary DB but good habit)
4. Always validate both upgrade AND downgrade paths
5. Use `alembbic check` before generating empty migrations

**Migration Workflow:**
```bash
alembic revision --autogenerate -m "add notes_projection table"
alembbic upgrade head
alembbic downgrade -1  # test rollback
```

**Sources:**
- https://docs.sqlalchemy.org/en/20/
- https://alembic.sqlalchemy.org/

---

## 5. Driver

### Psycopg 3
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why Psycopg 3 over psycopg2:**
- Full async support (asyncpg driver is built on it)
- Connection pool management built-in
- Server-side cursors for large result sets
- Better PostgreSQL feature support (COPY, LISTEN/NOTIFY)
- `psycopg-pool` for connection pooling

**Configuration Pattern:**
```python
from psycopg import AsyncConnectionPool
from contextlib import asynccontextmanager

async with AsyncConnectionPool(dsn) as pool:
    async with pool.connection() as conn:
        await conn.execute("SELECT...")
```

**Sources:**
- https://www.psycopg.org/psycopg3/

---

## 6. Job Queue

### Postgres-Backed Queue + Custom Worker
**Decision:** CONFIRMED
**Confidence:** HIGH

**Implementation Pattern:**
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    claimed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT
);

-- Claim with FOR UPDATE SKIP LOCKED
UPDATE jobs
SET claimed_at = now(), status = 'running'
WHERE id = (
    SELECT id FROM jobs
    WHERE status = 'pending'
    ORDER BY created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
) RETURNING *;
```

**Why NOT Celery:**
- Requires Redis/RabbitMQ (extra service)
- Heavy for simple job needs
- Overkill for this scale

**Why NOT Temporal:**
- Excellent for complex workflows
- Significant operational overhead
- Appropriate for later phase when research workflows mature

**When to Add LangGraph:**
- Research pipeline with checkpoint/resume needs
- Human-in-the-loop approval flows
- Stateful agent runs requiring memory persistence

**Sources:**
- https://docs.langchain.com/oss/python/langgraph/durable-execution

---

## 7. Agent Runtime

### PydanticAI
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why PydanticAI:**
- Model-agnostic (OpenAI, Anthropic, Gemini, Ollama, etc.)
- First-class Pydantic integration for tool schemas
- Dependency injection via `RunContext`
- Structured output guaranteed via Pydantic models
- Built-in Logfire observability
- MCP protocol support
- Self-correction/Reflection on validation failure

**Tool Definition Pattern:**
```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class NoteInput(BaseModel):
    path: str
    content: str

class NoteOutput(BaseModel):
    note_id: str
    created: bool

agent = Agent(
    'openai:gpt-4o',
    result_type=NoteOutput,
    system_prompt="You manage a knowledge vault..."
)

@agent.tool
async def create_note(
    ctx: RunContext[VaultDeps],
    note: NoteInput
) -> NoteOutput:
    """Create a new note in the vault."""
    return await ctx.deps.vault_service.create(note)
```

**Hermes Integration:**
- Hermes provides conceptual architecture for agent brain
- Extract: SOUL.md, MEMORY.md, USER.md, skills pattern
- Don't import Hermes wholesale; extract core patterns
- PydanticAI handles tool execution, Hermes handles brain structure

**Sources:**
- https://ai.pydantic.dev/

---

### Hermes Agent (Conceptual Reference)
**Decision:** EXTRACT CORE PATTERNS ONLY
**Confidence:** MEDIUM

**From Hermes Architecture:**
- **Memory System:** Agent-curated with periodic nudges, FTS5 session search, LLM summarization
- **Skills System:** Autonomous skill creation after complex tasks, self-improvement
- **Agent Loop:** Core agent logic in `agent/`, skills in `skills/`, user modeling via Honcho
- **Session Management:** Persistent stores for user profiles and best practices

**What to Extract:**
1. File-based brain structure (markdown files as memory)
2. Session summarization pattern
3. Skill creation from experience
4. Periodic memory nudge mechanism

**What NOT to Import:**
- Full Hermes codebase
- ACP adapter/registry complexity
- Cron-based automation

**Sources:**
- https://github.com/NousResearch/hermes-agent

---

## 8. Research Runtime

### Crawl4AI + Playwright
**Decision:** CONFIRMED
**Confidence:** HIGH

**Crawl4AI Architecture:**
```
Browser Automation Layer (Playwright)
    ├── Multi-browser support (Chromium, Firefox, WebKit)
    ├── Session management
    ├── Proxy/stealth modes
    └── Full page scrolling (infinite scroll)

Extraction Layer
    ├── CSS/XPath extraction
    ├── LLM-driven extraction
    ├── BM25 content filtering
    └── Adaptive pattern learning

Output Layer
    ├── Clean Markdown generation
    ├── Structured JSON output
    └── Source citations
```

**Production Deployment:**
```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

browser_cfg = BrowserConfig(
    headless=True,
    browser_type="chromium",
    pool_size=4  # Browser pool for parallelism
)

async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun(
        url="https://example.com",
        config=CrawlerRunConfig(
            content_filter="pruning",  # or "bm25"
            extraction_strategy="llm"  # for structured extraction
        )
    )
```

**Key Features for This Project:**
- `AsyncWebCrawler` for async pipeline integration
- LLM-ready Markdown output
- Structured extraction for repeated patterns
- Session management for authenticated crawls
- Browser pooling for production

**Why NOT Just Playwright:**
- Would need to build all extraction logic
- Markdown generation requires additional work
- No adaptive crawling intelligence

**Sources:**
- https://docs.crawl4ai.com/

---

### Docling
**Decision:** CONFIRMED
**Confidence:** HIGH

**Supported Formats (2025):**
- PDF (including scanned with OCR)
- DOCX, PPTX, XLSX
- HTML, Markdown
- Images (PNG, TIFF, JPEG)
- LaTeX
- WAV, MP3 (transcription)
- WebVTT
- XBRL (financial reports)
- Plain text files

**Core Capabilities:**
```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")

# Export options
result.export_to_markdown()  # For knowledge ingestion
result.export_to_json()       # Lossless for processing
result.export_to_html()       # For rendering
```

**Key Features:**
- Unified document model across all formats
- Table structure understanding
- Reading order detection
- Page layout analysis
- Visual Language Models (GraniteDocling)
- MCP server for agent connectivity
- Air-gapped/local execution support

**Why Docling over Unstructured:**
- Better Markdown/JSON output alignment
- More format support
- Stronger document understanding
- Actively maintained

**Sources:**
- https://docling-project.github.io/docling/

---

## 9. Frontend Stack

### React + Vite + TypeScript
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why This Stack:**
- Vite provides 10x faster HMR vs webpack
- TypeScript catches errors at write-time
- React ecosystem is mature for complex UIs
- SPA pattern fits (no SSR requirements)
- Clear separation from Python backend

**Sources:**
- https://vite.dev/

---

### TanStack Query
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why TanStack Query:**
- Server state management with cache
- Automatic refetching/polling for job status
- Optimistic updates for approvals
- Request cancellation on unmount
- Cache invalidation by query key

**Pattern for Jobs:**
```typescript
const { data: job } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => api.getJob(jobId),
  refetchInterval: () => job?.status === 'running' ? 2000 : false,
});
```

**Sources:**
- https://tanstack.com/query

---

### Zustand
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why Zustand:**
- Minimal boilerplate
- React context-free (no provider nesting)
- DevTools for debugging
- Persist middleware for local storage
- Good for UI state, not server state

**What NOT to Use Zustand For:**
- Server state (use TanStack Query)
- Complex derived state (consider Jotai atoms)

---

### CodeMirror 6
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why CodeMirror 6:**
- Modular, extensible editor
- Markdown-first with syntax highlighting
- Extension ecosystem for:
  - Markdown shortcuts
  - Vim/Emacs keybindings
  - Code blocks
  - Collaborative editing (future)
- Best fit for textual canonical knowledge

**Why NOT Monaco:**
- Too heavy for note editing
- Feels like IDE, not note workspace
- Better for code-focused applications

**Why NOT Tiptap:**
- Rich-text-first, we are Markdown-first
- Patch/diff/Git cleaner with CodeMirror
- Overkill for canonical text editing

**Sources:**
- https://codemirror.net/

---

### Tailwind CSS
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why Tailwind:**
- Rapid UI development
- Consistent design system
- Small production bundle (purges unused)
- Easy to customize

**With Radix UI Primitives:**
- Headless components for accessibility
- Full styling control via Tailwind
- Avoids component library lock-in

---

## 10. Observability

### structlog
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why structlog:**
- Structured logging with key-value pairs
- Integrates with stdlib logging
- JSON output for production
- Context propagation across async boundaries

**Configuration:**
```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

**Sources:**
- https://www.structlog.org/

---

### OpenTelemetry
**Decision:** CONFIRMED (lightweight initially)
**Confidence:** HIGH

**What to Instrument:**
- HTTP requests (auto-instrumentation)
- Database queries
- Job processing spans
- Agent tool calls

**What to Defer:**
- Complex sampling strategies
- Custom exporters beyond console/OTLP
- Full distributed tracing initially

**Sources:**
- https://opentelemetry.io/docs/languages/python/

---

## 11. Dev Tooling

### uv
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why uv:**
- 10-100x faster than pip
- Replaces pip, pip-tools, pipx, poetry, pyenv
- Single tool for project management
- Lockfiles for reproducibility

**Commands:**
```bash
uv pip install fastapi
uv sync  # install from lockfile
uv run pytest
uv add --dev ruff
```

**Sources:**
- https://docs.astral.sh/uv/

---

### Ruff
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why Ruff:**
- 10-100x faster than Flake8
- Replaces: flake8, isort, pydocstyle, pyupgrade, autoflake
- Built-in fixer
- Black-compatible formatting

**Configuration in pyproject.toml:**
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP"]

[tool.ruff.format]
quote-style = "double"
```

**Sources:**
- https://docs.astral.sh/ruff/

---

### mypy
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why mypy over pyright:**
- More mature in Python ecosystem
- Better Django/Pydantic integration
- Less toolchain complexity (no Node.js)

**Configuration:**
```toml
[tool.mypy]
python_version = "3.12"
strict = false  # Start permissive, tighten later
plugins = ["pydantic.mypy"]
```

**Sources:**
- https://mypy.readthedocs.io/

---

## 12. Testing

### pytest
**Decision:** CONFIRMED
**Confidence:** HIGH

**Key Plugins:**
- `pytest-asyncio` for async tests
- `pytest-anyio` for anyio/trio support
- `pytest-cov` for coverage

**Pattern:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_note(client: AsyncClient):
    response = await client.post("/api/v1/notes", json={
        "title": "Test",
        "content": "Content"
    })
    assert response.status_code == 201
```

---

### Playwright
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why Playwright:**
- Cross-browser testing
- Built-in runner, assertions, fixtures
- API testing support
- Good for SPA (vs Cypress for React)

**Sources:**
- https://playwright.dev/

---

## 13. Deployment

### Docker Compose
**Decision:** CONFIRMED
**Confidence:** HIGH

**Services:**
- `app-api` - FastAPI application
- `worker` - Background job processor
- `postgres` - Database
- `caddy` - Reverse proxy with auto-HTTPS

**Why Caddy over Nginx:**
- Automatic HTTPS
- Simpler configuration
- Good for self-hosted OSS

**Why NOT Kubernetes:**
- Overkill for v1
- Adds operational complexity
- Solo founder should focus on product

---

## 14. Git Integration

### Git CLI via GitService
**Decision:** CONFIRMED
**Confidence:** HIGH

**Why Git CLI:**
- Worktree support is mature
- Full compatibility with Git behavior
- No library edge cases
- Maximum portability

**GitService Pattern:**
```python
import subprocess
from pathlib import Path

class GitService:
    def create_worktree(self, branch: str, path: Path) -> None:
        subprocess.run(
            ["git", "worktree", "add", str(path), branch],
            check=True,
            cwd=self.repo_path
        )

    def diff(self, ref_a: str, ref_b: str) -> str:
        result = subprocess.run(
            ["git", "diff", ref_a, ref_b],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
```

**Why NOT GitPython/dulwich:**
- Worktree support more complex
- Lag behind Git CLI features
- More debugging overhead

---

## 15. Explicitly NOT Using (for Clarity)

| Technology | Why NOT | Instead Use |
|------------|---------|------------|
| Redis | Adds service, Postgres handles queue | Postgres-backed queue |
| Qdrant | Premature for <100K chunks | pgvector |
| Temporal | Heavy for initial phase | Simple queue + LangGraph later |
| LangChain | Over-abstracts, couples to framework | PydanticAI + direct abstractions |
| Next.js | Backend is Python, not JS | React SPA |
| Tiptap | Rich-text, not Markdown-first | CodeMirror 6 |
| Django | Admin-centric, not service-centric | FastAPI |
| Celery | Requires Redis, heavy | Custom Postgres queue |

---

## 16. Implementation Priorities by Phase

### Phase 1 - Foundation
- FastAPI + Pydantic v2
- SQLAlchemy 2 + Alembic + Psycopg 3
- PostgreSQL + pgvector + FTS
- uv + Ruff + mypy + pytest

### Phase 2 - Boundary & Policy
- Git CLI via GitService
- Postgres job queue
- structlog + OpenTelemetry (light)

### Phase 3 - Agent & Retrieval
- PydanticAI (agent runtime)
- pgvector hybrid search
- Context pack builder

### Phase 4 - Research
- Crawl4AI + Playwright
- Docling
- Synthesis pipeline

### Phase 5 - Durability
- LangGraph (where durable workflows needed)
- Checkpoint/resume for research jobs

---

## 17. Key References

| Component | Reference |
|-----------|----------|
| FastAPI | https://fastapi.tiangolo.com/ |
| PydanticAI | https://ai.pydantic.dev/ |
| SQLAlchemy 2 | https://docs.sqlalchemy.org/en/20/ |
| Alembic | https://alembic.sqlalchemy.org/ |
| Psycopg 3 | https://www.psycopg.org/psycopg3/ |
| pgvector | https://github.com/pgvector/pgvector |
| PostgreSQL FTS | https://www.postgresql.org/docs/current/textsearch.html |
| Crawl4AI | https://docs.crawl4ai.com/ |
| Docling | https://docling-project.github.io/docling/ |
| Hermes | https://github.com/NousResearch/hermes-agent |
| uv | https://docs.astral.sh/uv/ |
| Ruff | https://docs.astral.sh/ruff/ |
| structlog | https://www.structlog.org/ |
| OpenTelemetry | https://opentelemetry.io/docs/languages/python/ |
| Playwright | https://playwright.dev/ |
