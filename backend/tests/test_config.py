"""Tests for config validation."""

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestDatabaseUrlValidation:
    """Test database URL validation."""

    def test_valid_postgresql_url(self):
        """Test that valid PostgreSQL URLs are accepted."""
        settings = Settings(
            database_url="postgresql://user:password@localhost:5432/mydb"
        )
        assert settings.database_url == "postgresql://user:password@localhost:5432/mydb"

    def test_valid_sqlite_url(self):
        """Test that SQLite URLs are accepted."""
        settings = Settings(database_url="sqlite+aiosqlite:///./test.db")
        assert settings.database_url == "sqlite+aiosqlite:///./test.db"

    def test_invalid_placeholder_url(self):
        """Test that placeholder URLs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(database_url="postgresql://user:password@host:port/database?sslmode=require")
        
        assert "placeholder" in str(exc_info.value).lower()

    def test_invalid_host_port_url(self):
        """Test that URLs with host:port placeholder are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(database_url="postgresql://user:password@host:port/db")
        
        assert "placeholder" in str(exc_info.value).lower()

    def test_empty_database_url(self):
        """Test that empty database URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(database_url="")
        
        assert "cannot be empty" in str(exc_info.value).lower()
