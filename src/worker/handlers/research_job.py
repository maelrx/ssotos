"""Handler for research_job job type — per F12-02.

Full research pipeline: planning -> discovering -> crawling -> parsing -> synthesizing -> ingest proposal.
"""
from __future__ import annotations
from typing import Any
from uuid import UUID
import structlog
import os

logger = structlog.get_logger(__name__)


async def handle_research_job(
    input_data: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
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

    # Check if resuming from checkpoint
    resume_from = None
    checkpoint_data = None
    if context:
        resume_from = context.get("resume_from_checkpoint")
        checkpoint_data = context.get("checkpoint_data", {})

    try:
        # ─── Stage 1: Planning ─── (10%)
        if resume_from != "stage-1-planning":
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

            # Record checkpoint after planning stage
            if context and "record_checkpoint" in context:
                await context["record_checkpoint"](job_id, "stage-1-planning", {
                    "state": "planning",
                    "blueprint_path": blueprint_path,
                })
        else:
            # Resuming from checkpoint - restore state
            blueprint_path = checkpoint_data.get("blueprint_path") if checkpoint_data else None
            logger.info("research_stage_skipped", stage="planning", job_id=job_id)

        # ─── Stage 2: Discovering (20%) ───
        if resume_from != "stage-2-discovering":
            state = "discovering"
            logger.info("research_stage", stage=state, job_id=job_id)
            # For v1: use provided sources or treat as URL list
            urls_to_crawl = [s for s in sources if s.startswith(("http://", "https://"))]
            if not urls_to_crawl:
                urls_to_crawl = []  # No URLs provided

            # Record checkpoint after discovering stage
            if context and "record_checkpoint" in context:
                await context["record_checkpoint"](job_id, "stage-2-discovering", {
                    "state": "discovering",
                    "urls_to_crawl": urls_to_crawl,
                })
        else:
            # Resuming from checkpoint - restore state
            urls_to_crawl = checkpoint_data.get("urls_to_crawl", []) if checkpoint_data else []
            logger.info("research_stage_skipped", stage="discovering", job_id=job_id)

        # ─── Stage 3: Crawling (40%) ───
        if resume_from not in ("stage-3-crawling", "stage-3-crawling-partial"):
            state = "crawling"
            logger.info("research_stage", stage=state, job_id=job_id, url_count=len(urls_to_crawl))
            # Check if we have partial results from checkpoint
            if checkpoint_data and resume_from == "stage-3-crawling-partial":
                source_results = checkpoint_data.get("sources_crawled", [])
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

            # Record checkpoint after crawling stage
            if context and "record_checkpoint" in context:
                await context["record_checkpoint"](job_id, "stage-3-crawling", {
                    "state": "crawling",
                    "sources_crawled": source_results,
                })
        else:
            # Resuming from checkpoint - restore state
            source_results = checkpoint_data.get("sources_crawled", []) if checkpoint_data else source_results
            logger.info("research_stage_skipped", stage="crawling", job_id=job_id)

        # ─── Stage 4: Parsing (60%) ───
        if resume_from != "stage-4-parsing":
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

            # Record checkpoint after parsing stage
            if context and "record_checkpoint" in context:
                await context["record_checkpoint"](job_id, "stage-4-parsing", {
                    "state": "parsing",
                    "sources_parsed": [s for s in source_results if s.get("status") == "parsed"],
                })
        else:
            logger.info("research_stage_skipped", stage="parsing", job_id=job_id)

        # ─── Stage 5: Synthesizing (80%) ───
        if resume_from != "stage-5-synthesizing":
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

            # Record checkpoint after synthesizing stage
            if context and "record_checkpoint" in context:
                await context["record_checkpoint"](job_id, "stage-5-synthesizing", {
                    "state": "synthesizing",
                    "synthesis_path": synthesis_path,
                })
        else:
            synthesis_path = checkpoint_data.get("synthesis_path") if checkpoint_data else None
            logger.info("research_stage_skipped", stage="synthesizing", job_id=job_id)

        # ─── Stage 6: Ingest proposal + Approval (90%) ───
        if resume_from != "stage-6-ingest":
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

            # Record checkpoint before pausing for approval
            if context and "record_checkpoint" in context:
                await context["record_checkpoint"](job_id, "stage-6-ingest", {
                    "state": "awaiting_approval",
                })

            # Pause for approval — job will not complete until user approves
            approval_id = None
            if context and "pause_for_approval" in context:
                approval_id = await context["pause_for_approval"](
                    reason=f"Research job awaiting approval to ingest findings for: {research_query}"
                )

            return {
                "job_id": job_id,
                "workspace_id": str(workspace_id),
                "research_query": research_query,
                "state": state,
                "approval_id": approval_id,
                "sources": source_results,
                "blueprint_path": blueprint_path,
                "synthesis_path": synthesis_path,
                "sources_crawled": sum(1 for s in source_results if s.get("status") == "crawled"),
                "sources_failed": sum(1 for s in source_results if s.get("status") == "failed"),
            }

        # If resuming after approval, complete the job
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
