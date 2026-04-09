"""Cell update operations."""

import logging
import math

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset
from app.routers.auth import get_current_active_user
from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

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
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[CELL_UPDATE] Received request - dataset_id: {dataset_id}, row_index: {update.row_index}, column: {update.column}, value: {update.value}")
    
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        logger.warning(f"[CELL_UPDATE] Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not dataset.data_json or "data" not in dataset.data_json:
        logger.warning(f"[CELL_UPDATE] No data in dataset: {dataset_id}")
        raise HTTPException(status_code=400, detail="No data")

    # Convert to DataFrame
    df = pd.DataFrame(dataset.data_json["data"])
    logger.info(f"[CELL_UPDATE] DataFrame created with {len(df)} rows, columns: {list(df.columns)}")

    # Validate column
    if update.column not in df.columns:
        logger.warning(f"[CELL_UPDATE] Column not found: {update.column}, available: {list(df.columns)}")
        raise HTTPException(
            status_code=400, detail=f"Column '{update.column}' not found"
        )

    # Validate row index
    logger.info(f"[CELL_UPDATE] Validating row_index: {update.row_index} (df length: {len(df)})")
    if update.row_index < 0 or update.row_index >= len(df):
        logger.warning(f"[CELL_UPDATE] Invalid row_index: {update.row_index}, df length: {len(df)}")
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
    logger.info(f"[CELL_UPDATE] Cell updated at row {update.row_index}, column {update.column}")

    # Save back — use centralized functions for consistent data handling
    # Get data from whichever source we have (prefer data_json if available for full dataset)
    if dataset.data_json and "data" in dataset.data_json:
        # Update from data_json (full dataset)
        df = pd.DataFrame(dataset.data_json["data"])
    else:
        # Fall back to preview_data
        df = pd.DataFrame(dataset.data_json["data"])
    
    # Apply the cell update
    df.at[update.row_index, update.column] = new_value
    
    # Update data_json using centralized function
    dataset.data_json = get_full_data_json(df)
    logger.info(f"[CELL_UPDATE] Saved data_json with {len(df)} rows")
    
    # Also update columns metadata
    dataset.columns = detect_columns(df)
    
    await session.commit()

    return {
        "status": "success",
        "message": f"Updated cell at row {update.row_index}, column '{update.column}'",
        "old_value": old_value if not pd.isna(old_value) else None,
    }
