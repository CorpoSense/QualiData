"""Search engine tool factory for LangChain agents.

Creates LangChain-compatible search tools from SearchEngine configuration.
Supports: duckduckgo, serper, brave, serpapi, google, exa, searxng, custom.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = [
    "duckduckgo",
    "serper",
    "brave",
    "serpapi",
    "google",
    "exa",
    "searxng",
    "custom",
]


def create_search_tool(
    provider: str, api_key: str | None = None, config: dict | None = None
):
    """Create a LangChain search tool from provider + config.

    Args:
        provider: Search engine provider name.
        api_key: Decrypted API key for the provider (if required).
        config: Free-form provider-specific configuration dict.

    Returns:
        A LangChain tool or tool-like object.

    Raises:
        ValueError: If the provider is not supported.
    """
    config = config or {}

    match provider:
        case "duckduckgo":
            return _create_duckduckgo_tool(api_key, config)
        case "serper":
            return _create_serper_tool(api_key, config)
        case "brave":
            return _create_brave_tool(api_key, config)
        case "serpapi":
            return _create_serpapi_tool(api_key, config)
        case "google":
            return _create_google_tool(api_key, config)
        case "exa":
            return _create_exa_tool(api_key, config)
        case "searxng":
            return _create_searxng_tool(api_key, config)
        case "custom":
            return _create_custom_rest_tool(api_key, config)
        case _:
            raise ValueError(
                f"Unsupported search provider: {provider}. "
                f"Supported: {SUPPORTED_PROVIDERS}"
            )


def _create_duckduckgo_tool(api_key: str | None, config: dict):
    """Create a DuckDuckGo search tool. No API key required."""
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    from langchain_community.tools import DuckDuckGoSearchResults

    wrapper = DuckDuckGoSearchAPIWrapper(
        region=config.get("region", "us-en"),
        max_results=config.get("max_results", 5),
    )
    search = DuckDuckGoSearchResults(api_wrapper=wrapper)

    @tool
    def duckduckgo_search(query: str) -> str:
        """Search the web using DuckDuckGo. Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return duckduckgo_search


def _create_serper_tool(api_key: str | None, config: dict):
    """Create a Serper (Google Search) tool. Requires API key."""
    from langchain_community.utilities import GoogleSerperAPIWrapper

    kwargs = {}
    if api_key:
        kwargs["serper_api_key"] = api_key
    if config.get("gl"):
        kwargs["gl"] = config["gl"]
    if config.get("hl"):
        kwargs["hl"] = config["hl"]

    search = GoogleSerperAPIWrapper(**kwargs)

    @tool
    def serper_search(query: str) -> str:
        """Search the web using Google (via Serper). Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return serper_search


def _create_brave_tool(api_key: str | None, config: dict):
    """Create a Brave Search tool. Requires API key."""
    from langchain_community.tools import BraveSearch

    kwargs = {}
    if api_key:
        kwargs["brave_api_key"] = api_key
    search_kwargs = {}
    if config.get("max_results"):
        search_kwargs["count"] = config["max_results"]
    if search_kwargs:
        kwargs["search_kwargs"] = search_kwargs

    search = BraveSearch(**kwargs)

    @tool
    def brave_search(query: str) -> str:
        """Search the web using Brave Search. Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return brave_search


def _create_serpapi_tool(api_key: str | None, config: dict):
    """Create a SerpAPI tool. Requires API key."""
    from langchain_community.utilities import SerpAPIWrapper

    kwargs = {}
    if api_key:
        kwargs["serpapi_api_key"] = api_key
    # Pass through any params (engine, gl, hl, etc.)
    params = {k: v for k, v in config.items() if k not in ("api_key",)}
    if params:
        kwargs["params"] = params

    search = SerpAPIWrapper(**kwargs)

    @tool
    def serpapi_search(query: str) -> str:
        """Search the web using SerpAPI. Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return serpapi_search


def _create_google_tool(api_key: str | None, config: dict):
    """Create a Google Custom Search tool. Requires API key + CSE ID."""
    from langchain_google_community import GoogleSearchAPIWrapper

    kwargs = {}
    if api_key:
        kwargs["google_api_key"] = api_key
    if config.get("google_cse_id"):
        kwargs["google_cse_id"] = config["google_cse_id"]
    if config.get("k"):
        kwargs["k"] = config["k"]

    search = GoogleSearchAPIWrapper(**kwargs)

    @tool
    def google_search(query: str) -> str:
        """Search the web using Google Custom Search. Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return google_search


def _create_exa_tool(api_key: str | None, config: dict):
    """Create an Exa search tool. Requires API key."""
    from langchain_exa import ExaSearchResults

    kwargs = {}
    if api_key:
        kwargs["exa_api_key"] = api_key

    search = ExaSearchResults(**kwargs)

    @tool
    def exa_search(query: str) -> str:
        """Search the web using Exa. Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return exa_search


def _create_searxng_tool(api_key: str | None, config: dict):
    """Create a SearXNG search tool. Self-hosted, no API key required."""
    from langchain_community.utilities import SearxSearchWrapper

    searx_host = config.get("searx_host", "http://localhost:8080")
    kwargs = {"searx_host": searx_host}
    if config.get("k"):
        kwargs["k"] = config["k"]

    search = SearxSearchWrapper(**kwargs)

    @tool
    def searxng_search(query: str) -> str:
        """Search the web using SearXNG. Useful for finding current information, looking up facts, or validating data."""
        return search.run(query)

    return searxng_search


def _create_custom_rest_tool(api_key: str | None, config: dict):
    """Create a custom REST API search tool from user-provided config."""
    import requests

    url = config.get("url", "")
    method = config.get("method", "GET").upper()
    headers = config.get("headers", {})
    params_template = config.get("params", {})
    body_template = config.get("body_template", "")

    @tool
    def custom_search(query: str) -> str:
        """Search the web using a custom REST API endpoint. Useful for finding current information, looking up facts, or validating data."""
        req_headers = {**headers}
        if api_key and "Authorization" not in req_headers:
            req_headers["Authorization"] = f"Bearer {api_key}"

        req_params = {k: v for k, v in params_template.items()}
        req_params["q"] = query

        try:
            if method == "POST":
                body = (
                    body_template.replace("{query}", query)
                    if body_template
                    else json.dumps({"q": query})
                )
                response = requests.post(
                    url, headers=req_headers, data=body, params=req_params, timeout=10
                )
            else:
                response = requests.get(
                    url, headers=req_headers, params=req_params, timeout=10
                )
            return response.text
        except Exception as e:
            return f"Search error: {str(e)}"

    return custom_search


def build_tools_from_search_engine(search_engine: dict | None) -> list:
    """Build a list of LangChain tools from a search engine config dict.

    Args:
        search_engine: Dict with 'provider', 'api_key', 'config' keys,
                       or None if no search engine is configured.

    Returns:
        A list containing one search tool, or an empty list if no engine.
    """
    if not search_engine:
        return []

    provider = search_engine.get("provider")
    api_key = search_engine.get("api_key")
    config = search_engine.get("config")

    try:
        tool = create_search_tool(provider, api_key, config)
        return [tool]
    except Exception as e:
        logger.error(f"Failed to create search tool for provider '{provider}': {e}")
        return []
