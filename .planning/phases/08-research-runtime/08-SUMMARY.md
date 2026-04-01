# Phase 8: Research Runtime — Summary

**Phase:** 08-research-runtime
**Status:** Planned
**Created:** 2026-04-01

---

## Overview

Implements the research job pipeline: crawl -> parse -> synthesize -> ingest proposal. Turns ephemeral chat into durable, traceable knowledge production.

---

## Requirements Covered

| ID | Requirement | Plan |
|----|-------------|------|
| F12-01 | Research brief and blueprint | 08-01 |
| F12-02 | Job lifecycle | 08-01 |
| F12-03 | Source crawl | 08-01 |
| F12-04 | Raw artifact materialization | 08-01 |
| F12-05 | Synthesis generation | 08-01 |
| F12-06 | Ingest proposal bundle | 08-01 |
| F12-07 | Research outputs | 08-01 |
| F12-08 | Source deduplication | 08-01 |
| F12-09 | Job cancellation | 08-01 |
| F12-10 | Research workspace UI | 08-02 |

---

## Key Files to Create

### Services (src/services/)

| File | Purpose |
|------|---------|
| `crawl_service.py` | Crawl4AI AsyncWebCrawler wrapper |
| `docling_service.py` | Docling DocumentConverter wrapper |
| `synthesis_service.py` | PydanticAI synthesis generator |
| `ingest_proposal_service.py` | Creates Exchange Zone proposals |
| `blueprint_service.py` | Generates research blueprints |

### Schemas (src/schemas/)

| File | Purpose |
|------|---------|
| `research.py` | Research pipeline Pydantic models |

### Handlers (src/worker/handlers/)

| File | Purpose |
|------|---------|
| `research_job.py` | Full research pipeline orchestrator |

### API (src/api/)

| File | Purpose |
|------|---------|
| `research.py` | Extended with briefs, sources, cancel |

### Frontend (frontend/src/)

| File | Purpose |
|------|---------|
| `components/research/ResearchWorkspace.tsx` | Research UI |
| `api/research.ts` | Research API hooks |

---

## Dependencies

**From Prior Phases:**
- Phase 4: Job queue, worker, Postgres, API infrastructure
- Phase 5: PydanticAI
- Phase 6: Retrieval service

**New External:**
- crawl4ai
- playwright
- docling

---

## Storage Structure

```
workspace/
  raw/
    web/<hash>.md         # Crawled web content
    documents/<hash>.md   # Parsed documents
    parsed/<hash>.md      # Normalized content
    manifests/<job_id>.yaml
    failed/<hash>.json

exchange/
  research/<job_id>/
    blueprint.md
    synthesis.md
    sources/
  proposals/research-<job_id>/
```

---

## Wave Plan

| Wave | Plans | Focus |
|------|-------|-------|
| 1 | 08-01 | Research pipeline core |
| 2 | 08-02 | Research UI |

---

## Next Steps

Execute:
```
/gsd:execute-phase 08-01  # Research pipeline core
# Then
/gsd:execute-phase 08-02  # Research UI
```

---

*Summary created: 2026-04-01*
