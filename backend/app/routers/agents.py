"""Agent routes for AI configuration management."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Agent, User
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/agents", tags=["agents"])


# Pydantic schemas
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    provider: str = "openai"
    model: Optional[str] = None
    temperature: float = Field(default=0.3, ge=0, le=2)
    system_prompt: Optional[str] = None
    is_template: bool = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    system_prompt: Optional[str] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    provider: str
    model: Optional[str]
    temperature: float
    system_prompt: Optional[str]
    is_template: bool
    usage_count: int
    owner_id: int
    created_at: str

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int


# Routes
@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new AI agent configuration."""
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        provider=agent_data.provider,
        model=agent_data.model,
        temperature=agent_data.temperature,
        system_prompt=agent_data.system_prompt,
        is_template=agent_data.is_template,
        owner_id=current_user.id,
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


@router.get("", response_model=AgentListResponse)
async def list_agents(
    include_templates: bool = False,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """List all agents for current user."""
    query = select(Agent)
    
    if include_templates:
        # Include templates (is_template=True) or user's own agents
        query = query.where(
            (Agent.owner_id == current_user.id) | (Agent.is_template == True)
        )
    else:
        query = query.where(Agent.owner_id == current_user.id)
    
    result = await session.execute(query)
    agents = result.scalars().all()
    
    return {"agents": agents, "total": len(agents)}


@router.get("/templates", response_model=AgentListResponse)
async def list_templates(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """List available agent templates."""
    result = await session.execute(
        select(Agent).where(Agent.is_template == True)
    )
    agents = result.scalars().all()
    
    return {"agents": agents, "total": len(agents)}


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific agent."""
    result = await session.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Allow access if owner or if it's a template
    if agent.owner_id != current_user.id and not agent.is_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update an agent."""
    result = await session.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.owner_id == current_user.id
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if agent_data.name is not None:
        agent.name = agent_data.name
    if agent_data.description is not None:
        agent.description = agent_data.description
    if agent_data.provider is not None:
        agent.provider = agent_data.provider
    if agent_data.model is not None:
        agent.model = agent_data.model
    if agent_data.temperature is not None:
        agent.temperature = agent_data.temperature
    if agent_data.system_prompt is not None:
        agent.system_prompt = agent_data.system_prompt
    
    await session.commit()
    await session.refresh(agent)
    
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete an agent."""
    result = await session.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.owner_id == current_user.id
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    await session.delete(agent)
    await session.commit()
    
    return None


@router.post("/{agent_id}/use", response_model=AgentResponse)
async def use_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Increment usage count for an agent."""
    result = await session.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Allow usage if owner or if it's a template
    if agent.owner_id != current_user.id and not agent.is_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    agent.usage_count += 1
    await session.commit()
    await session.refresh(agent)
    
    return agent
