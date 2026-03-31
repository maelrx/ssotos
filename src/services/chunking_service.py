"""Chunking service — D-101, D-102, D-103.

Heading-guided chunking with 512 token max and 50 token overlap.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# --- Token counting ---


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken for accurate counting.

    Falls back to approximate chars/4 for non-OpenAI models.
    """
    try:
        import tiktoken

        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except (ImportError, KeyError):
        # Fallback: approximate 1 token ≈ 4 chars for English
        return len(text) // 4


# --- Break point finding ---


def find_break_point(text: str, start: int, end: int) -> int:
    """Find a good split point near 'end' using priority: paragraph > sentence > word.

    Returns the break position, or 'end' if none found.
    """
    # Try paragraph break (\n\n) first
    paragraph_break = text.rfind("\n\n", start, end)
    if paragraph_break > start:
        return paragraph_break

    # Try sentence break (. or ! or ? followed by space)
    sentence_breaks = [
        text.rfind(". ", start, end),
        text.rfind("! ", start, end),
        text.rfind("? ", start, end),
    ]
    sentence_break = max(sentence_breaks)
    if sentence_break > start:
        return sentence_break + 2  # Include the period and space

    # Fall back to word boundary
    word_break = text.rfind(" ", start, end)
    if word_break > start:
        return word_break

    return end


# --- Chunk result dataclass ---


@dataclass(frozen=True)
class ChunkResult:
    """Result of a single chunk operation."""

    content: str
    heading_path: str
    chunk_index: int
    char_start: int
    char_end: int
    token_count: int


# --- Heading-guided chunking ---


def chunk_by_headings(
    markdown: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[ChunkResult]:
    """Split markdown into chunks at heading boundaries.

    Rules (D-101, D-102, D-103):
    - Split on H1 (#), H2 (##), H3 (###) boundaries
    - Max chunk size: max_tokens (default 512)
    - Overlap: overlap_tokens (default 50) between consecutive chunks
    - Sections <100 tokens are merged with next section
    """
    # Split by heading lines
    heading_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

    sections: list[tuple[int, int, str]] = []  # (char_start, char_start_of_next, heading_path)
    last_pos = 0
    last_heading = "## Untitled"  # Root heading for content before first heading

    for match in heading_pattern.finditer(markdown):
        heading_level = len(match.group(1))
        heading_text = match.group(2).strip()
        heading_path = f"{'#' * heading_level} {heading_text}"

        # The section runs from last_pos to match.start()
        if last_pos < match.start():
            sections.append((last_pos, match.start(), last_heading))

        last_pos = match.start()
        last_heading = heading_path

    # Last section goes to end of file
    sections.append((last_pos, len(markdown), last_heading))

    # Now split sections larger than max_tokens
    chunks: list[ChunkResult] = []
    chunk_index = 0
    overlap_chars = overlap_tokens * 4  # approximate chars for overlap_tokens

    for section_idx, (start, end, heading_path) in enumerate(sections):
        section_text = markdown[start:end]
        section_tokens = count_tokens(section_text)

        if section_tokens <= max_tokens:
            chunks.append(
                ChunkResult(
                    content=section_text,
                    heading_path=heading_path,
                    chunk_index=chunk_index,
                    char_start=start,
                    char_end=end,
                    token_count=section_tokens,
                )
            )
            chunk_index += 1
        else:
            # Split this section into smaller chunks with overlap
            char_limit = max_tokens * 4  # approximate chars per token
            pos = start

            while pos < end:
                chunk_end = min(pos + char_limit, end)

                # Try to break at a paragraph or sentence boundary
                if chunk_end < end:
                    break_point = find_break_point(markdown, pos, chunk_end)
                    if break_point > pos:
                        chunk_end = break_point

                chunk_text = markdown[pos:chunk_end]
                chunk_tokens = count_tokens(chunk_text)

                chunks.append(
                    ChunkResult(
                        content=chunk_text,
                        heading_path=heading_path,
                        chunk_index=chunk_index,
                        char_start=pos,
                        char_end=chunk_end,
                        token_count=chunk_tokens,
                    )
                )
                chunk_index += 1

                # Move pos with overlap
                pos = chunk_end - overlap_chars
                if pos <= chunks[-1].char_start:
                    # Prevent infinite loop - advance past last chunk start
                    pos = chunks[-1].char_start + 1

    # Merge very short sections (<100 tokens) with next section
    MERGE_THRESHOLD = 100
    merged_chunks: list[ChunkResult] = []
    pending_merge: ChunkResult | None = None

    for chunk in chunks:
        if pending_merge is not None:
            # Merge with current chunk
            merged_content = pending_merge.content + "\n\n" + chunk.content
            merged_tokens = count_tokens(merged_content)
            merged_chunks.append(
                ChunkResult(
                    content=merged_content,
                    heading_path=chunk.heading_path,
                    chunk_index=pending_merge.chunk_index,
                    char_start=pending_merge.char_start,
                    char_end=chunk.char_end,
                    token_count=merged_tokens,
                )
            )
            pending_merge = None
        elif chunk.token_count < MERGE_THRESHOLD:
            # Mark for merging with next chunk
            pending_merge = chunk
        else:
            merged_chunks.append(chunk)

    # If last chunk is pending merge with nothing, keep it
    if pending_merge is not None:
        merged_chunks.append(pending_merge)

    # Re-index chunks
    final_chunks: list[ChunkResult] = []
    for i, chunk in enumerate(merged_chunks):
        final_chunks.append(
            ChunkResult(
                content=chunk.content,
                heading_path=chunk.heading_path,
                chunk_index=i,
                char_start=chunk.char_start,
                char_end=chunk.char_end,
                token_count=chunk.token_count,
            )
        )

    return final_chunks


# --- Frontmatter parsing ---


def parse_frontmatter(markdown: str) -> tuple[dict[str, object], str]:
    """Parse YAML frontmatter from markdown.

    Returns (frontmatter_dict, body_without_frontmatter).
    Handles ---...--- delimiters.
    """
    frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = frontmatter_pattern.match(markdown)

    if match:
        import yaml

        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            frontmatter = {}
        body = markdown[match.end() :]
        return frontmatter, body

    return {}, markdown


# --- Chunk model conversion ---


def markdown_to_chunks(
    markdown: str,
    note_projection_id: uuid.UUID,
) -> list["Chunk"]:
    """Convert markdown to full Chunk model instances ready for insertion.

    Args:
        markdown: The full markdown content including frontmatter
        note_projection_id: The note projection UUID to associate chunks with

    Returns:
        List of Chunk model instances
    """
    from src.db.models.chunk import Chunk

    # Parse and strip frontmatter
    _, body = parse_frontmatter(markdown)

    # Run heading-guided chunking
    chunk_results = chunk_by_headings(body)

    # Convert to Chunk model instances
    chunks = []
    for result in chunk_results:
        chunk = Chunk(
            note_projection_id=note_projection_id,
            heading_path=result.heading_path,
            content=result.content,
            chunk_index=result.chunk_index,
            char_start=result.char_start,
            char_end=result.char_end,
        )
        chunks.append(chunk)

    return chunks
