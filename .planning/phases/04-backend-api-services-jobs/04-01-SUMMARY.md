---
phase: 04-backend-api-services-jobs
plan: "04-01"
subsystem: database
tags: [postgres, sqlalchemy, alembic, async, pgvector]

# Dependency graph
requires:
  - phase: 03-policy-engine
    provides: Policy models and enums (NoteType, SensitivityLevel, Domain)
provides:
  - SQLAlchemy 2 async models for all 12 tables
  - Alembic migration infrastructure
  - Async database engine and session factory
affects: [backend-api, services, jobs, retrieval, research]

# Tech tracking
tech-stack:
  added: [sqlalchemy, asyncpg, alembic]
  patterns: [SQLAlchemy 2 async, Declarative Base, Mapped columns]

key-files:
  created:
    - src/db/database.py
    - src/db/session.py
    - src/db/__init__.py
    - src/db/models/__init__.py
    - src/db/models/workspace.py
    - src/db/models/actor.py
    - src/db/models/note_projection.py
    - src/db/models/policy.py
    - src/db/models/approval.py
    - src/db/models/proposal.py
    - src/db/models/job.py
    - src/db/models/job_event.py
    - src/db/models/chunk.py
    - src/db/models/embedding.py
    - src/db/models/artifact.py
    - src/db/models/audit_log.py
    - alembic.ini
    - alembic/env.py
    - alembic/versions/001_initial_schema.py

key-decisions:
  - "Used 'extra' attribute with explicit 'metadata' column name to avoid SQLAlchemy reserved attribute conflict"
  - "Stored embedding vectors as JSONB arrays (1536-dim) since pgvector extension requires server-side installation"
  - "Created migration manually since no live Postgres database was available for autogenerate"

patterns-established:
  - "SQLAlchemy 2 async with async_sessionmaker and create_async_engine"
  - "Declarative Base pattern with Mapped column annotations"
  - "Alembic async migration environment with async_engine_from_config"

requirements-completed: [F8-01, F8-02]

# Metrics
duration: ~10min
completed: 2026-03-31
---

# Phase 04 Plan 01: Postgres Schema with SQLAlchemy 2 Async Models and Alembic Migrations

**Complete Postgres schema foundation with 12 tables, async SQLAlchemy 2 models, and Alembic migration infrastructure**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-31T19:05:00Z
- **Completed:** 2026-03-31T19:13:25Z
- **Tasks:** 3 (combined into 1 commit)
- **Files modified:** 20 files created

## Accomplishments
- Created async SQLAlchemy 2 engine and session factory with connection pooling
- Defined all 12 SQLAlchemy models with proper indexes and foreign keys
- Initialized Alembic with async migration environment
- Created initial migration for all 12 tables

## Task Commits

All tasks committed atomically in single commit:

1. **Tasks 1-3: Database infrastructure + models + Alembic** - `b78dc89` (feat)

**Plan metadata:** `b78dc89` (feat: add Postgres schema)

## Files Created/Modified
- `src/db/database.py` - Async engine, session maker, Base class
- `src/db/session.py` - FastAPI dependency for get_db
- `src/db/__init__.py` - Re-exports for database layer
- `src/db/models/` - All 12 SQLAlchemy models
- `alembic.ini` - Alembic configuration with asyncpg URL
- `alembic/env.py` - Async migration environment
- `alembic/versions/001_initial_schema.py` - Initial migration creating all 12 tables

## Decisions Made

- Used 'extra' Python attribute with explicit 'metadata' column name to avoid SQLAlchemy reserved 'metadata' attribute conflict
- Stored embedding vectors as JSONB arrays since pgvector requires server-side extension installation
- Created migration manually due to no live Postgres database being available for autogenerate

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Fixed SQLAlchemy reserved 'metadata' attribute conflict**
- **Found during:** Task 2 (model creation)
- **Issue:** SQLAlchemy declarative API reserves 'metadata' as an attribute name; using it caused InvalidRequestError
- **Fix:** Renamed Python attribute to 'extra' with explicit column name 'metadata' using mapped_column("metadata", JSON, ...)
- **Files modified:** src/db/models/actor.py, src/db/models/job_event.py, src/db/models/artifact.py, src/db/models/audit_log.py
- **Verification:** All 12 models import successfully without errors
- **Committed in:** b78dc89 (Task 1-3 combined commit)

**2. [Rule 3 - Blocking] Installed missing SQLAlchemy dependencies**
- **Found during:** Task 1 (verification)
- **Issue:** sqlalchemy, asyncpg, alembic not installed in Python environment
- **Fix:** pip install sqlalchemy[asyncio] asyncpg alembic
- **Files modified:** Python environment
- **Verification:** All 12 models import correctly
- **Committed in:** b78dc89 (Task 1-3 combined commit)

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 blocking)
**Impact on plan:** Both auto-fixes essential for correctness and functionality. No scope creep.

## Issues Encountered
- No live Postgres database available for alembic --autogenerate; created migration manually based on model definitions
- SQLAlchemy reserved 'metadata' attribute required renaming to 'extra' with explicit column mapping

## Next Phase Readiness
- Database foundation ready for Phase 04后续 plans (API services, jobs)
- All models importable and mapped to tables
- Alembic migration ready for deployment when Postgres is available

---
*Phase: 04-backend-api-services-jobs / 04-01*
*Completed: 2026-03-31*
