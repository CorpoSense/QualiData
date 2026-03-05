"""Dataset routes for import/export."""

import tempfile
import os

from app.services.smart_importer import SmartImporter

import io

import pandas as pd
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/datasets", tags=["datasets"])


# Pydantic schemas
class DatasetCreate(BaseModel):
    name: str
    description: str | None = None
    project_id: str


class DatasetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class DatasetResponse(BaseModel):
    id: str
    name: str
    description: str | None
    project_id: str
    file_name: str | None
    file_size: int
    file_type: str | None
    row_count: int
    columns: list | None
    preview_data: list | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class ColumnInfo(BaseModel):
    name: str
    dtype: str


class DatasetPreviewResponse(BaseModel):
    columns: list[ColumnInfo]
    preview_data: list[dict]
    row_count: int


def detect_columns(df: pd.DataFrame) -> list[dict]:
    """Detect column names and types from DataFrame."""
    columns = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        # Map pandas dtypes to simpler types
        if "int" in dtype:
            dtype = "integer"
        elif "float" in dtype:
            dtype = "float"
        elif "object" in dtype:
            dtype = "string"
        elif "datetime" in dtype:
            dtype = "datetime"
        elif "bool" in dtype:
            dtype = "boolean"
        columns.append({"name": col, "dtype": dtype})
    return columns


def get_preview_data(df: pd.DataFrame, max_rows: int = 10) -> list[dict]:
    """Get preview data from DataFrame."""
    return df.head(max_rows).to_dict(orient="records")


# Routes
@router.post("/import", response_model=DatasetResponse)
async def import_dataset(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    name: str | None = Form(None),
    description: str | None = Form(None),
    # Smart import options
    auto_detect: bool = Form(True),
    delimiter: str | None = Form(None),
    encoding: str | None = Form(None),
    has_header: bool | None = Form(None),
    sheet_name: str | None = Form(None),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Import data from CSV, Excel, or JSON file."""
    # Verify project belongs to user
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

    # Save uploaded file to temp file for smart importer
    filename = file.filename or "data.csv"
    content = await file.read()
    file_size = len(content)
    
    # Determine file type
    file_ext = os.path.splitext(filename)[1].lower()
    file_type = "csv"
    if file_ext in (".xlsx", ".xls", ".xlsb", ".ods"):
        file_type = "excel"
    elif file_ext == ".json":
        file_type = "json"
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        if auto_detect:
            # Use smart importer for automatic detection
            importer = SmartImporter()
            analysis = importer.analyze(tmp_path)
            
            if not analysis.is_importable:
                error_msgs = [m.message for m in analysis.messages if m.severity.value == "error"]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot analyze file: {'; '.join(error_msgs)}"
                )
            
            df = importer.import_file(
                tmp_path,
                analysis=analysis,
                delimiter=delimiter,
                encoding=encoding,
                has_header=has_header,
                sheet_name=sheet_name,
            )
        else:
            # Use manual settings (no auto detection)
            if file_type == "csv":
                df = pd.read_csv(
                    tmp_path,
                    sep=delimiter or ',',
                    encoding=encoding or 'utf-8',
                    header=0 if has_header else None,
                )
            elif file_type == "excel":
                df = pd.read_excel(
                    tmp_path,
                    sheet_name=sheet_name,
                    header=0 if has_header else None,
                )
            elif file_type == "json":
                df = pd.read_json(tmp_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type.",
                )
    finally:
        # Clean up temp file
        os.unlink(tmp_path)

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
    dataset_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get dataset preview (columns and sample data)."""
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )

    # Verify ownership via project
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Apply limit to preview data
    preview_data = (dataset.preview_data or [])[:limit]

    return {
        "columns": dataset.columns or [],
        "preview_data": preview_data,
        "row_count": dataset.row_count,
        "limit": limit,
    }


@router.get("/{dataset_id}/export")
async def export_dataset(
    dataset_id: str,
    format: str = "csv",
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Export dataset to CSV, Excel, or JSON."""
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Reconstruct DataFrame from preview (simplified - in production, store full data)
    if not dataset.preview_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data to export"
        )

    df = pd.DataFrame(dataset.preview_data)

    # Export to requested format
    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        return {
            "content": output.getvalue(),
            "content_type": "text/csv",
            "filename": f"{dataset.name}.csv",
        }
    elif format == "json":
        return {
            "content": df.to_json(orient="records", indent=2),
            "content_type": "application/json",
            "filename": f"{dataset.name}.json",
        }
    elif format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return {
            "content": output.getvalue().decode("latin-1"),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "filename": f"{dataset.name}.xlsx",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Use csv, json, or excel.",
        )


@router.get("", response_model=list[DatasetResponse])
async def list_datasets(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all datasets for a project."""
    # Verify project ownership
    result = await session.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    datasets_result = await session.execute(
        select(Dataset).where(Dataset.project_id == project_id)
    )
    datasets = datasets_result.scalars().all()

    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get a specific dataset."""
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a dataset."""
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Update project stats
    project.row_count -= dataset.row_count
    project.storage_bytes -= dataset.file_size

    await session.delete(dataset)
    await session.commit()

    return None
