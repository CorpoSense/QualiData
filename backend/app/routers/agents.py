"""Agent management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.database import get_async_session
from app.db.models import Agent, User
from app.routers.auth import get_current_active_user
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o-mini")
    system_prompt: str | None = None
    prompt_template: str | None = None
    temperature: float = Field(default=0.3, ge=0, le=2)
    is_template: bool = False
    is_builtin: bool = False

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    provider: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    prompt_template: str | None = None
    temperature: float | None = Field(None, ge=0, le=2)
    is_template: bool | None = None
    is_builtin: bool | None = None

class AgentResponse(AgentBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Agent).where(Agent.user_id == current_user.id))
    agents = result.scalars().all()
    return agents

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    agent = Agent(
        user_id=current_user.id,
        **agent_in.dict()
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent

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
    return agent

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
    for field, value in agent_in.dict(exclude_unset=True).items():
        setattr(agent, field, value)
    agent.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(agent)
    return agent

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
