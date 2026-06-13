"""Chart persistence endpoints.

Provides CRUD operations for chart configurations tied to datasets.
Charts are dataset-wide (shared across all users with access).
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Chart, Dataset, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["charts"])


# --- Pydantic schemas ---


class ChartCreateRequest(BaseModel):
    config: dict
    meta: dict | None = None


class ChartUpdateRequest(BaseModel):
    config: dict | None = None
    meta: dict | None = None
    sort_order: int | None = None


class ReorderRequest(BaseModel):
    chart_ids: List[str]


class ChartResponse(BaseModel):
    id: str
    dataset_id: str
    config: dict
    meta: dict | None = None
    sort_order: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


def _chart_to_response(chart: Chart) -> dict:
    """Convert Chart model to response dict."""
    return {
        "id": chart.id,
        "dataset_id": chart.dataset_id,
        "config": chart.config,
        "meta": chart.meta,
        "sort_order": chart.sort_order,
        "created_at": chart.created_at,
    }


# --- Helper: validate dataset access ---


async def _get_and_validate_dataset(
    dataset_id: str,
    current_user: User,
    session: AsyncSession,
) -> Dataset:
    """Validate dataset exists and user has access via project ownership."""
    from app.db.models import Project

    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Validate project ownership
    proj_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id,
            Project.user_id == current_user.id,
        )
    )
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset


# --- Endpoints ---


@router.get("/datasets/{dataset_id}/charts")
async def list_charts(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all charts for a dataset, sorted by sort_order."""
    await _get_and_validate_dataset(dataset_id, current_user, session)

    result = await session.execute(
        select(Chart)
        .where(Chart.dataset_id == dataset_id)
        .order_by(Chart.sort_order, Chart.created_at)
    )
    charts = result.scalars().all()
    return {"charts": [_chart_to_response(c) for c in charts]}


@router.post(
    "/datasets/{dataset_id}/charts",
    status_code=status.HTTP_201_CREATED,
)
async def create_chart(
    dataset_id: str,
    body: ChartCreateRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new chart configuration for a dataset."""
    await _get_and_validate_dataset(dataset_id, current_user, session)

    # Determine sort_order: append after existing charts
    existing = await session.execute(
        select(Chart)
        .where(Chart.dataset_id == dataset_id)
        .order_by(Chart.sort_order.desc())
        .limit(1)
    )
    last_chart = existing.scalar_one_or_none()
    next_order = (last_chart.sort_order + 1) if last_chart else 0

    chart = Chart(
        dataset_id=dataset_id,
        config=body.config,
        meta=body.meta,
        sort_order=next_order,
    )
    session.add(chart)
    await session.commit()
    await session.refresh(chart)

    return _chart_to_response(chart)


# --- Reorder must come BEFORE {chart_id} routes to avoid matching ---


@router.put("/datasets/{dataset_id}/charts/reorder")
async def reorder_charts(
    dataset_id: str,
    body: ReorderRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Bulk reorder charts by providing an ordered list of chart IDs."""
    await _get_and_validate_dataset(dataset_id, current_user, session)

    result = await session.execute(
        select(Chart).where(Chart.dataset_id == dataset_id)
    )
    charts = result.scalars().all()
    chart_map = {c.id: c for c in charts}

    for idx, chart_id in enumerate(body.chart_ids):
        if chart_id in chart_map:
            chart_map[chart_id].sort_order = idx

    await session.commit()
    return {"status": "ok"}


@router.put("/datasets/{dataset_id}/charts/{chart_id}")
async def update_chart(
    dataset_id: str,
    chart_id: str,
    body: ChartUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Update a chart's configuration, metadata, or sort order."""
    await _get_and_validate_dataset(dataset_id, current_user, session)

    result = await session.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dataset_id == dataset_id,
        )
    )
    chart = result.scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    if body.config is not None:
        chart.config = body.config
    if body.meta is not None:
        chart.meta = body.meta
    if body.sort_order is not None:
        chart.sort_order = body.sort_order

    await session.commit()
    await session.refresh(chart)

    return _chart_to_response(chart)


@router.delete(
    "/datasets/{dataset_id}/charts/{chart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chart(
    dataset_id: str,
    chart_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a chart configuration."""
    await _get_and_validate_dataset(dataset_id, current_user, session)

    result = await session.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dataset_id == dataset_id,
        )
    )
    chart = result.scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    session.delete(chart)
    await session.commit()
    return None
