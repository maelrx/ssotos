---
phase: 05
slug: 05-agent-brain
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-31
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | pytest.ini_options in pyproject.toml |
| **Quick run command** | `pytest tests/test_agent_brain_service.py tests/test_skill_service.py tests/test_reflect_agent.py tests/test_agent_policy.py -x -q` |
| **Full suite command** | `pytest tests/ -x --cov=src/schemas/agent --cov=src/services/agent_brain_service --cov=src/services/skill_service --cov=src/api/agent --cov=src/agent --cov=src/worker/handlers/reflect_agent --cov=src/worker/handlers/consolidate_memory --tb=short` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_agent_brain_service.py tests/test_skill_service.py tests/test_reflect_agent.py tests/test_agent_policy.py -x -q`
- **After every plan wave:** Run `pytest tests/ -x --cov=src/agent --cov=src/services --cov=src/api/agent --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | F9-01, F9-02, F9-03, F9-04, F9-05 | unit | `ruff check pyproject.toml src/schemas/agent.py src/services/agent_brain_service.py src/services/skill_service.py && python -c "from src.schemas.agent import SoulSection,SoulUpdate,SoulResponse,MemorySection,MemoryUpdate,MemoryResponse,UserProfileSection,UserProfileUpdate,UserProfileResponse,SkillManifest,SkillResponse,SkillListResponse,SkillInvokeRequest,SkillInvokeResponse,SessionSummary,SessionResponse,SessionListResponse; print('OK')"` | W0 gap | pending |
| 05-01-02 | 01 | 1 | F9-02, F9-03, F9-04 | unit | `ruff check src/schemas/agent.py && python -c "from src.schemas.agent import SoulSection,SoulUpdate,SoulResponse,MemorySection,MemoryUpdate,MemoryResponse,UserProfileSection,UserProfileUpdate,UserProfileResponse; print('OK')"` | W0 gap | pending |
| 05-01-03 | 01 | 1 | F9-02, F9-03, F9-04 | unit | `ruff check src/services/agent_brain_service.py && python -c "from src.services.agent_brain_service import AgentBrainService; print('OK')"` | W0 gap | pending |
| 05-01-04 | 01 | 1 | F9-05 | unit | `ruff check src/services/skill_service.py && python -c "from src.services.skill_service import SkillService; print('OK')"` | W0 gap | pending |
| 05-02-01 | 02 | 2 | F9-01, F9-02, F9-03, F9-04, F9-07 | unit | `ruff check src/api/agent.py && grep -c "policy_service.check" src/api/agent.py && grep -c "job_service.enqueue" src/api/agent.py` | W0 gap | pending |
| 05-02-02 | 02 | 2 | F9-01 | unit | `ruff check src/agent/runtime.py && python -c "from src.agent.runtime import build_agent,AgentDeps; print('OK')"` | W0 gap | pending |
| 05-02-03 | 02 | 2 | F9-05 | unit | `ruff check src/agent/tools.py && python -c "from src.agent.tools import invoke_skillTool,make_skill_tool,get_all_skill_tools; print('OK')"` | W0 gap | pending |
| 05-02-04 | 02 | 2 | F9-01 | unit | `ruff check src/app.py src/agent/__init__.py && grep -l "agent.router" src/app.py && python -c "from src.agent import build_agent,AgentDeps,invoke_skillTool,make_skill_tool,get_all_skill_tools; print('OK')"` | W0 gap | pending |
| 05-03-01 | 03 | 3 | F9-06 | unit | `ruff check src/worker/handlers/reflect_agent.py && grep -c "_process_brain_mutations" src/worker/handlers/reflect_agent.py && grep -c "brain_mutations" src/worker/handlers/reflect_agent.py` | W0 gap | pending |
| 05-03-02 | 03 | 3 | F9-03, F9-06 | unit | `ruff check src/worker/handlers/consolidate_memory.py && grep -c "MEMORY_CURATION_CRITERIA" src/worker/handlers/consolidate_memory.py && grep -c "temporal_stability" src/worker/handlers/consolidate_memory.py` | W0 gap | pending |
| 05-03-03 | 03 | 3 | F9-07 | unit | `grep -c "self-improve" src/api/agent.py && grep -c "brain_mutations" src/api/agent.py && ruff check src/api/agent.py` | W0 gap | pending |

*Status: pending / green / red*

---

## Requirement Coverage Map

| Requirement | Plan | Behavior | Automated Test Command | Wave 0 File |
|-------------|------|----------|------------------------|-------------|
| F9-01 | 01, 02 | Brain filesystem structure (workspace/agent-brain/, dirs exist) | `pytest tests/test_agent_brain_service.py::test_brain_filesystem_structure -x` | tests/test_agent_brain_service.py |
| F9-02 | 01, 02 | SOUL.md read/write via AgentBrainService | `pytest tests/test_agent_brain_service.py::test_soul_read_write -x` | tests/test_agent_brain_service.py |
| F9-03 | 01, 02, 03 | MEMORY.md read/write with correct sections | `pytest tests/test_agent_brain_service.py::test_memory_sections -x` | tests/test_agent_brain_service.py |
| F9-04 | 01, 02 | USER.md read/write with correct sections | `pytest tests/test_agent_brain_service.py::test_user_profile_sections -x` | tests/test_agent_brain_service.py |
| F9-05 | 01, 02 | Skill manifest parsing, list, invocation | `pytest tests/test_skill_service.py -x` | tests/test_skill_service.py |
| F9-06 | 03 | Session summary generation in reflect_agent handler | `pytest tests/test_reflect_agent.py -x` | tests/test_reflect_agent.py |
| F9-07 | 02, 03 | Policy check on brain mutation + self-improve endpoint | `pytest tests/test_agent_policy.py -x` | tests/test_agent_policy.py |

---

## Wave 0 Requirements

- [ ] `tests/test_agent_brain_service.py` — covers F9-01, F9-02, F9-03, F9-04 (brain filesystem structure, soul/memory/user read/write)
- [ ] `tests/test_skill_service.py` — covers F9-05 (manifest parsing, skill list, skill invoke)
- [ ] `tests/test_reflect_agent.py` — covers F9-06 (session summary generation, brain_mutations processing)
- [ ] `tests/test_agent_policy.py` — covers F9-07 (policy check on brain mutations, self-improve endpoint)
- [ ] `tests/conftest.py` — shared fixtures (brain_service, skill_service, tmp_brain_dir)
- [ ] Framework install: `uv add pydanticai` — verify in pyproject.toml before running tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Brain filesystem visible in workspace/agent-brain/ directory structure | F9-01 | Filesystem inspection requires human verification of directory layout | Run `ls -la workspace/agent-brain/` and verify dirs: SOUL.md, MEMORY.md, USER.md, skills/, heuristics/, reflections/, sessions/, scratchpads/, playbooks/, traces/ |
| Skill invocation produces correct output from SKILL.md procedure | F9-05 | Markdown procedure execution requires LLM interpretation | POST /agent/skills/{skill_name}/invoke with test input, verify output format matches outputs_schema |
| PydanticAI agent builds with skill tools registered | F9-01, F9-05 | Agent runtime initialization requires runtime verification | Verify `build_agent(skill_service)` completes without error and agent.tools is populated |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter (requires Wave 0 test files to exist)

**Approval:** pending
