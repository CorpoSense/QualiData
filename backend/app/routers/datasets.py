"""Dataset routes for import/export."""

import tempfile
import os

from app.services.smart_importer import SmartImporter

import io

import pandas as pd
import numpy as np
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


def get_preview_data(df: pd.DataFrame, max_rows: int = 500, offset: int = 0) -> list[dict]:
    """Get preview data from DataFrame."""
    # Convert datetime columns FIRST (before NaN replacement, since NaT != NaN)
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
            df[col] = df[col].replace("NaT", None)
    # Replace NaN/inf with None for JSON compatibility
    df = df.replace([np.inf, -np.inf], np.nan).replace({np.nan: None})
    return df.iloc[offset:offset + max_rows].to_dict(orient="records")


# Routes
@router.post("/import", response_model=DatasetResponse)
async def import_dataset(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    name: str | None = Form(None),
    description: str | None = Form(None),
    # Smart import options
    auto_detect: str | None = Form('true'),
    delimiter: str | None = Form(None),
    encoding: str | None = Form(None),
    has_header: str | None = Form(None),
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
    
    # Convert string values from FormData
    auto_detect_bool = auto_detect.lower() == 'true' if auto_detect else True
    has_header_bool = has_header.lower() == 'true' if has_header else True
    
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
                delimiter=delimiter if not auto_detect_bool else None,
                encoding=encoding,
                has_header=has_header_bool if not auto_detect_bool else None,
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
    limit: int = Query(10, ge=1, le=500),
    page: int = Query(1, ge=1),
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

    # Apply limit and page to preview_data
    # Note: preview_data is cached, so we can only return up to the cached amount
    # For full pagination, the data would need to be stored in data_json
    preview_list = dataset.preview_data or []
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    preview_data = preview_list[start_idx:end_idx]

    return {
        "columns": dataset.columns or [],
        "preview_data": preview_data,
        "row_count": dataset.row_count,
        "page": page,
        "limit": limit,
    }


@router.post("/{dataset_id}/filtered")
async def filtered_dataset_post(
    dataset_id: str,
    filters: dict,
    limit: int = Query(10, ge=1, le=500),
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Filter dataset rows by column values (POST with JSON body).

    Body: {"country": "N/A", "city": "Paris"} — only non-empty values are used as filters.
    Returns matching rows with pagination + total matching count.
    """
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

    preview_list = dataset.preview_data or []
    if not preview_list:
        return {"columns": dataset.columns or [], "preview_data": [], "row_count": 0, "total_matching": 0, "page": page, "limit": limit}

    # Build active filters (non-empty values only)
    active_filters = {k: str(v).strip().lower() for k, v in filters.items() if v and str(v).strip()}

    # Filter rows
    matching_indices = []
    for i, row in enumerate(preview_list):
        match = True
        for col, filter_val in active_filters.items():
            cell_val = str(row.get(col, "")).lower()
            if filter_val not in cell_val:
                match = False
                break
        if match:
            matching_indices.append(i)

    total_matching = len(matching_indices)

    # Paginate matching indices
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_indices = matching_indices[start_idx:end_idx]

    preview_data = [preview_list[i] for i in page_indices]

    return {
        "columns": dataset.columns or [],
        "preview_data": preview_data,
        "row_count": dataset.row_count,
        "total_matching": total_matching,
        "matching_indices": matching_indices,
        "page": page,
        "limit": limit,
    }


@router.get("/{dataset_id}/export")
async def export_dataset(
    dataset_id: str,
    format: str = "csv",
    columns: str | None = None,  # comma-separated column names
    limit: int = 0,  # 0 = all rows
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Export dataset to CSV, JSON, or Excel. Returns a file download."""
    from fastapi.responses import StreamingResponse

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
        raise HTTPException(status_code=400, detail="No data to export")

    df = pd.DataFrame(dataset.preview_data)

    # Filter columns if specified
    if columns:
        col_list = [c.strip() for c in columns.split(",") if c.strip()]
        valid_cols = [c for c in col_list if c in df.columns]
        if valid_cols:
            df = df[valid_cols]

    # Limit rows if specified
    if limit > 0:
        df = df.head(limit)

    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in (dataset.name or "export"))

    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.csv"'},
        )
    elif format == "json":
        content = df.to_json(orient="records", indent=2)
        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.json"'},
        )
    elif format == "tsv":
        output = io.StringIO()
        df.to_csv(output, index=False, sep="\t")
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/tab-separated-values",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.tsv"'},
        )
    elif format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.xlsx"'},
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use csv, json, tsv, or excel.")


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


