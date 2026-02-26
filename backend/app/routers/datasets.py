"""Dataset routes for import/export."""

import io
import json
from typing import Optional, List
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal, get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/datasets", tags=["datasets"])


# Pydantic schemas
class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: int


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    project_id: int
    file_name: Optional[str]
    file_size: int
    file_type: Optional[str]
    row_count: int
    columns: Optional[dict]
    preview_data: Optional[list]
    created_at: str

    class Config:
        from_attributes = True


class ColumnInfo(BaseModel):
    name: str
    dtype: str


class DatasetPreviewResponse(BaseModel):
    columns: List[ColumnInfo]
    preview_data: List[dict]
    row_count: int


def detect_columns(df: pd.DataFrame) -> List[dict]:
    """Detect column names and types from DataFrame."""
    columns = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        # Map pandas dtypes to simpler types
        if 'int' in dtype:
            dtype = 'integer'
        elif 'float' in dtype:
            dtype = 'float'
        elif 'object' in dtype:
            dtype = 'string'
        elif 'datetime' in dtype:
            dtype = 'datetime'
        elif 'bool' in dtype:
            dtype = 'boolean'
        columns.append({"name": col, "dtype": dtype})
    return columns


def get_preview_data(df: pd.DataFrame, max_rows: int = 10) -> List[dict]:
    """Get preview data from DataFrame."""
    return df.head(max_rows).to_dict(orient='records')


# Routes
@router.post("/import", response_model=DatasetResponse)
async def import_dataset(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Import data from CSV, Excel, or JSON file."""
    # Verify project belongs to user
    result = await session.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Determine file type
    filename = file.filename or ""
    if filename.endswith('.csv'):
        file_type = 'csv'
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith(('.xlsx', '.xls')):
        file_type = 'excel'
        df = pd.read_excel(io.BytesIO(content))
    elif filename.endswith('.json'):
        file_type = 'json'
        df = pd.read_json(io.BytesIO(content))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Use CSV, Excel, or JSON."
        )
    
    # Get column info and preview
    columns = detect_columns(df)
    preview_data = get_preview_data(df)
    row_count = len(df)
    
    # Use filename as name if not provided
    if not name:
        name = filename
    
    # Create dataset record
    dataset = Dataset(
        name=name,
        description=description,
        project_id=project_id,
        file_name=filename,
        file_size=file_size,
        file_type=file_type,
        columns=columns,
        preview_data=preview_data,
        row_count=row_count,
    )
    session.add(dataset)
    
    # Update project stats
    project.row_count += row_count
    project.storage_bytes += file_size
    
    await session.commit()
    await session.refresh(dataset)
    
    return dataset


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
async def preview_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get dataset preview (columns and sample data)."""
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Verify ownership via project
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id,
            Project.owner_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "columns": dataset.columns or [],
        "preview_data": dataset.preview_data or [],
        "row_count": dataset.row_count
    }


@router.get("/{dataset_id}/export")
async def export_dataset(
    dataset_id: int,
    format: str = "csv",
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Export dataset to CSV, Excel, or JSON."""
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id,
            Project.owner_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Reconstruct DataFrame from preview (simplified - in production, store full data)
    if not dataset.preview_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to export"
        )
    
    df = pd.DataFrame(dataset.preview_data)
    
    # Export to requested format
    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        return {
            "content": output.getvalue(),
            "content_type": "text/csv",
            "filename": f"{dataset.name}.csv"
        }
    elif format == "json":
        return {
            "content": df.to_json(orient='records', indent=2),
            "content_type": "application/json",
            "filename": f"{dataset.name}.json"
        }
    elif format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return {
            "content": output.getvalue().decode('latin-1'),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "filename": f"{dataset.name}.xlsx"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Use csv, json, or excel."
        )


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """List all datasets for a project."""
    # Verify project ownership
    result = await session.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    datasets_result = await session.execute(
        select(Dataset).where(Dataset.project_id == project_id)
    )
    datasets = datasets_result.scalars().all()
    
    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific dataset."""
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id,
            Project.owner_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a dataset."""
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id,
            Project.owner_id == current_user.id
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update project stats
    project.row_count -= dataset.row_count
    project.storage_bytes -= dataset.file_size
    
    await session.delete(dataset)
    await session.commit()
    
    return None
