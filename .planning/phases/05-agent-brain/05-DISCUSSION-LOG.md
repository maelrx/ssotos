# Phase 5: Agent Brain - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 05-agent-brain
**Areas discussed:** Skill Manifest Format, Skill Invocation, Session Summary Format, Self-Improve Workflow, Brain API Surface
**Mode:** Auto (all gray areas auto-selected with documented defaults)

---

## Skill Manifest Format

| Option | Description | Selected |
|--------|-------------|----------|
| manifest.yaml with trigger_patterns | Structured YAML with name, description, trigger regex, procedure body | ✓ |
| JSON schema | More rigid, less human-readable | |
| Markdown frontmatter | Simpler but less structured | |

**User's choice:** manifest.yaml (auto-selected — follows Phase 1 precedent of YAML frontmatter for structured metadata)

---

## Skill Invocation

| Option | Description | Selected |
|--------|-------------|----------|
| PydanticAI tool calls | Agent explicitly calls invoke_skill tool — predictable, testable | ✓ |
| Natural language pattern matching | Agent interprets user intent — flexible but unpredictable | |
| Hybrid (tool + NL) | Both mechanisms — adds complexity | |

**User's choice:** PydanticAI tool calls (auto-selected — most reliable, matches Phase 4's tool-call pattern)

---

## Session Summary Format

| Option | Description | Selected |
|--------|-------------|----------|
| Structured sections | ## What happened, ## Key decisions, ## Open questions, ## Next steps | ✓ |
| Free-form narrative | Agent writes natural summary | |
| Bullet-point highlights | Timestamped event list | |

**User's choice:** Structured sections (auto-selected — matches SOUL/MEMORY/USER template pattern established in Phase 1)

---

## Self-Improve Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| On explicit request only | Agent requests improvement after significant learning | ✓ |
| Automatic after every session | Always writes back after session | |
| Periodic batch | Weekly consolidation runs | |

**User's choice:** On explicit request (auto-selected — safer, avoids agent overwrite cycles)

---

## Brain API Surface

| Option | Description | Selected |
|--------|-------------|----------|
| /agent/brain/*, /agent/skills/*, /agent/sessions/* | Three resource groups | ✓ |
| Single /agent/* flat namespace | Simpler but less organized | |
| Separate /brain, /skills, /sessions top-level | More REST-aligned but偏离 existing pattern | |

**User's choice:** Three resource groups under /agent/* (auto-selected — follows Phase 4 router pattern)

---

## Claude's Discretion

All gray areas selected with recommended defaults from SSOT/PRD documentation and Phase 1 precedent.
No user discretion required — decisions already documented.

## Deferred Ideas

None — discussion stayed within phase scope.
