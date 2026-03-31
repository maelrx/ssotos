---
phase: 04-backend-api-services-jobs
plan: 04-03
subsystem: jobs
tags: [postgres, async, worker, queue, structlog, sse]

# Dependency graph
requires:
  - phase: 04-01
    provides: Job and JobEvent SQLAlchemy models, database schema with 12 tables
  - phase: 04-02
    provides: FastAPI app factory, broadcast_job_event() in SSE endpoint
provides:
  - Postgres-backed job queue with SELECT FOR UPDATE SKIP LOCKED atomic claiming
  - JobProcessor dispatching to 8 handler types
  - Worker main loop with graceful shutdown and poll-based job polling
  - Retry logic with exponential backoff up to max_attempts
affects:
  - Phase 5 (Agent Brain) - reflect_agent and consolidate_memory handlers
  - Phase 6 (Retrieval) - index_note, reindex_scope, generate_embeddings handlers
  - Phase 8 (Research Runtime) - research_job and parse_source handlers

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FOR UPDATE SKIP LOCKED for atomic row claiming"
    - "Handler registry pattern (HANDLERS dict)"
    - "Polling worker loop with configurable interval"
    - "Graceful shutdown via SIGTERM/SIGINT signal handlers"

key-files:
  created:
    - src/worker/queue.py
    - src/worker/processor.py
    - src/worker/main.py
    - src/worker/handlers/__init__.py
    - src/worker/handlers/index_note.py
    - src/worker/handlers/reindex_scope.py
    - src/worker/handlers/generate_embeddings.py
    - src/worker/handlers/research_job.py
    - src/worker/handlers/parse_source.py
    - src/worker/handlers/apply_patch_bundle.py
    - src/worker/handlers/reflect_agent.py
    - src/worker/handlers/consolidate_memory.py
  modified: []

key-decisions:
  - "Used JobEvent.extra field (not metadata) per actual model column name"
  - "JobClaim dataclass holds both job and db session for handler processing"
  - "All handlers are placeholder stubs with notes indicating which phase implements full logic"

patterns-established:
  - "Worker module: queue.py (claims), processor.py (dispatches), main.py (entry point)"
  - "Handler per job type in handlers/ subdirectory"
  - "HANDLERS registry dict maps job_type string to async handler function"

requirements-completed: [F13-01, F13-02, F13-03, F13-04]

# Metrics
duration: 148s
completed: 2026-03-31
---

# Phase 04-03: Worker Runtime Summary

**Postgres-backed job queue with FOR UPDATE SKIP LOCKED claiming, 8 placeholder handlers, and polling worker loop with graceful shutdown**

## Performance

- **Duration:** 148s (~2.5 min)
- **Started:** 2026-03-31T19:25:20Z
- **Completed:** 2026-03-31T19:27:48Z
- **Tasks:** 3
- **Files modified:** 13 created

## Accomplishments
- JobQueue with atomic Postgres row claiming using FOR UPDATE SKIP LOCKED
- JobProcessor that dispatches jobs to handlers based on job_type
- All 8 job type handlers registered in HANDLERS dict
- Worker main loop with graceful SIGTERM/SIGINT shutdown
- Retry logic with exponential backoff, all state changes broadcast via SSE
- Job events recorded in job_events table on every state transition

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Postgres-backed job queue with row claiming** - `eb58d68` (feat)
2. **Task 2: Create job handlers for all 8 job types** - `eb58d68` (feat)
3. **Task 3: Create job processor and worker main loop** - `eb58d68` (feat)

**Plan metadata:** `eb58d68` (docs: complete plan)

## Files Created/Modified
- `src/worker/__init__.py` - Worker module exports
- `src/worker/queue.py` - JobQueue with claim(), complete(), fail(), record_progress()
- `src/worker/processor.py` - JobProcessor with process_one() and run() loop
- `src/worker/main.py` - run_worker() entry point with structlog config
- `src/worker/handlers/__init__.py` - HANDLERS registry dict
- `src/worker/handlers/index_note.py` - Placeholder handler (Phase 6)
- `src/worker/handlers/reindex_scope.py` - Placeholder handler (Phase 6)
- `src/worker/handlers/generate_embeddings.py` - Placeholder handler (Phase 6)
- `src/worker/handlers/research_job.py` - Placeholder handler (Phase 8)
- `src/worker/handlers/parse_source.py` - Placeholder handler (Phase 8)
- `src/worker/handlers/apply_patch_bundle.py` - Placeholder handler (Phase 2 integration)
- `src/worker/handlers/reflect_agent.py` - Placeholder handler (Phase 5)
- `src/worker/handlers/consolidate_memory.py` - Placeholder handler (Phase 5)

## Decisions Made

None - plan executed exactly as specified.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Worker runtime is complete and ready to process jobs from the Postgres queue
- All 8 handler placeholders are registered and will return success-like results
- Full implementation of handlers will come in their respective phases:
  - Phase 5: reflect_agent, consolidate_memory
  - Phase 6: index_note, reindex_scope, generate_embeddings
  - Phase 8: research_job, parse_source
  - Phase 2 integration: apply_patch_bundle

---
*Phase: 04-backend-api-services-jobs*
*Completed: 2026-03-31*
