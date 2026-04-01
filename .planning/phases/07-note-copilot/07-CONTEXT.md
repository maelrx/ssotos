# Phase 7 Context: Note Copilot

## Problem Statement

The Agent Brain (Phase 5) gave the agent memory and skills. The Retrieval layer (Phase 6) gave the system knowledge. But the user has no direct "AI assistance" surface on individual notes. The first "magic" moment — per-note AI that suggests improvements without breaking sovereignty.

## Key Insight: Sovereignty-Preserving AI

The Note Copilot is NOT a chat interface that edits notes directly. Every mutation goes through the Exchange Zone (Phase 2). The AI:
- **Explains/Summarizes** — reads note, returns text (no mutation)
- **Suggests** — reads note + context, returns recommendations (no mutation)
- **Proposes** — reads note + context, generates a diff → creates a GitService Proposal in Exchange Zone (user approves before mutation)

## Three UX Modes

1. **Chat (conversation)** — free-form Q&A about the note. Not a full chatbot; scoped to the open note. No memory between turns (stateless).
2. **Suggestion (recommendation)** — user clicks action button (Explain, Summarize, Suggest Links, etc.). Returns a structured card. No mutation.
3. **Proposal (patch-to-approve)** — user requests a patch. AI generates a diff. A GitService Proposal is created. User reviews in Exchange Zone and approves/rejects.

## UX Design Decision: Side Panel

The copilot panel lives as a **right-side panel** on NoteView, toggleable via toolbar button. This is:
- Less disruptive than a modal
- Always accessible when viewing a note
- Can be collapsed to focus on reading

Visual distinction:
- Chat tab: conversational UI (chat bubbles)
- Suggestions tab: card-based UI (action results)
- Proposal tab: diff view (unified diff format)

## Backend Architecture

### CopilotService

A new service that coordinates between:
- `RetrievalService` — for building context packs (note + neighbors + provenance)
- `AgentBrainService` — for reading SOUL.md to build system prompt
- `GitService` / `ProposalService` — for creating patches (Proposal mode)
- PydanticAI agent — for generating responses

Each action (explain, summarize, suggest-links, etc.) maps to a PydanticAI tool or structured output call.

### Per-Action Design

| Action | Method | Output | Mutation? |
|--------|--------|--------|-----------|
| Explain | RetrievalService context + PydanticAI | Markdown explanation | No |
| Summarize | RetrievalService context + PydanticAI | Markdown summary | No |
| Suggest links | RetrievalService hybrid search + PydanticAI | List of {note_path, reason} | No |
| Suggest tags | Note content analysis + PydanticAI | List of tag strings | No |
| Suggest structure | Note content analysis + PydanticAI | Structured improvement list | No |
| Propose patch | Note content + PydanticAI generates diff | Git diff string → Proposal | Yes (Proposal) |

### Patch Generation Flow (Propose Patch)

1. User clicks "Propose Patch", enters change description
2. `CopilotService.propose_patch()` calls PydanticAI with note content + change description
3. PydanticAI returns structured diff/patch
4. `ProposalService.create_proposal()` writes to Exchange Zone
5. Proposal appears in Exchange Zone UI for user approval
6. On approval → GitService applies patch to vault

## Reference: Existing Patterns

- `src/agent/runtime.py` — PydanticAI agent builder with SOUL.md system prompt
- `src/services/retrieval_service.py` — `build_context_pack()` for note context
- `src/services/agent_brain_service.py` — brain file CRUD
- `src/api/copilot.py` — stub endpoints (4 actions)
- `src/api/exchange.py` — ProposalService, PatchService reference

## Open Questions

1. Should copilot actions be synchronous (FastAPI HTTP) or async (job queue)?
   - Explain/Summarize: sync is fine (fast)
   - Propose patch: could be async (slower LLM call), but for v1 sync is acceptable

2. Should the PydanticAI agent be the same `build_agent()` or a separate copilot-specific agent?
   - Separate agent with copilot-specific system prompt (different identity/scope)
   - Shares skill tools from SkillService

3. How does the frontend toggle the copilot panel?
   - Add `copilotPanelOpen` to uiStore
   - Add `CopilotPanel` component that slides in from right
   - NoteView already has a MetadataPanel on the right — copilot panel could replace or coexist
