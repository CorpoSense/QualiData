"""Tests for additional routes - route validation."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


client = TestClient(app)


class TestDatasetRoutes:
    """Test dataset routes require authentication."""

    def test_list_requires_auth(self):
        """Test listing datasets requires authentication."""
        response = client.get("/api/datasets?project_id=1")
        assert response.status_code == 401

    def test_import_requires_auth(self):
        """Test importing dataset requires authentication."""
        response = client.post("/api/datasets/import/single")
        assert response.status_code == 401

    def test_preview_requires_auth(self):
        """Test preview requires authentication."""
        response = client.get("/api/datasets/1/preview")
        assert response.status_code == 401

    def test_export_requires_auth(self):
        """Test export requires authentication."""
        response = client.get("/api/datasets/1/export")
        assert response.status_code == 401

    def test_delete_requires_auth(self):
        """Test delete requires authentication."""
        response = client.delete("/api/datasets/1")
        assert response.status_code == 401


class TestOperationsRoutes:
    """Test operations routes."""

    def test_operations_history_requires_auth(self):
        """Test operations history requires authentication."""
        response = client.get("/api/datasets/1/operations/history")
        assert response.status_code == 401

    def test_add_column_requires_auth(self):
        """Test add column requires authentication."""
        response = client.post("/api/datasets/1/operations/add-column")
        assert response.status_code == 401


class TestHealthRoute:
    """Test health endpoint."""

    def test_health_no_auth_required(self):
        """Test health endpoint works without auth."""
        response = client.get("/api/health")
        assert response.status_code == 200


class TestProjectsEdgeCases:
    """Test projects edge cases."""

    def test_create_project_unauthenticated(self):
        """Test create project without auth."""
        response = client.post("/api/projects", json={"name": "Test"})
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
