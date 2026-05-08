"""Agent management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Literal, Union

from app.db.database import get_async_session
from app.db.models import Agent, User
from app.routers.auth import get_current_active_user
from app.config import get_settings
from app.utils.crypto import encrypt_value
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

router = APIRouter(prefix="/agents", tags=["agents"])


# --- Memory configuration schemas ---


class SlidingWindowConfig(BaseModel):
    """Sliding window memory: removes oldest messages when count exceeds threshold."""
    type: Literal["sliding_window"] = "sliding_window"
    max_messages: int = Field(default=20, ge=5, le=100)


class SummarizerConfig(BaseModel):
    """Summarizer memory: condenses older messages into a summary when token threshold is hit."""
    type: Literal["summarizer"] = "summarizer"
    trigger_tokens: int = Field(default=4000, ge=1000, le=128000)
    keep_messages: int = Field(default=20, ge=5, le=50)


class TrimTokensConfig(BaseModel):
    """Trim tokens memory: keeps only system message + recent N messages."""
    type: Literal["trim_tokens"] = "trim_tokens"
    keep_recent: int = Field(default=4, ge=2, le=20)


MemoryConfig = Union[SlidingWindowConfig, SummarizerConfig, TrimTokensConfig]


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o-mini")
    system_prompt: str | None = None
    prompt_template: str | None = None
    temperature: float = Field(default=0.3, ge=0, le=2)
    memory_config: MemoryConfig | None = None
    is_template: bool = False
    is_builtin: bool = False


class AgentCreate(AgentBase):
    api_key: str | None = None
    base_url: str | None = None
    search_engine_id: str | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    provider: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    prompt_template: str | None = None
    temperature: float | None = Field(None, ge=0, le=2)
    memory_config: MemoryConfig | None = None
    is_template: bool | None = None
    is_builtin: bool | None = None
    api_key: str | None = None
    base_url: str | None = None
    search_engine_id: str | None = None


class AgentResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None = None
    provider: str
    model: str
    system_prompt: str | None = None
    prompt_template: str | None = None
    temperature: float
    memory_config: dict | None = None
    is_template: bool
    is_builtin: bool
    created_at: datetime
    updated_at: datetime
    has_api_key: bool = False
    search_engine_id: str | None = None
    has_search_engine: bool = False

    model_config = ConfigDict(from_attributes=True)

def _agent_to_response(agent: Agent) -> dict:
    """Convert Agent model to response dict, masking api_key."""
    return {
        "id": agent.id,
        "user_id": agent.user_id,
        "name": agent.name,
        "description": agent.description,
        "provider": agent.provider,
        "model": agent.model,
        "system_prompt": agent.system_prompt,
        "prompt_template": agent.prompt_template,
        "temperature": agent.temperature,
        "memory_config": agent.memory_config,
        "is_template": agent.is_template,
        "is_builtin": agent.is_builtin,
        "base_url": agent.base_url,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
        "has_api_key": bool(agent.api_key),
        "search_engine_id": agent.search_engine_id,
        "has_search_engine": bool(agent.search_engine_id),
    }


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Agent).where(Agent.user_id == current_user.id))
    agents = result.scalars().all()
    return [_agent_to_response(a) for a in agents]


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    data = agent_in.model_dump()
    if data.get("api_key"):
        data["api_key"] = encrypt_value(data["api_key"], get_settings().secret_key)
    agent = Agent(user_id=current_user.id, **data)
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return _agent_to_response(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _agent_to_response(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_in: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for field, value in agent_in.model_dump(exclude_unset=True).items():
        if field == "api_key" and value:
            value = encrypt_value(value, get_settings().secret_key)
        setattr(agent, field, value)
    agent.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(agent)
    return _agent_to_response(agent)

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await session.delete(agent)
    await session.commit()
    return None
