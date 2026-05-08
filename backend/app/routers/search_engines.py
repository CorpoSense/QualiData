"""Search engine management endpoints."""

from datetime import datetime
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.database import get_async_session
from app.db.models import SearchEngine, User
from app.routers.auth import get_current_active_user
from app.utils.crypto import encrypt_value

router = APIRouter(prefix="/search-engines", tags=["search-engines"])

# --- Supported providers ---

SUPPORTED_SEARCH_PROVIDERS = [
    {
        "provider": "duckduckgo",
        "label": "DuckDuckGo",
        "requires_api_key": False,
        "description": "Free, no API key needed. Uses the DuckDuckGo Search API.",
        "config_example": {"region": "us-en", "max_results": 5},
    },
    {
        "provider": "serper",
        "label": "Serper (Google Search)",
        "requires_api_key": True,
        "description": "Google search results via the Serper API.",
        "config_example": {"gl": "us", "hl": "en"},
    },
    {
        "provider": "brave",
        "label": "Brave Search",
        "requires_api_key": True,
        "description": "Privacy-focused search via the Brave Search API.",
        "config_example": {"max_results": 5},
    },
    {
        "provider": "serpapi",
        "label": "SerpAPI",
        "requires_api_key": True,
        "description": "Google search results via SerpAPI.",
        "config_example": {"engine": "google", "gl": "us", "hl": "en"},
    },
    {
        "provider": "google",
        "label": "Google Custom Search",
        "requires_api_key": True,
        "description": "Google Programmable Search Engine. Requires both API key and CSE ID.",
        "config_example": {"google_cse_id": "your-cse-id", "k": 5},
    },
    {
        "provider": "exa",
        "label": "Exa",
        "requires_api_key": True,
        "description": "AI-optimized search via the Exa API.",
        "config_example": {"num_results": 5},
    },
    {
        "provider": "searxng",
        "label": "SearXNG",
        "requires_api_key": False,
        "description": "Self-hosted or public SearXNG metasearch engine instance.",
        "config_example": {"searx_host": "https://seek.fyi", "k": 5},
    },
    {
        "provider": "custom",
        "label": "Custom REST API",
        "requires_api_key": False,
        "description": "Any REST API endpoint with custom headers and body template.",
        "config_example": {
            "method": "POST",
            "url": "https://my-api.com/search",
            "headers": {},
            "params": {},
            "body_template": '{"query": "{query}"}',
        },
    },
]

VALID_PROVIDERS = {p["provider"] for p in SUPPORTED_SEARCH_PROVIDERS}


# --- Pydantic schemas ---


class SearchEngineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., pattern="^(duckduckgo|serper|brave|serpapi|google|exa|searxng|custom)$")
    api_key: str | None = None
    config: dict | None = None


class SearchEngineUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    provider: str | None = None
    api_key: str | None = None
    config: dict | None = None


class SearchEngineResponse(BaseModel):
    id: str
    user_id: str
    name: str
    provider: str
    config: dict | None = None
    has_api_key: bool = False
    is_builtin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


def _search_engine_to_response(engine: SearchEngine) -> dict:
    """Convert SearchEngine model to response dict, masking api_key."""
    return {
        "id": engine.id,
        "user_id": engine.user_id,
        "name": engine.name,
        "provider": engine.provider,
        "config": engine.config,
        "has_api_key": bool(engine.api_key),
        "is_builtin": engine.is_builtin,
        "created_at": engine.created_at,
        "updated_at": engine.updated_at,
    }


# --- Endpoints ---


@router.get("/providers")
async def list_search_providers():
    """List supported search engine providers with their requirements."""
    return SUPPORTED_SEARCH_PROVIDERS


@router.get("/", response_model=List[SearchEngineResponse])
async def list_search_engines(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(SearchEngine).where(SearchEngine.user_id == current_user.id)
    )
    engines = result.scalars().all()
    return [_search_engine_to_response(e) for e in engines]


@router.post("/", response_model=SearchEngineResponse, status_code=status.HTTP_201_CREATED)
async def create_search_engine(
    engine_in: SearchEngineCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    if engine_in.provider not in VALID_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {engine_in.provider}. Valid: {sorted(VALID_PROVIDERS)}",
        )

    data = engine_in.model_dump()
    if data.get("api_key"):
        data["api_key"] = encrypt_value(data["api_key"], get_settings().secret_key)

    engine = SearchEngine(user_id=current_user.id, **data)
    session.add(engine)
    await session.commit()
    await session.refresh(engine)
    return _search_engine_to_response(engine)


@router.get("/{engine_id}", response_model=SearchEngineResponse)
async def get_search_engine(
    engine_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(SearchEngine).where(
            SearchEngine.id == engine_id, SearchEngine.user_id == current_user.id
        )
    )
    engine = result.scalar_one_or_none()
    if not engine:
        raise HTTPException(status_code=404, detail="Search engine not found")
    return _search_engine_to_response(engine)


@router.patch("/{engine_id}", response_model=SearchEngineResponse)
async def update_search_engine(
    engine_id: str,
    engine_in: SearchEngineUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(SearchEngine).where(
            SearchEngine.id == engine_id, SearchEngine.user_id == current_user.id
        )
    )
    engine = result.scalar_one_or_none()
    if not engine:
        raise HTTPException(status_code=404, detail="Search engine not found")

    for field, value in engine_in.model_dump(exclude_unset=True).items():
        if field == "api_key" and value:
            value = encrypt_value(value, get_settings().secret_key)
        setattr(engine, field, value)
    engine.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(engine)
    return _search_engine_to_response(engine)


@router.delete("/{engine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_engine(
    engine_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(SearchEngine).where(
            SearchEngine.id == engine_id, SearchEngine.user_id == current_user.id
        )
    )
    engine = result.scalar_one_or_none()
    if not engine:
        raise HTTPException(status_code=404, detail="Search engine not found")
    await session.delete(engine)
    await session.commit()
    return None
