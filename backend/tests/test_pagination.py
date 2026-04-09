"""Test pagination for datasets with more than 500 rows."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Import app from conftest (already patched)
from tests.conftest import app

client = TestClient(app)


def test_pagination_beyond_preview_data():
    """Test that pagination works correctly for datasets with more than 500 rows."""
    # Create mock user
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email = "test@example.com"
    mock_user.is_active = True
    
    # Create mock session
    mock_session = MagicMock()
    
    # Mock the execute method to return appropriate results
    async def mock_execute(query):
        result = MagicMock()
        query_str = str(query)
        if "dataset" in query_str.lower():
            # Return a mock dataset
            mock_dataset = MagicMock()
            mock_dataset.id = "test-dataset-id"
            mock_dataset.project_id = "test-project-id"
            mock_dataset.row_count = 1000
            mock_dataset.preview_data = [{"id": i, "value": f"row_{i}"} for i in range(500)]
            mock_dataset.data_json = {"data": [{"id": i, "value": f"row_{i}"} for i in range(1000)]}
            mock_dataset.columns = [{"name": "id", "dtype": "int"}, {"name": "value", "dtype": "str"}]
            result.scalar_one_or_none.return_value = mock_dataset
        elif "project" in query_str.lower():
            # Return a mock project
            mock_project = MagicMock()
            mock_project.id = "test-project-id"
            mock_project.user_id = "test-user-id"
            result.scalar_one_or_none.return_value = mock_project
        return result
    
    mock_session.execute = mock_execute
    
    # Override dependencies
    from app.routers.auth import get_current_active_user
    from app.routers.datasets import get_async_session
    
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    app.dependency_overrides[get_async_session] = lambda: mock_session
    
    try:
        # Test page 1 (rows 0-9)
        response = client.get(
            "/api/datasets/test-dataset-id/preview",
            params={"limit": 10, "page": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 10
        assert data["row_count"] == 1000
        assert data["preview_data"][0]["id"] == 0

        # Test page 50 (rows 490-499) - last page of preview_data
        response = client.get(
            "/api/datasets/test-dataset-id/preview",
            params={"limit": 10, "page": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 10
        assert data["preview_data"][0]["id"] == 490

        # Test page 51 (rows 500-509) - should use data_json
        response = client.get(
            "/api/datasets/test-dataset-id/preview",
            params={"limit": 10, "page": 51},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 10, f"Expected 10 rows, got {len(data['preview_data'])}"
        assert data["preview_data"][0]["id"] == 500, f"Expected id=500, got {data['preview_data'][0]['id']}"

        # Test page 100 (rows 990-999) - last page
        response = client.get(
            "/api/datasets/test-dataset-id/preview",
            params={"limit": 10, "page": 100},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 10
        assert data["preview_data"][0]["id"] == 990

        # Test page 101 (rows 1000-1009) - should return empty
        response = client.get(
            "/api/datasets/test-dataset-id/preview",
            params={"limit": 10, "page": 101},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 0
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()


def test_pagination_with_data_json():
    """Test that pagination works correctly when data_json is available."""
    # Create mock user
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email = "test@example.com"
    mock_user.is_active = True
    
    # Create mock session
    mock_session = MagicMock()
    
    # Mock the execute method to return appropriate results
    async def mock_execute(query):
        result = MagicMock()
        query_str = str(query)
        if "dataset" in query_str.lower():
            # Return a mock dataset with only preview_data
            mock_dataset = MagicMock()
            mock_dataset.id = "test-dataset-id-2"
            mock_dataset.project_id = "test-project-id-2"
            mock_dataset.row_count = 100
            mock_dataset.data_json = {"data": [{"id": i, "value": f"row_{i}"} for i in range(100)]}
            mock_dataset.columns = [{"name": "id", "dtype": "int"}, {"name": "value", "dtype": "str"}]
            result.scalar_one_or_none.return_value = mock_dataset
        elif "project" in query_str.lower():
            # Return a mock project
            mock_project = MagicMock()
            mock_project.id = "test-project-id-2"
            mock_project.user_id = "test-user-id"
            result.scalar_one_or_none.return_value = mock_project
        return result
    
    mock_session.execute = mock_execute
    
    # Override dependencies
    from app.routers.auth import get_current_active_user
    from app.routers.datasets import get_async_session
    
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    app.dependency_overrides[get_async_session] = lambda: mock_session
    
    try:
        # Test page 1 (rows 0-9)
        response = client.get(
            "/api/datasets/test-dataset-id-2/preview",
            params={"limit": 10, "page": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 10
        assert data["row_count"] == 100

        # Test page 10 (rows 90-99) - last page
        response = client.get(
            "/api/datasets/test-dataset-id-2/preview",
            params={"limit": 10, "page": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 10
        assert data["preview_data"][0]["id"] == 90

        # Test page 11 (rows 100-109) - should return empty
        response = client.get(
            "/api/datasets/test-dataset-id-2/preview",
            params={"limit": 10, "page": 11},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_data"]) == 0
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()
