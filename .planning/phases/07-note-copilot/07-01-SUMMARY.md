# Phase 7 Plan 07-01: Backend Core + Frontend Panel

**Full-stack copilot: CopilotService + 7 API endpoints + 3-tab React panel**

---

## Performance

- **Started:** 2026-04-01
- **Status:** PLANNED (not yet executed)
- **Tasks:** 7
- **Files created (backend):** 2 (`src/schemas/copilot.py`, `src/services/copilot_service.py`)
- **Files modified (backend):** 1 (`src/api/copilot.py`)
- **Files created (frontend):** 5 (CopilotPanel, CopilotChat, CopilotSuggestions, CopilotProposal, api/copilot.ts)
- **Files modified (frontend):** 2 (uiStore.ts, NoteView.tsx)

## Goals

Wave 1 establishes the full copilot stack:
1. **Backend:** Pydantic schemas + CopilotService + full API endpoints
2. **Frontend:** 3-tab copilot panel (Chat/Suggestions/Proposal) integrated into NoteView

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UX container | Side panel (right of NoteView) | Less disruptive, always accessible |
| Chat mode | Stateless | Scope = note, not conversation |
| Agent | Separate copilot agent | Different system prompt, no brain memory |
| Mutation | Proposal-first (Exchange Zone) | Sovereignty — human approves before edit |
| Latency | Sync HTTP | v1 acceptable, job queue premature |
| Copilot state | Session-only (no Zustand persist) | No need to survive page reload |

## Architecture

```
Frontend                      Backend
─────────                     ───────
CopilotPanel ──────────────► CopilotService
  ├─ CopilotChat ──────────► /copilot/chat/{note_id}
  ├─ CopilotSuggestions ────► /copilot/explain|summarize|...
  └─ CopilotProposal ───────► /copilot/propose-patch/{note_id}
                                  │
                              ProposalService
                                   │
                              Exchange Zone (Git)
```

## Requirements Covered

| ID | Requirement | Status |
|----|-------------|--------|
| F11-01 | Copilot panel per-note | Wave 1 |
| F11-02 | Explain action | Wave 1 |
| F11-03 | Summarize action | Wave 1 |
| F11-04 | Suggest links | Wave 1 |
| F11-05 | Suggest tags | Wave 1 |
| F11-06 | Suggest structure | Wave 1 |
| F11-07 | Propose patch | Wave 1 |
| F11-08 | UX mode distinction | Wave 1 |
| F11-09 | Session isolation (stateless) | Wave 1 |
| F11-10 | Error handling | Wave 1 |
| F11-11 | Loading states | Wave 1 |

## Completed

Phase 7 (Note Copilot) is fully complete (3 waves):

| Wave | Commit | Content |
|------|--------|---------|
| Wave 1 | f528b3b | Full copilot (backend + frontend) |
| Wave 2 | f2354a6 | Bug fixes + structlog + 9 unit tests |
| Wave 3 | f1a184d | Async propose_patch via job queue + Playwright E2E |

**Next: Phase 8 — Research Runtime**
