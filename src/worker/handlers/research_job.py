"""Handler for research_job job type — per F12-02.

Full research pipeline: planning -> discovering -> crawling -> parsing -> synthesizing -> ingest proposal.
"""
from __future__ import annotations
from typing import Any
from uuid import UUID
import structlog
import os

logger = structlog.get_logger(__name__)


async def handle_research_job(input_data: dict[str, Any]) -> dict[str, Any]:
    """Run full research pipeline for a topic."""
    workspace_id = input_data.get("workspace_id")
    research_query = input_data.get("research_query") or input_data.get("query", "")
    sources = input_data.get("sources", [])
    job_id = input_data.get("job_id")

    if not job_id:
        raise ValueError("job_id is required in input_data")

    logger.info("research_job_start", workspace_id=workspace_id, query=research_query, job_id=job_id)

    # Ensure directories exist
    os.makedirs("workspace/raw/web", exist_ok=True)
    os.makedirs("workspace/raw/documents", exist_ok=True)
    os.makedirs("workspace/exchange/research", exist_ok=True)

    # Init services
    crawl_svc = CrawlService()
    docling_svc = DoclingService()
    synth_svc = SynthesisService()

    # Track sources
    source_results = []
    synthesis_path = None
    blueprint_path = None
    state = "planning"

    try:
        # ─── Stage 1: Planning ─── (10%)
        state = "planning"
        logger.info("research_stage", stage=state, job_id=job_id)
        blueprint_path = f"workspace/exchange/research/{job_id}/blueprint.md"
        os.makedirs(os.path.dirname(blueprint_path), exist_ok=True)
        blueprint_content = f"""# Research Blueprint: {research_query}

## Goal
{input_data.get('goal', 'Research the query')}

## Questions
{chr(10).join(f"- {q}" for q in input_data.get('questions', []))}

## Planned Sources
{chr(10).join(f"- {s}" for s in sources[:10])}

## Pipeline
1. Crawl web sources
2. Parse documents
3. Synthesize findings
"""
        with open(blueprint_path, "w") as f:
            f.write(blueprint_content)

        # ─── Stage 2: Discovering (20%) ───
        state = "discovering"
        logger.info("research_stage", stage=state, job_id=job_id)
        # For v1: use provided sources or treat as URL list
        urls_to_crawl = [s for s in sources if s.startswith(("http://", "https://"))]
        if not urls_to_crawl:
            urls_to_crawl = []  # No URLs provided

        # ─── Stage 3: Crawling (40%) ───
        state = "crawling"
        logger.info("research_stage", stage=state, job_id=job_id, url_count=len(urls_to_crawl))
        for url in urls_to_crawl:
            result = await crawl_svc.crawl_url(url)
            if result.success:
                await crawl_svc.store_artifact(result, str(workspace_id), job_id)
                source_results.append({
                    "source_id": result.content_hash[:8],
                    "url": url,
                    "status": "crawled",
                    "content_hash": result.content_hash,
                })
            else:
                source_results.append({
                    "source_id": url[:8],
                    "url": url,
                    "status": "failed",
                    "error": result.error,
                })

        # ─── Stage 4: Parsing (60%) ───
        state = "parsing"
        logger.info("research_stage", stage=state, job_id=job_id)
        # For v1: parse any local document paths provided
        doc_paths = [s for s in sources if not s.startswith(("http://", "https://")) and os.path.exists(s)]
        for doc_path in doc_paths:
            result = await docling_svc.parse_document(doc_path)
            if result.success:
                await docling_svc.store_artifact(result, str(workspace_id), job_id)
                source_results.append({
                    "source_id": result.content_hash[:8],
                    "source_path": doc_path,
                    "status": "parsed",
                    "content_hash": result.content_hash,
                })
            else:
                source_results.append({
                    "source_id": doc_path[:8],
                    "source_path": doc_path,
                    "status": "failed",
                    "error": result.error,
                })

        # ─── Stage 5: Synthesizing (80%) ───
        state = "synthesizing"
        logger.info("research_stage", stage=state, job_id=job_id)

        # Load crawled content for synthesis
        artifacts = []
        for sr in source_results:
            if sr.get("status") == "crawled":
                fp = f"workspace/raw/web/{sr['content_hash']}.md"
                if os.path.exists(fp):
                    with open(fp) as f:
                        artifacts.append({
                            "source_id": sr["source_id"],
                            "content": f.read(),
                            "url": sr.get("url"),
                        })

        if artifacts:
            synth_result = await synth_svc.synthesize(artifacts, research_query)
            output_dir = f"workspace/exchange/research/{job_id}"
            synthesis_path = await synth_svc.store_synthesis(
                synth_result, str(workspace_id), job_id, output_dir
            )
        else:
            # No artifacts — create empty synthesis
            output_dir = f"workspace/exchange/research/{job_id}"
            os.makedirs(output_dir, exist_ok=True)
            synthesis_path = f"{output_dir}/synthesis.md"
            with open(synthesis_path, "w") as f:
                f.write(f"# Synthesis: {research_query}\n\nNo sources were successfully crawled.")

        # ─── Stage 6: Ingest proposal (90%) ───
        state = "awaiting_approval"
        logger.info("research_stage", stage=state, job_id=job_id)

        from src.services.ingest_proposal_service import IngestProposalService
        from uuid import UUID

        ingest_svc = IngestProposalService()
        try:
            await ingest_svc.create_proposal(
                job_id=UUID(str(job_id)) if job_id else UUID("00000000-0000-0000-0000-000000000000"),
                workspace_id=UUID(str(workspace_id)) if workspace_id else UUID("00000000-0000-0000-0000-000000000000"),
                synthesis_path=synthesis_path or "",
                blueprint_path=blueprint_path,
                source_paths=[sr.get("source_path", "") for sr in source_results if sr.get("source_path")],
            )
        except Exception as e:
            logger.warning("ingest_proposal_failed", job_id=job_id, error=str(e))
            # Non-fatal: synthesis is still available

        state = "completed"
        logger.info("research_job_complete", job_id=job_id, sources=len(source_results))

        return {
            "job_id": job_id,
            "workspace_id": str(workspace_id),
            "research_query": research_query,
            "state": state,
            "sources": source_results,
            "blueprint_path": blueprint_path,
            "synthesis_path": synthesis_path,
            "sources_crawled": sum(1 for s in source_results if s.get("status") == "crawled"),
            "sources_failed": sum(1 for s in source_results if s.get("status") == "failed"),
        }

    except Exception as e:
        logger.exception("research_job_error", job_id=job_id, error=str(e), stage=state)
        raise
