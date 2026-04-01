"""Synthesis service using PydanticAI — per F12-05."""
from pydantic import BaseModel, Field
import hashlib

import structlog

logger = structlog.get_logger(__name__)


class Citation(BaseModel):
    """A citation to a source."""
    source_id: str
    url: str | None = None
    excerpt: str


class Finding(BaseModel):
    """A key finding from synthesis."""
    topic: str
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)


class SynthesisResult(BaseModel):
    """Structured synthesis output."""
    summary: str
    key_findings: list[Finding] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    gaps: list[str] = Field(default_factory=list)
    research_query: str


class SynthesisService:
    """Generates synthesis from research artifacts using PydanticAI."""

    def __init__(self) -> None:
        pass

    async def synthesize(
        self,
        artifacts: list[dict],
        query: str,
    ) -> SynthesisResult:
        """Analyze artifacts, generate coherent synthesis.

        Args:
            artifacts: List of dicts with keys: content, source_id, url
            query: The original research query

        Returns:
            SynthesisResult with structured findings
        """
        # Build context from artifacts
        context_parts = []
        for a in artifacts:
            source_label = a.get("source_id", "unknown")
            content = a.get("content", "")[:2000]  # Truncate for token limit
            context_parts.append(f"=== Source: {source_label} ===\n{content}")

        context = "\n\n".join(context_parts)

        prompt = f"""You are a research assistant. Given the following sources, produce a structured synthesis.

Research query: {query}

Sources:
{context}

Respond with a JSON object containing:
- "summary": 2-3 paragraph summary of findings
- "key_findings": array of {{topic, summary, confidence (0-1), citations: [{{source_id, excerpt}}]}}
- "sources": array of source_ids used
- "confidence": overall confidence 0-1
- "gaps": areas not covered by the sources

Return ONLY valid JSON, no markdown formatting."""

        # For v1: basic structured extraction
        # In production, this would call PydanticAI with structured output
        logger.info("synthesis_generate", query=query, artifact_count=len(artifacts))

        return SynthesisResult(
            summary=f"Synthesis of {len(artifacts)} sources regarding: {query}. "
                    f"This is a placeholder — full LLM synthesis comes in a later iteration.",
            key_findings=[],
            sources=[a.get("source_id", "?") for a in artifacts],
            confidence=0.6,
            gaps=["Full synthesis requires PydanticAI integration"],
            research_query=query,
        )

    async def store_synthesis(
        self,
        result: SynthesisResult,
        workspace_id: str,
        job_id: str,
        output_dir: str,
    ) -> str:
        """Store synthesis as a file. Returns file_path."""
        from src.db.session import async_session_maker
        from src.db.models import Artifact
        import os

        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/synthesis.md"

        # Write markdown
        markdown = f"# Research Synthesis: {result.research_query}\n\n"
        markdown += f"## Summary\n\n{result.summary}\n\n"
        if result.key_findings:
            markdown += "## Key Findings\n\n"
            for f in result.key_findings:
                markdown += f"- **{f.topic}**: {f.summary} (confidence: {f.confidence:.0%})\n"
        if result.gaps:
            markdown += "\n## Research Gaps\n\n"
            for gap in result.gaps:
                markdown += f"- {gap}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Store artifact
        content_hash = hashlib.sha256(markdown.encode()).hexdigest()

        async with async_session_maker() as db:
            artifact = Artifact(
                workspace_id=workspace_id,
                job_id=job_id,
                artifact_type="synthesis",
                source_url=None,
                file_path=file_path,
                content_hash=content_hash,
                extra={"confidence": result.confidence, "source_count": len(result.sources)},
                provenance={"query": result.research_query},
            )
            db.add(artifact)
            await db.commit()

        return file_path
