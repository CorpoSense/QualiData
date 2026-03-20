"""AI endpoints for data cleaning assistance."""

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


# Common models per provider (curated list for autocomplete suggestions)
COMMON_MODELS = {
    "openai": [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
        "o1", "o1-mini", "o3-mini",
    ],
    "anthropic": [
        "claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229", "claude-3-haiku-20240307",
    ],
    "google": [
        "gemini-2.0-flash", "gemini-2.0-pro", "gemini-1.5-pro",
        "gemini-1.5-flash", "gemini-1.0-pro",
    ],
    "ollama": [
        "llama3.2", "llama3.1", "llama3", "mistral", "codellama",
        "phi3", "gemma2", "qwen2.5",
    ],
    "groq": [
        "llama-3.3-70b-versatile", "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant", "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "deepseek": [
        "deepseek-chat", "deepseek-reasoner", "deepseek-coder",
    ],
    "openrouter": [
        "openai/gpt-4o", "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet", "anthropic/claude-3-haiku",
        "google/gemini-2.0-flash", "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mistral-large",
    ],
}


@router.get("/models/{provider}")
async def get_models(provider: str):
    """List common models for a provider."""
    models = COMMON_MODELS.get(provider.lower(), [])
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
