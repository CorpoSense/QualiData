"""AI Provider configuration and factory."""

from enum import Enum

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter


class AIProvider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    GROQ = "groq"
    NVIDIA = "nvidia"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"


# Providers that support custom base URLs
CUSTOM_BASE_URL_PROVIDERS = {"openai", "huggingface", "ollama", "groq", "nvidia", "deepseek"}

# Default models per provider
DEFAULT_MODELS = {
    AIProvider.OPENAI: "gpt-4o-mini",
    AIProvider.ANTHROPIC: "claude-sonnet-4-20250514",
    AIProvider.GOOGLE: "gemini-2.0-flash",
    AIProvider.OLLAMA: "llama3.2",
    AIProvider.GROQ: "llama-3.3-70b-versatile",
    AIProvider.NVIDIA: "nvidia/nemotron-3-super-120b-a12b",
    AIProvider.DEEPSEEK: "deepseek-chat",
    AIProvider.OPENROUTER: "openai/gpt-4o-mini",
    AIProvider.HUGGINGFACE: "meta-llama/Llama-3.1-8B-Instruct",
}


def get_chat_model(
    provider: AIProvider,
    model: str | None = None,
    temperature: float = 0.7,
    base_url: str | None = None,
    **kwargs,
) -> BaseChatModel:
    """
    Get a chat model for the specified provider.

    Args:
        provider: The AI provider to use
        model: Specific model name (uses default if not provided)
        temperature: Sampling temperature (0-1)
        base_url: Custom API base URL (for providers that support it)
        **kwargs: Additional provider-specific arguments (api_key, etc.)

    Returns:
        A LangChain chat model instance
    """
    model_name = model or DEFAULT_MODELS[provider]

    # Apply custom base URL if provided and supported
    if base_url and provider.value in CUSTOM_BASE_URL_PROVIDERS:
        kwargs["base_url"] = base_url

    match provider:
        case AIProvider.OPENAI:
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.ANTHROPIC:
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.OLLAMA:
            return ChatOllama(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.GROQ:
            return ChatGroq(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.NVIDIA:
            return ChatNVIDIA(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.DEEPSEEK:
            return ChatDeepSeek(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.OPENROUTER:
            return ChatOpenRouter(
                model=model_name,
                temperature=temperature,
                **kwargs,
            )

        case AIProvider.HUGGINGFACE:
            from langchain_huggingface import HuggingFaceEndpoint
            hf_kwargs = {
                "repo_id": model_name,
                "temperature": temperature,
            }
            if kwargs.get("api_key"):
                hf_kwargs["huggingfacehub_api_token"] = kwargs["api_key"]
            if base_url:
                hf_kwargs["endpoint_url"] = base_url
            endpoint = HuggingFaceEndpoint(**hf_kwargs)
            from langchain_huggingface import ChatHuggingFace
            return ChatHuggingFace(llm=endpoint)

        case _:
            raise ValueError(f"Unsupported provider: {provider}")


def list_providers() -> list[dict]:
    """List all supported AI providers with their default models."""
    return [
        {
            "provider": p.value,
            "default_model": DEFAULT_MODELS[p],
            "supports_base_url": p.value in CUSTOM_BASE_URL_PROVIDERS,
        }
        for p in AIProvider
    ]
