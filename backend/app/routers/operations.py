"""Dataset operations routes - pandas-based data cleaning."""

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, OperationHistory, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["dataset-operations"])


# Operation schemas
class AddColumnRequest(BaseModel):
    column_name: str
    default_value: str | None = None
    formula: str | None = None


class RemoveColumnsRequest(BaseModel):
    columns: list[str]


class RenameColumnRequest(BaseModel):
    old_name: str
    new_name: str


class MergeColumnsRequest(BaseModel):
    columns: list[str]
    new_column: str
    delimiter: str = ""


class SplitColumnRequest(BaseModel):
    column: str
    delimiter: str
    new_columns: list[str]


class DuplicateColumnRequest(BaseModel):
    source_column: str
    new_column: str


class ReorderColumnsRequest(BaseModel):
    columns: list[str]


class OperationResponse(BaseModel):
    status: str
    message: str
    columns: list[dict] | None = None


async def get_dataset_with_owner_check(dataset_id: str, user_id: str, session: AsyncSession):
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == user_id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    return dataset


from app.utils.operations import save_operation


# Routes
@router.post(
    "/datasets/{dataset_id}/operations/add-column", response_model=OperationResponse
)
async def add_column(
    dataset_id: str,
    request: AddColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    if request.formula:
        if request.formula.startswith("row_number"):
            df[request.column_name] = range(1, len(df) + 1)
        elif request.formula.startswith("constant:"):
            df[request.column_name] = request.formula.replace("constant:", "")
        else:
            raise HTTPException(status_code=400, detail="Invalid formula")
    else:
        df[request.column_name] = request.default_value or None
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}
    await save_operation(dataset_id, "add_column", request.dict(), before, after, session)
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Column '{request.column_name}' added",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/remove-columns", response_model=OperationResponse
)
async def remove_columns(
    dataset_id: str,
    request: RemoveColumnsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    missing = [c for c in request.columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    df = df.drop(columns=request.columns)
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}
    await save_operation(dataset_id, "remove_columns", request.dict(), before, after, session)
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Columns {request.columns} removed",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/rename-column", response_model=OperationResponse
)
async def rename_column(
    dataset_id: str,
    request: RenameColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    if request.old_name not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.old_name}' not found"
        )
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    df = df.rename(columns={request.old_name: request.new_name})
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    await save_operation(dataset_id, "rename_column", request.dict(), before, after, session)
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Column renamed to '{request.new_name}'",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/merge-columns", response_model=OperationResponse
)
async def merge_columns(
    dataset_id: str,
    request: MergeColumnsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    missing = [c for c in request.columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    df[request.new_column] = (
        df[request.columns].astype(str).agg(request.delimiter.join, axis=1)
    )
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    await save_operation(dataset_id, "merge_columns", request.dict(), before, after, session)
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Columns merged into '{request.new_column}'",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/split-column", response_model=OperationResponse
)
async def split_column(
    dataset_id: str,
    request: SplitColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    split_data = (
        df[request.column].astype(str).str.split(request.delimiter, expand=True)
    )
    for i, col_name in enumerate(request.new_columns):
        df[col_name] = split_data[i] if i < len(split_data.columns) else None
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    await save_operation(dataset_id, "split_column", request.dict(), before, after, session)
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Column split into {len(request.new_columns)} columns",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/duplicate-column",
    response_model=OperationResponse,
)
async def duplicate_column(
    dataset_id: str,
    request: DuplicateColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    if request.source_column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.source_column}' not found"
        )
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    df[request.new_column] = df[request.source_column]
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    await save_operation(
        dataset_id, "duplicate_column", request.dict(), before, after, session
    )
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Column duplicated as '{request.new_column}'",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/reorder-columns",
    response_model=OperationResponse,
)
async def reorder_columns(
    dataset_id: str,
    request: ReorderColumnsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.preview_data)
    if set(df.columns) != set(request.columns):
        raise HTTPException(status_code=400, detail="Column mismatch")
    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "preview_data": dataset.preview_data}
    df = df[request.columns]
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    await save_operation(
        dataset_id, "reorder_columns", request.dict(), before, after, session
    )
    await session.commit()
    return OperationResponse(
        status="success", message="Columns reordered", columns=dataset.columns
    )


