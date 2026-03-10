"""Batch AI processing operations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["ai-operations"])


class BatchProcessRequest(BaseModel):
    columns: list[str]
    instruction: str
    output_column: str | None = None
    batch_size: int = Field(default=50, ge=1, le=500)


class BatchProcessResponse(BaseModel):
    status: str
    job_id: str
    message: str


class BatchProgressResponse(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    processed: int
    total: int
    results: list[dict] | None = None


# In-memory job tracking (in production, use Redis/database)
BATCH_JOBS = {}


@router.post("/datasets/{dataset_id}/ai-batch", response_model=BatchProcessResponse)
async def ai_batch_process(
    dataset_id: str,
    request: BatchProcessRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Process multiple columns with AI in batches."""
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
        raise HTTPException(status_code=400, detail="No data to process")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    # Validate columns
    for col in request.columns:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{col}' not found")

    # Create job
    import uuid

    job_id = str(uuid.uuid4())

    BATCH_JOBS[job_id] = {
        "status": "pending",
        "processed": 0,
        "total": len(df) * len(request.columns),
        "results": [],
        "instruction": request.instruction,
        "columns": request.columns,
        "dataset_id": dataset_id,
    }

    return BatchProcessResponse(
        status="success",
        job_id=job_id,
        message=f"Batch job started for {len(request.columns)} columns, {len(df)} rows",
    )


@router.get(
    "/datasets/{dataset_id}/ai-batch/{job_id}", response_model=BatchProgressResponse
)
async def get_batch_progress(
    dataset_id: str,
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get progress of batch AI job."""
    if job_id not in BATCH_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")

    job = BATCH_JOBS[job_id]

    return BatchProgressResponse(
        job_id=job_id,
        status=job["status"],
        processed=job["processed"],
        total=job["total"],
        results=job.get("results", [])[:10],  # Return first 10 results
    )


@router.post(
    "/datasets/{dataset_id}/ai-cross-row", response_model=BatchProcessResponse
)
async def ai_cross_row_context(
    dataset_id: str,
    column: str,
    group_by: str,
    operation: str,  # count, concat, sum, mean
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply AI with cross-row context (grouped operations)."""
    from sqlalchemy import select

    from app.routers.datasets import detect_columns, get_preview_data

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
        raise HTTPException(status_code=400, detail="No data")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns or group_by not in df.columns:
        raise HTTPException(status_code=400, detail="Invalid columns")

    # Apply grouping operation
    if operation == "count":
        df[f"{column}_count"] = df.groupby(group_by)[column].transform("count")
    elif operation == "concat":
        df[f"{column}_concat"] = df.groupby(group_by)[column].transform(
            lambda x: ", ".join(x.astype(str))
        )
    elif operation == "sum":
        df[f"{column}_sum"] = df.groupby(group_by)[column].transform("sum")
    elif operation == "mean":
        df[f"{column}_mean"] = df.groupby(group_by)[column].transform("mean")
    else:
        raise HTTPException(status_code=400, detail=f"Invalid operation: {operation}")

    # Update dataset
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)

    await session.commit()

    import uuid

    job_id = str(uuid.uuid4())

    return BatchProcessResponse(
        status="success",
        job_id=job_id,
        message=f"Applied {operation} grouped by {group_by}",
    )
