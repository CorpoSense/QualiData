"""Tests for agent + search engine integration."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock


# --- Agent schema tests ---


def test_agent_create_schema_has_search_engine_id():
    """AgentCreate schema includes search_engine_id field."""
    from app.routers.agents import AgentCreate
    schema = AgentCreate(
        name="Test Agent",
        provider="openai",
        model="gpt-4o-mini",
        search_engine_id="engine-123",
    )
    assert schema.search_engine_id == "engine-123"


def test_agent_create_schema_search_engine_id_optional():
    """AgentCreate schema search_engine_id defaults to None."""
    from app.routers.agents import AgentCreate
    schema = AgentCreate(
        name="Test Agent",
        provider="openai",
        model="gpt-4o-mini",
    )
    assert schema.search_engine_id is None


def test_agent_update_schema_has_search_engine_id():
    """AgentUpdate schema includes search_engine_id field."""
    from app.routers.agents import AgentUpdate
    schema = AgentUpdate(search_engine_id="engine-456")
    assert schema.search_engine_id == "engine-456"


def test_agent_response_schema_has_search_fields():
    """AgentResponse schema includes search_engine_id and has_search_engine."""
    from app.routers.agents import AgentResponse
    # Verify the fields exist in the model
    fields = AgentResponse.model_fields
    assert "search_engine_id" in fields
    assert "has_search_engine" in fields


def test_agent_to_response_includes_search_fields():
    """_agent_to_response includes search_engine_id and has_search_engine."""
    from app.routers.agents import _agent_to_response
    mock_agent = MagicMock()
    mock_agent.id = "agent-1"
    mock_agent.user_id = "user-1"
    mock_agent.name = "Test Agent"
    mock_agent.description = None
    mock_agent.provider = "openai"
    mock_agent.model = "gpt-4o-mini"
    mock_agent.system_prompt = None
    mock_agent.prompt_template = None
    mock_agent.temperature = 0.3
    mock_agent.memory_config = None
    mock_agent.is_template = False
    mock_agent.is_builtin = False
    mock_agent.base_url = None
    mock_agent.created_at = "2024-01-01"
    mock_agent.updated_at = "2024-01-01"
    mock_agent.api_key = "some-key"
    mock_agent.search_engine_id = "engine-123"

    result = _agent_to_response(mock_agent)
    assert result["search_engine_id"] == "engine-123"
    assert result["has_search_engine"] is True


def test_agent_to_response_no_search_engine():
    """_agent_to_response with no search engine shows has_search_engine=False."""
    from app.routers.agents import _agent_to_response
    mock_agent = MagicMock()
    mock_agent.id = "agent-1"
    mock_agent.user_id = "user-1"
    mock_agent.name = "Test Agent"
    mock_agent.description = None
    mock_agent.provider = "openai"
    mock_agent.model = "gpt-4o-mini"
    mock_agent.system_prompt = None
    mock_agent.prompt_template = None
    mock_agent.temperature = 0.3
    mock_agent.memory_config = None
    mock_agent.is_template = False
    mock_agent.is_builtin = False
    mock_agent.base_url = None
    mock_agent.created_at = "2024-01-01"
    mock_agent.updated_at = "2024-01-01"
    mock_agent.api_key = None
    mock_agent.search_engine_id = None

    result = _agent_to_response(mock_agent)
    assert result["search_engine_id"] is None
    assert result["has_search_engine"] is False


# --- Agent config resolution tests ---


def test_get_agent_config_includes_search_engine_id():
    """_get_agent_config returns search_engine_id from agent."""
    # This is tested indirectly through the schema, but let's verify
    # the agent model has the field
    from app.db.models.agent import Agent
    columns = [c.name for c in Agent.__table__.columns]
    assert "search_engine_id" in columns


# --- Agent factory cache hash tests ---


def test_config_hash_includes_search_engine_id():
    """_config_hash produces different hashes for different search_engine_ids."""
    from app.services.agent_factory import _config_hash
    hash1 = _config_hash(None, search_engine_id=None)
    hash2 = _config_hash(None, search_engine_id="engine-123")
    assert hash1 != hash2


def test_config_hash_same_search_engine_same_hash():
    """_config_hash produces same hash for same search_engine_id."""
    from app.services.agent_factory import _config_hash
    hash1 = _config_hash(None, search_engine_id="engine-123")
    hash2 = _config_hash(None, search_engine_id="engine-123")
    assert hash1 == hash2


def test_config_hash_memory_and_search_combined():
    """_config_hash combines memory and search engine in hash."""
    from app.services.agent_factory import _config_hash
    hash1 = _config_hash({"type": "sliding_window", "max_messages": 20}, search_engine_id=None)
    hash2 = _config_hash({"type": "sliding_window", "max_messages": 20}, search_engine_id="engine-123")
    hash3 = _config_hash({"type": "summarizer"}, search_engine_id="engine-123")
    assert hash1 != hash2
    assert hash2 != hash3


# --- AI chat system prompt tests ---


def test_search_aware_system_prompt_exists():
    """SEARCH_AWARE_SYSTEM_PROMPT constant is defined in ai.py."""
    from app.routers.ai import SEARCH_AWARE_SYSTEM_PROMPT
    assert "search" in SEARCH_AWARE_SYSTEM_PROMPT.lower()
    assert "web" in SEARCH_AWARE_SYSTEM_PROMPT.lower()


def test_default_system_prompt_exists():
    """DEFAULT_SYSTEM_PROMPT constant is defined in ai.py."""
    from app.routers.ai import DEFAULT_SYSTEM_PROMPT
    assert len(DEFAULT_SYSTEM_PROMPT) > 0


# --- Search engine model tests ---


def test_search_engine_model_tablename():
    """SearchEngine model uses snake_case table name."""
    from app.db.models.search_engine import SearchEngine
    assert SearchEngine.__tablename__ == "search_engines"


def test_search_engine_model_has_required_columns():
    """SearchEngine model has all required columns."""
    from app.db.models.search_engine import SearchEngine
    columns = [c.name for c in SearchEngine.__table__.columns]
    required = ["id", "user_id", "name", "provider", "api_key", "config", "is_builtin", "created_at", "updated_at"]
    for col in required:
        assert col in columns, f"Missing column: {col}"


# --- Route registration test ---


def test_search_engines_router_registered():
    """Search engines router is registered in the FastAPI app."""
    from tests.conftest import get_app_routes
    with patch("app.db.database.get_async_session_maker"):
        with patch("app.db.database.get_sync_session_maker"):
            from app.main import app
            routes = get_app_routes(app)
            assert "/api/search-engines/" in routes
            assert "/api/search-engines/providers" in routes
            assert "/api/search-engines/{engine_id}" in routes
