"""Tests for search engine CRUD endpoints."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# --- Fixtures ---

mock_user = MagicMock()
mock_user.id = "test-user-id"
mock_user.email = "test@example.com"
mock_user.is_active = True


@pytest.fixture
def client():
    """Create test client with auth and session mocked via dependency overrides."""
    with patch("app.db.database.get_async_session_maker"):
        with patch("app.db.database.get_sync_session_maker"):
            from app.main import app
            from app.routers.auth import get_current_active_user
            from app.routers.search_engines import get_async_session

            mock_session = MagicMock()

            async def mock_execute(query):
                result = MagicMock()
                result.scalars.return_value.all.return_value = []
                result.scalar_one_or_none.return_value = None
                return result

            async def mock_commit():
                pass

            async def mock_refresh(obj):
                # Simulate DB-assigned fields after commit
                if not obj.id:
                    obj.id = "mock-engine-id"
                if not hasattr(obj, 'is_builtin') or obj.is_builtin is None:
                    obj.is_builtin = False
                from datetime import datetime
                if not obj.created_at:
                    obj.created_at = datetime.utcnow()
                if not obj.updated_at:
                    obj.updated_at = datetime.utcnow()

            mock_session.execute = mock_execute
            mock_session.add = MagicMock()
            mock_session.commit = mock_commit
            mock_session.refresh = mock_refresh
            mock_session.delete = AsyncMock()

            app.dependency_overrides[get_current_active_user] = lambda: mock_user
            app.dependency_overrides[get_async_session] = lambda: mock_session

            from fastapi.testclient import TestClient
            yield TestClient(app)

            # Clean up overrides
            app.dependency_overrides.clear()


# --- Tests ---


def test_list_search_providers(client):
    """GET /api/search-engines/providers returns supported providers."""
    response = client.get("/api/search-engines/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    providers = [p["provider"] for p in data]
    assert "duckduckgo" in providers
    assert "serper" in providers
    assert "brave" in providers
    assert "serpapi" in providers
    assert "google" in providers
    assert "exa" in providers
    assert "searxng" in providers
    assert "custom" in providers


def test_list_search_providers_has_required_fields(client):
    """Each provider entry has required fields."""
    response = client.get("/api/search-engines/providers")
    data = response.json()
    for p in data:
        assert "provider" in p
        assert "label" in p
        assert "requires_api_key" in p
        assert "description" in p
        assert "config_example" in p


def test_list_search_engines_empty(client):
    """GET /api/search-engines/ returns empty list when no engines."""
    response = client.get("/api/search-engines/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_search_engine_duckduckgo(client):
    """POST /api/search-engines/ creates a DuckDuckGo engine (no API key)."""
    payload = {
        "name": "My DuckDuckGo",
        "provider": "duckduckgo",
        "config": {"region": "us-en", "max_results": 5},
    }
    with patch("app.routers.search_engines.encrypt_value", return_value="encrypted"):
        response = client.post("/api/search-engines/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My DuckDuckGo"
    assert data["provider"] == "duckduckgo"
    assert data["has_api_key"] is False
    assert data["config"] == {"region": "us-en", "max_results": 5}


def test_create_search_engine_with_api_key(client):
    """POST /api/search-engines/ creates an engine with encrypted API key."""
    payload = {
        "name": "My Serper",
        "provider": "serper",
        "api_key": "test-serper-key-123",
    }
    with patch("app.routers.search_engines.encrypt_value", return_value="encrypted-key"):
        response = client.post("/api/search-engines/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["has_api_key"] is True


def test_create_search_engine_invalid_provider(client):
    """POST /api/search-engines/ rejects invalid provider."""
    payload = {
        "name": "Bad Engine",
        "provider": "nonexistent",
    }
    response = client.post("/api/search-engines/", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_create_search_engine_missing_name(client):
    """POST /api/search-engines/ rejects missing name."""
    payload = {
        "provider": "duckduckgo",
    }
    response = client.post("/api/search-engines/", json=payload)
    assert response.status_code == 422


def test_create_search_engine_searxng(client):
    """POST /api/search-engines/ creates a SearXNG engine."""
    payload = {
        "name": "My SearXNG",
        "provider": "searxng",
        "config": {"searx_host": "https://seek.fyi", "k": 5},
    }
    with patch("app.routers.search_engines.encrypt_value", return_value="encrypted"):
        response = client.post("/api/search-engines/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["provider"] == "searxng"
    assert data["config"]["searx_host"] == "https://seek.fyi"


def test_create_search_engine_custom(client):
    """POST /api/search-engines/ creates a custom REST API engine."""
    payload = {
        "name": "My Custom API",
        "provider": "custom",
        "config": {
            "method": "POST",
            "url": "https://my-api.com/search",
            "headers": {"X-Custom-Auth": "my-key"},
            "body_template": '{"query": "{query}"}',
        },
    }
    with patch("app.routers.search_engines.encrypt_value", return_value="encrypted"):
        response = client.post("/api/search-engines/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["provider"] == "custom"
    assert data["config"]["url"] == "https://my-api.com/search"


def test_get_search_engine_not_found(client):
    """GET /api/search-engines/{id} returns 404 for non-existent engine."""
    response = client.get("/api/search-engines/nonexistent-id")
    assert response.status_code == 404


def test_delete_search_engine_not_found(client):
    """DELETE /api/search-engines/{id} returns 404 for non-existent engine."""
    response = client.delete("/api/search-engines/nonexistent-id")
    assert response.status_code == 404
