"""Pytest configuration for tests."""

import os

# Set test database before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from unittest.mock import patch

import pytest

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient

    return TestClient(app)
