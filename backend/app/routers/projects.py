"""Project routes."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Project, User, Dataset
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/projects", tags=["projects"])


# Pydantic schemas
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    user_id: str
    row_count: int
    storage_bytes: int
    datasets_count: int = 0
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
    page: int
    page_size: int


# Routes
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new project."""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        user_id=current_user.id,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all projects for current user."""
    # Subquery to count datasets per project
    dataset_count_subquery = (
        select(
            Dataset.project_id,
            func.count(Dataset.id).label("datasets_count")
        )
        .group_by(Dataset.project_id)
        .subquery()
    )

    # Main query with datasets_count from subquery
    query = (
        select(Project, dataset_count_subquery.c.datasets_count)
        .outerjoin(
            dataset_count_subquery,
            Project.id == dataset_count_subquery.c.project_id
        )
        .where(Project.user_id == current_user.id)
    )

    if search:
        query = query.where(Project.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = (
        query
        .order_by(Project.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await session.execute(query)
    rows = result.all()

    # Map to ProjectResponse
    projects = []
    for row in rows:
        project = row[0]
        datasets_count = row[1] or 0
        projects.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "user_id": project.user_id,
            "row_count": project.row_count,
            "storage_bytes": project.storage_bytes,
            "datasets_count": datasets_count,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        })

    return {"projects": projects, "total": total, "page": page, "page_size": page_size}



@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get a specific project."""
    # Subquery to count datasets
    dataset_count_subquery = (
        select(
            Dataset.project_id,
            func.count(Dataset.id).label("datasets_count")
        )
        .group_by(Dataset.project_id)
        .subquery()
    )

    result = await session.execute(
        select(Project, dataset_count_subquery.c.datasets_count)
        .outerjoin(
            dataset_count_subquery,
            Project.id == dataset_count_subquery.c.project_id
        )
        .where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    project = row[0]
    datasets_count = row[1] or 0

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "user_id": project.user_id,
        "row_count": project.row_count,
        "storage_bytes": project.storage_bytes,
        "datasets_count": datasets_count,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Update a project."""
    result = await session.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    await session.commit()
    await session.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a project."""
    result = await session.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    await session.delete(project)
    await session.commit()

    return None
