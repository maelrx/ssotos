# Phase 5: Agent Brain - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the persistent Agent Brain — the private memory domain where the agent evolves freely. This makes the agent stateful across sessions with proper curation of skills, memories, and user context.

</domain>

<decisions>
## Implementation Decisions

### Agent Brain Filesystem (F9-01)
- **D-65:** Structure already scaffolded in Phase 1: `SOUL.md`, `MEMORY.md`, `USER.md`, `skills/`, `heuristics/`, `reflections/`, `sessions/`, `scratchpads/`, `playbooks/`, `traces/`
- **D-66:** All brain files live in `workspace/agent-brain/` — accessible via `/agent/brain/*` API

### Skill System (F9-05)
- **D-67:** Skill format: `skills/<skill-name>/manifest.yaml` with name, description, trigger_patterns (regex), procedure (Markdown body)
- **D-68:** Skills invoked via PydanticAI tool calls (not natural language pattern matching) — agent explicitly calls `agent.invoke_skill(skill_name)`
- **D-69:** Skill curation criteria: recurring pattern + reusable procedure + clear operational gain + justifiable maintenance

### Session Summaries (F9-06)
- **D-70:** Session summaries stored at `agent-brain/sessions/<session-id>.md`
- **D-71:** Summary triggered via `reflect_agent` job at end of session (async, not blocking)
- **D-72:** Session summary format: ## What happened, ## Key decisions, ## Open questions, ## Next steps

### SOUL.md (F9-02)
- **D-73:** SOUL.md contains: identity statement, operating principles, communication style, constraints, self-improvement guidelines
- **D-74:** SOUL.md is agent-editable with policy checks (agent.* capabilities apply)

### MEMORY.md (F9-03)
- **D-75:** MEMORY.md contains curated high-value learnings, established patterns, operational heuristics
- **D-76:** Memory consolidation via `consolidate_memory` job — triggered periodically or on explicit request
- **D-77:** Memory curation criteria: recurrence, future utility, temporal stability, reliability, operational impact

### USER.md (F9-04)
- **D-78:** USER.md captures: user preferences, work patterns, context, restrictions, communication style
- **D-79:** Agent updates USER.md proactively after observing user behavior patterns
- **D-80:** User can directly edit USER.md — agent respects user overrides

### Self-Improve Workflow (F9-07)
- **D-81:** Agent can self-improve freely in `agent-brain/` domain (no policy restrictions on agent.* capabilities)
- **D-82:** Changes to `agent-brain/` via `reflect_agent` job — logged but not gated
- **D-83:** Self-improve happens on explicit agent request (not automatic after every session)

### API Endpoints (F9 + F7-01)
- **D-84:** `/agent/brain/*` — read/update SOUL.md, MEMORY.md, USER.md
- **D-85:** `/agent/skills/*` — list skills, invoke skill, create skill
- **D-86:** `/agent/sessions/*` — list session summaries, create session summary
- **D-87:** `/agent/skills/<name>/invoke` — POST with {input} → {output} (skill procedure executed as agent tool)

### Worker Integration (F9-06)
- **D-88:** `reflect_agent` job processes: session summary + memory consolidation + skill creation from heuristics
- **D-89:** `consolidate_memory` job: reads recent sessions, extracts patterns, updates MEMORY.md if criteria met

### Claude's Discretion
- Specific skill trigger pattern format (simple regex vs full pattern DSL) — use simple regex
- Heuristic-to-skill conversion threshold — defer to implementation (default: 3+ occurrences)
- Session summary length targets — defer to implementation

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `docs/SSOT_Knowledge_OS_V1.md` §12 — Agent Brain mission, artifacts (12.2), rules (12.3), memory curation (12.4), skill curation (12.5)

### Phase-Specific
- `.planning/ROADMAP.md` §Phase 5 — Success criteria, key deliverables
- `.planning/REQUIREMENTS.md` §F9 — F9-01 to F9-07

### Prior Phases
- `.planning/phases/01-knowledge-filesystem-foundation/01-CONTEXT.md` — D-03: agent-brain structure
- `.planning/phases/04-backend-api-services-jobs/04-CONTEXT.md` — D-48: agent module, D-55: reflect_agent job type

</canonical_refs>

<existing_code>
## Existing Code Insights

### Reusable Assets
- Phase 1 scaffold: `workspace/agent-brain/` with SOUL.md, MEMORY.md, USER.md, skills/, heuristics/, reflections/, sessions/, scratchpads/, playbooks/, traces/ (all empty templates)
- Phase 4: `src/worker/handlers/reflect_agent.py` — placeholder handler waiting for Phase 5 implementation
- Phase 4: `src/api/` — 11 routers already registered; agent router NOT yet created

### Integration Points
- `/agent/*` API router → registers in `src/app.py` alongside existing routers
- `reflect_agent` job handler → uses brain files + session summaries
- `consolidate_memory` job handler → updates MEMORY.md

</existing_code>

<specifics>
## Specific Ideas

No external references beyond SSOT/PRD and Phase 1 scaffold.

</specifics>

<deferred>
## Deferred Ideas

- Marketplace of static skill profiles — out of scope for v1
- Agent-to-agent communication protocol — future phase
- Autonomous skill self-creation beyond heuristics — Phase 5 implements trigger, full auto-creation deferred

</deferred>

---

*Phase: 05-agent-brain*
*Context gathered: 2026-03-31*
*Auto-mode: all gray areas auto-selected with documented defaults*
