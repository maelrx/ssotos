# Phase 5: Agent Brain - Research

**Researched:** 2026-03-31
**Domain:** Agent Brain — persistent memory, skills system, session management, PydanticAI integration
**Confidence:** HIGH

## Summary

Phase 5 implements the persistent Agent Brain: the private memory domain where the agent evolves freely across sessions. The key components are (1) the filesystem at `workspace/agent-brain/` with SOUL.md, MEMORY.md, USER.md, and subdirectories for skills/heuristics/sessions/etc., (2) a new `/agent/*` API router with brain read/write, skill management, and session endpoints, (3) PydanticAI tool registration for skills via `invoke_skill` tool call, (4) full implementations of `reflect_agent` and `consolidate_memory` job handlers replacing the placeholders. The phase uses PydanticAI as the agent runtime (per STACK_DECISION_RECORD D-67 to D-69), with skills stored as YAML manifests and invoked as tools.

**Primary recommendation:** Build `src/services/agent_brain_service.py` as the central module for all brain filesystem operations, expose it via a new `src/api/agent.py` router, integrate skills into PydanticAI via dynamic `Tool` registration, and wire up the `reflect_agent`/`consolidate_memory` handlers with real logic reading from session summaries and writing to MEMORY.md.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-65:** Structure already scaffolded in Phase 1: `SOUL.md`, `MEMORY.md`, `USER.md`, `skills/`, `heuristics/`, `reflections/`, `sessions/`, `scratchpads/`, `playbooks/`, `traces/`
- **D-66:** All brain files live in `workspace/agent-brain/` — accessible via `/agent/brain/*` API
- **D-67:** Skill format: `skills/<skill-name>/manifest.yaml` with name, description, trigger_patterns (regex), procedure (Markdown body)
- **D-68:** Skills invoked via PydanticAI tool calls (not natural language pattern matching) — agent explicitly calls `agent.invoke_skill(skill_name)`
- **D-69:** Skill curation criteria: recurring pattern + reusable procedure + clear operational gain + justifiable maintenance
- **D-70:** Session summaries stored at `agent-brain/sessions/<session-id>.md`
- **D-71:** Summary triggered via `reflect_agent` job at end of session (async, not blocking)
- **D-72:** Session summary format: ## What happened, ## Key decisions, ## Open questions, ## Next steps
- **D-73:** SOUL.md contains: identity statement, operating principles, communication style, constraints, self-improvement guidelines
- **D-74:** SOUL.md is agent-editable with policy checks (agent.* capabilities apply)
- **D-75:** MEMORY.md contains curated high-value learnings, established patterns, operational heuristics
- **D-76:** Memory consolidation via `consolidate_memory` job — triggered periodically or on explicit request
- **D-77:** Memory curation criteria: recurrence, future utility, temporal stability, reliability, operational impact
- **D-78:** USER.md captures: user preferences, work patterns, context, restrictions, communication style
- **D-79:** Agent updates USER.md proactively after observing user behavior patterns
- **D-80:** User can directly edit USER.md — agent respects user overrides
- **D-81:** Agent can self-improve freely in `agent-brain/` domain (no policy restrictions on agent.* capabilities)
- **D-82:** Changes to `agent-brain/` via `reflect_agent` job — logged but not gated
- **D-83:** Self-improve happens on explicit agent request (not automatic after every session)
- **D-84:** `/agent/brain/*` — read/update SOUL.md, MEMORY.md, USER.md
- **D-85:** `/agent/skills/*` — list skills, invoke skill, create skill
- **D-86:** `/agent/sessions/*` — list session summaries, create session summary
- **D-87:** `/agent/skills/<name>/invoke` — POST with {input} → {output} (skill procedure executed as agent tool)
- **D-88:** `reflect_agent` job processes: session summary + memory consolidation + skill creation from heuristics
- **D-89:** `consolidate_memory` job: reads recent sessions, extracts patterns, updates MEMORY.md if criteria met

### Claude's Discretion
- Specific skill trigger pattern format (simple regex vs full pattern DSL) — use simple regex
- Heuristic-to-skill conversion threshold — defer to implementation (default: 3+ occurrences)
- Session summary length targets — defer to implementation

