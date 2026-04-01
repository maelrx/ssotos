# Phase 7 Discussion Log

## 2026-04-01 — UX Design Decision: Side Panel vs Modal

**Question:** Should the copilot panel be a side panel or a modal?

**Decision:** Side panel (right side of NoteView).

**Rationale:**
- Less disruptive — doesn't block the note being read
- Always accessible when viewing a note
- Easier to toggle on/off without leaving flow
- Modal would require explicit close action and would interrupt reading

**Alternatives considered:**
- Modal: More attention-grabbing but interrupts reading flow
- Separate route (/note/:id/copilot): Best for focus, but requires navigation

---

## 2026-04-01 — Architecture Decision: Separate Copilot Agent

**Question:** Should the copilot use the same PydanticAI agent as the general agent brain (`build_agent()`)?

**Decision:** Separate copilot-specific PydanticAI agent with different system prompt.

**Rationale:**
- The general agent has a long-term memory/skill context that is inappropriate for per-note assistance
- Copilot should be scoped to the note content only (stateless)
- A different system prompt keeps the copilot identity focused: "You are a note assistant"
- Sharing skill tools is still possible (SkillsService.list_skills())

**Concern:** Code duplication — but acceptable for v1. Can be refactored later to share agent builder logic.

---

## 2026-04-01 — Mutation Strategy: Proposal-First

**Question:** Should "Propose Patch" directly edit the note or create a proposal?

**Decision:** Create a GitService Proposal in the Exchange Zone.

**Rationale (per CLAUDE.md principles):**
- "Policy-first: nenhuma ferramenta decide sozinha se pode mutar domínio sensível"
- The Exchange Zone already exists from Phase 2
- PatchService already exists and can generate diffs
- User must approve before any mutation — this is the core sovereignty principle
- The UX clearly shows this is a "proposal" not a direct edit (F11-08)

---

## 2026-04-01 — Chat Mode: Stateless

**Question:** Should the chat mode maintain conversation history (like a chatbot)?

**Decision:** Stateless — each chat message is independent, no memory between turns.

**Rationale:**
- The copilot is about the NOTE, not about the conversation
- Persistent chat memory would be confusing (which note is this about?)
- If user wants to discuss the note, each turn should be self-contained
- This simplifies implementation significantly
- Future: could add optional context from agent brain session history

---

## 2026-04-01 — Sync vs Async Endpoints

**Question:** Should copilot endpoints be synchronous (FastAPI HTTP) or asynchronous (job queue)?

**Decision:** Synchronous for v1.

**Rationale:**
- All actions are under 30s even for large notes
- Simpler implementation — no job queue complexity
- Frontend can show loading states
- Phase 8 (Research Runtime) will have async jobs anyway — keep them separate
- "Premature optimization is the root of all evil" — sync is fine until proven otherwise

**Note:** `propose_patch` could be slower (LLM generating diff) but still acceptable under 30s.
