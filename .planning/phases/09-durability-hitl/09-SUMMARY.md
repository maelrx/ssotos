# Phase 9: Durability / HITL — Summary

**Phase:** 09-durability-hitl
**Status:** Planned
**Created:** 2026-04-01

---

## Overview

Add retries with exponential backoff, checkpoint/resume, and approval-aware execution — making the system robust for real workloads.

---

## Requirements Covered

| ID | Requirement | Plan |
|----|-------------|------|
| F13-01 | Postgres-backed job queue with row claiming | Already done (Phase 4) |
| F13-02 | Job types: index_note, reindex_scope, etc. | Already done (Phase 4) |
| F13-03 | Job status tracking with events | Already done (Phase 4) |
| F13-04 | Retries for idempotent steps | Refinement in Wave 1 |

### New Requirements (Phase 9)

| ID | Requirement | Plan |
|----|-------------|------|
| F13-05 | Exponential backoff on retry | Wave 1 |
| F13-06 | Checkpoint/resume for long-running jobs | Wave 1 |
| F13-07 | Approval-aware job execution | Wave 2 |
| F13-08 | Job idempotency verification | Wave 3 |

---

## Key Files to Create

### Backend

| File | Purpose |
|------|---------|
| `src/schemas/approval.py` | ApprovalRequest, ApprovalResponse Pydantic models |
| `src/services/approval_service.py` | Approval lifecycle management |
| `alembic/versions/00X_add_job_retry_and_approval.py` | Migration for new Job fields |

### Handlers Modified

| File | Changes |
|------|---------|
| `src/worker/queue.py` | Exponential backoff, pause/resume, checkpoint support |
| `src/worker/processor.py` | Approval gate before claiming, checkpoint resume logic |
| `src/worker/handlers/research_job.py` | Checkpoint recording, approval pause point |

---

## Storage Structure

No new storage. Uses existing:
- `result_data` JSON column for checkpoint data
- `JobEvent` table for audit trail
- `exchange/proposals/` for approval bundles

---

## Wave Plan

| Wave | Plans | Focus |
|------|-------|-------|
| 1 | 09-01 | Retry with backoff + Checkpoint/Resume |
| 2 | 09-02 | Approval-aware execution |
| 3 | 09-03 | Idempotency + tests |

---

## Dependencies

**From Prior Phases:**
- Phase 4: Job queue, worker, Postgres schema
- Phase 8: Research pipeline (approval use case)

---

## Next Steps

Execute:
```
/gsd:execute-phase 09-01  # Retry + Checkpoint/Resume
# Then
/gsd:execute-phase 09-02  # Approval-aware execution
# Then
/gsd:execute-phase 09-03  # Idempotency + tests
```

---

*Summary created: 2026-04-01*
