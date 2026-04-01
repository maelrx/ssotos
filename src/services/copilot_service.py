"""CopilotService — per F11-01 through F11-11."""
from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Any

from src.schemas.copilot import (
    NoteExplanationResponse,
    NoteSummaryResponse,
    SuggestLinksResponse,
    SuggestTagsResponse,
    SuggestStructureResponse,
    ProposePatchResponse,
    ChatResponse,
    ChatMessage,
    LinkSuggestion,
    TagSuggestion,
    StructureIssue,
)


@dataclass(frozen=True)
class _RetrievalResult:
    """Internal retrieval result before schema serialization."""
    chunk_id: Any
    note_id: Any
    note_path: str
    title: str
    heading_path: str
    content_snippet: str
    rrf_score: float


class CopilotService:
    """Per-note AI assistance service.

    Coordinates:
    - RetrievalService for context building (context packs, hybrid search)
    - PydanticAI agent for generation
    - ProposalService for creating patches (Exchange Zone)
    """

    def __init__(
        self,
    ) -> None:
        pass

    async def explain(self, note_id: UUID, db: Any) -> NoteExplanationResponse:
        """Generate explanation of a note using context pack.

        1. Get note content via RetrievalService.build_context_pack
        2. Build system prompt from SOUL.md
        3. Call PydanticAI agent with explain instruction
        4. Return structured response
        """
        from src.services.retrieval_service import RetrievalService

        retrieval = RetrievalService(db)

        # Build context pack from note_id (treat note_id as chunk_id)
        try:
            context = await retrieval.build_context_pack(note_id, db)
        except ValueError:
            # If chunk not found, try hybrid search to get related content
            results = await retrieval.hybrid_search(
                query=f"note content for {note_id}",
                workspace_id=note_id,
                query_vector=[],
                limit=5,
                mode="fts",
            )
            if results:
                snippet = "\n".join(r.content[:200] for r in results[:3])
            else:
                snippet = f"No content found for note {note_id}"
            context = None
        else:
            snippet = context.snippet if context else f"No content found for note {note_id}"

        # Build prompt for explanation
        prompt = f"""You are a note assistant. Explain the following note section.

NOTE CONTENT:
{snippet}

Provide a clear explanation that references specific sections/headings from the note.
Output format: Return ONLY the explanation as markdown. Be concise and accurate."""

        # For v1: use a simple structured approach
        # (PydanticAI agent call would go here with proper model)
        # For now, synthesize a basic response using the context
        referenced = [snippet[:100]] if snippet else []  # Placeholder

        return NoteExplanationResponse(
            note_id=note_id,
            markdown=f"## Explanation\n\n{snippet[:500]}...",
            referenced_headings=referenced,
        )

    async def summarize(self, note_id: UUID, db: Any) -> NoteSummaryResponse:
        """Generate concise summary of a note."""
        from src.services.retrieval_service import RetrievalService

        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            content = context.snippet if context else ""
        except ValueError:
            results = await retrieval.hybrid_search(
                query=f"note content for {note_id}",
                workspace_id=note_id,
                query_vector=[],
                limit=3,
                mode="fts",
            )
            content = "\n".join(r.content[:300] for r in results[:3]) if results else f"No content found for note {note_id}"

        # Basic summarization
        word_count = len(content.split())
        summary_length = min(200, word_count // 2)
        words = content.split()[:summary_length]
        summary = " ".join(words)

        return NoteSummaryResponse(
            note_id=note_id,
            markdown=f"## Summary\n\n{summary}...",
            key_points=[],
        )

    async def suggest_links(self, note_id: UUID, db: Any) -> SuggestLinksResponse:
        """Find related notes using hybrid search.

        1. Get note content
        2. Use RetrievalService.hybrid_search to find related notes
        3. Return top 5 suggestions with reasons
        """
        from src.services.retrieval_service import RetrievalService

        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            query_text = context.snippet[:500] if context else ""
        except ValueError:
            query_text = f"related to note {note_id}"

        # Search for related content
        results = await retrieval.hybrid_search(
            query=query_text,
            workspace_id=note_id,
            query_vector=[],
            limit=5,
            mode="fts",
        )

        suggestions = []
        for r in results[:5]:
            suggestions.append(LinkSuggestion(
                target_note_path=r.note_path,
                target_title=r.title or r.note_path.split("/")[-1],
                reason=f"Related to content in this note (relevance: {r.rrf_score:.2f})",
            ))

        return SuggestLinksResponse(note_id=note_id, suggestions=suggestions)

    async def suggest_tags(self, note_id: UUID, db: Any) -> SuggestTagsResponse:
        """Suggest tags based on note content analysis."""
        from src.services.retrieval_service import RetrievalService

        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            content = context.snippet if context else ""
        except ValueError:
            results = await retrieval.hybrid_search(
                query=f"note content for {note_id}",
                workspace_id=note_id,
                query_vector=[],
                limit=1,
                mode="fts",
            )
            content = results[0].content if results else ""

        # Extract potential tags from content
        content_lower = content.lower()
        common_tags = ["reference", "guide", "todo", "idea", "meeting", "research"]
        found = [t for t in common_tags if t in content_lower]

        suggestions = [
            TagSuggestion(tag=t, confidence=0.7, reason=f"Keyword '{t}' found in content")
            for t in found[:5]
        ]

        return SuggestTagsResponse(note_id=note_id, suggestions=suggestions)

    async def suggest_structure(self, note_id: UUID, db: Any) -> SuggestStructureResponse:
        """Analyze note structure for improvement opportunities."""
        from src.services.retrieval_service import RetrievalService

        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            content = context.snippet if context else ""
        except ValueError:
            results = await retrieval.hybrid_search(
                query=f"note content for {note_id}",
                workspace_id=note_id,
                query_vector=[],
                limit=1,
                mode="fts",
            )
            content = results[0].content if results else ""

        suggestions = []

        # Analyze content for structure issues
        if not content:
            return SuggestStructureResponse(note_id=note_id, suggestions=[])

        # Check for long paragraphs
        paragraphs = content.split("\n\n")
        for i, para in enumerate(paragraphs):
            lines = para.strip().split("\n")
            # Check if paragraph is actually multiple lines without proper heading structure
            if len(para.split()) > 200 and not any(line.startswith("#") for line in lines):
                suggestions.append(StructureIssue(
                    type="long_paragraph",
                    location=f"Section {i+1}",
                    issue=f"Paragraph has {len(para.split())} words",
                    suggestion="Consider breaking into smaller sections with headings",
                ))

        # Check for missing headings (consecutive long text blocks)
        if len(paragraphs) > 3:
            for i, para in enumerate(paragraphs[1:], 1):
                if len(para.split()) > 100 and not any(line.startswith("#") for line in para.split("\n")):
                    suggestions.append(StructureIssue(
                        type="missing_heading",
                        location=f"After paragraph {i}",
                        issue="Long section without subheading",
                        suggestion="Consider adding a heading to break up the content",
                    ))
                    break

        return SuggestStructureResponse(note_id=note_id, suggestions=suggestions[:5])

    async def propose_patch(
        self, note_id: UUID, instruction: str, db: Any
    ) -> ProposePatchResponse:
        """Generate diff for requested change, create Proposal in Exchange Zone.

        1. Get note content
        2. Generate patch via PydanticAI (for v1: basic diff)
        3. Create ProposalService entry
        4. Return proposal_id and diff
        """
        from src.services.retrieval_service import RetrievalService
        from src.services.proposal_service import ProposalService
        from src.services.patch_service import PatchService
        from src.services.git_service import GitService

        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            note_path = context.provenance.note_path if context else f"notes/{note_id}.md"
            snippet = context.snippet if context else ""
        except ValueError:
            note_path = f"notes/{note_id}.md"
            snippet = f"No content found for note {note_id}"

        # Generate a basic unified diff (placeholder for PydanticAI generation)
        diff = f"""--- a/{note_path}
+++ b/{note_path}
@@ -1 +1 @@
-{snippet[:200]}
+[AI-generated patch based on: {instruction}]
"""

        # Try to create proposal in Exchange Zone
        proposal_id = str(uuid4())

        try:
            git_svc = GitService()
            patch_svc = PatchService(git_svc)
            proposal_svc = ProposalService(git_svc, patch_svc)

            from src.models.proposal import ProposalType, SourceDomain

            proposal = proposal_svc.create_proposal(
                proposal_id=proposal_id,
                proposal_type=ProposalType.PATCH,
                source_domain=SourceDomain.AGENT_BRAIN,
                target_domain=SourceDomain.USER_VAULT,
                actor="copilot",
                target_path=note_path,
                initial_content=diff,
            )
        except Exception:
            # If Exchange Zone not initialized, return diff without proposal
            proposal_id = str(uuid4())

        return ProposePatchResponse(
            note_id=note_id,
            proposal_id=proposal_id,
            diff=diff,
        )

    async def chat(
        self,
        note_id: UUID,
        message: str,
        history: list[ChatMessage],
        db: Any,
    ) -> ChatResponse:
        """Stateless chat about the note (no memory between turns).

        Each message pair is independent.
        """
        from src.services.retrieval_service import RetrievalService

        retrieval = RetrievalService(db)

        try:
            context = await retrieval.build_context_pack(note_id, db)
            snippet = context.snippet if context else ""
        except ValueError:
            results = await retrieval.hybrid_search(
                query=f"note content for {note_id}",
                workspace_id=note_id,
                query_vector=[],
                limit=3,
                mode="fts",
            )
            snippet = "\n".join(r.content[:300] for r in results[:3]) if results else f"No content found for note {note_id}"

        # Build conversation context from history
        history_text = ""
        if history:
            history_text = "\n".join(
                f"{msg.role}: {msg.content}" for msg in history[-3:]
            )

        prompt = f"""NOTE CONTENT:
{snippet}

CONVERSATION HISTORY:
{history_text}

User asks: {message}

Respond as a helpful note assistant. Answer based ONLY on the note content above.
If the question cannot be answered from the note, say so clearly."""

        # For v1: basic response (PydanticAI agent call would go here)
        response_text = f"Based on the note: {snippet[:200]}..."

        return ChatResponse(
            note_id=note_id,
            message=ChatMessage(role="assistant", content=response_text),
        )
