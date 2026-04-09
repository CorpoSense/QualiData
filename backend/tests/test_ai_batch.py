"""Tests for AI batch processing: ProgressStream, JobManager, batch endpoints."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.progress import JobManager, JobState, JobStatus, sse_event


class TestJobManager:
    """Test JobManager state tracking."""

    def test_create_job(self):
        mgr = JobManager()
        job = mgr.create(total=10)
        assert job.status == JobStatus.PENDING
        assert job.total == 10
        assert job.completed == 0
        assert job.job_id  # non-empty

    def test_get_job(self):
        mgr = JobManager()
        job = mgr.create(total=5)
        assert mgr.get(job.job_id) is job

    def test_get_missing(self):
        mgr = JobManager()
        assert mgr.get("nonexistent") is None

    def test_update_job(self):
        mgr = JobManager()
        job = mgr.create(total=10)
        mgr.update(job.job_id, completed=3, status=JobStatus.RUNNING)
        updated = mgr.get(job.job_id)
        assert updated.completed == 3
        assert updated.status == JobStatus.RUNNING

    def test_percentage(self):
        job = JobState(job_id="test", total=10, completed=3, failed=1)
        assert job.percentage == 40  # (3+1)/10 * 100

    def test_percentage_zero_total(self):
        job = JobState(job_id="test", total=0)
        assert job.percentage == 0

    def test_to_dict(self):
        job = JobState(job_id="test", total=10, completed=5, failed=1, current_row=60)
        d = job.to_dict()
        assert d["job_id"] == "test"
        assert d["total"] == 10
        assert d["completed"] == 5
        assert d["failed"] == 1
        assert d["percentage"] == 60
        assert d["current_row"] == 60


class TestSSEFormat:
    """Test SSE event formatting."""

    def test_sse_event_format(self):
        result = sse_event("progress", {"completed": 5, "total": 10})
        assert result.startswith("event: progress\n")
        assert "data: " in result
        data = json.loads(result.split("data: ")[1].strip())
        assert data["completed"] == 5


class TestBatchEndpoint:
    """Test POST /ai-batch validation."""

    @pytest.mark.asyncio
    async def test_batch_requires_process_all(self):
        """Calling /ai-batch without process_all should return 400."""
        from app.routers.ai_operations import start_ai_batch

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(
            id="ds-1", project_id="proj-1", data_json={"data": [{"a": 1}]}, columns=[]
        )
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(Exception) as exc_info:
            await start_ai_batch(
                dataset_id="ds-1",
                request=MagicMock(
                    column_list=["a"],
                    process_all=False,
                ),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert "process_all=true" in str(exc_info.value.detail)