@router.patch("/{dataset_id}")
async def update_dataset(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Update dataset name and/or description."""
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

    name = request.get("name")
    description = request.get("description")

    if name is not None:
        if not name.strip():
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        dataset.name = name.strip()
    if description is not None:
        dataset.description = description.strip()

    await session.commit()
    await session.refresh(dataset)

    return {"status": "success", "message": "Dataset updated", "dataset": {"id": dataset.id, "name": dataset.name, "description": dataset.description}}


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


def _build_db_url(db_type: str, host: str, port: str, database: str, username: str, password: str) -> str:
    """Build SQLAlchemy connection URL from parameters."""
    drivers = {
        "postgresql": "postgresql+psycopg2",
        "mysql": "mysql+pymysql",
        "sqlite": "sqlite",
        "oracle": "oracle+oracledb",
    }
    driver = drivers.get(db_type)
    if not driver:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {db_type}")
    if db_type == "sqlite":
        return f"sqlite:///{database}"
    return f"{driver}://{username}:{password}@{host}:{port}/{database}"


@router.post("/import/db/test")
async def test_db_connection(request: dict):
    """Test a database connection."""
    from sqlalchemy import create_engine, text

    try:
        url = _build_db_url(
            request.get("db_type", "postgresql"),
            request.get("host", "localhost"),
            str(request.get("port", 5432)),
            request.get("database", ""),
            request.get("username", ""),
            request.get("password", ""),
        )
        engine = create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@router.post("/import/db/tables")
async def list_db_tables(request: dict):
    """List tables in a database."""
    from sqlalchemy import create_engine, inspect

    try:
        url = _build_db_url(
            request.get("db_type", "postgresql"),
            request.get("host", "localhost"),
            str(request.get("port", 5432)),
            request.get("database", ""),
            request.get("username", ""),
            request.get("password", ""),
        )
        engine = create_engine(url, connect_args={"connect_timeout": 5})
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        engine.dispose()
        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list tables: {str(e)}")


@router.post("/import/db", response_model=dict)
async def import_from_database(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Import a database table as a dataset."""
    from sqlalchemy import create_engine, text

    table_name = request.get("table")
    if not table_name:
        raise HTTPException(status_code=400, detail="table is required")

    try:
        url = _build_db_url(
            request.get("db_type", "postgresql"),
            request.get("host", "localhost"),
            str(request.get("port", 5432)),
            request.get("database", ""),
            request.get("username", ""),
            request.get("password", ""),
        )
        engine = create_engine(url, connect_args={"connect_timeout": 10})
        df = pd.read_sql_table(table_name, engine)
        engine.dispose()

        # Convert datetime columns to ISO strings for JSON serialization
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read table: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Table is empty")

    # Create dataset
    project_id = request.get("project_id")
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")

    project_result = await session.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    dataset = Dataset(
        project_id=project_id,
        name=request.get("name", table_name),
        description=f"Imported from {request.get('db_type', 'database')} table: {table_name}",
        file_name=f"{table_name}.csv",
        file_type="csv",
        row_count=len(df),
        columns=detect_columns(df),
        preview_data=get_preview_data(df),
    )

    session.add(dataset)
    await session.commit()
    await session.refresh(dataset)

    return {
        "status": "success",
        "message": f"Imported {len(df)} rows from '{table_name}'",
        "dataset_id": dataset.id,
        "row_count": len(df),
    }
