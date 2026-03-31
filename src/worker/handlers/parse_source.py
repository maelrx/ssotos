"""Handler for parse_source job type.

Parses a document source (PDF, DOCX, HTML, etc.) into Markdown.
Input: {workspace_id: UUID, source_path: str, source_type: str}
"""
from typing import Any
import structlog

logger = structlog.get_logger(__name__)

async def handle_parse_source(input_data: dict) -> dict:
    workspace_id = input_data.get("workspace_id")
    source_path = input_data.get("source_path")
    source_type = input_data.get("source_type")

    logger.info("parse_source_start", workspace_id=workspace_id, source_path=source_path, source_type=source_type)

    # Phase 8 (Research Runtime) will implement actual parsing with Docling/Crawl4AI
    # For now, simulate work and return success
    result = {
        "workspace_id": str(workspace_id),
        "source_path": source_path,
        "source_type": source_type,
        "markdown_content": "",
        "pages_processed": 0,
        "status": "placeholder",
        "note": "Full implementation comes in Phase 8 (Research Runtime)",
    }

    logger.info("parse_source_complete", workspace_id=workspace_id, source_path=source_path)
    return result
