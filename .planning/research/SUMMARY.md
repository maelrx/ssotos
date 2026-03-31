# Research Summary: Knowledge OS Core OSS v1

**Domain:** Knowledge OS / Agent-aware knowledge management system
**Researched:** 2026-03-31
**Overall Confidence:** HIGH

## Executive Summary

This is a greenfield project for a self-hosted, local-first, agent-aware, policy-driven Knowledge OS. The canonical knowledge layer is a filesystem in Markdown, with formal boundaries between User Vault, Agent Brain, Exchange Zone, Research Runtime, and Retrieval Layer.

The technology stack is well-aligned with 2025/2026 ecosystem standards. Python dominates the backend for AI/agent tooling, FastAPI provides the API layer, PostgreSQL with pgvector handles both operational data and hybrid retrieval, and a Postgres-backed queue handles jobs. The frontend uses React with modern tooling. The research runtime uses Crawl4AI for web crawling and Docling for document parsing.

## Key Findings

**Stack is well-chosen:**
- Python + FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic + Psycopg 3 is the modern Python data stack
- PostgreSQL + pgvector provides hybrid FTS + vector retrieval without extra services
- Postgres-backed queue is sufficient for v1; Temporal/LangGraph reserved for complex workflows later
- PydanticAI is the right choice for agent runtime (model-agnostic, Pydantic-native)
- Crawl4AI + Docling covers research/crawling/parsing needs

**Architecture principles confirmed:**
- Filesystem-first: canonical knowledge is Markdown files
- Agent Brain is separate from User Vault
- Exchange Zone mediates all agent/user boundary crossings
- Policy engine gates mutations
- Git provides revision boundary, not knowledge storage

**No major red flags found:**
- All selected technologies are actively maintained
- Ecosystem is mature for each component
- No obvious missing pieces in the stack

## Implications for Roadmap

Based on research, the build order is sound:

1. **Filesystem Foundation** - Establish canonical structure, schemas, templates first
2. **Revision Boundary** - Git + Exchange Zone + patch pipeline provides safety
3. **Control Plane** - FastAPI + Postgres + Policy Engine enables safe multi-domain operations
4. **Agent Brain** - Hermes-core-lite concept + PydanticAI gives agent without coupling
5. **Retrieval** - FTS + pgvector + context packs provides useful search
6. **Note Copilot** - Single-note AI assistance builds trust
7. **Research Runtime** - Crawl4AI + Docling + synthesis creates durable research jobs
8. **Durability/HITL** - Checkpoint/resume, approval flows complete the loop
9. **MCP/Integrations** - External exposure once internals stabilize

**Research flags for phases:**
- Phase 4 (Agent Brain): Policy engine design needs deeper research before implementation
- Phase 7 (Research Runtime): Crawl4AI browser pool sizing and Docling model requirements need profiling
- Phase 8 (Durability): LangGraph adoption criteria should be defined quantitatively

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Based on official docs, verified web sources, ecosystem alignment |
| Features | HIGH | Well-specified in SSOT, standard patterns for KM systems |
| Architecture | HIGH | Solid principles, matches known successful systems (Notion, Obsidian, Hermes) |
| Pitfalls | MEDIUM | General pitfalls known, project-specific ones emerge during build |

## Gaps to Address

- Policy engine implementation patterns (OPA vs custom vs rule-based)
- Specific embedding model choice (OpenAI vs local via Ollama)
- Browser pool sizing for Crawl4AI in production
- Docling resource requirements for large documents
- Session memory storage implementation (FTS5 vs full-text table)
