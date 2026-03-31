# Knowledge OS Core

## What This Is

Knowledge OS Core é um **Knowledge OS self-hosted, local-first, agent-aware e policy-driven** cujo centro é um filesystem canônico de conhecimento em Markdown, com fronteiras formais entre:
- **User Vault** — conhecimento soberano do usuário
- **Agent Brain** — memória operacional privada do agente
- **Exchange Zone** — fronteira auditável de mediação
- **Research Runtime** — fábrica de jobs de pesquisa rastreáveis
- **Retrieval Layer** — projeção derivada (nunca soberana)

O produto resolve um problema estrutural: ferramentas atuais misturam camadas que deveriam ser separadas, causando poluição de vault por IA, RAG como verdade canônica, e pesquisa como chat efêmero.

## Core Value

**Soberania do filesystem canônico**: o centro do sistema são arquivos Markdown reais, versionados e auditáveis — não vetores, não聊天, não memória de agente.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Sistema de arquivos canônico com estrutura de vault (user-vault/, agent-brain/, exchange/, raw/)
- [ ] Schemas e templates-base (daily, project, area, resource, fleeting, permanent, source, synthesis)
- [ ] Daily notes com templates selecionáveis
- [ ] Git como ledger editorial (branches, worktrees, diff, patch, merge)
- [ ] Exchange Zone com proposals, reviews e patch pipeline
- [ ] Policy Engine mínimo com capability model (vault.*, agent.*, research.*, exchange.*)
- [ ] Backend FastAPI modular (módulos: auth, vault, templates, gitops, exchange, policy, approvals, retrieval, agent, research, jobs, audit)
- [ ] Postgres como banco operacional (tabelas: workspaces, actors, notes_projection, policy_rules, approvals, proposals, jobs, chunks, embeddings, artifacts, audit_logs)
- [ ] Worker runtime para jobs assíncronos
- [ ] Agent Brain persistente em Markdown (SOUL.md, MEMORY.md, USER.md, skills/, heuristics/, reflections/)
- [ ] Retrieval híbrido (FTS + pgvector + context packs)
- [ ] Note Copilot (explicar, resumir, sugerir links/tags, propor patches)
- [ ] Research Runtime v1 (blueprint → job → raw → synthesis → ingest proposal)
- [ ] Observabilidade e auditoria (eventos, trace IDs, audit logs)
- [ ] UI web (React + Vite + CodeMirror 6)
- [ ] Deployment self-hosted (Docker Compose + Caddy)

### Out of Scope

- Multi-user maduro, SSO/SAML, enterprise controls — self-hosted single-user é o foco
- Microservices — modular monolith + workers é a arquitetura
- Kubernetes — Docker Compose é suficiente para v1
- Mobile app — web app é a interface principal
- Real-time collaboration — markdown-first editor é o foco
- LangChain como espinha dorsal — PydanticAI + abstractions próprias
- Qdrant/Redis cedo — pgvector no Postgres resolve v1
- MCP interno — superfície de exposição futura, não barramento interno
- Sync protocol próprio — Syncthing como solução externa
- Marketplace de templates/skills — profiles estáticos na v1

## Context

### Domaine Ecosystem
- Second brain / PKM tools (Obsidian, Logseq, Notion)
- Agent frameworks (LangChain, PydanticAI, Hermes-agent)
- RAG and retrieval systems
- Research automation (Crawl4AI, Docling)
- Local-first software movement

### Technical Environment
- **Backend**: Python + FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic + Psycopg 3
- **Database**: PostgreSQL + pgvector + PostgreSQL FTS
- **Jobs**: Postgres-backed queue + custom worker (LangGraph apenas em fluxos específicos)
- **Agent**: Hermes-core-lite conceitual + PydanticAI
- **Research**: Crawl4AI + Playwright + Docling
- **Frontend**: React + Vite + TypeScript + TanStack Query + Zustand + CodeMirror 6
- **Editor**: CodeMirror 6 + react-markdown
- **Ops**: Docker Compose + Caddy
- **Dev**: uv + Ruff + mypy + pytest + Playwright

### Build Order (mandatório)
1. Canonical filesystem and schemas
2. Git/exchange boundary
3. Policy engine
4. Backend/services/jobs
5. Agent brain
6. Retrieval
7. Note copilot
8. Research runtime
9. Durability/HITL
10. MCP/integrations

A ordem não é negociável — cada fase constrói sobre a anterior.

## Constraints

- **Tech stack (immutable)**: Python/FastAPI no backend, React/Vite no frontend, Postgres/pgvector — decisões do STACK_DECISION_RECORD
- **Arquitecture (immutable)**: Modular monolith + workers, não microservices — v1 não precisa de mais
- **Build order (immutable)**: A sequência de fases é parte do design, não detalhe de gestão
- **Filesystem sovereignty (law)**: Canonical knowledge vive em arquivos reais Markdown — vetores/embeddings são auxiliares
- **Domain separation (law)**: User Vault e Agent Brain são fisicamente separados — nenhuma confusão
- **Policy-first (law)**: Nenhuma ferramenta decide sozinha se pode mutar domínio sensível

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python como linguagem principal | Ecossistema AI/agent mais forte, ergonomia para parsing/workers, velocidade de iteração | — Pending |
| FastAPI como web framework | Tipagem natural, integração Pydantic, API-first, modular monolith friendly | — Pending |
| Postgres + pgvector para retrieval | Stack única, zero serviço extra, bom enough para v1 | — Pending |
| PydanticAI para agent runtime | Model-agnostic, tools tipadas, bom fit com Pydantic | — Pending |
| Crawl4AI + Docling para research | Web→Markdown otimizado para LLM, múltiplos formatos document | — Pending |
| CodeMirror 6 como editor | Modular, extensível, textual/Markdown-first, não rich-text | — Pending |
| Patch-first mutation no User Vault | Soberania do usuário, nenhuma escrita silenciosa de IA | — Pending |
| Git como ledger editorial | Versionamento, diff, patch, rollback, worktrees — não substitui policy | — Pending |

---

*Last updated: 2026-03-31 after initialization*
