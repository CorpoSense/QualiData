"""Cell update operations."""

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/datasets", tags=["datasets"])


class CellUpdate(BaseModel):
    row_index: int
    column: str
    value: str


@router.post("/{dataset_id}/operations/update-cell")
async def update_cell(
    dataset_id: int,
    update: CellUpdate,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Update a single cell value."""
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data")

    # Convert to DataFrame
    df = pd.DataFrame(dataset.preview_data)

    # Validate column
    if update.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{update.column}' not found"
        )

    # Validate row index
    if update.row_index < 0 or update.row_index >= len(df):
        raise HTTPException(status_code=400, detail="Invalid row index")

    # Update cell
    df.at[update.row_index, update.column] = update.value

    # Save back
    dataset.preview_data = df.to_dict(orient="records")
    await session.commit()

    return {
        "status": "success",
        "message": f"Updated cell at row {update.row_index}, column '{update.column}'",
        "old_value": dataset.preview_data[update.row_index].get(update.column),
    }
