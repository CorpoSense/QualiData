"""Embedding provider factory for creating LangChain Embeddings instances.

Reads provider/model catalog from backend/app/data/embedding_providers.json.
To add a new provider or model, update the JSON file — no code changes needed.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_PROVIDERS_CACHE: dict | None = None


def _load_catalog() -> dict:
    """Load the embedding provider catalog from JSON (cached in memory)."""
    global _PROVIDERS_CACHE
    if _PROVIDERS_CACHE is None:
        json_path = Path(__file__).parent.parent / "data" / "embedding_providers.json"
        with open(json_path) as f:
            _PROVIDERS_CACHE = json.load(f)
    return _PROVIDERS_CACHE


def load_embedding_providers() -> dict:
    """Load the full embedding provider catalog.

    Returns the raw dict from the JSON file, including
    'providers', 'supported_file_types', 'default_chunk_size', etc.
    """
    return _load_catalog()


def list_embedding_providers() -> list[dict]:
    """Return list of available embedding providers with their models."""
    catalog = _load_catalog()
    return catalog["providers"]


def get_default_embedding_model(provider: str) -> str:
    """Get the default model for an embedding provider."""
    for p in list_embedding_providers():
        if p["provider"] == provider:
            return p["default_model"]
    raise ValueError(f"Unknown embedding provider: {provider}")


def get_provider_info(provider: str) -> dict | None:
    """Get provider info dict by provider name."""
    for p in list_embedding_providers():
        if p["provider"] == provider:
            return p
    return None


def get_supported_file_types() -> dict:
    """Return supported file types for document upload."""
    catalog = _load_catalog()
    return catalog["supported_file_types"]


def get_default_chunk_size() -> int:
    """Return default chunk size from catalog."""
    catalog = _load_catalog()
    return catalog.get("default_chunk_size", 500)


def get_default_chunk_overlap() -> int:
    """Return default chunk overlap from catalog."""
    catalog = _load_catalog()
    return catalog.get("default_chunk_overlap", 80)


def _resolve_api_key(
    provider: str,
    config_api_key: str | None = None,
    fallback_api_key: str | None = None,
) -> str | None:
    """Resolve API key for an embedding provider.

    Resolution order:
    1. config_api_key (from doc_kb_config.embedding_api_key)
    2. fallback_api_key (from agent's own api_key)
    3. Environment variable for the provider
    """
    import os

    if config_api_key:
        return config_api_key

    if fallback_api_key:
        return fallback_api_key

    env_keys = {
        "openai": "OPENAI_API_KEY",
        "huggingface": "HUGGINGFACEHUB_API_TOKEN",
        "nvidia": "NVIDIA_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    env_var = env_keys.get(provider)
    if env_var:
        return os.environ.get(env_var)

    return None


def get_embeddings(
    provider: str,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    fallback_api_key: str | None = None,
    **kwargs,
):
    """Create an Embeddings instance for the given provider.

    Args:
        provider: Embedding provider name (openai, huggingface, ollama, nvidia, google).
        model: Model name (uses provider default if not provided).
        api_key: API key from doc_kb_config (takes priority).
        base_url: Custom base URL (for providers that support it).
        fallback_api_key: Agent's own API key as fallback.
        **kwargs: Additional provider-specific arguments.

    Returns:
        A LangChain Embeddings instance.

    Raises:
        ValueError: If the provider is not supported.
    """
    model = model or get_default_embedding_model(provider)
    resolved_key = _resolve_api_key(provider, api_key, fallback_api_key)

    match provider:
        case "openai":
            from langchain_openai import OpenAIEmbeddings

            kw = {"model": model}
            if resolved_key:
                kw["api_key"] = resolved_key
            if base_url:
                kw["base_url"] = base_url
            return OpenAIEmbeddings(**kw)

        case "huggingface":
            from langchain_huggingface import HuggingFaceEndpointEmbeddings

            kw = {"model": model}
            if resolved_key:
                kw["huggingfacehub_api_token"] = resolved_key
            return HuggingFaceEndpointEmbeddings(**kw)

        case "ollama":
            from langchain_ollama import OllamaEmbeddings

            kw = {"model": model}
            if base_url:
                kw["base_url"] = base_url
            return OllamaEmbeddings(**kw)

        case "nvidia":
            from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

            kw = {"model": model}
            if resolved_key:
                kw["api_key"] = resolved_key
            if base_url:
                kw["base_url"] = base_url
            return NVIDIAEmbeddings(**kw)

        case "google":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            kw = {"model": model}
            if resolved_key:
                kw["google_api_key"] = resolved_key
            return GoogleGenerativeAIEmbeddings(**kw)

        case _:
            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                f"Supported: openai, huggingface, ollama, nvidia, google"
            )
