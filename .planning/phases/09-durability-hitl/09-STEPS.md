# Phase 9: Durability / HITL — Implementation Steps

**Phase:** 09-durability-hitl
**Created:** 2026-04-01
**Granularity:** Fine (3 waves)

---

## Wave Structure

| Wave | Plans | Focus | Dependencies |
|------|-------|-------|--------------|
| 1 | 09-01 | Retry with backoff + Checkpoint/Resume | 04-03, 08-01 |
| 2 | 09-02 | Approval-aware execution | 09-01 |
| 3 | 09-03 | Idempotency + tests | 09-02 |

---

## Plan 09-01: Retry + Checkpoint/Resume

**Wave:** 1 | **Type:** execute

Implements exponential backoff for failed jobs and checkpoint/resume for long-running jobs.

### Tasks

#### Task 1: Add retry fields to Job model
**Files:** `src/db/models/job.py`, `alembic/versions/00X_add_job_retry_fields.py`

Add: `next_retry_at: datetime | None`, `last_checkpoint: str | None`

#### Task 2: Implement exponential backoff in JobQueue.fail()
**Files:** `src/worker/queue.py`

Compute delay: `min(base_delay * 2^(attempt_count-1), max_delay)` where base_delay=30s, max_delay=3600s.

#### Task 3: Modify JobQueue.claim() to skip jobs not yet ready for retry
**Files:** `src/worker/queue.py`

Filter: `WHERE next_retry_at IS NULL OR next_retry_at <= now()`

#### Task 4: Add checkpoint recording to JobQueue
**Files:** `src/worker/queue.py`

New method: `record_checkpoint(db, job, checkpoint_id, data)` — stores intermediate state in `result_data`.

#### Task 5: Modify processor to resume from checkpoint
**Files:** `src/worker/processor.py`

If `job.last_checkpoint` is set, pass checkpoint data to handler so it can resume.

#### Task 6: Update research_job handler to use checkpointing
**Files:** `src/worker/handlers/research_job.py`

Record checkpoint after each pipeline stage.

---

## Plan 09-02: Approval-Aware Execution

**Wave:** 2 | **Type:** execute

Implements human-in-the-loop pause and resume for approval-gated jobs.

### Tasks

#### Task 1: Add approval fields to Job model
**Files:** `src/db/models/job.py`, `alembic/versions/00X_add_job_approval_fields.py`

Add: `approval_required: bool`, `approval_id: UUID | None`

#### Task 2: Create ApprovalService
**Files:** `src/services/approval_service.py`

Methods: `request_approval(job)`, `approve(approval_id)`, `reject(approval_id, reason)`.

#### Task 3: Add pause/resume methods to JobQueue
**Files:** `src/worker/queue.py`

New methods: `pause_for_approval(db, job, approval_id)`, `resume_from_approval(db, job)`.

#### Task 4: Modify JobQueue.claim() to skip jobs awaiting approval
**Files:** `src/worker/queue.py`

Filter: `WHERE NOT (approval_required = true AND approval_id IS NOT NULL AND status = 'running')`

#### Task 5: Create approval API endpoints
**Files:** `src/api/approvals.py`

`GET /approvals`, `GET /approvals/{id}`, `POST /approvals/{id}/approve`, `POST /approvals/{id}/reject`.

#### Task 6: Update research_job to use approval pause
**Files:** `src/worker/handlers/research_job.py`

After creating ingest proposal, call `queue.pause_for_approval()` instead of immediately completing.

---

## Plan 09-03: Idempotency + Tests

**Wave:** 3 | **Type:** execute

Verifies job idempotency and adds test coverage.

### Tasks

#### Task 1: Add idempotency key to job creation
**Files:** `src/schemas/jobs.py`, `src/api/jobs.py`

Accept optional `idempotency_key` on job creation. If key already exists and job succeeded/failed, return existing job.

#### Task 2: Add unit tests for retry/backoff
**Files:** `tests/unit/test_job_queue.py`

Test: exponential backoff calculation, max_attempts boundary, next_retry_at scheduling.

#### Task 3: Add unit tests for checkpoint/resume
**Files:** `tests/unit/test_job_queue.py`

Test: checkpoint recording, resume from checkpoint, partial result preservation.

#### Task 4: Add unit tests for approval flow
**Files:** `tests/unit/test_approval_service.py`

Test: request_approval, approve resumes job, reject marks failed.

---

## Success Criteria

1. Failed jobs retry with exponential backoff up to max_attempts
2. Long-running jobs can checkpoint and resume after interrupt
3. Approval-required jobs pause and resume after approval
4. Job idempotency verified — re-running same job produces same result

---

*Steps documented: 2026-04-01*
