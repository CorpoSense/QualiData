"""Column profiling operations."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["column-profiling"])


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    total_rows: int
    null_count: int
    null_percent: float
    unique_count: int
    unique_percent: float
    quality_score: float
    sample_values: List[Any]
    stats: Dict[str, Any]


class ProfilingResponse(BaseModel):
    status: str
    columns: List[ColumnProfile]
    total_rows: int


@router.get("/api/datasets/{dataset_id}/profile", response_model=ProfilingResponse)
async def profile_columns(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get detailed profile of all columns in a dataset."""
    from sqlalchemy import select
    
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id,
            Project.owner_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to profile")
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(dataset.preview_data)
    total_rows = len(df)
    
    profiles = []
    
    for col in df.columns:
        col_data = df[col]
        null_count = int(col_data.isna().sum())
        unique_count = int(col_data.nunique())
        
        # Calculate quality score (0-100)
        null_percent = (null_count / total_rows) * 100 if total_rows > 0 else 0
        unique_percent = (unique_count / total_rows) * 100 if total_rows > 0 else 0
        
        # Quality score: lower nulls = higher score,适度 unique is good
        quality_score = 100 - null_percent
        if pd.api.types.is_numeric_dtype(col_data):
            # Numeric columns get bonus for having some variety but not too much
            if unique_percent > 5 and unique_percent < 95:
                quality_score += 5
        
        quality_score = min(100, max(0, quality_score))
        
        # Basic stats
        stats = {"dtype": str(col_data.dtype)}
        
        # Numeric stats
        if pd.api.types.is_numeric_dtype(col_data):
            stats.update({
                "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                "mean": float(col_data.mean()) if not pd.isna(col_data.mean()) else None,
                "median": float(col_data.median()) if not pd.isna(col_data.median()) else None,
                "std": float(col_data.std()) if not pd.isna(col_data.std()) else None,
            })
        
        # Categorical stats
        if unique_count < 50:  # Low cardinality = might be categorical
            value_counts = col_data.value_counts().head(5)
            stats["top_values"] = [
                {"value": str(v), "count": int(c)} 
                for v, c in value_counts.items()
            ]
        
        # String stats
        if col_data.dtype == 'object':
            stats["avg_length"] = float(col_data.astype(str).str.len().mean())
            stats["min_length"] = int(col_data.astype(str).str.len().min())
            stats["max_length"] = int(col_data.astype(str).str.len().max())
        
        # Detect potential issues
        issues = []
        if null_percent > 20:
            issues.append(f"High null rate ({null_percent:.1f}%)")
        if unique_count == total_rows and total_rows > 10:
            issues.append("All unique values - might be identifiers")
        if unique_count == 1:
            issues.append("Only one unique value")
        
        stats["issues"] = issues
        
        # Sample values
        sample = col_data.dropna().head(5).tolist()
        
        profiles.append(ColumnProfile(
            name=col,
            dtype=str(col_data.dtype),
            total_rows=total_rows,
            null_count=null_count,
            null_percent=round(null_percent, 2),
            unique_count=unique_count,
            unique_percent=round(unique_percent, 2),
            quality_score=round(quality_score, 1),
            sample_values=sample,
            stats=stats
        ))
    
    return ProfilingResponse(
        status="success",
        columns=profiles,
        total_rows=total_rows
    )
