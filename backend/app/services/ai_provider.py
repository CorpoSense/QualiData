"""AI Provider configuration and factory."""

from enum import Enum
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
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
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"


# Default models per provider
DEFAULT_MODELS = {
    AIProvider.OPENAI: "gpt-4o-mini",
    AIProvider.ANTHROPIC: "claude-sonnet-4-20250514",
    AIProvider.GOOGLE: "gemini-2.0-flash",
    AIProvider.OLLAMA: "llama3.2",
    AIProvider.GROQ: "llama-3.3-70b-versatile",
    AIProvider.DEEPSEEK: "deepseek-chat",
    AIProvider.OPENROUTER: "openai/gpt-4o-mini",  # OpenRouter uses provider/model format
}


def get_chat_model(
    provider: AIProvider,
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs,
) -> BaseChatModel:
    """
    Get a chat model for the specified provider.

    Args:
        provider: The AI provider to use
        model: Specific model name (uses default if not provided)
        temperature: Sampling temperature (0-1)
        **kwargs: Additional provider-specific arguments

    Returns:
        A LangChain chat model instance
    """
    model_name = model or DEFAULT_MODELS[provider]

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

        case _:
            raise ValueError(f"Unsupported provider: {provider}")


def list_providers() -> list[dict]:
    """List all supported AI providers with their default models."""
    return [
        {
            "provider": p.value,
            "default_model": DEFAULT_MODELS[p],
        }
        for p in AIProvider
    ]
