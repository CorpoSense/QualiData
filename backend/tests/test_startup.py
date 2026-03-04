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

class TestPasswordHashing:
    """Test password hashing functions."""

    def test_get_password_hash_returns_string(self):
        """Test that password hashing returns a string."""
        from app.routers.auth import get_password_hash
        result = get_password_hash("testpassword")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_password_hash_consistency(self):
        """Test that same password produces same hash."""
        from app.routers.auth import get_password_hash
        pwd = "mysecretpassword"
        hash1 = get_password_hash(pwd)
        hash2 = get_password_hash(pwd)
        assert hash1 == hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        from app.routers.auth import get_password_hash, verify_password
        pwd = "testpassword123"
        hashed = get_password_hash(pwd)
        assert verify_password(pwd, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with wrong password."""
        from app.routers.auth import get_password_hash, verify_password
        pwd = "testpassword123"
        hashed = get_password_hash(pwd)
        assert verify_password("wrongpassword", hashed) is False


class TestUserModel:
    """Test User model fields."""

    def test_user_has_password_hash_field(self):
        """Test User model has password_hash field."""
        from app.db.models import User
        user = User(email="test@test.com")
        assert hasattr(user, 'password_hash')

    def test_user_model_fields(self):
        """Test User model has all required fields."""
        from app.db.models import User
        user = User(email="test@test.com", name="Test User")
        assert user.email == "test@test.com"
        assert user.name == "Test User"
