"""Docling service for document parsing — per F12-04."""
from dataclasses import dataclass
from typing import Any
import hashlib
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ParseResult:
    """Result of parsing a document."""
    source_path: str
    markdown: str
    content_hash: str
    pages: int
    tables: int
    metadata: dict[str, Any]
    success: bool
    error: str | None = None


class DoclingService:
    """Wraps DocumentConverter for document parsing."""

    def __init__(self) -> None:
        self.converter = None  # Lazy init

    def _get_converter(self):
        if self.converter is None:
            from docling import DocumentConverter
            self.converter = DocumentConverter()
        return self.converter

    async def parse_document(self, file_path: str) -> ParseResult:
        """Parse single document, return markdown + structure."""
        try:
            converter = self._get_converter()
            result = converter.convert(file_path)
            markdown = result.markdown or ""
            content_hash = hashlib.sha256(markdown.encode()).hexdigest()
            pages = len(getattr(result, 'pages', []))
            tables = len(getattr(result, 'tables', []))

            return ParseResult(
                source_path=file_path,
                markdown=markdown,
                content_hash=content_hash,
                pages=pages,
                tables=tables,
                metadata={"format": Path(file_path).suffix},
                success=True,
            )
        except Exception as e:
            logger.error("docling_parse_error", file_path=file_path, error=str(e))
            return ParseResult(
                source_path=file_path,
                markdown="",
                content_hash="",
                pages=0,
                tables=0,
                metadata={},
                success=False,
                error=str(e),
            )

    async def parse_documents(self, file_paths: list[str]) -> list[ParseResult]:
        """Parse multiple documents sequentially."""
        results = []
        for fp in file_paths:
            results.append(await self.parse_document(fp))
        return results

    async def store_artifact(
        self,
        result: ParseResult,
        workspace_id: str,
        job_id: str | None = None,
    ) -> str:
        """Store parse result as artifact. Returns file_path."""
        from src.db.session import async_session_maker
        from src.db.models import Artifact

        file_path = f"workspace/raw/documents/{result.content_hash}.md"

        async with async_session_maker() as db:
            artifact = Artifact(
                workspace_id=workspace_id,
                job_id=job_id,
                artifact_type="raw_document",
                source_url=None,
                file_path=file_path,
                content_hash=result.content_hash,
                extra={"pages": result.pages, "tables": result.tables, "parse_error": result.error},
                provenance={
                    "source_path": result.source_path,
                    "parsed_at": __import__("datetime").datetime.utcnow().isoformat(),
                    "content_hash": result.content_hash,
                },
            )
            db.add(artifact)
            await db.commit()

        import os
        os.makedirs("workspace/raw/documents", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)

        return file_path