### Deferred Ideas (OUT OF SCOPE)
- Marketplace of static skill profiles — out of scope for v1
- Agent-to-agent communication protocol — future phase
- Autonomous skill self-creation beyond heuristics — Phase 5 implements trigger, full auto-creation deferred

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| F9-01 | Agent Brain filesystem: SOUL.md, MEMORY.md, USER.md, skills/, heuristics/, reflections/, sessions/, scratchpads/, playbooks/ | Already scaffolded in Phase 1; just needs service layer to read/write |
| F9-02 | Agent identity and constitution (SOUL.md) | Service writes/reads SOUL.md; schema fields: identity, operating_principles, communication_style, constraints, self_improve_guidelines |
| F9-03 | Persistent curated memory (MEMORY.md) | Service manages MEMORY.md with sections for high_value_learnings, patterns_established, operational_heuristics |
| F9-04 | User operational profile (USER.md) | Service manages USER.md with sections for preferences, work_patterns, context, restrictions, communication_style |
| F9-05 | Skills with manifest.yaml and reusable procedures | Skill manifest schema: id, name, version, status, kind, triggers (list), inputs_schema, outputs_schema; body is markdown in SKILL.md |
| F9-06 | Session summaries and traces | Session summary stored at `sessions/<session-id>.md` with D-72 format sections; reflect_agent handler generates them |
| F9-07 | Self-improve within agent domain (free) vs user vault (restricted) | Policy checks apply `agent.*` capabilities; brain domain is unrestricted; vault mutations go through patch pipeline |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydanticai | latest (verify via `npm view pydanticai version`) | Agent runtime, tool calling, structured output | Per D-67 and STACK_DECISION_RECORD §13 — model-agnostic, Pydantic v2 native, RunContext DI |
| pyyaml | already in pyproject.toml | Skill manifest parsing | Required for `manifest.yaml` parsing per D-67 |
| pydantic | already in pyproject.toml | All DTOs, tool input/output schemas | Already project standard |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| git CLI (shell out) | system | Version agent-brain | Already used by GitService; agent-brain IS a git repo (confirmed: workspace/agent-brain is a bare-ish git repo with hooks) |
| uuid | stdlib | Session ID generation | For unique session identifiers |
| pathlib | stdlib | Brain file paths | For constructing paths under workspace/agent-brain |

### Dependencies to Add
```bash
uv add pydanticai
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── api/
│   └── agent.py           # NEW: /agent/brain/*, /agent/skills/*, /agent/sessions/* routes
├── services/
│   └── agent_brain_service.py  # NEW: Brain filesystem operations
│   └── skill_service.py         # NEW: Skill manifest read/invoke
├── agent/
│   └── runtime.py         # NEW: PydanticAI Agent setup with skill tools
│   └── tools.py           # NEW: invoke_skill tool, other brain tools
├── schemas/
│   └── agent.py           # NEW: BrainRead, SkillManifest, SessionSummary, etc.
└── worker/handlers/
    ├── reflect_agent.py    # REPLACE PLACEHOLDER: session summary + skill creation
    └── consolidate_memory.py  # REPLACE PLACEHOLDER: pattern extraction, MEMORY.md update
```

### Pattern 1: PydanticAI Skill Tool via `Tool` Dataclass

**What:** Skills are registered as PydanticAI tools using the `Tool` dataclass with a `prepare` method for dynamic behavior.

**When to use:** When the set of skills changes at runtime (loaded from manifest files).

**Example:**
```python
# src/agent/tools.py
from pydantic import BaseModel, Field
from pydanticai import Tool
from typing import Any

class InvokeSkillInput(BaseModel):
    skill_name: str = Field(description="Name of the skill to invoke")
    input_data: dict = Field(default_factory=dict, description="Input data for the skill")

async def invoke_skill(ctx, skill_name: str, input_data: dict) -> dict:
    """Invoke a skill by name with given input."""
    skill_service = ctx.deps.skill_service  # injected via RunContext
    return await skill_service.invoke_skill(skill_name, input_data)

def make_skill_tool(skill_name: str, manifest: dict) -> Tool:
    """Create a Tool from a skill manifest for dynamic registration."""
    return Tool(
        invoke_skill,
        takes_ctx=True,
        name=f"skill_{skill_name}",
        description=manifest.get("description", ""),
        parameters_schema=InvokeSkillInput,
    )
```

