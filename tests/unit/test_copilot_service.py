"""Unit tests for CopilotService — F11-01 through F11-11."""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.copilot_service import CopilotService, _RetrievalResult
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

pytestmark = pytest.mark.anyio


def _fake_context_pack(note_id, snippet="Test note content for explanation"):
    """Build a fake ContextPack object."""
    fake = MagicMock()
    fake.snippet = snippet
    fake.provenance.note_path = f"notes/{note_id}.md"
    return fake


def _make_db_mock(workspace_id=None):
    """Build a db mock that properly handles async execute."""
    db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = workspace_id or uuid4()
    db.execute = AsyncMock(return_value=mock_result)
    return db


class TestCopilotService:
    """Test CopilotService methods."""

    def setup_method(self):
        """Set up fresh CopilotService instance before each test."""
        self.service = CopilotService()
        self.note_id = uuid4()
        self.workspace_id = uuid4()
        self.db = _make_db_mock(self.workspace_id)

    async def test_explain_returns_markdown(self):
        """explain() should return markdown and referenced_headings."""
        fake_context = _fake_context_pack(self.note_id)

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)

            result = await self.service.explain(self.note_id, self.db)

        assert isinstance(result, NoteExplanationResponse)
        assert result.note_id == self.note_id
        assert isinstance(result.markdown, str)
        assert len(result.markdown) > 0
        assert isinstance(result.referenced_headings, list)

    async def test_summarize_returns_summary(self):
        """summarize() should return markdown and key_points."""
        fake_context = _fake_context_pack(self.note_id, snippet="Content for summary test")

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)

            result = await self.service.summarize(self.note_id, self.db)

        assert isinstance(result, NoteSummaryResponse)
        assert result.note_id == self.note_id
        assert isinstance(result.markdown, str)
        assert "## Summary" in result.markdown
        assert isinstance(result.key_points, list)

    async def test_suggest_links_returns_suggestions(self):
        """suggest_links() should return list of LinkSuggestion objects."""
        fake_results = [
            _RetrievalResult(
                chunk_id=uuid4(),
                note_id=uuid4(),
                note_path="notes/related1.md",
                title="Related Note 1",
                heading_path="",
                content_snippet="Related content",
                rrf_score=0.95,
            ),
            _RetrievalResult(
                chunk_id=uuid4(),
                note_id=uuid4(),
                note_path="notes/related2.md",
                title="Related Note 2",
                heading_path="",
                content_snippet="More related content",
                rrf_score=0.88,
            ),
        ]

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(
                return_value=_fake_context_pack(self.note_id)
            )
            instance.hybrid_search = AsyncMock(return_value=fake_results)

            result = await self.service.suggest_links(self.note_id, self.db)

        assert isinstance(result, SuggestLinksResponse)
        assert result.note_id == self.note_id
        assert len(result.suggestions) == 2
        for s in result.suggestions:
            assert isinstance(s, LinkSuggestion)
            assert s.target_note_path
            assert s.target_title
            assert s.reason

    async def test_suggest_tags_returns_tags(self):
        """suggest_tags() should return list of TagSuggestion objects."""
        fake_context = _fake_context_pack(
            self.note_id, snippet="This is a reference guide for todo items"
        )

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)

            result = await self.service.suggest_tags(self.note_id, self.db)

        assert isinstance(result, SuggestTagsResponse)
        assert result.note_id == self.note_id
        assert len(result.suggestions) > 0
        for s in result.suggestions:
            assert isinstance(s, TagSuggestion)
            assert s.tag
            assert 0.0 <= s.confidence <= 1.0
            assert s.reason

    async def test_suggest_structure_returns_issues(self):
        """suggest_structure() should return structure issues."""
        # Long paragraph without heading
        long_content = " ".join(["word"] * 250)
        fake_context = _fake_context_pack(self.note_id, snippet=long_content)

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)

            result = await self.service.suggest_structure(self.note_id, self.db)

        assert isinstance(result, SuggestStructureResponse)
        assert result.note_id == self.note_id
        assert isinstance(result.suggestions, list)
        for issue in result.suggestions:
            assert isinstance(issue, StructureIssue)
            assert issue.type in ("missing_heading", "deeply_nested", "long_paragraph", "logical_gap")

    async def test_propose_patch_creates_proposal(self):
        """propose_patch() should return proposal_id and diff."""
        fake_context = _fake_context_pack(self.note_id)

        # Mock ProposalType to have PATCH attribute (workaround for non-existent enum value)
        mock_proposal_type = MagicMock()
        mock_proposal_type.PATCH = MagicMock()
        mock_proposal_type.NOTE_EDIT = MagicMock()

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval, \
             patch("src.services.proposal_service.ProposalService") as MockProposal, \
             patch("src.services.patch_service.PatchService"), \
             patch("src.services.git_service.GitService"), \
             patch("src.models.proposal.ProposalType", mock_proposal_type):

            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)

            # ProposalService.create_proposal returns a mock proposal
            mock_proposal = MagicMock()
            MockProposal.return_value.create_proposal.return_value = mock_proposal

            result = await self.service.propose_patch(
                self.note_id, "Add more details", self.db
            )

        assert isinstance(result, ProposePatchResponse)
        assert result.note_id == self.note_id
        assert result.proposal_id
        assert isinstance(result.diff, str)
        assert "---" in result.diff  # unified diff format

    async def test_propose_patch_raises_on_failure(self):
        """propose_patch() should re-raise exceptions from ProposalService after logging."""
        fake_context = _fake_context_pack(self.note_id)

        # Mock ProposalType to have PATCH attribute (workaround for non-existent enum value)
        mock_proposal_type = MagicMock()
        mock_proposal_type.PATCH = MagicMock()
        mock_proposal_type.NOTE_EDIT = MagicMock()

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval, \
             patch("src.services.proposal_service.ProposalService") as MockProposal, \
             patch("src.services.patch_service.PatchService"), \
             patch("src.services.git_service.GitService"), \
             patch("src.models.proposal.ProposalType", mock_proposal_type):

            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)
            MockProposal.return_value.create_proposal.side_effect = RuntimeError("Exchange Zone error")

            # propose_patch re-raises exceptions after logging
            with pytest.raises(RuntimeError, match="Exchange Zone error"):
                await self.service.propose_patch(
                    self.note_id, "Add more details", self.db
                )

    async def test_chat_returns_response(self):
        """chat() should return ChatResponse with ChatMessage."""
        fake_context = _fake_context_pack(self.note_id, snippet="Note content for chat")

        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(return_value=fake_context)

            result = await self.service.chat(
                self.note_id, "What is this about?", [], self.db
            )

        assert isinstance(result, ChatResponse)
        assert result.note_id == self.note_id
        assert isinstance(result.message, ChatMessage)
        assert result.message.role == "assistant"
        assert len(result.message.content) > 0

    async def test_explain_handles_missing_note(self):
        """explain() should handle ValueError from build_context_pack gracefully."""
        with patch("src.services.retrieval_service.RetrievalService") as MockRetrieval:
            instance = MockRetrieval.return_value
            instance.build_context_pack = AsyncMock(side_effect=ValueError("Not found"))
            instance.hybrid_search = AsyncMock(return_value=[])

            result = await self.service.explain(self.note_id, self.db)

        assert isinstance(result, NoteExplanationResponse)
        assert result.note_id == self.note_id
        assert "No content found" in result.markdown