@router.get("/datasets/{dataset_id}/operations")
async def list_operations(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all operations for a dataset."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    result = await session.execute(
        select(OperationHistory)
        .where(cast(OperationHistory.dataset_id, String) == dataset_id)
        .order_by(OperationHistory.created_at.desc())
    )
    operations = result.scalars().all()
    return [
        {
            "id": op.id,
            "operation_type": op.operation_type,
            "operation_params": op.operation_params,
            "created_at": op.created_at.isoformat() if op.created_at else None,
            "is_undone": op.is_undone,
        }
        for op in operations
    ]


@router.get("/operations/recent")
async def get_recent_operations(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get recent operations across all datasets for the current user."""
    # Get all projects for the user
    projects_result = await session.execute(
        select(Project).where(Project.user_id == current_user.id)
    )
    projects = projects_result.scalars().all()
    project_ids = [p.id for p in projects]
    
    if not project_ids:
        return []
    
    # Get all datasets for these projects
    datasets_result = await session.execute(
        select(Dataset).where(Dataset.project_id.in_(project_ids))
    )
    datasets = datasets_result.scalars().all()
    dataset_ids = [d.id for d in datasets]
    
    if not dataset_ids:
        return []
    
    # Get recent operations for these datasets
    result = await session.execute(
        select(OperationHistory)
        .where(OperationHistory.dataset_id.in_(dataset_ids))
        .order_by(OperationHistory.created_at.desc())
        .limit(limit)
    )
    operations = result.scalars().all()
    
    # Build a map of dataset_id to dataset name
    dataset_map = {d.id: d.name for d in datasets}
    project_map = {p.id: p.name for p in projects}
    dataset_to_project = {d.id: d.project_id for d in datasets}
    
    return [
        {
            "id": op.id,
            "operation_type": op.operation_type,
            "operation_params": op.operation_params,
            "created_at": op.created_at.isoformat() if op.created_at else None,
            "is_undone": op.is_undone,
            "dataset_id": op.dataset_id,
            "dataset_name": dataset_map.get(op.dataset_id, "Unknown"),
            "project_id": dataset_to_project.get(op.dataset_id),
            "project_name": project_map.get(dataset_to_project.get(op.dataset_id), "Unknown"),
        }
        for op in operations
    ]


@router.get("/datasets/{dataset_id}/operations/history")
async def get_operation_history(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    result = await session.execute(
        select(OperationHistory)
        .where(dataset.project_id)
        .order_by(OperationHistory.created_at.desc())
    )
    operations = result.scalars().all()
    return [
        {
            "id": op.id,
            "operation_type": op.operation_type,
            "operation_params": op.operation_params,
            "created_at": op.created_at.isoformat() if op.created_at else None,
            "is_undone": op.is_undone,
        }
        for op in operations
    ]


# String operations
@router.post("/datasets/{dataset_id}/operations/string-operations")
async def string_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """String operations like uppercase, lowercase, trim, etc.

    Supports both single-column and batch (multi-column) mode:
    - Single: { "column": "name", "operation": "uppercase" }
    - Batch:  { "columns": ["name", "email"], "operation": "uppercase" }
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)

    # Support both single column and batch (multiple columns)
    column = request.get('column')
    columns = request.get('columns')
    operation = request.get('operation')

    # Determine target columns
    if columns and isinstance(columns, list):
        target_columns = columns
    elif column:
        target_columns = [column]
    else:
        raise HTTPException(status_code=400, detail="Either 'column' or 'columns' required")

    # Validate all columns exist
    missing = [c for c in target_columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")

    # Track results
    results = []

    # Apply operation to each column
    for col in target_columns:
        # Check if column is string-compatible
        try:
            df[col] = df[col].astype(str)
        except Exception:
            results.append({"column": col, "status": "skipped", "reason": "cannot convert to string"})
            continue

        # Normalize operation names
        op_map = {
            'upper': 'uppercase',
            'lower': 'lowercase',
            'strip': 'trim',
            'title': 'titlecase',
        }
        op = op_map.get(operation, operation)

        try:
            if op == 'uppercase':
                df[col] = df[col].astype(str).str.upper()
            elif op == 'lowercase':
                df[col] = df[col].astype(str).str.lower()
            elif op == 'trim':
                df[col] = df[col].astype(str).str.strip()
            elif op == 'titlecase':
                df[col] = df[col].astype(str).str.title()
            elif op == 'capitalize':
                df[col] = df[col].astype(str).str.capitalize()
            elif op == 'remove_whitespace':
                df[col] = df[col].astype(str).str.replace(r'\s+', '', regex=True)
            else:
                results.append({"column": col, "status": "skipped", "reason": f"unknown operation: {operation}"})
                continue

            results.append({"column": col, "status": "success", "operation": op})
        except Exception as e:
            results.append({"column": col, "status": "error", "reason": str(e)})

    # Check if any operations succeeded
    successful = [r for r in results if r.get('status') == 'success']
    if not successful:
        raise HTTPException(status_code=400, detail=f"No operations succeeded: {results}")

    from app.routers.datasets import detect_columns, get_preview_data
    before = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "string_operations", request, before, after, session)
    await session.commit()

    success_count = len(successful)
    msg = f"Applied {operation} to {success_count} column(s)"

    return {"status": "success", "message": msg, "columns": dataset.columns, "results": results}


