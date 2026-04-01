# Phase 8: Research Runtime — Architecture Notes

**Created:** 2026-04-01
**Phase:** 08-research-runtime
**Status:** Ready for planning

---

## Domain

Implement the research job pipeline — turning ephemeral chat into durable, traceable knowledge production. The research runtime is the "factory" that produces research artifacts from arbitrary sources, with full audit trail through the Exchange Zone.

---

## Conceptual Architecture

### Research Pipeline Stages

1. **Brief/Blueprint** (F12-01)
   - User provides: goal, questions, scope, depth, max_sources
   - System generates: research blueprint with planned sources and approach
   - Stored as: `blueprint.md` in exchange/research/<job_id>/

2. **Source Discovery** (F12-02)
   - Job lifecycle states: queued, planning, discovering, crawling, parsing, synthesizing, awaiting_approval, completed, failed
   - Transitions tracked in job_events table

3. **Crawl** (F12-03)
   - Crawl4AI AsyncWebCrawler for web sources
   - Raw markdown stored with provenance metadata
   - Handles: HTML pages, JavaScript-rendered content

4. **Parse** (F12-04)
   - Docling DocumentConverter for documents
   - Raw artifacts: PDF, DOCX, PPTX, XLSX -> Markdown
   - Stores in workspace/raw/parsed/

5. **Synthesize** (F12-05)
   - PydanticAI analyzes all raw artifacts
   - Generates coherent synthesis with citations
   - Output: synthesis.md with source attribution

6. **Ingest Proposal** (F12-06)
   - Creates patch bundle for Exchange Zone
   - Includes: synthesis.md, raw artifacts manifest, source links
   - Follows standard proposal workflow (F5-05)

### Research Job State Machine

```
pending -> running [planning] -> discovering -> crawling -> parsing -> synthesizing -> awaiting_approval -> completed
                |                |              |           |            |              |
                v                v              v           v            v              v
             failed           failed         failed     failed       failed          failed
```

State stored in `job.result_data['research_state']`.

---

## Technology Integration

### Crawl4AI Service

**Module:** `src/services/crawl_service.py`

```python
class CrawlService:
    """Wraps AsyncWebCrawler for research pipeline."""

    async def crawl_url(self, url: str, options: CrawlOptions) -> CrawlResult:
        """Crawl single URL, return markdown + metadata."""

    async def crawl_urls(self, urls: list[str], options: CrawlOptions) -> list[CrawlResult]:
        """Crawl multiple URLs concurrently."""
```

**Dependencies:** crawl4ai, playwright

### Docling Service

**Module:** `src/services/docling_service.py`

```python
class DoclingService:
    """Wraps DocumentConverter for document parsing."""

    async def parse_document(self, file_path: str, options: ParseOptions) -> ParseResult:
        """Parse document, return markdown + structure."""

    async def parse_documents(self, file_paths: list[str]) -> list[ParseResult]:
        """Parse multiple documents."""
```

**Dependencies:** docling, docling-core

### Synthesis Service

**Module:** `src/services/synthesis_service.py`

```python
class SynthesisService:
    """Generates synthesis from research artifacts using PydanticAI."""

    async def synthesize(self, artifacts: list[Artifact], query: str) -> SynthesisResult:
        """Analyze artifacts, generate coherent synthesis."""
```

**Dependencies:** pydantic-ai, openai/anthropic

---

## Storage Structure

### Exchange Zone (exchange/research/<job_id>/)

```
exchange/
  research/
    <job_id>/
      blueprint.md          # Research plan and approach
      synthesis.md          # Final synthesized findings
      manifest.yaml         # Source manifest with hashes
      sources/
        <source_id>.md      # Raw source content
        ...
      normalized/
        <source_id>.md      # Normalized/cleaned content
        ...
```

### Raw Zone (workspace/raw/)

```
workspace/
  raw/
    web/
      <url_hash>.md         # Raw crawled web content
      <url_hash>.json       # Provenance metadata
    documents/
      <doc_hash>.md         # Raw parsed documents
      <doc_hash>.json       # Provenance metadata
    parsed/
      <source_id>.md         # Normalized content
    manifests/
      <job_id>.yaml          # Manifest linking all sources
    failed/
      <source_id>.json       # Failed crawl/parse attempts
```

### Artifact Types

| artifact_type | Description | Storage |
|--------------|-------------|---------|
| raw_web | Raw crawled web content | workspace/raw/web/ |
| raw_document | Raw parsed document | workspace/raw/documents/ |
| normalized | Cleaned/normalized content | workspace/raw/parsed/ |
| synthesis | Research synthesis | exchange/research/<job_id>/ |
| blueprint | Research plan | exchange/research/<job_id>/ |
| manifest | Source manifest | workspace/raw/manifests/ |

---

## Key Decisions

### D-110: Research outputs go to Exchange Zone first
- All research outputs are staged in exchange/research/<job_id>/
- Ingest proposal creates patch bundle for vault integration
- User must approve before research enters vault
- Follows established audit boundary principle

### D-111: Synthesis uses PydanticAI with structured output
- SynthesisResult Pydantic model for guaranteed structure
- Includes: summary, findings[], sources[], confidence, gaps
- Model-agnostic (works with OpenAI, Anthropic, etc.)

### D-112: Checkpointing via job.result_data
- Each pipeline stage stores state in job.result_data
- On failure, can resume from last checkpoint
- Enables retry without re-crawling sources

### D-113: Source deduplication by content hash
- Each source artifact stored by SHA-256 hash of content
- Avoids re-crawling same content
- Enables cache reuse across jobs

---

## Dependencies

- **Phase 4:** Job queue, worker, Postgres schema (artifacts table)
- **Phase 5:** Agent brain (for PydanticAI synthesis)
- **Phase 6:** Retrieval service (for context)
- **Phase 7:** Note copilot (for UX patterns)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Crawl4AI breaking changes | Low | High | Pin version, test on major releases |
| Docling parsing failures | Medium | Medium | Store raw + parsed, fallback to raw |
| Synthesis quality | Medium | Medium | Human review via Exchange Zone |
| Large document handling | Medium | Low | Stream processing, chunked storage |

---

*Phase: 08-research-runtime*
*Context gathered: 2026-04-01*
