"""Crawl4AI service for web crawling — per F12-03."""
from dataclasses import dataclass
from typing import Any
import hashlib

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CrawlResult:
    """Result of crawling a single URL."""
    url: str
    markdown: str
    content_hash: str
    metadata: dict[str, Any]
    success: bool
    error: str | None = None


class CrawlService:
    """Wraps AsyncWebCrawler for research pipeline."""

    def __init__(self) -> None:
        self.browser_config = None  # Use defaults
        self.crawl_config = None

    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl single URL, return markdown + metadata."""
        try:
            from crawl4ai import AsyncWebCrawler

            async with AsyncWebCrawler() as crawler:
                result = await crawler.crawl(url)
                if result.success:
                    content_hash = hashlib.sha256(result.markdown.encode()).hexdigest()
                    return CrawlResult(
                        url=url,
                        markdown=result.markdown or "",
                        content_hash=content_hash,
                        metadata={"title": getattr(result, 'title', '') or ''},
                        success=True,
                    )
                else:
                    return CrawlResult(
                        url=url,
                        markdown="",
                        content_hash="",
                        metadata={},
                        success=False,
                        error=getattr(result, 'error', str(result)) or "Unknown error",
                    )
        except Exception as e:
            logger.error("crawl_error", url=url, error=str(e))
            return CrawlResult(
                url=url,
                markdown="",
                content_hash="",
                metadata={},
                success=False,
                error=str(e),
            )

    async def crawl_urls(self, urls: list[str]) -> list[CrawlResult]:
        """Crawl multiple URLs concurrently."""
        import asyncio
        tasks = [self.crawl_url(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def store_artifact(
        self,
        result: CrawlResult,
        workspace_id: str,
        job_id: str | None = None,
    ) -> str:
        """Store crawl result as artifact. Returns file_path."""
        from src.db.session import async_session_maker
        from src.db.models import Artifact

        file_path = f"workspace/raw/web/{result.content_hash}.md"

        async with async_session_maker() as db:
            artifact = Artifact(
                workspace_id=workspace_id,
                job_id=job_id,
                artifact_type="raw_web",
                source_url=result.url,
                file_path=file_path,
                content_hash=result.content_hash,
                extra={"title": result.metadata.get("title", ""), "crawl_error": result.error},
                provenance={
                    "url": result.url,
                    "crawled_at": __import__("datetime").datetime.utcnow().isoformat(),
                    "content_hash": result.content_hash,
                },
            )
            db.add(artifact)
            await db.commit()

        # Write markdown file
        import os
        os.makedirs("workspace/raw/web", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)

        return file_path
