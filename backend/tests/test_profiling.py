"""Tests for profiling endpoint - ensure total_rows reflects actual row count, not truncated preview."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


client = TestClient(app)


class TestProfilingTotalRows:
    """Test that profiling endpoint returns correct total_rows based on dataset.row_count, not preview_data."""

    @pytest.mark.asyncio
    async def test_profile_uses_row_count_not_preview_length(self):
        """
        Regression test: The profile endpoint should use dataset.row_count for total_rows,
        not len(preview_data) which is limited to 500 rows.
        
        This test verifies that:
        - A dataset with row_count=1000 but preview_data limited to 500 rows
        - The profile endpoint returns total_rows=1000 (not 500)
        """
        from app.routers.profiling import profile_columns
        from app.db.models import Dataset, Project
        
        # Mock dataset with 1000 actual rows but only 500 in preview_data
        mock_dataset = MagicMock(spec=Dataset)
        mock_dataset.id = "test-dataset-id"
        mock_dataset.project_id = "test-project-id"
        mock_dataset.preview_data = [{"id": i, "value": f"row_{i}"} for i in range(500)]  # Only 500 preview rows
        mock_dataset.row_count = 1000  # Actual row count is 1000
        mock_dataset.columns = [{"name": "id", "dtype": "int"}, {"name": "value", "dtype": "str"}]
        
        # Mock project
        mock_project = MagicMock(spec=Project)
        mock_project.id = "test-project-id"
        mock_project.user_id = "test-user-id"
        
        # Mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        # Track call count to return different results
        call_count = [0]
        
        async def mock_execute(query):
            query_str = str(query)
            result = MagicMock()
            if "project" in query_str.lower() and "user" in query_str.lower():
                result.scalar_one_or_none.return_value = mock_project
            elif "dataset" in query_str.lower():
                result.scalar_one_or_none.return_value = mock_dataset
            return result
        
        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        
        # Call the profile function
        response = await profile_columns(
            dataset_id="test-dataset-id",
            current_user=mock_user,
            session=mock_session
        )
        
        # Assert: total_rows should be 1000 (from dataset.row_count), not 500 (from preview_data)
        assert response.total_rows == 1000, f"Expected total_rows=1000, got {response.total_rows}"
        assert response.total_rows != len(mock_dataset.preview_data), "total_rows should not equal preview_data length"
        
        # Also verify each column profile has correct total_rows
        for col in response.columns:
            assert col.total_rows == 1000, f"Column {col.name} has wrong total_rows: {col.total_rows}"
        
        # Verify total_columns is returned
        assert response.total_columns == 2, f"Expected total_columns=2, got {response.total_columns}"

    @pytest.mark.asyncio
    async def test_profile_uses_row_count_when_zero(self):
        """Test profile handles edge case when row_count is 0 but preview has data."""
        from app.routers.profiling import profile_columns
        from app.db.models import Dataset, Project
        
        # Mock dataset with row_count=0
        mock_dataset = MagicMock(spec=Dataset)
        mock_dataset.id = "test-dataset-id"
        mock_dataset.project_id = "test-project-id"
        mock_dataset.preview_data = [{"id": 1}]  # Has some preview data
        mock_dataset.row_count = 0  # But row_count says 0
        mock_dataset.columns = [{"name": "id", "dtype": "int"}]
        
        mock_project = MagicMock(spec=Project)
        mock_project.id = "test-project-id"
        mock_project.user_id = "test-user-id"
        
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        call_count = [0]
        
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "project" in query_str.lower() and "user" in query_str.lower():
                result.scalar_one_or_none.return_value = mock_project
            elif "dataset" in query_str.lower():
                result.scalar_one_or_none.return_value = mock_dataset
            return result
        
        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        
        response = await profile_columns(
            dataset_id="test-dataset-id",
            current_user=mock_user,
            session=mock_session
        )
        
        # When row_count is 0 (falsy), should fallback to len(df) which is 1
        assert response.total_rows == 1, f"Expected total_rows=1 (fallback), got {response.total_rows}"


class TestProfilingEndpoint:
    """Test the profiling HTTP endpoint."""

    def test_profile_endpoint_requires_auth(self):
        """Test that profile endpoint requires authentication."""
        response = client.get("/api/datasets/1/profile")
        # Should fail auth, not 404
        assert response.status_code in [401, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
