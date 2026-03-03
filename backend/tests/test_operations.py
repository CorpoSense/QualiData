"""Tests for data operations endpoints - route validation."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


client = TestClient(app)


class TestOperationsRoutes:
    """Test that operation routes are registered."""

    def test_add_column_requires_auth(self):
        """Test add column requires authentication."""
        response = client.post(
            "/api/datasets/1/operations/add-column",
            json={"name": "new_col", "dtype": "string"}
        )
        assert response.status_code == 401

    def test_remove_columns_requires_auth(self):
        """Test remove columns requires authentication."""
        response = client.post(
            "/api/datasets/1/operations/remove-columns",
            json={"columns": ["col1"]}
        )
        assert response.status_code == 401

    def test_rename_column_requires_auth(self):
        """Test rename column requires authentication."""
        response = client.post(
            "/api/datasets/1/operations/rename-column",
            json={"old_name": "col1", "new_name": "new_col"}
        )
        assert response.status_code == 401

    def test_history_requires_auth(self):
        """Test operation history requires authentication."""
        response = client.get("/api/datasets/1/operations/history")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
