"""Tests for app startup and configuration."""

import pytest
from unittest.mock import patch


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app, create_admin_user


class TestAppStartup:
    """Test app startup and configuration."""

    def test_app_creates(self):
        """Test that app creates without errors."""
        assert app is not None

    def test_admin_creation_function_exists(self):
        """Test admin creation function exists."""
        assert create_admin_user is not None

    def test_app_has_routers(self):
        """Test app has routers registered."""
        routes = [r.path for r in app.routes if hasattr(r, "path")]
        
        # Check key routes exist
        assert any("/api/auth" in r for r in routes)
        assert any("/api/projects" in r for r in routes)
        assert any("/api/datasets" in r for r in routes)
        assert any("/api/health" in r for r in routes)


class TestConfig:
    """Test configuration."""

    def test_settings_import(self):
        """Test settings can be imported."""
        from app.config import get_settings
        settings = get_settings()
        assert settings is not None

    def test_frontend_url_default(self):
        """Test frontend URL has default."""
        from app.config import get_settings
        settings = get_settings()
        # Should have a default or can be empty
        assert settings.frontend_url is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
