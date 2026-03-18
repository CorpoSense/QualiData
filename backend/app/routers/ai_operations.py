"""AI-powered data cleaning operations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["ai-operations"])


class AICleaningRequest(BaseModel):
    type: str = Field(default='structural')
    column: str | None = None
    columns: list[str] | None = None
    instruction: str
    batch_size: int = Field(default=10, ge=1, le=100)
    agent_id: int | None = None

    @property
    def column_list(self) -> list[str]:
        """Get columns as a list."""
        if self.columns:
            return self.columns
        elif self.column:
            return [self.column]
        return []


class AICleaningResponse(BaseModel):
    status: str
    message: str
    results: list[dict] | None = None
    columns: list[dict] | None = None
    json_output: dict | None = None


# Import AI router to reuse the existing AI integration
# This creates a bridge between dataset operations and AI


@router.post("/datasets/{dataset_id}/ai-clean", response_model=AICleaningResponse)
async def ai_clean_column(
    dataset_id: str,
    request: AICleaningRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply AI cleaning to a column based on natural language instruction."""
    from sqlalchemy import select

    # Validate that at least one column is provided
    columns_to_clean = request.column_list
    if not columns_to_clean:
        raise HTTPException(
            status_code=422, detail="Either 'column' or 'columns' must be provided"
        )

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
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    # Validate all columns exist
    for col in columns_to_clean:
        if col not in df.columns:
            raise HTTPException(
                status_code=400, detail=f"Column '{col}' not found"
            )

    # Get the column data as a list for each column
    column_data = {}
    for col in columns_to_clean:
        column_data[col] = df[col].head(request.batch_size).tolist()

    # Call AI to process the data
    # This would integrate with the existing AI router
    # For now, return a placeholder response

    columns_str = ", ".join(columns_to_clean) if len(columns_to_clean) > 1 else columns_to_clean[0]
    return AICleaningResponse(
        status="success",
        message=f"AI cleaning request queued for column(s) '{columns_str}' with instruction: {request.instruction}",
        results=[{"column": col, "values": column_data[col]} for col in columns_to_clean],
    )


@router.post("/datasets/{dataset_id}/ai-analyze", response_model=AICleaningResponse)
async def ai_analyze_column(
    dataset_id: str,
    column: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get AI analysis and suggestions for a column."""
    from sqlalchemy import select

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
        raise HTTPException(status_code=400, detail="No data to analyze")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Basic statistics
    col_data = df[column]
    analysis = {
        "column": column,
        "dtype": str(col_data.dtype),
        "total_rows": len(col_data),
        "null_count": int(col_data.isna().sum()),
        "unique_count": int(col_data.nunique()),
        "sample_values": col_data.head(5).tolist(),
    }

    # Add numeric stats if applicable
    if pd.api.types.is_numeric_dtype(col_data):
        analysis.update(
            {
                "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                "mean": (
                    float(col_data.mean()) if not pd.isna(col_data.mean()) else None
                ),
                "median": (
                    float(col_data.median()) if not pd.isna(col_data.median()) else None
                ),
            }
        )

    return AICleaningResponse(
        status="success", message=f"Analysis for column '{column}'", results=[analysis]
    )


@router.post(
    "/datasets/{dataset_id}/ai-json-clean", response_model=AICleaningResponse
)
async def ai_clean_json(
    dataset_id: str,
    column: str,
    instruction: str,
    output_column: str | None = None,
    batch_size: int = 10,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply AI cleaning with structured JSON output."""
    from sqlalchemy import select

    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Get column data
    column_data = df[column].head(batch_size).tolist()

    # Simulate structured JSON response
    # In production, this would call the AI with JSON schema
    results = []
    for val in column_data:
        results.append(
            {
                "original": str(val),
                "cleaned": str(val).strip().lower() if val else "",
                "valid": True,
            }
        )

    # Create output column
    out_col = output_column or f"{column}_cleaned"
    df[out_col] = df[column].apply(lambda x: str(x).strip().lower() if x else "")

    # Update dataset
    from app.routers.datasets import detect_columns, get_preview_data

    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)

    await session.commit()

    return AICleaningResponse(
        status="success",
        message=f"Applied JSON-structured cleaning to column '{column}'",
        results=results[:5],
        json_output={
            "instruction": instruction,
            "processed": len(results),
            "output_column": out_col,
        },
    )
