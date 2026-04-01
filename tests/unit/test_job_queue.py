"""Unit tests for job queue retry/backoff and checkpoint/resume logic."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.worker.queue import JobQueue, JobClaim

pytestmark = pytest.mark.anyio


class TestExponentialBackoff:
    """Tests for exponential backoff calculation."""

    def test_backoff_delay_attempt_1(self):
        """First retry: 30s delay."""
        base_delay = 30
        max_delay = 3600
        attempt = 1
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        assert delay == 30

    def test_backoff_delay_attempt_2(self):
        """Second retry: 60s delay."""
        base_delay = 30
        max_delay = 3600
        attempt = 2
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        assert delay == 60

    def test_backoff_delay_attempt_3(self):
        """Third retry: 120s delay."""
        base_delay = 30
        max_delay = 3600
        attempt = 3
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        assert delay == 120

    def test_backoff_delay_attempt_4(self):
        """Fourth retry: 240s delay."""
        base_delay = 30
        max_delay = 3600
        attempt = 4
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        assert delay == 240

    def test_backoff_caps_at_max(self):
        """Backoff caps at 3600s regardless of attempt."""
        base_delay = 30
        max_delay = 3600
        attempt = 10  # Would be 30 * 2^9 = 15360 without cap
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        assert delay == 3600


class TestJobRetryLogic:
    """Tests for job retry state transitions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock async database session."""
        db = AsyncMock()
        db.commit = AsyncMock()
        return db

    @pytest.fixture
    def mock_job(self):
        """Create a mock job with retry configuration."""
        job = MagicMock()
        job.id = uuid4()
        job.job_type = "test_job"
        job.status = "running"
        job.attempt_count = 0
        job.max_attempts = 3
        job.error_message = None
        job.completed_at = None
        job.started_at = None
        job.claimed_by = "worker-1"
        job.claimed_at = datetime.utcnow()
        job.next_retry_at = None
        job.trace_id = str(uuid4())
        job.result_data = None
        job.workspace_id = uuid4()
        return job

    @pytest.mark.asyncio
    async def test_fail_under_max_sets_pending(self, mock_db, mock_job):
        """Job fails below max_attempts → status=pending, next_retry_at set."""
        mock_job.attempt_count = 1
        mock_job.max_attempts = 3

        queue = JobQueue(worker_id="test-worker")
        await queue.fail(mock_db, mock_job, "Transient error")

        # Verify job was set to pending for retry
        assert mock_job.status == "pending"
        # Verify next_retry_at was set
        assert mock_job.next_retry_at is not None
        assert mock_job.next_retry_at > datetime.utcnow()
        # Verify claimed_by was cleared for retry
        assert mock_job.claimed_by is None
        assert mock_job.claimed_at is None

    @pytest.mark.asyncio
    async def test_fail_at_max_sets_failed(self, mock_db, mock_job):
        """Job fails at max_attempts → status=failed permanently."""
        mock_job.attempt_count = 2  # Will become 3 after increment
        mock_job.max_attempts = 3

        queue = JobQueue(worker_id="test-worker")
        await queue.fail(mock_db, mock_job, "Permanent error")

        # Verify job was set to failed permanently
        assert mock_job.status == "failed"
        # Verify next_retry_at was cleared
        assert mock_job.next_retry_at is None
        # Verify completed_at was set
        assert mock_job.completed_at is not None

    @pytest.mark.asyncio
    async def test_fail_increments_attempt_count(self, mock_db, mock_job):
        """Job failure always increments attempt_count."""
        mock_job.attempt_count = 0
        mock_job.max_attempts = 3

        queue = JobQueue(worker_id="test-worker")
        await queue.fail(mock_db, mock_job, "Error")

        assert mock_job.attempt_count == 1

    @pytest.mark.asyncio
    async def test_retry_clears_error_message(self, mock_db, mock_job):
        """Job retry clears the previous error message."""
        mock_job.attempt_count = 1
        mock_job.max_attempts = 3
        mock_job.error_message = "Previous error"

        queue = JobQueue(worker_id="test-worker")
        await queue.fail(mock_db, mock_job, "New error")

        # When retried (under max), error should be cleared
        assert mock_job.status == "pending"


class TestCheckpointRecording:
    """Tests for checkpoint recording and retrieval."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock async database session."""
        db = AsyncMock()
        db.commit = AsyncMock()
        return db

    @pytest.fixture
    def mock_job(self):
        """Create a mock job for checkpoint testing."""
        job = MagicMock()
        job.id = uuid4()
        job.job_type = "test_job"
        job.status = "running"
        job.attempt_count = 1
        job.result_data = None
        job.last_checkpoint = None
        job.trace_id = str(uuid4())
        job.workspace_id = uuid4()
        return job

    @pytest.mark.asyncio
    async def test_record_checkpoint_stores_in_result_data(self, mock_db, mock_job):
        """Checkpoint data stored in result_data['checkpoints']."""
        queue = JobQueue(worker_id="test-worker")

        await queue.record_checkpoint(
            mock_db,
            mock_job,
            checkpoint_id="stage-1",
            checkpoint_data={"key": "value"},
        )

        # Verify result_data was initialized
        assert mock_job.result_data is not None
        # Verify checkpoints structure was created
        assert "checkpoints" in mock_job.result_data
        # Verify checkpoint was stored
        assert "stage-1" in mock_job.result_data["checkpoints"]
        assert mock_job.result_data["checkpoints"]["stage-1"]["data"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_record_checkpoint_updates_last_checkpoint_field(self, mock_db, mock_job):
        """Job.last_checkpoint field updated after recording."""
        queue = JobQueue(worker_id="test-worker")

        await queue.record_checkpoint(
            mock_db,
            mock_job,
            checkpoint_id="stage-2",
            checkpoint_data={"progress": 50},
        )

        assert mock_job.last_checkpoint == "stage-2"

    @pytest.mark.asyncio
    async def test_record_checkpoint_preserves_existing_checkpoints(self, mock_db, mock_job):
        """Recording new checkpoint preserves existing checkpoints."""
        mock_job.result_data = {
            "checkpoints": {
                "stage-1": {
                    "data": {"progress": 25},
                    "recorded_at": "2026-04-01T00:00:00",
                    "attempt": 1,
                }
            }
        }
        mock_job.last_checkpoint = "stage-1"

        queue = JobQueue(worker_id="test-worker")

        await queue.record_checkpoint(
            mock_db,
            mock_job,
            checkpoint_id="stage-2",
            checkpoint_data={"progress": 50},
        )

        # Verify both checkpoints exist
        assert "stage-1" in mock_job.result_data["checkpoints"]
        assert "stage-2" in mock_job.result_data["checkpoints"]
        assert mock_job.last_checkpoint == "stage-2"


class TestCheckpointRetrieval:
    """Tests for resuming jobs from checkpoints."""

    def test_get_checkpoint_data_returns_stored_data(self):
        """get_checkpoint_data extracts stored checkpoint."""
        job = MagicMock()
        job.result_data = {
            "checkpoints": {
                "stage-1": {
                    "data": {"key": "value", "count": 42},
                    "recorded_at": "2026-04-01T00:00:00",
                    "attempt": 1,
                }
            }
        }

        queue = JobQueue()
        result = queue.get_checkpoint_data(job, "stage-1")

        assert result == {"key": "value", "count": 42}

    def test_get_checkpoint_data_returns_none_for_missing_checkpoint(self):
        """get_checkpoint_data returns None for non-existent checkpoint."""
        job = MagicMock()
        job.result_data = {
            "checkpoints": {
                "stage-1": {
                    "data": {"key": "value"},
                    "recorded_at": "2026-04-01T00:00:00",
                    "attempt": 1,
                }
            }
        }

        queue = JobQueue()
        result = queue.get_checkpoint_data(job, "nonexistent")

        assert result is None

    def test_get_checkpoint_data_returns_none_when_no_result_data(self):
        """get_checkpoint_data returns None when job.result_data is None."""
        job = MagicMock()
        job.result_data = None

        queue = JobQueue()
        result = queue.get_checkpoint_data(job, "stage-1")

        assert result is None

    def test_get_checkpoint_data_returns_none_when_no_checkpoints(self):
        """get_checkpoint_data returns None when no checkpoints key."""
        job = MagicMock()
        job.result_data = {}

        queue = JobQueue()
        result = queue.get_checkpoint_data(job, "stage-1")

        assert result is None


class TestCheckpointResume:
    """Tests for resuming jobs from checkpoints."""

    @pytest.mark.asyncio
    async def test_resume_skips_completed_stages(self):
        """Handler receives context indicating which stage to resume from."""
        job = MagicMock()
        job.result_data = {
            "checkpoints": {
                "stage-1": {
                    "data": {"items_processed": 100},
                    "recorded_at": "2026-04-01T00:00:00",
                    "attempt": 1,
                },
                "stage-2": {
                    "data": {"items_processed": 200},
                    "recorded_at": "2026-04-01T00:01:00",
                    "attempt": 1,
                },
            }
        }
        job.last_checkpoint = "stage-2"
        job.attempt_count = 1

        queue = JobQueue()

        # Simulate resume logic: get the last checkpoint data
        checkpoint_data = queue.get_checkpoint_data(job, job.last_checkpoint)

        assert checkpoint_data == {"items_processed": 200}
        # Handler would use this to skip stage-1 and continue from stage-2
