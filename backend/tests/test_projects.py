"""Tests for projects endpoints - route validation."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import get_app_routes

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


client = TestClient(app)


class TestProjectRoutes:
    """Test that project routes are registered."""

    def test_list_requires_auth(self):
        """Test list projects requires authentication."""
        response = client.get("/api/projects")
        assert response.status_code == 401

    def test_get_requires_auth(self):
        """Test get project requires authentication."""
        response = client.get("/api/projects/1")
        assert response.status_code == 401

    def test_create_requires_auth(self):
        """Test create project requires authentication."""
        response = client.post("/api/projects", json={"name": "Test Project"})
        assert response.status_code == 401

    def test_update_requires_auth(self):
        """Test update project requires authentication."""
        response = client.put("/api/projects/1", json={"name": "Updated"})
        assert response.status_code == 401

    def test_delete_requires_auth(self):
        """Test delete project requires authentication."""
        response = client.delete("/api/projects/1")
        assert response.status_code == 401

    def test_routes_registered(self):
        """Test all project routes are registered."""
        routes = get_app_routes(app)
        assert "/api/projects" in routes
        assert "/api/projects/{project_id}" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