**Source:** PydanticAI docs — `Tool` dataclass with `prepare` parameter for dynamic tool registration, `toolsets` for managing collections

### Pattern 2: PydanticAI Agent with Dynamic `toolsets`

**What:** The PydanticAI `Agent` accepts a `toolsets` argument — a list of `Tool` instances that can be built dynamically from the skill manifests on disk.

**When to use:** When the agent needs to discover and register skills at startup or when skills change.

**Example:**
```python
# src/agent/runtime.py
from pydanticai import Agent
from src.agent.tools import make_skill_tool
from src.services.skill_service import SkillService

class AgentDeps:
    skill_service: SkillService

def build_agent(skill_service: SkillService) -> Agent:
    # Discover all skills from manifests
    skill_tools = []
    for manifest in skill_service.list_skills():
        tool = make_skill_tool(manifest["name"], manifest)
        skill_tools.append(tool)

    return Agent(
        model="anthropic:claude-3-5-sonnet",
        tools=skill_tools,
        deps_type=AgentDeps,
    )
```

**Source:** PydanticAI docs — `toolsets` keyword argument, `Tool` dataclass with `prepare`

### Pattern 3: Session Summary Generation

**What:** At session end, `reflect_agent` handler generates a structured summary from session trace.

**When to use:** End of every agent session (async via job queue).

**Session summary format (per D-72):**
```markdown
# Session Summary — <session-id>

**Date:** YYYY-MM-DD
**Duration:** N minutes

## What happened
[Concise description of session activities]

## Key decisions
- [Decision 1]
- [Decision 2]

## Open questions
- [Question 1]

## Next steps
- [Action item 1]
```

**Source:** D-72 from CONTEXT.md

### Pattern 4: Memory Consolidation

**What:** `consolidate_memory` job reads recent session summaries, extracts recurring patterns using criteria from D-77 (recurrence, future utility, temporal stability, reliability, operational impact), and updates MEMORY.md sections.

**When to use:** Periodic or on explicit request.

**Source:** D-75 to D-77 from CONTEXT.md; SSOT §12.4 memory curation criteria

### Pattern 5: Brain File Read/Write via Service

**What:** Central `AgentBrainService` encapsulates all filesystem operations on `workspace/agent-brain/`.

**When to use:** All API routes and job handlers that need brain files.

**Example:**
```python
# src/services/agent_brain_service.py
from pathlib import Path

class AgentBrainService:
    BRAIN_ROOT = Path("workspace/agent-brain")

    async def read_soul(self) -> dict: ...
    async def write_soul(self, data: dict) -> None: ...
    async def read_memory(self) -> dict: ...
    async def write_memory(self, data: dict) -> None: ...
    async def read_user_profile(self) -> dict: ...
    async def write_user_profile(self, data: dict) -> None: ...
    async def list_sessions(self) -> list[dict]: ...
    async def get_session(self, session_id: str) -> dict: ...
    async def write_session_summary(self, session_id: str, summary: dict) -> None: ...
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Agent runtime framework | Custom LLM tool-calling loop | PydanticAI | Model-agnostic, structured output, RunContext DI, tool validation already solved |
| Skill invocation | Natural language skill matching | Explicit `invoke_skill` PydanticAI tool call | Per D-68; explicit is more reliable and auditable |
| Session summary format | Ad-hoc string formatting | Structured sections with D-72 format | Consistency enables parsing and retrieval |
| Brain file operations | Scattered file I/O | AgentBrainService | Single place to add validation, policy checks, error handling |
| Skill manifest parsing | ad-hoc dict access | Pydantic model for manifest schema | Type safety, validation, IDE support |

## Common Pitfalls

### Pitfall 1: Brain Files Treated as Sovereign (Instead of Derived)
**What goes wrong:** Treating MEMORY.md/SOUL.md as if they are as authoritative as the User Vault notes.
**Why it happens:** The SSOT says brain files are "autonomous but not sovereign over the user." Confusion about what is canonical.
**How to avoid:** Brain files are derived operational state — they inform agent behavior but do not override user vault canonicity. Always log when brain content influences vault mutation decisions.

### Pitfall 2: Skills Without Curatorial Gate
**What goes wrong:** Every heuristic or pattern gets promoted to a skill, causing skill bloat.
**Why it happens:** No enforcement of D-69 curation criteria.
**How to avoid:** Require explicit justification against D-69 criteria before a skill is created. The `reflect_agent` handler should recommend, not auto-promote.

### Pitfall 3: Session Summary Blocking
**What goes wrong:** Reflect runs synchronously at session end, adding latency.
**Why it happens:** Not using the job queue as designed (D-71 says async).
**How to avoid:** Always enqueue `reflect_agent` job rather than calling reflection inline. The handler is the right place for LLM calls.

### Pitfall 4: PydanticAI Deps Not Thread-Safe Across Requests
**What goes wrong:** Agent instance shared across concurrent requests with shared state in deps.
**Why it happens:** Agent with mutable deps passed across concurrent requests.
**How to avoid:** Build fresh `AgentDeps` per request. The agent itself (system prompt, tools) can be shared — deps are request-scoped.

### Pitfall 5: Brain Files Not Versioned
**What goes wrong:** Agent updates brain files but changes are lost or not audited.
**Why it happens:** Not treating agent-brain as a git repo (it already IS one per `workspace/agent-brain/` structure).
**How to avoid:** Use GitService to commit brain changes after write operations. This also satisfies F9-07 self-improve with versioning.

## Code Examples

### Skill Manifest Schema (D-67)

```yaml
# workspace/agent-brain/skills/web-search/manifest.yaml
id: skill-uuid-here
name: web-search
version: 1
status: active
kind: procedure
description: Search the web for information on a given query
triggers:
  - "search.*web"
  - "look.*up.*online"
