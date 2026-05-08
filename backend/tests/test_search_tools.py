"""Tests for search_tools service — tool creation and build_tools_from_search_engine."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock


from app.services.search_tools import (
    create_search_tool,
    build_tools_from_search_engine,
    SUPPORTED_PROVIDERS,
)


# --- create_search_tool tests ---


def test_create_duckduckgo_tool():
    """DuckDuckGo tool is created successfully."""
    tool = create_search_tool("duckduckgo", config={"region": "us-en", "max_results": 3})
    assert tool is not None
    assert hasattr(tool, "name")
    assert hasattr(tool, "description")


def test_create_duckduckgo_tool_no_config():
    """DuckDuckGo tool works with no config."""
    tool = create_search_tool("duckduckgo")
    assert tool is not None


def test_create_serper_tool():
    """Serper tool is created with API key."""
    tool = create_search_tool("serper", api_key="test-key", config={"gl": "us"})
    assert tool is not None


def test_create_brave_tool():
    """Brave tool is created with API key via env var."""
    with patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test-key"}):
        tool = create_search_tool("brave", api_key="test-key", config={"max_results": 5})
    assert tool is not None


def test_create_serpapi_tool():
    """SerpAPI tool is created with API key (requires google-search-results)."""
    # SerpAPI requires the `google-search-results` package
    # If not installed, the test should gracefully skip or mock
    try:
        tool = create_search_tool("serpapi", api_key="test-key", config={"engine": "google"})
        assert tool is not None
    except ImportError:
        pytest.skip("google-search-results package not installed")


def test_create_searxng_tool():
    """SearXNG tool is created with host config."""
    tool = create_search_tool("searxng", config={"searx_host": "https://seek.fyi", "k": 5})
    assert tool is not None


def test_create_searxng_tool_default_host():
    """SearXNG tool defaults to localhost if no host provided."""
    tool = create_search_tool("searxng")
    assert tool is not None


def test_create_custom_rest_tool():
    """Custom REST API tool is created from config."""
    config = {
        "method": "POST",
        "url": "https://my-api.com/search",
        "headers": {"X-API-KEY": "test"},
        "body_template": '{"query": "{query}"}',
    }
    tool = create_search_tool("custom", config=config)
    assert tool is not None


def test_create_tool_invalid_provider():
    """Invalid provider raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported search provider"):
        create_search_tool("nonexistent_provider")


def test_create_tool_core_providers():
    """Core providers (duckduckgo, serper, searxng, custom) can create tools."""
    core_providers = ["duckduckgo", "serper", "searxng", "custom"]
    for provider in core_providers:
        if provider == "custom":
            tool = create_search_tool(provider, config={"url": "https://example.com", "method": "GET"})
        else:
            tool = create_search_tool(provider, api_key="test-key")
        assert tool is not None, f"Failed to create tool for provider: {provider}"


# --- build_tools_from_search_engine tests ---


def test_build_tools_none():
    """None search engine returns empty list."""
    tools = build_tools_from_search_engine(None)
    assert tools == []


def test_build_tools_empty_dict():
    """Empty dict search engine returns empty list (no provider)."""
    tools = build_tools_from_search_engine({})
    assert tools == []


def test_build_tools_duckduckgo():
    """DuckDuckGo search engine config returns one tool."""
    search_engine = {
        "provider": "duckduckgo",
        "api_key": None,
        "config": {"region": "us-en", "max_results": 5},
    }
    tools = build_tools_from_search_engine(search_engine)
    assert len(tools) == 1


def test_build_tools_serper():
    """Serper search engine config returns one tool."""
    search_engine = {
        "provider": "serper",
        "api_key": "test-serper-key",
        "config": {"gl": "us"},
    }
    tools = build_tools_from_search_engine(search_engine)
    assert len(tools) == 1


def test_build_tools_invalid_provider_returns_empty():
    """Invalid provider in search engine config returns empty list (no crash)."""
    search_engine = {
        "provider": "invalid_provider",
        "api_key": None,
        "config": {},
    }
    tools = build_tools_from_search_engine(search_engine)
    assert tools == []


def test_build_tools_searxng():
    """SearXNG search engine config returns one tool."""
    search_engine = {
        "provider": "searxng",
        "api_key": None,
        "config": {"searx_host": "https://seek.fyi", "k": 5},
    }
    tools = build_tools_from_search_engine(search_engine)
    assert len(tools) == 1


def test_build_tools_custom():
    """Custom REST API search engine config returns one tool."""
    search_engine = {
        "provider": "custom",
        "api_key": None,
        "config": {
            "method": "GET",
            "url": "https://example.com/search",
        },
    }
    tools = build_tools_from_search_engine(search_engine)
    assert len(tools) == 1
