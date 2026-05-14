"""Tests for embedding_factory service — provider catalog, defaults, and factory."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock

from app.services.embedding_factory import (
    load_embedding_providers,
    list_embedding_providers,
    get_default_embedding_model,
    get_provider_info,
    get_supported_file_types,
    get_default_chunk_size,
    get_default_chunk_overlap,
    _resolve_api_key,
    get_embeddings,
)


# --- Catalog loading tests ---


def test_load_embedding_providers_returns_dict():
    """load_embedding_providers returns a valid dict with expected keys."""
    catalog = load_embedding_providers()
    assert isinstance(catalog, dict)
    assert "providers" in catalog
    assert "supported_file_types" in catalog
    assert "default_chunk_size" in catalog
    assert "default_chunk_overlap" in catalog


def test_list_embedding_providers_returns_list():
    """list_embedding_providers returns a list of provider dicts."""
    providers = list_embedding_providers()
    assert isinstance(providers, list)
    assert len(providers) > 0
    for p in providers:
        assert "provider" in p
        assert "label" in p
        assert "default_model" in p
        assert "requires_api_key" in p
        assert "models" in p


def test_known_providers_present():
    """All expected providers are in the catalog."""
    providers = list_embedding_providers()
    provider_names = {p["provider"] for p in providers}
    expected = {"openai", "huggingface", "ollama", "nvidia", "google"}
    assert expected.issubset(provider_names)


def test_get_default_embedding_model():
    """get_default_embedding_model returns correct defaults."""
    assert get_default_embedding_model("openai") == "text-embedding-3-small"
    assert get_default_embedding_model("huggingface") == "BAAI/bge-small-en-v1.5"
    assert get_default_embedding_model("ollama") == "nomic-embed-text"
    assert get_default_embedding_model("nvidia") == "nvidia/llama-nemotron-embed-vl-1b-v2"
    assert get_default_embedding_model("google") == "models/embedding-001"


def test_get_default_embedding_model_invalid():
    """get_default_embedding_model raises ValueError for unknown provider."""
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        get_default_embedding_model("nonexistent")


def test_get_provider_info():
    """get_provider_info returns provider dict for valid provider."""
    info = get_provider_info("openai")
    assert info is not None
    assert info["provider"] == "openai"
    assert info["requires_api_key"] is True
    assert len(info["models"]) > 0


def test_get_provider_info_not_found():
    """get_provider_info returns None for unknown provider."""
    assert get_provider_info("nonexistent") is None


def test_get_supported_file_types():
    """get_supported_file_types returns expected file types."""
    file_types = get_supported_file_types()
    assert "application/pdf" in file_types
    assert "text/plain" in file_types
    assert "text/csv" in file_types
    assert "text/markdown" in file_types


def test_get_default_chunk_size():
    """get_default_chunk_size returns a positive integer."""
    assert get_default_chunk_size() == 500


def test_get_default_chunk_overlap():
    """get_default_chunk_overlap returns a positive integer."""
    assert get_default_chunk_overlap() == 80


# --- API key resolution tests ---


def test_resolve_api_key_config_key_priority():
    """Config API key takes priority over fallback and env var."""
    result = _resolve_api_key("openai", config_api_key="config-key", fallback_api_key="fallback-key")
    assert result == "config-key"


def test_resolve_api_key_fallback():
    """Fallback API key is used when config key is not set."""
    result = _resolve_api_key("openai", config_api_key=None, fallback_api_key="fallback-key")
    assert result == "fallback-key"


def test_resolve_api_key_env_var():
    """Environment variable is used when neither config nor fallback key is set."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
        result = _resolve_api_key("openai", config_api_key=None, fallback_api_key=None)
        assert result == "env-key"


def test_resolve_api_key_no_key():
    """Returns None when no key is available."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("OPENAI_API_KEY", None)
        result = _resolve_api_key("openai", config_api_key=None, fallback_api_key=None)
        assert result is None


def test_resolve_api_key_ollama_no_key_needed():
    """Ollama doesn't need an API key — returns None gracefully."""
    result = _resolve_api_key("ollama", config_api_key=None, fallback_api_key=None)
    assert result is None


# --- get_embeddings factory tests (mocked at import source) ---


def test_get_embeddings_invalid_provider():
    """get_embeddings raises ValueError for unsupported provider."""
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        get_embeddings("nonexistent_provider")


def test_get_embeddings_openai():
    """get_embeddings creates OpenAIEmbeddings with correct params."""
    with patch("langchain_openai.OpenAIEmbeddings") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        result = get_embeddings("openai", model="text-embedding-3-small", api_key="test-key")
        mock_cls.assert_called_once()
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["model"] == "text-embedding-3-small"
        assert call_kwargs["api_key"] == "test-key"


def test_get_embeddings_openai_with_base_url():
    """get_embeddings passes base_url for OpenAI-compatible providers."""
    with patch("langchain_openai.OpenAIEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("openai", model="test-model", api_key="key", base_url="http://localhost:8080")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["base_url"] == "http://localhost:8080"


def test_get_embeddings_ollama():
    """get_embeddings creates OllamaEmbeddings without API key."""
    with patch("langchain_ollama.OllamaEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        result = get_embeddings("ollama", model="nomic-embed-text")
        mock_cls.assert_called_once()
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["model"] == "nomic-embed-text"
        assert "api_key" not in call_kwargs


def test_get_embeddings_ollama_with_base_url():
    """get_embeddings passes base_url for Ollama."""
    with patch("langchain_ollama.OllamaEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("ollama", model="nomic-embed-text", base_url="http://ollama:11434")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["base_url"] == "http://ollama:11434"


def test_get_embeddings_huggingface():
    """get_embeddings creates HuggingFaceEndpointEmbeddings with token."""
    with patch("langchain_huggingface.HuggingFaceEndpointEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("huggingface", model="BAAI/bge-small-en-v1.5", api_key="hf-token")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["model"] == "BAAI/bge-small-en-v1.5"
        assert call_kwargs["huggingfacehub_api_token"] == "hf-token"


def test_get_embeddings_nvidia():
    """get_embeddings creates NVIDIAEmbeddings with api_key and base_url."""
    with patch("langchain_nvidia_ai_endpoints.NVIDIAEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("nvidia", model="NV-Embed-QA", api_key="nv-key", base_url="https://integrate.api.nvidia.com")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["model"] == "NV-Embed-QA"
        assert call_kwargs["api_key"] == "nv-key"
        assert call_kwargs["base_url"] == "https://integrate.api.nvidia.com"


def test_get_embeddings_google():
    """get_embeddings creates GoogleGenerativeAIEmbeddings with google_api_key."""
    with patch("langchain_google_genai.GoogleGenerativeAIEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("google", model="models/embedding-001", api_key="google-key")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["model"] == "models/embedding-001"
        assert call_kwargs["google_api_key"] == "google-key"


def test_get_embeddings_uses_default_model():
    """get_embeddings uses provider default model when model is None."""
    with patch("langchain_openai.OpenAIEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("openai", model=None, api_key="key")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["model"] == "text-embedding-3-small"


def test_get_embeddings_fallback_api_key():
    """get_embeddings uses fallback_api_key when api_key is not set."""
    with patch("langchain_openai.OpenAIEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_embeddings("openai", model="test", fallback_api_key="fallback-key")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["api_key"] == "fallback-key"
