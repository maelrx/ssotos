"""Unit tests for approval service."""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.services.approval_service import ApprovalService

pytestmark = pytest.mark.anyio


def _make_mock_db_with_job(job):
    """Create a mock db that returns the given job from execute."""
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=job)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    return mock_db


def _make_mock_session_maker(mock_db):
    """Create a mock async_session_maker that yields the mock db."""
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_db)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    return mock_cm


class TestApprovalLifecycle:
    """Tests for approval request → approve/reject flow."""

    @pytest.fixture
    def mock_job(self):
        """Create a mock job for approval testing."""
        job = MagicMock()
        job.id = uuid4()
        job.job_type = "test_job"
        job.status = "running"
        job.approval_required = False
        job.approval_id = None
        return job

    @pytest.mark.asyncio
    async def test_request_approval_sets_job_status(self, mock_job):
        """request_approval() sets job to awaiting_approval."""
        mock_db = _make_mock_db_with_job(mock_job)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            approval_id = await service.request_approval(job_id=mock_job.id)

        # Verify approval_id was generated
        assert approval_id is not None
        assert len(approval_id) == 36  # UUID string length

        # Verify job fields were updated
        assert mock_job.approval_required is True
        assert mock_job.approval_id is not None
        assert mock_job.status == "awaiting_approval"

    @pytest.mark.asyncio
    async def test_request_approval_raises_for_missing_job(self):
        """request_approval() raises ValueError when job not found."""
        mock_db = _make_mock_db_with_job(None)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            with pytest.raises(ValueError, match="not found"):
                await service.request_approval(job_id=uuid4())

    @pytest.mark.asyncio
    async def test_approve_resumes_job(self, mock_job):
        """approve() transitions job back to pending."""
        # Setup: job is awaiting approval
        mock_job.status = "awaiting_approval"
        mock_job.approval_required = True
        mock_job.approval_id = uuid4()
        mock_job.claimed_by = "old-worker"

        mock_db = _make_mock_db_with_job(mock_job)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            await service.approve(approval_id=str(mock_job.approval_id))

        # Verify job was updated for resume
        assert mock_job.status == "pending"
        assert mock_job.claimed_by is None  # Cleared to allow any worker
        assert mock_job.approval_required is False
        # approval_id left intact for audit trail

    @pytest.mark.asyncio
    async def test_approve_raises_for_unknown_approval_id(self):
        """approve() raises ValueError when approval_id not found."""
        mock_db = _make_mock_db_with_job(None)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            with pytest.raises(ValueError, match="No job found for approval"):
                await service.approve(approval_id=str(uuid4()))

    @pytest.mark.asyncio
    async def test_reject_fails_job(self, mock_job):
        """reject() sets job status to failed with error_message."""
        # Setup: job is awaiting approval
        mock_job.status = "awaiting_approval"
        mock_job.approval_required = True
        mock_job.approval_id = uuid4()

        mock_db = _make_mock_db_with_job(mock_job)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            await service.reject(
                approval_id=str(mock_job.approval_id),
                resolution_note="Content policy violation",
            )

        # Verify job was failed
        assert mock_job.status == "failed"
        assert "Content policy violation" in mock_job.error_message
        assert mock_job.approval_required is False

    @pytest.mark.asyncio
    async def test_reject_raises_for_unknown_approval_id(self):
        """reject() raises ValueError when approval_id not found."""
        mock_db = _make_mock_db_with_job(None)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            with pytest.raises(ValueError, match="No job found for approval"):
                await service.reject(approval_id=str(uuid4()))

    @pytest.mark.asyncio
    async def test_reject_uses_default_message_when_no_note(self, mock_job):
        """reject() uses default message when resolution_note is None."""
        mock_job.status = "awaiting_approval"
        mock_job.approval_required = True
        mock_job.approval_id = uuid4()

        mock_db = _make_mock_db_with_job(mock_job)
        mock_session = _make_mock_session_maker(mock_db)

        with patch("src.services.approval_service.async_session_maker", return_value=mock_session):
            service = ApprovalService()
            await service.reject(approval_id=str(mock_job.approval_id), resolution_note=None)

        assert "No reason provided" in mock_job.error_message
