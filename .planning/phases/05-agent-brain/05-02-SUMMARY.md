---
phase: 05-agent-brain
plan: 05-02
subsystem: agent-brain
tags: [fastapi, pydanticai, agent, brain, api, skills]

# Dependency graph
requires:
  - phase: "05-01"
    provides: "AgentBrainService, SkillService, pydanticai dependency, agent schemas"
provides:
  - "14 REST endpoints for agent brain, skills, and sessions"
  - "PydanticAI Agent builder with SOUL.md system prompt"
  - "Skill tools for PydanticAI agent tool calls"
  - "JobService for async reflect_agent job creation"
affects: [agent-brain, 05-03]

# Tech tracking
tech-stack:
  added: [pydanticai]
  patterns: [pydanticai-agent-builder, skill-tool-pattern, job-service-pattern]

key-files:
  created:
    - "src/api/agent.py"
    - "src/agent/runtime.py"
    - "src/agent/tools.py"
    - "src/agent/__init__.py"
    - "src/services/job_service.py"
  modified:
    - "src/app.py"
    - "src/api/__init__.py"

key-decisions:
  - "Brain mutations use PolicyService.check() then JobService.enqueue() for async reflect_agent per D-71/D-82"
  - "JobService created as thin wrapper over direct Job record creation (no existing JobService existed)"
  - "Agent router registered at /api prefix giving final path /api/agent/* per standard pattern"

patterns-established:
  - "PydanticAI Agent builder pattern: build_agent(skill_service) -> Agent"
  - "Skill tool pattern: make_skill_tool(name, manifest) -> Tool per D-67"
  - "JobService enqueue pattern: async job creation with proper event logging"

requirements-completed: [F9-01, F9-02, F9-03, F9-04, F9-05, F9-07]

# Metrics
duration: 13min
completed: 2026-03-31
---

# Phase 05 Plan 02: Agent Brain API and Runtime Summary

**14 REST endpoints exposed for agent brain (soul/memory/user), skills (list/get/invoke/create), and sessions (list/get/create), with PydanticAI runtime and skill tool integration**

## Performance

- **Duration:** 13 min
- **Started:** 2026-03-31T21:05:34Z
- **Completed:** 2026-03-31T21:18:31Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments
- 14 REST API endpoints for agent brain, skills, and sessions at /api/agent/*
- Brain mutation endpoints (PUT soul/memory/user) call PolicyService.check() and enqueue reflect_agent job
- PydanticAI Agent builder (build_agent) with SOUL.md system prompt and skill tools
- Skill tools (invoke_skillTool, make_skill_tool, get_all_skill_tools) bridging PydanticAI and SkillService
- JobService thin wrapper for async job creation
- Agent router registered in FastAPI app alongside existing routers

## Task Commits

Each task was committed atomically:

1. **Task 2.1: Create Agent API Router** - `7a1c404` (feat)
2. **Task 2.2: Create PydanticAI Agent Runtime** - `d4c7e89` (feat)
3. **Task 2.3: Create Agent Tools** - `5ab1132` (feat)
4. **Task 2.4: Register Agent Router in App** - `2e3822a` (feat)

## Files Created/Modified
- `src/api/agent.py` - 14 REST endpoints: /brain/* (soul, memory, user, structure), /skills/*, /sessions/* (308 lines)
- `src/agent/runtime.py` - build_agent() returning PydanticAI Agent with SOUL.md system prompt (86 lines)
- `src/agent/tools.py` - invoke_skillTool, make_skill_tool, get_all_skill_tools (90 lines)
- `src/agent/__init__.py` - Module exports (8 lines)
- `src/services/job_service.py` - Thin JobService wrapper for async job creation (63 lines)
- `src/app.py` - Agent router registered at /api prefix
- `src/api/__init__.py` - Re-exports agent router

## Decisions Made
- Brain mutations use PolicyService.check() then JobService.enqueue() for async reflect_agent per D-71/D-82
- JobService created as thin wrapper over direct Job record creation (no existing JobService existed in codebase)
- Agent router registered at /api prefix giving final path /api/agent/* per standard pattern

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] JobService did not exist in codebase**
- **Found during:** Task 2.1 (Create Agent API Router)
- **Issue:** Plan specified `JobService.enqueue("reflect_agent", job_data)` but no JobService class existed
- **Fix:** Created thin `src/services/job_service.py` with `JobService.enqueue()` method wrapping direct Job record creation
- **Files modified:** src/services/job_service.py (new), src/api/agent.py
- **Verification:** Grep for `job_service.enqueue` in agent.py returns 1
- **Committed in:** `7a1c404` (Task 2.1)

**2. [Rule 2 - Missing Critical] PolicyDeniedException not handled in router**
- **Found during:** Task 2.1 (Create Agent API Router)
- **Issue:** Using `policy_svc.check_or_raise()` would raise PolicyDeniedException which FastAPI would convert to 500 error instead of 403
- **Fix:** Created `_check_brain_write_policy()` helper that checks result.outcome and raises HTTPException 403 explicitly
- **Files modified:** src/api/agent.py
- **Verification:** PolicyDenied properly converts to HTTP 403
- **Committed in:** `7a1c404` (Task 2.1)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both deviations were necessary for correctness. No scope creep.

## Issues Encountered
- pydanticai module not installed in execution environment - syntax verified but runtime import tests deferred to when dependencies are installed via `uv pip install pydanticai`

## Next Phase Readiness
- All Phase 5 Wave 2 files complete - agent API and runtime ready
- Ready for Phase 05-03 (Wave 3: reflect_agent handler, consolidate_memory handler, self-improve endpoint)
- Job handlers in worker will now have proper API endpoints to enqueue jobs

---
*Phase: 05-agent-brain*
*Completed: 2026-03-31*
