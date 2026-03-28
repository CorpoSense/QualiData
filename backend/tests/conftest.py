"""Pytest configuration for tests."""

import os

# Set test database before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# Create mock user
mock_user = MagicMock()
mock_user.id = "test-user-id"
mock_user.email = "test@example.com"
mock_user.is_active = True


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication for tests."""
    # Patch the oauth2_scheme to return a valid token
    with patch("app.routers.auth.oauth2_scheme", return_value="test-token"):
        # Patch the get_current_user to return our mock user
        with patch("app.routers.auth.get_current_user", return_value=mock_user):
            yield mock_user


@pytest.fixture
def mock_session():
    """Mock database session for tests."""
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
    
    with patch("app.routers.datasets.get_async_session", return_value=mock_session):
        yield mock_session