# Datetime operations
@router.post("/datasets/{dataset_id}/operations/datetime-operations")
async def datetime_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Datetime operations like parse, format, extract year, etc.

    Supports both single-column and batch (multi-column) mode:
    - Single: { "column": "date", "operation": "extract_year" }
    - Batch:  { "columns": ["date1", "date2"], "operation": "extract_year" }
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)

    # Support both single column and batch (multiple columns)
    column = request.get('column')
    columns = request.get('columns')
    operation = request.get('operation')

    # Determine target columns
    if columns and isinstance(columns, list):
        target_columns = columns
    elif column:
        target_columns = [column]
    else:
        raise HTTPException(status_code=400, detail="Either 'column' or 'columns' required")

    # Validate all columns exist
    missing = [c for c in target_columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")

    # Normalize operation names
    op_map = {
        'parse': 'parse_datetime',
        'year': 'extract_year',
        'month': 'extract_month',
        'day': 'extract_day',
        'weekday': 'extract_weekday',
    }
    operation = op_map.get(operation, operation)

    # Validate datetime operations require datetime column
    if operation in ['extract_year', 'extract_month', 'extract_day', 'extract_weekday']:
        for col in target_columns:
            try:
                pd.to_datetime(df[col], errors='raise')
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{col}' is not a datetime column. Datetime extraction requires datetime data."
                )

    results = []

    # Apply operation to each column
    for col in target_columns:
        try:
            if operation == 'parse_datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
                results.append({"column": col, "status": "success", "operation": "parse_datetime"})
            elif operation == 'extract_year':
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.year
                results.append({"column": col, "status": "success", "operation": "extract_year"})
            elif operation == 'extract_month':
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.month
                results.append({"column": col, "status": "success", "operation": "extract_month"})
            elif operation == 'extract_day':
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.day
                results.append({"column": col, "status": "success", "operation": "extract_day"})
            elif operation == 'extract_weekday':
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.day_name()
                results.append({"column": col, "status": "success", "operation": "extract_weekday"})
            else:
                results.append({"column": col, "status": "skipped", "reason": f"unknown operation: {operation}"})
        except Exception as e:
            results.append({"column": col, "status": "error", "reason": str(e)})

    # Check if any operations succeeded
    successful = [r for r in results if r.get('status') == 'success']
    if not successful:
        raise HTTPException(status_code=400, detail=f"No operations succeeded: {results}")

    from app.routers.datasets import detect_columns, get_preview_data
    before = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "datetime_operations", request, before, after, session)
    await session.commit()

    success_count = len(successful)
    msg = f"Applied {operation} to {success_count} column(s)"

    return {"status": "success", "message": msg, "columns": dataset.columns, "results": results}


