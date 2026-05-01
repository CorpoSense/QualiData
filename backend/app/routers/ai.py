"""AI endpoints for data cleaning assistance."""

import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Agent, User
from app.models.schemas import (
    AnalyzeDataRequest,
    AnalyzeDataResponse,
    ChatRequest,
    ChatResponse,
    GenerateCodeRequest,
    GenerateCodeResponse,
    ProviderInfo,
    ProvidersListResponse,
    SuggestFixRequest,
    SuggestFixResponse,
)
from app.routers.auth import get_current_active_user
from app.services.ai_provider import AIProvider, get_chat_model, list_providers
from app.services.cleaner import DataCleaningAssistant

router = APIRouter(prefix="/ai", tags=["ai"])


def _get_provider(provider_name: str) -> AIProvider:
    """Convert provider name to enum."""
    try:
        return AIProvider(provider_name.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider_name}. "
            f"Valid providers: {[p.value for p in AIProvider]}",
        )


@router.get("/providers", response_model=ProvidersListResponse)
async def get_providers():
    """List all supported AI providers."""
    providers = [ProviderInfo(**p) for p in list_providers()]
    return ProvidersListResponse(providers=providers)


# Anthropic has no public model listing API — keep curated fallback
ANTHROPIC_FALLBACK = [
    "claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229", "claude-3-haiku-20240307",
]


async def _fetch_models_from_api(provider: str, api_key: str | None = None) -> list[str]:
    """Fetch available models from provider's API."""
    import logging
    logger = logging.getLogger(__name__)
    provider = provider.lower()

    # Resolve API key: param > env var
    env_keys = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    key = api_key or os.environ.get(env_keys.get(provider, ""), "")

    # Ollama: local, no auth needed
    if provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get("http://localhost:11434/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return sorted([m["name"] for m in data.get("models", [])])
        except Exception as e:
            logger.debug(f"Ollama models fetch failed: {e}")
            return ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "gemma2"]

    # All other providers need an API key
    if not key:
        return []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if provider == "anthropic":
                # Anthropic uses x-api-key header
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                )
            elif provider == "google":
                # Google uses query param
                resp = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
                )
            else:
                # OpenAI-compatible: OpenAI, Groq, DeepSeek, OpenRouter, Huggingface
                base_urls = {
                    "openai": "https://api.openai.com/v1",
                    "groq": "https://api.groq.com/openai/v1",
                    "deepseek": "https://api.deepseek.com",
                    "openrouter": "https://openrouter.ai/api/v1",
                    "huggingface": "https://router.huggingface.co/v1",
                }
                base = base_urls.get(provider)
                if not base:
                    return []
                headers = {}
                if key:
                    headers["Authorization"] = f"Bearer {key}"
                resp = await client.get(f"{base}/models", headers=headers)

            resp.raise_for_status()
            data = resp.json()

            # Parse response based on provider
            if provider == "google":
                models = [
                    m["name"].split("/")[-1]
                    for m in data.get("models", [])
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
            else:
                models = [m["id"] for m in data.get("data", [])]

            return sorted(models)

    except Exception as e:
        logger.warning(f"Models fetch failed for {provider}: {e}")
        # Return fallback for Anthropic only
        if provider == "anthropic":
            return ANTHROPIC_FALLBACK
        return []


@router.get("/models/{provider}")
async def get_models(provider: str, api_key: str | None = None):
    """List available models for a provider. Fetches from provider's API dynamically."""
    models = await _fetch_models_from_api(provider, api_key)
    return {"provider": provider, "models": models}


@router.post("/analyze", response_model=AnalyzeDataResponse)
async def analyze_data(request: AnalyzeDataRequest):
    """
    Analyze data and get cleaning recommendations.

    Requires appropriate API key environment variable for the chosen provider:
    - openai: OPENAI_API_KEY
    - anthropic: ANTHROPIC_API_KEY
    - google: GOOGLE_API_KEY
    - groq: GROQ_API_KEY
    - deepseek: DEEPSEEK_API_KEY
    - ollama: No key needed (runs locally)
    """
    provider = _get_provider(request.provider)
    assistant = DataCleaningAssistant(
        provider=provider,
        model=request.model,
    )

    try:
        analysis = await assistant.analyze_data(request.data_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AnalyzeDataResponse(
        analysis=analysis,
        provider=provider.value,
        model=request.model or assistant.llm.model_name,
    )


@router.post("/suggest-fix", response_model=SuggestFixResponse)
async def suggest_fix(request: SuggestFixRequest):
    """Get suggestions for fixing a specific data quality issue."""
    provider = _get_provider(request.provider)
    assistant = DataCleaningAssistant(
        provider=provider,
        model=request.model,
    )

    try:
        suggestion = await assistant.suggest_fix(request.issue_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return SuggestFixResponse(
        suggestion=suggestion,
        provider=provider.value,
        model=request.model or assistant.llm.model_name,
    )


@router.post("/generate-code", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest):
    """Generate code for a data cleaning task."""
    provider = _get_provider(request.provider)
    assistant = DataCleaningAssistant(
        provider=provider,
        model=request.model,
    )

    try:
        code = await assistant.generate_code(
            request.task_description,
            request.language,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return GenerateCodeResponse(
        code=code,
        provider=provider.value,
        model=request.model or assistant.llm.model_name,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """General chat with the data cleaning assistant.

    When agent_id is provided, uses the agent's configured provider, model,
    API key, and system prompt instead of the request-level provider/model.
    """
    # If agent_id is provided, resolve agent config and use it directly
    if request.agent_id:
        from app.routers.ai_operations import _get_agent_config

        agent_config = await _get_agent_config(request.agent_id, current_user.id, session)
        provider = AIProvider(agent_config["provider"])
        llm_kwargs = {}
        if agent_config.get("api_key"):
            llm_kwargs["api_key"] = agent_config["api_key"]
        if agent_config.get("base_url"):
            llm_kwargs["base_url"] = agent_config["base_url"]
        llm = get_chat_model(
            provider,
            model=agent_config.get("model"),
            temperature=agent_config.get("temperature", 0.3),
            **llm_kwargs,
        )
        system_prompt = agent_config.get("system_prompt") or "You are a helpful data cleaning assistant."
        try:
            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=request.message),
            ])
            response_text = response.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return ChatResponse(
            response=response_text,
            provider=provider.value,
            model=agent_config.get("model") or llm.model_name,
        )

    # Fallback: use provider/model from request (legacy behavior)
    provider = _get_provider(request.provider)
    assistant = DataCleaningAssistant(
        provider=provider,
        model=request.model,
    )

    try:
        response = await assistant.chat(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        response=response,
        provider=provider.value,
        model=request.model or assistant.llm.model_name,
    )