inputs_schema:
  type: object
  properties:
    query:
      type: string
      description: The search query
  required: [query]
outputs_schema:
  type: object
  properties:
    results:
      type: list
      description: Search results
policy_requirements: []
```

```markdown
# workspace/agent-brain/skills/web-search/SKILL.md
# Web Search Skill

## Procedure

1. Formulate search query from input
2. Execute search using the research tool
3. Return top 5 results with titles and snippets
```

### API Route Pattern (per existing routers like vault.py)

```python
# src/api/agent.py
from fastapi import APIRouter, Depends
from src.services.agent_brain_service import AgentBrainService

router = APIRouter(prefix="/agent", tags=["agent"])
brain_service = AgentBrainService()

@router.get("/brain/soul")
async def get_soul():
    return await brain_service.read_soul()

@router.put("/brain/soul")
async def update_soul(data: SoulUpdate):
    return await brain_service.write_soul(data)

@router.get("/skills")
async def list_skills():
    return await brain_service.list_skills()

@router.post("/skills/{skill_name}/invoke")
async def invoke_skill(skill_name: str, input_data: dict):
    return await brain_service.invoke_skill(skill_name, input_data)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Agent memory in vector DB | Agent memory as Markdown files in brain/ | Pre-project (architectural decision) | Files are sovereign, derivable, versioned |
| Skills as prompt templates | Skills as manifest.yaml + markdown procedure + PydanticAI tool call | D-67, D-68 (Phase 5 context) | Type-safe, auditable, versioned |
| Session memory via embedding search | Session summaries as Markdown with FTS | D-70 to D-72 | Human-readable, rebuildable from raw traces |
| Auto self-improvement | Explicit reflect_agent job request | D-83 | Controlled, auditable, no surprise mutations |

**Deprecated/outdated:**
- None specific to this phase — the SSOT and stack decisions already established the right model.

## Open Questions

1. **How does the agent get its initial SOUL.md at workspace creation?**
   - What we know: SOUL.md template exists at `workspace/agent-brain/SOUL.md` with placeholder sections.
   - What's unclear: Who/what populates the initial content — a setup wizard, first-run prompt, or LLM generation from a user description?
   - Recommendation: Use a simple editable template with guidance comments; the agent can refine it over time.

2. **Should brain files be committed to git automatically or on explicit reflect?**
   - What we know: `workspace/agent-brain/` is already a git repo; D-82 says changes go via reflect_agent job.
   - What's unclear: Should every brain write auto-commit, or batch commits on reflect_agent completion?
   - Recommendation: Auto-commit on every successful brain write operation with a descriptive message pattern `brain: update <file> — <reason>`.

