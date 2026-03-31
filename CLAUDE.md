<!-- GSD:project-start source:PROJECT.md -->
## Project

**Knowledge OS Core**

Knowledge OS Core é um **Knowledge OS self-hosted, local-first, agent-aware e policy-driven** cujo centro é um filesystem canônico de conhecimento em Markdown, com fronteiras formais entre:
- **User Vault** — conhecimento soberano do usuário
- **Agent Brain** — memória operacional privada do agente
- **Exchange Zone** — fronteira auditável de mediação
- **Research Runtime** — fábrica de jobs de pesquisa rastreáveis
- **Retrieval Layer** — projeção derivada (nunca soberana)

O produto resolve um problema estrutural: ferramentas atuais misturam camadas que deveriam ser separadas, causando poluição de vault por IA, RAG como verdade canônica, e pesquisa como chat efêmero.

**Core Value:** **Soberania do filesystem canônico**: o centro do sistema são arquivos Markdown reais, versionados e auditáveis — não vetores, não聊天, não memória de agente.

### Constraints

- **Tech stack (immutable)**: Python/FastAPI no backend, React/Vite no frontend, Postgres/pgvector — decisões do STACK_DECISION_RECORD
- **Arquitecture (immutable)**: Modular monolith + workers, não microservices — v1 não precisa de mais
- **Build order (immutable)**: A sequência de fases é parte do design, não detalhe de gestão
- **Filesystem sovereignty (law)**: Canonical knowledge vive em arquivos reais Markdown — vetores/embeddings são auxiliares
- **Domain separation (law)**: User Vault e Agent Brain são fisicamente separados — nenhuma confusão
- **Policy-first (law)**: Nenhuma ferramenta decide sozinha se pode mutar domínio sensível
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Executive Summary
## 1. Backend Framework
### FastAPI
- Native async support essential for job polling and WebSocket updates
- Automatic OpenAPI/Swagger for API discovery
- Pydantic v2 integration is seamless
- BackgroundTasks for lightweight operations, workers for heavy lifting
- WebSocket support for real-time job status updates
- Use `BackgroundTasks` sparingly; prefer workers for anything beyond trivial
- Modular app structure with APIRouters per bounded context
- Dependency injection for services and database sessions
- https://fastapi.tiangolo.com/
## 2. Schema and Validation
### Pydantic v2
- `BaseModel` for all DTOs, API schemas, tool inputs/outputs
- `Field` for validation with clear error messages
- `computed_field` for derived metadata
- `validator`/`field_validator` for complex domain rules
- `Settings` management via `pydantic-settings`
- JSON Schema generation for tool calling compatibility
- https://docs.pydantic.dev/latest/
## 3. Database Layer
### PostgreSQL + pgvector
- pgvector 0.8+ support (HNSW, IVFFlat, iterative index scans)
- JSONB for flexible metadata storage
- Full-text search (tsvector/tsquery)
- Advisory locks for job queue
- pg_trgm for fuzzy matching on titles/paths
- HNSW index: Better query performance, slower builds
- IVFFlat index: Faster builds, less memory
- Iterative index scans: Automatic expansion for filtered searches
- Multiple distance metrics: L2, cosine, inner product, Hamming, Jaccard
- Adds operational complexity (separate service)
- pgvector is "good enough" for <100K chunks
- Hybrid search simpler with single database
- Point-in-time recovery, ACID compliance maintained
- No JOIN complexity across systems
- >100K chunks with latency requirements <50ms
- Sophisticated hybrid scoring needed
- Distributed vector search required
- https://github.com/pgvector/pgvector
- https://www.postgresql.org/docs/current/textsearch.html
## 4. ORM and Migrations
### SQLAlchemy 2
- First-class async support via `asyncpg` and `AsyncSession`
- Unified tutorial for Core + ORM
- `select()` statements by default (vs `query()`)
- Type annotation hints throughout
- `Mapped` column mapping with automatic type coercion
- Simpler for basic CRUD, limiting for complex domain
- Less flexibility when relational model gets serious
- Adds another dependency with marginal benefit
### Alembic
- https://docs.sqlalchemy.org/en/20/
- https://alembic.sqlalchemy.org/
## 5. Driver
### Psycopg 3
- Full async support (asyncpg driver is built on it)
- Connection pool management built-in
- Server-side cursors for large result sets
- Better PostgreSQL feature support (COPY, LISTEN/NOTIFY)
- `psycopg-pool` for connection pooling
- https://www.psycopg.org/psycopg3/
## 6. Job Queue
### Postgres-Backed Queue + Custom Worker
- Requires Redis/RabbitMQ (extra service)
- Heavy for simple job needs
- Overkill for this scale
- Excellent for complex workflows
- Significant operational overhead
- Appropriate for later phase when research workflows mature
- Research pipeline with checkpoint/resume needs
- Human-in-the-loop approval flows
- Stateful agent runs requiring memory persistence
- https://docs.langchain.com/oss/python/langgraph/durable-execution
## 7. Agent Runtime
### PydanticAI
- Model-agnostic (OpenAI, Anthropic, Gemini, Ollama, etc.)
- First-class Pydantic integration for tool schemas
- Dependency injection via `RunContext`
- Structured output guaranteed via Pydantic models
- Built-in Logfire observability
- MCP protocol support
- Self-correction/Reflection on validation failure
- Hermes provides conceptual architecture for agent brain
- Extract: SOUL.md, MEMORY.md, USER.md, skills pattern
- Don't import Hermes wholesale; extract core patterns
- PydanticAI handles tool execution, Hermes handles brain structure
- https://ai.pydantic.dev/
### Hermes Agent (Conceptual Reference)
- **Memory System:** Agent-curated with periodic nudges, FTS5 session search, LLM summarization
- **Skills System:** Autonomous skill creation after complex tasks, self-improvement
- **Agent Loop:** Core agent logic in `agent/`, skills in `skills/`, user modeling via Honcho
- **Session Management:** Persistent stores for user profiles and best practices
- Full Hermes codebase
- ACP adapter/registry complexity
- Cron-based automation
- https://github.com/NousResearch/hermes-agent
## 8. Research Runtime
### Crawl4AI + Playwright
- `AsyncWebCrawler` for async pipeline integration
- LLM-ready Markdown output
- Structured extraction for repeated patterns
- Session management for authenticated crawls
- Browser pooling for production
- Would need to build all extraction logic
- Markdown generation requires additional work
- No adaptive crawling intelligence
- https://docs.crawl4ai.com/
### Docling
- PDF (including scanned with OCR)
- DOCX, PPTX, XLSX
- HTML, Markdown
- Images (PNG, TIFF, JPEG)
- LaTeX
- WAV, MP3 (transcription)
- WebVTT
- XBRL (financial reports)
- Plain text files
# Export options
- Unified document model across all formats
- Table structure understanding
- Reading order detection
- Page layout analysis
- Visual Language Models (GraniteDocling)
- MCP server for agent connectivity
- Air-gapped/local execution support
- Better Markdown/JSON output alignment
- More format support
- Stronger document understanding
- Actively maintained
- https://docling-project.github.io/docling/
## 9. Frontend Stack
### React + Vite + TypeScript
- Vite provides 10x faster HMR vs webpack
- TypeScript catches errors at write-time
- React ecosystem is mature for complex UIs
- SPA pattern fits (no SSR requirements)
- Clear separation from Python backend
- https://vite.dev/
### TanStack Query
- Server state management with cache
- Automatic refetching/polling for job status
- Optimistic updates for approvals
- Request cancellation on unmount
- Cache invalidation by query key
- https://tanstack.com/query
### Zustand
- Minimal boilerplate
- React context-free (no provider nesting)
- DevTools for debugging
- Persist middleware for local storage
- Good for UI state, not server state
- Server state (use TanStack Query)
- Complex derived state (consider Jotai atoms)
### CodeMirror 6
- Modular, extensible editor
- Markdown-first with syntax highlighting
- Extension ecosystem for:
- Best fit for textual canonical knowledge
- Too heavy for note editing
- Feels like IDE, not note workspace
- Better for code-focused applications
- Rich-text-first, we are Markdown-first
- Patch/diff/Git cleaner with CodeMirror
- Overkill for canonical text editing
- https://codemirror.net/
### Tailwind CSS
- Rapid UI development
- Consistent design system
- Small production bundle (purges unused)
- Easy to customize
- Headless components for accessibility
- Full styling control via Tailwind
- Avoids component library lock-in
## 10. Observability
### structlog
- Structured logging with key-value pairs
- Integrates with stdlib logging
- JSON output for production
- Context propagation across async boundaries
- https://www.structlog.org/
### OpenTelemetry
- HTTP requests (auto-instrumentation)
- Database queries
- Job processing spans
- Agent tool calls
- Complex sampling strategies
- Custom exporters beyond console/OTLP
- Full distributed tracing initially
- https://opentelemetry.io/docs/languages/python/
## 11. Dev Tooling
### uv
- 10-100x faster than pip
- Replaces pip, pip-tools, pipx, poetry, pyenv
- Single tool for project management
- Lockfiles for reproducibility
- https://docs.astral.sh/uv/
### Ruff
- 10-100x faster than Flake8
- Replaces: flake8, isort, pydocstyle, pyupgrade, autoflake
- Built-in fixer
- Black-compatible formatting
- https://docs.astral.sh/ruff/
### mypy
- More mature in Python ecosystem
- Better Django/Pydantic integration
- Less toolchain complexity (no Node.js)
- https://mypy.readthedocs.io/
## 12. Testing
### pytest
- `pytest-asyncio` for async tests
- `pytest-anyio` for anyio/trio support
- `pytest-cov` for coverage
### Playwright
- Cross-browser testing
- Built-in runner, assertions, fixtures
- API testing support
- Good for SPA (vs Cypress for React)
- https://playwright.dev/
## 13. Deployment
### Docker Compose
- `app-api` - FastAPI application
- `worker` - Background job processor
- `postgres` - Database
- `caddy` - Reverse proxy with auto-HTTPS
- Automatic HTTPS
- Simpler configuration
- Good for self-hosted OSS
- Overkill for v1
- Adds operational complexity
- Solo founder should focus on product
## 14. Git Integration
### Git CLI via GitService
- Worktree support is mature
- Full compatibility with Git behavior
- No library edge cases
- Maximum portability
- Worktree support more complex
- Lag behind Git CLI features
- More debugging overhead
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
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
