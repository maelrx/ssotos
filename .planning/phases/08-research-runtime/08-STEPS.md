# Phase 8: Research Runtime — Implementation Steps

**Phase:** 08-research-runtime
**Created:** 2026-04-01
**Granularity:** Fine (2 waves)

---

## Wave Structure

| Wave | Plans | Focus | Dependencies |
|------|-------|-------|--------------|
| 1 | 08-01 | Research pipeline core (crawl/parse/synth) | 04-03, 06-03 |
| 2 | 08-02 | Research UI + workspace integration | 08-01, 04-05 |

---

## Plan 08-01: Research Pipeline Core

**Wave:** 1 | **Type:** execute

Implements the core research pipeline: Crawl4AI integration, Docling integration, synthesis generation, and ingest proposal creation.

### Tasks

#### Task 1: Install Dependencies
**Files:** `pyproject.toml`

Install: `crawl4ai>=0.4`, `docling>=2.0`, `playwright>=1.50`

#### Task 2: Create CrawlService
**Files:** `src/services/crawl_service.py`

Wraps AsyncWebCrawler for web crawling. Stores raw artifacts with artifact_type='raw_web'.

#### Task 3: Create DoclingService
**Files:** `src/services/docling_service.py`

Wraps DocumentConverter for document parsing. Stores raw artifacts with artifact_type='raw_document'.

#### Task 4: Create SynthesisService
**Files:** `src/services/synthesis_service.py`

Uses PydanticAI for synthesis generation. Stores artifact with artifact_type='synthesis'.

#### Task 5: Create Research Schemas
**Files:** `src/schemas/research.py`

Models: ResearchBriefRequest, BlueprintResponse, SourceStatus, ResearchJobStatus.

#### Task 6: Implement handle_research_job
**Files:** `src/worker/handlers/research_job.py`

Full pipeline orchestrator: planning -> discovering -> crawling -> parsing -> synthesizing -> ingest_proposal.

#### Task 7: Extend Research API
**Files:** `src/api/research.py`

Add: POST /research/briefs, GET /research/jobs/{id}/sources, POST /research/jobs/{id}/cancel, GET /research/jobs/{id}/blueprint, GET /research/jobs/{id}/synthesis.

#### Task 8: Create IngestProposalService
**Files:** `src/services/ingest_proposal_service.py`

Creates Exchange Zone proposals for research outputs.

---

## Plan 08-02: Research UI + Workspace Integration

**Wave:** 2 | **Type:** execute

Implements the research workspace UI and connects to the backend API.

### Tasks

#### Task 1: Research Workspace Component
**Files:** `frontend/src/components/research/ResearchWorkspace.tsx`

Job list, source list, blueprint/synthesis viewers, action buttons.

#### Task 2: Connect to Research API
**Files:** `frontend/src/api/research.ts`

API hooks: useResearchJobs, useResearchJob, useCreateResearchBrief, useCancelResearchJob.

#### Task 3: Integrate into App Shell
**Files:** `frontend/src/App.tsx`

Add /research route, research indicator in sidebar.

---

## Verification

For 08-01:
```bash
python -c "from src.services.crawl_service import CrawlService; print('CrawlService OK')"
python -c "from src.services.docling_service import DoclingService; print('DoclingService OK')"
python -c "from src.services.synthesis_service import SynthesisService; print('SynthesisService OK')"
python -c "from src.worker.handlers.research_job import handle_research_job; print('Handler OK')"
```

For 08-02:
```bash
cd frontend && npx tsc --noEmit
```

---

## Implementation Order

1. Install dependencies (crawl4ai, docling, playwright)
2. Create CrawlService
3. Create DoclingService
4. Create SynthesisService
5. Create Research schemas
6. Implement handle_research_job (orchestrator)
7. Extend Research API
8. Create IngestProposalService
9. UI components (08-02)

---

## Success Criteria

1. Research job transitions through all states correctly
2. Web sources crawled via Crawl4AI
3. Documents parsed via Docling
4. Synthesis generated via PydanticAI
5. Ingest proposal created in Exchange Zone
6. Research workspace UI displays job status and outputs

---

*Steps documented: 2026-04-01*
