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
    dataset_id: str,
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

    # Capture old value
    old_value = df.at[update.row_index, update.column]

    # Coerce new value to match column dtype
    new_value = update.value
    dtype = df[update.column].dtype

    if new_value in (None, '', 'null', 'NaN', 'nan', 'None'):
        new_value = None
    elif pd.api.types.is_numeric_dtype(dtype):
        try:
            if '.' in str(new_value):
                new_value = float(new_value)
            else:
                new_value = int(new_value)
        except (ValueError, TypeError):
            return {
                "status": "failed",
                "message": f"Cannot convert '{new_value}' to numeric for column '{update.column}'",
            }
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        try:
            new_value = pd.to_datetime(new_value)
        except Exception:
            return {
                "status": "failed",
                "message": f"Cannot parse '{new_value}' as datetime for column '{update.column}'",
            }
    elif pd.api.types.is_bool_dtype(dtype):
        lower = str(new_value).lower()
        if lower in ('true', '1', 'yes'):
            new_value = True
        elif lower in ('false', '0', 'no'):
            new_value = False
        else:
            return {
                "status": "failed",
                "message": f"Cannot convert '{new_value}' to boolean for column '{update.column}'",
            }

    # Update cell
    df.at[update.row_index, update.column] = new_value

    # Save back — replace NaN/NaT/Infinity with None for JSON compatibility
    records = df.to_dict(orient="records")
    import math
    for record in records:
        for key, val in record.items():
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                record[key] = None
            elif pd.isna(val):
                record[key] = None

    dataset.preview_data = records
    await session.commit()

    return {
        "status": "success",
        "message": f"Updated cell at row {update.row_index}, column '{update.column}'",
        "old_value": old_value if not pd.isna(old_value) else None,
    }
