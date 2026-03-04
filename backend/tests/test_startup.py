"""Tests for app startup and configuration."""

import pytest
from unittest.mock import patch, MagicMock


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
        assert settings.frontend_url is not None

    def test_admin_env_vars(self):
        """Test admin env vars configuration."""
        from app.config import get_settings
        settings = get_settings()
        assert hasattr(settings, 'admin_email')
        assert hasattr(settings, 'admin_password')


class TestDatabaseInit:
    """Test database initialization."""

    def test_models_import(self):
        """Test all models can be imported."""
        from app.db.models import User, Project, Dataset, OperationHistory, Agent
        assert User is not None
        assert Project is not None
        assert Dataset is not None
        assert OperationHistory is not None
        assert Agent is not None

    def test_database_functions_import(self):
        """Test database functions can be imported."""
        from app.db.database import get_async_engine, get_async_session_maker
        assert get_async_engine is not None
        assert get_async_session_maker is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
