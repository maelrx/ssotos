# Phase 8: Research Runtime — Requirements

**Phase:** 08-research-runtime
**Requirements:** F12-01, F12-02, F12-03, F12-04, F12-05, F12-06, F12-07
**Created:** 2026-04-01

---

## F12: Research Runtime

### F12-01: Research Brief and Blueprint Generation

**Description:** User can create a research brief with goal, questions, scope, depth, and max_sources. System generates a research blueprint.

**Acceptance Criteria:**
- [ ] API accepts research brief: {query, goal, questions[], scope, depth, max_sources}
- [ ] Blueprint generated with planned sources and approach
- [ ] Blueprint stored as blueprint.md in exchange/research/<job_id>/
- [ ] Blueprint includes: search strategy, source candidates, timeline

**Implementation:**
- Add `src/schemas/research.py` with Pydantic models
- Create `src/services/blueprint_service.py` for blueprint generation
- Extend `src/api/research.py` with POST /research/briefs endpoint

---

### F12-02: Research Job Lifecycle

**Description:** Research job transitions through all states correctly: queued, planning, discovering, crawling, parsing, synthesizing, awaiting_approval, completed, failed.

**Acceptance Criteria:**
- [ ] Job status reflects current pipeline stage
- [ ] Job events track all state transitions
- [ ] Failed jobs can be retried
- [ ] Progress updates via SSE

**Implementation:**
- Extend `handle_research_job` in `src/worker/handlers/research_job.py`
- Use job.result_data['research_state'] for stage tracking
- Record job events for each stage transition

---

### F12-03: Source Fetch and Crawl

**Description:** Crawler fetches sources using Crawl4AI and produces raw markdown.

**Acceptance Criteria:**
- [ ] Web URLs crawled via AsyncWebCrawler
- [ ] Raw markdown stored in workspace/raw/web/
- [ ] Provenance metadata captured (URL, timestamp, hash)
- [ ] Concurrent crawling for multiple sources
- [ ] Handles JavaScript-rendered pages

**Implementation:**
- Create `src/services/crawl_service.py` wrapping Crawl4AI
- Store artifacts with artifact_type='raw_web'
- Use asyncio.gather for concurrent crawling

**New Dependencies:** crawl4ai, playwright

---

### F12-04: Raw Artifact Materialization

**Description:** Raw artifacts persist with provenance metadata. Parse documents (PDF, DOCX, PPTX) into markdown.

**Acceptance Criteria:**
- [ ] Documents parsed via Docling DocumentConverter
- [ ] Raw markdown stored in workspace/raw/documents/
- [ ] Parsed content stored in workspace/raw/parsed/
- [ ] Table structure preserved
- [ ] Provenance metadata (source file, hash, pages)

**Implementation:**
- Create `src/services/docling_service.py` wrapping Docling
- Store artifacts with artifact_type='raw_document'

**New Dependencies:** docling

---

### F12-05: Synthesis Generation

**Description:** Synthesis generates coherent summary from multiple sources using PydanticAI.

**Acceptance Criteria:**
- [ ] PydanticAI analyzes all raw artifacts
- [ ] Synthesis includes: summary, key_findings[], sources[], confidence
- [ ] Source citations with links
- [ ] Identified gaps in research
- [ ] synthesis.md stored in exchange/research/<job_id>/

**Implementation:**
- Create `src/services/synthesis_service.py`
- Define SynthesisResult Pydantic model
- Store artifact with artifact_type='synthesis'

---

### F12-06: Ingest Proposal Bundle

**Description:** Create ingest proposal bundle for Exchange Zone review.

**Acceptance Criteria:**
- [ ] Proposal created with research outputs
- [ ] Bundle includes: synthesis.md, manifest.yaml, source references
- [ ] Proposal follows standard workflow (draft -> generated -> awaiting_review)
- [ ] User can approve/reject via Exchange Zone

**Implementation:**
- Create `src/services/ingest_proposal_service.py`
- Use ProposalService pattern from Phase 2

---

### F12-07: Research Outputs

**Description:** Research outputs traceable: blueprint.md, raw/, normalized/, synthesis.md, manifest.yaml, ingest-proposal.patch.

**Acceptance Criteria:**
- [ ] All outputs present in exchange/research/<job_id>/
- [ ] Manifest.yaml lists all sources with hashes
- [ ] Ingest proposal created in exchange/proposals/
- [ ] Full provenance trail from query to output

---

## New Requirements Discovered

### F12-08: Source Deduplication

**Description:** Avoid re-crawling same content using content hash deduplication.

**Acceptance Criteria:**
- [ ] Sources deduplicated by SHA-256 hash of content
- [ ] Cached sources reused across jobs
- [ ] Cache hit logged in job events

---

### F12-09: Research Job Cancellation

**Description:** User can cancel a running research job.

**Acceptance Criteria:**
- [ ] Cancel endpoint stops in-progress crawling
- [ ] Partial results preserved
- [ ] Job marked as failed with "cancelled" message

---

### F12-10: Research Workspace UI

**Description:** Research workspace in frontend shows job status, source list, synthesis view.

**Acceptance Criteria:**
- [ ] Job list with status filters
- [ ] Source list with status (crawled, parsed, failed)
- [ ] Synthesis viewer
- [ ] Blueprint viewer
- [ ] Create/retry/cancel actions

---

## Dependencies Summary

**From Prior Phases:**
- Phase 4: Job queue, worker, Postgres schema, API infrastructure
- Phase 5: PydanticAI (agent brain)
- Phase 6: Retrieval service, artifact storage

**New External Dependencies:**
- crawl4ai
- playwright
- docling

---

*Requirements gathered: 2026-04-01*