# Fill NA operations
@router.post("/datasets/{dataset_id}/operations/fillna")
async def fillna_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Fill NA operations."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)
    method = request.get('method')
    fill_value = request.get('fill_value')
    request.get('column')

    if method == 'drop':
        before_count = len(df)
        df = df.dropna()
        modified = before_count - len(df)
    elif method == 'forward':
        before = df.isna().sum().sum()
        df = df.ffill()
        modified = before - df.isna().sum().sum()
    elif method == 'backward':
        before = df.isna().sum().sum()
        df = df.bfill()
        modified = before - df.isna().sum().sum()
    elif method == 'constant':
        if fill_value:
            before = df.isna().sum().sum()
            df = df.fillna(fill_value)
            modified = before - df.isna().sum().sum()
        else:
            raise HTTPException(status_code=400, detail="fill_value required for constant method")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {method}")

    from app.routers.datasets import detect_columns, get_preview_data
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "fillna", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Applied fillna ({method}) - {modified} cells filled", "columns": dataset.columns, "row_count": dataset.row_count}


# Remove duplicates
@router.post("/datasets/{dataset_id}/operations/remove-duplicates")
async def remove_duplicates(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Remove duplicate rows."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)
    before_count = len(df)
    df = df.drop_duplicates()
    after_count = len(df)

    from app.routers.datasets import detect_columns, get_preview_data
    before_snapshot = {"columns": dataset.columns, "row_count": before_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": after_count, "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "remove_duplicates", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Removed {before_count - after_count} duplicate rows", "columns": dataset.columns, "row_count": dataset.row_count}


# Sort
@router.post("/datasets/{dataset_id}/operations/sort")
async def sort_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Sort by column."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)
    column = request.get('column')
    ascending = request.get('ascending', True)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    df = df.sort_values(by=column, ascending=ascending)

    from app.routers.datasets import detect_columns, get_preview_data
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "sort", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Sorted by {column}", "columns": dataset.columns}


# Structural operations (rename, drop column, change type)
@router.post("/datasets/{dataset_id}/operations/structural")
async def structural_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Structural operations like rename column, drop column, change type.

    Supports both single-column and batch (multi-column) mode for drop/astype:
    - Single: { "operation": "drop", "column": "name" }
    - Batch:  { "operation": "drop", "columns": ["name", "email"] }
    - Rename is single-column only.
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)
    operation = request.get('operation')
    column = request.get('column')
    columns = request.get('columns')

    results = []

    if operation == 'rename':
        # Rename is single-column only
        new_name = request.get('new_name')
        if not column or not new_name:
            raise HTTPException(status_code=400, detail="column and new_name required")
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column {column} not found")
        df = df.rename(columns={column: new_name})
        results.append({"column": column, "status": "success", "new_name": new_name})

    elif operation == 'drop':
        # Support batch drop
        target_columns = columns if isinstance(columns, list) else ([column] if column else [])
        if not target_columns:
            raise HTTPException(status_code=400, detail="column or columns required")

        missing = [c for c in target_columns if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")

        df = df.drop(columns=target_columns)
        results.append({"columns": target_columns, "status": "success"})

    elif operation == 'astype':
        # Support batch astype
        target_columns = columns if isinstance(columns, list) else ([column] if column else [])
        dtype = request.get('dtype')

        if not target_columns:
            raise HTTPException(status_code=400, detail="column or columns required")
        if not dtype:
            raise HTTPException(status_code=400, detail="dtype required")

        missing = [c for c in target_columns if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")

        for col in target_columns:
            try:
                df[col] = df[col].astype(dtype)
                results.append({"column": col, "status": "success", "dtype": dtype})
            except Exception as e:
                results.append({"column": col, "status": "error", "reason": str(e)})

    elif operation == 'add_column':
        new_name = request.get('new_name') or request.get('column')
        default_value = request.get('default_value', '')
        source = request.get('source')
        if not new_name:
            raise HTTPException(status_code=400, detail="new_name is required")
        if new_name in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{new_name}' already exists")
        if source and source in df.columns:
            df[new_name] = df[source].copy()
            results.append({"column": new_name, "source": source, "status": "success"})
        else:
            df[new_name] = default_value
            results.append({"column": new_name, "default": default_value, "status": "success"})

    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")

    from app.routers.datasets import detect_columns, get_preview_data
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "structural", request, before_snapshot, after_snapshot, session)
    await session.commit()

    msg = f"Applied {operation}"
    if operation == 'drop' and isinstance(columns, list):
        msg = f"Dropped {len(columns)} columns"
    elif operation == 'astype' and isinstance(columns, list):
        msg = f"Changed type on {len(columns)} columns"

    return {"status": "success", "message": msg, "columns": dataset.columns, "results": results}


# Fuzzy deduplication
@router.post("/datasets/{dataset_id}/operations/fuzzy-dedupe")
async def fuzzy_dedupe(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Fuzzy deduplication based on column similarity."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)
    column = request.get('column')
    threshold = request.get('threshold', 0.8)

    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column {column} not found")

    from difflib import SequenceMatcher
    rows = df[column].astype(str).tolist()
    to_keep = []
    for row in rows:
        is_duplicate = False
        for kept in to_keep:
            if SequenceMatcher(None, row, kept).ratio() > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            to_keep.append(row)

    df = df[df[column].astype(str).isin(to_keep)].reset_index(drop=True)

    from app.routers.datasets import detect_columns, get_preview_data
    before_count = dataset.row_count
    before_snapshot = {"columns": dataset.columns, "row_count": before_count, "preview_data": dataset.preview_data}
    removed = before_count - len(df)
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "fuzzy_dedupe", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Removed {removed} fuzzy duplicates", "columns": dataset.columns, "row_count": dataset.row_count}


# Numeric operations (round, normalize, outliers)
@router.post("/datasets/{dataset_id}/operations/numeric")
async def numeric_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Numeric operations like round, normalize, detect outliers.

    Supports both single-column and batch (multi-column) mode:
    - Single: { "column": "score", "operation": "round" }
    - Batch:  { "columns": ["score", "price", "qty"], "operation": "round" }
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.preview_data)
    operation = request.get('operation')

    # Support both single column and batch (multiple columns)
    column = request.get('column')
    columns = request.get('columns')

    # Determine target columns
    if columns and isinstance(columns, list):
        target_columns = columns
    elif column:
        target_columns = [column]
    else:
        raise HTTPException(status_code=400, detail="Either 'column' or 'columns' required")

    # Validate all columns exist
    missing = [c for c in target_columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")

    results = []

    # Apply operation to each column
    for col in target_columns:
        # Check if column is numeric
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
        except Exception:
            results.append({"column": col, "status": "skipped", "reason": "not numeric"})
            continue

        try:
            if operation == 'round':
                decimals = request.get('decimals', 2)
                df[col] = df[col].round(decimals)

            elif operation == 'normalize':
                # Min-max normalization to 0-1
                col_min = df[col].min()
                col_max = df[col].max()
                if col_max - col_min != 0:
                    df[col] = (df[col] - col_min) / (col_max - col_min)

            elif operation == 'outliers':
                # Simple IQR-based outlier detection - replace with median
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                median = df[col].median()
                df[col] = df[col].apply(lambda x: median if x < lower or x > upper else x)
            else:
                results.append({"column": col, "status": "skipped", "reason": f"unknown operation: {operation}"})
                continue

            results.append({"column": col, "status": "success", "operation": operation})
        except Exception as e:
            results.append({"column": col, "status": "error", "reason": str(e)})

    # Check if any operations succeeded
    successful = [r for r in results if r.get('status') == 'success']
    if not successful:
        raise HTTPException(status_code=400, detail=f"No operations succeeded: {results}")

    from app.routers.datasets import detect_columns, get_preview_data
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": dataset.preview_data}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "numeric", request, before_snapshot, after_snapshot, session)
    await session.commit()

    success_count = len(successful)
    msg = f"Applied {operation} to {success_count} column(s)"

    return {"status": "success", "message": msg, "columns": dataset.columns, "results": results}
