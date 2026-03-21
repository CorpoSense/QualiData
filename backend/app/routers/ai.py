"""AI endpoints for data cleaning assistance."""

import os

import httpx
from fastapi import APIRouter, HTTPException

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
from app.services.ai_provider import AIProvider, list_providers
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
            elif provider == "huggingface":
                # Huggingface: list popular models via Hub API
                resp = await client.get(
                    "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=50&filter=text-generation",
                    headers={"Authorization": f"Bearer {key}"},
                )
            else:
                # OpenAI-compatible: OpenAI, Groq, DeepSeek, OpenRouter
                base_urls = {
                    "openai": "https://api.openai.com/v1",
                    "groq": "https://api.groq.com/openai/v1",
                    "deepseek": "https://api.deepseek.com",
                    "openrouter": "https://openrouter.ai/api/v1",
                }
                base = base_urls.get(provider)
                if not base:
                    return []
                resp = await client.get(
                    f"{base}/models",
                    headers={"Authorization": f"Bearer {key}"},
                )

            resp.raise_for_status()
            data = resp.json()

            # Parse response based on provider
            if provider == "google":
                models = [
                    m["name"].split("/")[-1]
                    for m in data.get("models", [])
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
            elif provider == "huggingface":
                # Huggingface returns array of {id, ...}
                models = [m["id"] for m in data if isinstance(m, dict) and "id" in m]
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
async def chat(request: ChatRequest):
    """General chat with the data cleaning assistant."""
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
