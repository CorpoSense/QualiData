"""Pivot table operations for data analysis."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user
from app.services.pivot_service import PivotService

router = APIRouter(tags=["pivot"])


class PivotRequest(BaseModel):
    """Request model for creating a pivot table."""

    index_columns: list[str] = Field(..., description="Columns to use as rows (index)")
    column_columns: list[str] = Field(..., description="Columns to use as columns")
    value_column: str = Field(..., description="Column to aggregate")
    aggfunc: str = Field(
        default="count",
        description="Aggregation function: count, sum, mean, median, min, max, std",
    )
    bin_continuous: bool = Field(
        default=True, description="Whether to bin continuous columns"
    )
    bins: int = Field(
        default=10, ge=2, le=20, description="Number of bins for continuous columns"
    )
    binning_strategy: str = Field(
        default="equal_width",
        description="Binning strategy: 'equal_width' or 'equal_freq'",
    )
    include_nulls: bool = Field(
        default=False, description="Whether to include null values in aggregation"
    )
    unique_threshold: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum unique values to consider as categorical",
    )


class ValueCountsRequest(BaseModel):
    """Request model for value counts analysis."""

    columns: list[str] = Field(..., description="Columns to analyze")
    normalize: bool = Field(
        default=False, description="Whether to return proportions instead of counts"
    )


class PivotResponse(BaseModel):
    """Response model for pivot table."""

    status: str
    pivot: list[dict[str, Any]]
    columns: list[str]
    summary: dict[str, Any]


class ValueCountsResponse(BaseModel):
    """Response model for value counts."""

    status: str
    columns: list[str]
    normalize: bool
    data: list[dict[str, Any]]


class ColumnTypesResponse(BaseModel):
    """Response model for column types."""

    status: str
    categorical: list[str]
    continuous: list[str]
    datetime: list[str]


@router.post("/datasets/{dataset_id}/pivot", response_model=PivotResponse)
async def create_pivot_table(
    dataset_id: str,
    request: PivotRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create a pivot table from a dataset.

    Supports:
    - Multiple index and column columns
    - Various aggregation functions (count, sum, mean, median, min, max, std)
    - Auto-binning for continuous columns
    - Configurable binning strategies (equal_width, equal_freq)
    - Include/exclude null values
    - Configurable unique threshold for categorical detection
    """
    from sqlalchemy import select

    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data available for pivot")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    # Create pivot
    service = PivotService(df)
    try:
        result = service.create_pivot(
            index_columns=request.index_columns,
            column_columns=request.column_columns,
            value_column=request.value_column,
            aggfunc=request.aggfunc,
            bin_continuous=request.bin_continuous,
            bins=request.bins,
            binning_strategy=request.binning_strategy,
            include_nulls=request.include_nulls,
            unique_threshold=request.unique_threshold,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create pivot table: {str(e)}"
        )

    return PivotResponse(
        status="success",
        pivot=result["pivot"],
        columns=result["columns"],
        summary=result["summary"],
    )


@router.get(
    "/datasets/{dataset_id}/pivot/columns", response_model=ColumnTypesResponse
)
async def get_pivot_columns(
    dataset_id: str,
    unique_threshold: int = 20,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get available columns for pivot table with their types.

    Returns columns categorized as categorical, continuous, or datetime.
    The unique_threshold parameter allows customizing the cutoff for categorical detection.
    """
    from sqlalchemy import select

    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data available")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    # Get column types
    service = PivotService(df)
    column_types = service.get_column_types(unique_threshold=unique_threshold)

    return ColumnTypesResponse(
        status="success",
        categorical=column_types["categorical"],
        continuous=column_types["continuous"],
        datetime=column_types["datetime"],
    )


@router.post("/datasets/{dataset_id}/pivot/value-counts", response_model=ValueCountsResponse)
async def get_value_counts(
    dataset_id: str,
    request: ValueCountsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get frequency analysis for columns.

    Supports:
    - Single column value counts
    - Multi-column frequency analysis
    - Normalized (proportions) or raw counts
    """
    from sqlalchemy import select

    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data available")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    # Get value counts
    service = PivotService(df)
    try:
        result = service.value_counts_analysis(
            columns=request.columns, normalize=request.normalize
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compute value counts: {str(e)}"
        )

    return ValueCountsResponse(
        status="success",
        columns=result["columns"],
        normalize=result["normalize"],
        data=result["data"],
    )