3. **What is the session trace format used by `reflect_agent`?**
   - What we know: D-70 says session summaries stored at `sessions/<session-id>.md`. The trace (raw events) vs summary (curated) distinction is in SSOT §26.2.
   - What's unclear: What is the format of the "trace" that `reflect_agent` consumes? Is it stored in `traces/`?
   - Recommendation: Store raw conversation turns in `traces/<session-id>.jsonl`; the reflect_agent job reads these to produce the summary.

4. **Should `invoke_skill` tool use the LLM to interpret the markdown procedure, or execute it programmatically?**
   - What we know: D-67 says procedure body is Markdown. D-68 says "skill procedure executed as agent tool."
   - What's unclear: Is the markdown procedure executed as a prompt to the LLM, or parsed into steps?
   - Recommendation: Execute as LLM prompt — pass the markdown procedure body as a system prompt fragment to the LLM with the input context. Simpler and more flexible.

## Environment Availability

> Step 2.6: SKIPPED (no external dependencies identified beyond Python packages already in project)

The phase uses only Python stdlib (`pathlib`, `uuid`), project-standard packages (pyyaml, pydantic, fastapi), and PydanticAI (to be added). No external tools, services, or CLIs are required beyond those already used by the project.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already in pyproject.toml) |
| Config file | pytest.ini_options in pyproject.toml |
| Quick run command | `pytest tests/test_agent_brain.py -x` |
| Full suite command | `pytest tests/ -x --cov=src/agent --cov=src/services --cov=src/api/agent` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| F9-01 | Brain filesystem structure exists and is readable/writable | unit | `pytest tests/test_agent_brain_service.py::test_brain_filesystem_structure` | NO |
| F9-02 | SOUL.md read/write via AgentBrainService | unit | `pytest tests/test_agent_brain_service.py::test_soul_read_write` | NO |
| F9-03 | MEMORY.md read/write with correct sections | unit | `pytest tests/test_agent_brain_service.py::test_memory_sections` | NO |
| F9-04 | USER.md read/write with correct sections | unit | `pytest tests/test_agent_brain_service.py::test_user_profile_sections` | NO |
| F9-05 | Skill manifest parsing, skill list, skill invocation | unit | `pytest tests/test_skill_service.py -x` | NO |
| F9-06 | Session summary generation in reflect_agent handler | unit | `pytest tests/test_reflect_agent.py -x` | NO |
| F9-07 | Policy check on brain mutation (logged but not gated) | unit | `pytest tests/test_agent_policy.py -x` | NO |

### Sampling Rate
- **Per task commit:** `pytest tests/test_agent_brain/ -x -q`
- **Per wave merge:** `pytest tests/ -x -q --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_agent_brain_service.py` — covers F9-01, F9-02, F9-03, F9-04
- [ ] `tests/test_skill_service.py` — covers F9-05
- [ ] `tests/test_reflect_agent.py` — covers F9-06
- [ ] `tests/test_agent_policy.py` — covers F9-07
- [ ] `tests/conftest.py` — shared fixtures for brain service, skill service
- [ ] Framework install: `uv add pydanticai` — if not detected, add to pyproject.toml

*(If no gaps: "None — existing test infrastructure covers all phase requirements")*

## Sources

### Primary (HIGH confidence)
- D-65 through D-89 from `.planning/phases/05-agent-brain/05-CONTEXT.md` — locked decisions for this phase
- SSOT_Knowledge_OS_V1.md §12 (Agent Brain) — mission, artifacts, rules, memory curation, skill curation
- STACK_DECISION_RECORD_Knowledge_OS_Core.md §13 (Agent framework / LLM orchestration) — PydanticAI recommendation with Hermes conceptual reference
- PydanticAI docs https://ai.pydantic.dev/tools/ — Tool dataclass, toolsets, dynamic registration, prepare parameter

### Secondary (MEDIUM confidence)
- PydanticAI docs https://ai.pydantic.dev/ — Agent architecture, RunContext dependency injection, tool validation

### Tertiary (LOW confidence)
- None — all critical decisions are from primary sources or already verified

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — PydanticAI confirmed in STACK_DECISION_RECORD, all other tech already in project
- Architecture: HIGH — decisions D-65 to D-89 fully specify the architecture; PydanticAI patterns from docs
- Pitfalls: HIGH — based on established patterns from SSOT and known PydanticAI behavior

**Research date:** 2026-03-31
**Valid until:** 2026-04-30 (PydanticAI is stable; Phase 5 decisions are locked)
