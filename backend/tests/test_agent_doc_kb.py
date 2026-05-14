"""Tests for agent doc_kb_config — CRUD, encryption, and chat integration."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.routers.agents import (
    _mask_doc_kb_config,
    _encrypt_doc_kb_config,
    _agent_to_response,
)


# --- _mask_doc_kb_config tests ---


def test_mask_doc_kb_config_none():
    """None config returns None."""
    assert _mask_doc_kb_config(None) is None


def test_mask_doc_kb_config_no_key():
    """Config without embedding_api_key is returned as-is with has_embedding_api_key=False."""
    config = {
        "embedding_provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "chunk_size": 500,
        "chunk_overlap": 80,
    }
    result = _mask_doc_kb_config(config)
    assert result["embedding_provider"] == "openai"
    assert result["has_embedding_api_key"] is False
    assert "embedding_api_key" not in result or result.get("embedding_api_key") is None


def test_mask_doc_kb_config_with_key():
    """Config with embedding_api_key masks it and sets has_embedding_api_key=True."""
    config = {
        "embedding_provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "embedding_api_key": "sk-real-key-12345",
        "chunk_size": 500,
        "chunk_overlap": 80,
    }
    result = _mask_doc_kb_config(config)
    assert result["embedding_api_key"] == "••••••••"
    assert result["has_embedding_api_key"] is True
    assert result["embedding_provider"] == "openai"


def test_mask_doc_kb_config_empty_key():
    """Config with empty embedding_api_key sets has_embedding_api_key=False."""
    config = {
        "embedding_provider": "openai",
        "embedding_api_key": "",
    }
    result = _mask_doc_kb_config(config)
    assert result["has_embedding_api_key"] is False


# --- _encrypt_doc_kb_config tests ---


def test_encrypt_doc_kb_config_none():
    """None config returns None."""
    assert _encrypt_doc_kb_config(None, "secret") is None


def test_encrypt_doc_kb_config_no_key():
    """Config without embedding_api_key is returned unchanged."""
    config = {
        "embedding_provider": "ollama",
        "embedding_model": "nomic-embed-text",
        "chunk_size": 500,
    }
    result = _encrypt_doc_kb_config(config, "secret")
    assert result["embedding_provider"] == "ollama"
    assert "embedding_api_key" not in result


def test_encrypt_doc_kb_config_with_key():
    """Config with embedding_api_key encrypts it."""
    with patch("app.routers.agents.encrypt_value", return_value="encrypted-key") as mock_encrypt:
        config = {
            "embedding_provider": "openai",
            "embedding_api_key": "sk-real-key",
        }
        result = _encrypt_doc_kb_config(config, "test-secret")
        mock_encrypt.assert_called_once_with("sk-real-key", "test-secret")
        assert result["embedding_api_key"] == "encrypted-key"


# --- _agent_to_response tests ---


def test_agent_to_response_includes_doc_kb_fields():
    """_agent_to_response includes doc_kb_config and has_doc_kb."""
    mock_agent = MagicMock()
    mock_agent.id = "test-id"
    mock_agent.user_id = "user-id"
    mock_agent.name = "Test Agent"
    mock_agent.description = "Test"
    mock_agent.provider = "openai"
    mock_agent.model = "gpt-4o-mini"
    mock_agent.system_prompt = None
    mock_agent.prompt_template = None
    mock_agent.temperature = 0.3
    mock_agent.memory_config = None
    mock_agent.doc_kb_config = {
        "embedding_provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "embedding_api_key": "sk-key",
        "chunk_size": 500,
        "chunk_overlap": 80,
    }
    mock_agent.is_template = False
    mock_agent.is_builtin = False
    mock_agent.base_url = None
    mock_agent.created_at = "2026-01-01"
    mock_agent.updated_at = "2026-01-01"
    mock_agent.api_key = None
    mock_agent.search_engine_id = None

    result = _agent_to_response(mock_agent)

    assert result["has_doc_kb"] is True
    assert result["doc_kb_config"]["embedding_provider"] == "openai"
    # API key should be masked
    assert result["doc_kb_config"]["embedding_api_key"] == "••••••••"
    assert result["doc_kb_config"]["has_embedding_api_key"] is True


def test_agent_to_response_no_doc_kb():
    """_agent_to_response with no doc_kb_config has has_doc_kb=False."""
    mock_agent = MagicMock()
    mock_agent.id = "test-id"
    mock_agent.user_id = "user-id"
    mock_agent.name = "Test Agent"
    mock_agent.description = None
    mock_agent.provider = "openai"
    mock_agent.model = "gpt-4o-mini"
    mock_agent.system_prompt = None
    mock_agent.prompt_template = None
    mock_agent.temperature = 0.3
    mock_agent.memory_config = None
    mock_agent.doc_kb_config = None
    mock_agent.is_template = False
    mock_agent.is_builtin = False
    mock_agent.base_url = None
    mock_agent.created_at = "2026-01-01"
    mock_agent.updated_at = "2026-01-01"
    mock_agent.api_key = None
    mock_agent.search_engine_id = None

    result = _agent_to_response(mock_agent)

    assert result["has_doc_kb"] is False
    assert result["doc_kb_config"] is None


# --- ChatRequest doc_id tests ---


def test_chat_request_has_doc_id():
    """ChatRequest schema includes doc_id field."""
    from app.models.schemas import ChatRequest
    req = ChatRequest(
        message="What is this document about?",
        agent_id="test-agent",
        doc_id="test-doc-id",
    )
    assert req.doc_id == "test-doc-id"


def test_chat_request_doc_id_default_none():
    """ChatRequest doc_id defaults to None."""
    from app.models.schemas import ChatRequest
    req = ChatRequest(message="Hello")
    assert req.doc_id is None


# --- _get_agent_config doc_kb_config tests ---


@pytest.mark.asyncio
async def test_get_agent_config_includes_doc_kb_config():
    """_get_agent_config returns doc_kb_config with decrypted embedding_api_key."""
    from app.routers.ai_operations import _get_agent_config

    mock_agent = MagicMock()
    mock_agent.provider = "openai"
    mock_agent.model = "gpt-4o-mini"
    mock_agent.temperature = 0.3
    mock_agent.system_prompt = "Test prompt"
    mock_agent.api_key = "decrypted-agent-key"
    mock_agent.base_url = None
    mock_agent.memory_config = None
    mock_agent.search_engine_id = None
    mock_agent.doc_kb_config = {
        "embedding_provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "embedding_api_key": "encrypted-emb-key",
        "chunk_size": 500,
        "chunk_overlap": 80,
    }

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_agent

    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.utils.crypto.decrypt_value", return_value="decrypted-emb-key"), \
         patch("app.config.get_settings") as mock_settings:
        mock_settings.return_value.secret_key = "test-secret"

        config = await _get_agent_config("test-agent-id", "test-user-id", mock_session)

        assert config["doc_kb_config"] is not None
        assert config["doc_kb_config"]["embedding_provider"] == "openai"
        assert config["doc_kb_config"]["embedding_api_key"] == "decrypted-emb-key"


@pytest.mark.asyncio
async def test_get_agent_config_no_doc_kb():
    """_get_agent_config returns doc_kb_config=None when agent has no doc_kb_config."""
    from app.routers.ai_operations import _get_agent_config

    mock_agent = MagicMock()
    mock_agent.provider = "openai"
    mock_agent.model = "gpt-4o-mini"
    mock_agent.temperature = 0.3
    mock_agent.system_prompt = None
    mock_agent.api_key = None
    mock_agent.base_url = None
    mock_agent.memory_config = None
    mock_agent.search_engine_id = None
    mock_agent.doc_kb_config = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_agent

    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    config = await _get_agent_config("test-agent-id", "test-user-id", mock_session)

    assert config["doc_kb_config"] is None


@pytest.mark.asyncio
async def test_get_agent_config_default_doc_kb():
    """_get_agent_config returns doc_kb_config=None for default (no agent) config."""
    from app.routers.ai_operations import _get_agent_config

    mock_session = MagicMock()

    config = await _get_agent_config(None, "test-user-id", mock_session)

    assert config["doc_kb_config"] is None


# --- _chat_with_memory passes user_id (not agent_id) to _resolve_document ---


@pytest.mark.asyncio
async def test_chat_with_memory_uses_user_id_for_document_lookup():
    """_chat_with_memory must pass user_id (not agent_id) to _resolve_document.

    Regression test: previously _resolve_document was called with request.agent_id
    as the user_id parameter, which meant documents could never be found because
    Document.user_id stores the uploading user's ID, not the agent's ID.
    """
    from app.routers.ai import _chat_with_memory
    from app.models.schemas import ChatRequest, ChatMessage

    request = ChatRequest(
        message="Summarize the document",
        agent_id="test-agent-id",
        doc_id="test-doc-id",
        conversation_id="test-conv-id",
    )
    agent_config = {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": None,
        "api_key": "test-key",
        "base_url": None,
        "memory_config": None,
        "search_engine_id": None,
        "doc_kb_config": {
            "embedding_provider": "openai",
            "embedding_model": "text-embedding-3-small",
            "chunk_size": 500,
            "chunk_overlap": 80,
        },
    }
    dataset_context = ""
    mock_session = MagicMock()
    user_id = "real-user-id-123"

    with patch("app.routers.ai._resolve_document", new_callable=AsyncMock) as mock_resolve, \
         patch("app.routers.ai.get_chat_model") as mock_get_llm, \
         patch("app.services.agent_factory.create_agent_with_memory") as mock_create_agent:

        mock_resolve.return_value = None  # doc not found, but we just check the call args
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent.ainvoke = AsyncMock(return_value={"messages": [MagicMock(content="test")]})
        mock_create_agent.return_value = mock_agent

        try:
            await _chat_with_memory(
                request, agent_config, dataset_context, mock_session,
                user_id=user_id,
            )
        except Exception:
            pass  # We only care about _resolve_document call

        # The key assertion: _resolve_document must be called with user_id, NOT agent_id
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args
        # call_args[0] is positional args: (doc_id, user_id, session)
        assert call_args[0][0] == "test-doc-id", f"doc_id should be 'test-doc-id', got {call_args[0][0]!r}"
        assert call_args[0][1] == user_id, \
            f"_resolve_document should be called with user_id={user_id!r}, " \
            f"not agent_id='test-agent-id'. Got {call_args[0][1]!r}"
