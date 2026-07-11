"""Tests for authentication endpoints - route validation."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import get_app_routes

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


client = TestClient(app)


class TestAuthRoutes:
    """Test that auth routes are registered."""

    def test_me_requires_auth(self):
        """Test /me endpoint requires authentication."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_oauth_google_route_exists(self):
        """Test OAuth Google route exists."""
        response = client.get("/api/auth/oauth/google")
        # Should redirect or return error, not 404
        assert response.status_code != 404

    def test_oauth_github_route_exists(self):
        """Test OAuth GitHub route exists."""
        response = client.get("/api/auth/oauth/github")
        # Should redirect or return error, not 404
        assert response.status_code != 404

    def test_routes_registered(self):
        """Test all auth routes are registered."""
        routes = get_app_routes(app)
        assert "/api/auth/register" in routes
        assert "/api/auth/login" in routes
        assert "/api/auth/me" in routes
        assert "/api/auth/oauth/{provider}" in routes
        assert "/api/auth/password-reset-request" in routes
        assert "/api/auth/password-reset-confirm" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
