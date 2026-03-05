"""Dataset operations routes - pandas-based data cleaning."""

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
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


def save_operation(
    dataset_id: str,
    operation_type: str,
    params: dict,
    before: dict,
    after: dict,
    session: AsyncSession,
):
    op = OperationHistory(
        dataset_id=dataset_id,
        operation_type=operation_type,
        operation_params=params,
        before_snapshot=before,
        after_snapshot=after,
        is_applied=True,
        is_undone=False,
    )
    session.add(op)


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

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}
    save_operation(dataset_id, "add_column", request.dict(), before, after, session)
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

    before = {"columns": dataset.columns}
    df = df.drop(columns=request.columns)
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}
    save_operation(dataset_id, "remove_columns", request.dict(), before, after, session)
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

    before = {"columns": dataset.columns}
    df = df.rename(columns={request.old_name: request.new_name})
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    save_operation(dataset_id, "rename_column", request.dict(), before, after, session)
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

    before = {"columns": dataset.columns}
    df[request.new_column] = (
        df[request.columns].astype(str).agg(request.delimiter.join, axis=1)
    )
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    save_operation(dataset_id, "merge_columns", request.dict(), before, after, session)
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

    before = {"columns": dataset.columns}
    split_data = (
        df[request.column].astype(str).str.split(request.delimiter, expand=True)
    )
    for i, col_name in enumerate(request.new_columns):
        df[col_name] = split_data[i] if i < len(split_data.columns) else None
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    save_operation(dataset_id, "split_column", request.dict(), before, after, session)
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

    before = {"columns": dataset.columns}
    df[request.new_column] = df[request.source_column]
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    save_operation(
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

    before = {"columns": dataset.columns}
    df = df[request.columns]
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}
    save_operation(
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
        .where(OperationHistory.project_id == dataset.project_id)
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
    """String operations like uppercase, lowercase, trim, etc."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    
    df = pd.DataFrame(dataset.preview_data)
    column = request.get('column')
    operation = request.get('operation')
    
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    
    before_data = df[column].tolist()
    
    if operation == 'uppercase':
        df[column] = df[column].astype(str).str.upper()
    elif operation == 'lowercase':
        df[column] = df[column].astype(str).str.lower()
    elif operation == 'trim':
        df[column] = df[column].astype(str).str.strip()
    elif operation == 'titlecase':
        df[column] = df[column].astype(str).str.title()
    elif operation == 'capitalize':
        df[column] = df[column].astype(str).str.capitalize()
    elif operation == 'remove_whitespace':
        df[column] = df[column].astype(str).str.replace(r'\s+', '', regex=True)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")
    
    from app.routers.datasets import detect_columns, get_preview_data
    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}
    
    # Skip saving operation for now - model has different fields
# save_operation(dataset_id, "string_operations", request, before, after, session)
    await session.commit()
    
    return {"status": "success", "message": f"Applied {operation} to column {column}", "columns": dataset.columns}


# Datetime operations
@router.post("/datasets/{dataset_id}/operations/datetime-operations")
async def datetime_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Datetime operations like parse, format, extract year, etc."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    
    df = pd.DataFrame(dataset.preview_data)
    column = request.get('column')
    operation = request.get('operation')
    
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    
    if operation == 'parse_datetime':
        try:
            df[column] = pd.to_datetime(df[column], errors='coerce')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse datetime: {str(e)}")
    elif operation == 'extract_year':
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.year
    elif operation == 'extract_month':
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.month
    elif operation == 'extract_day':
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.day
    elif operation == 'extract_weekday':
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.day_name()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")
    
    from app.routers.datasets import detect_columns, get_preview_data
    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}
    
    # save_operation(dataset_id, "datetime_operations", request, before, after, session)
    await session.commit()
    
    return {"status": "success", "message": f"Applied {operation} to column {column}", "columns": dataset.columns}


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
    column = request.get('column')
    
    if method == 'drop':
        df = df.dropna()
    elif method == 'forward':
        df = df.fillna(method='ffill')
    elif method == 'backward':
        df = df.fillna(method='bfill')
    elif method == 'constant':
        if fill_value:
            df = df.fillna(fill_value)
        else:
            raise HTTPException(status_code=400, detail="fill_value required for constant method")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
    
    from app.routers.datasets import detect_columns, get_preview_data
    before = {"columns": dataset.columns, "row_count": dataset.row_count}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}
    
    # save_operation(dataset_id, "fillna", request, before, after, session)
    await session.commit()
    
    return {"status": "success", "message": f"Applied fillna ({method})", "columns": dataset.columns, "row_count": dataset.row_count}


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
    before = {"columns": dataset.columns, "row_count": before_count}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": after_count}
    
    # save_operation(dataset_id, "remove_duplicates", request, before, after, session)
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
    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}
    
    # save_operation(dataset_id, "sort", request, before, after, session)
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
    """Structural operations like rename column, drop column, change type."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")
    
    df = pd.DataFrame(dataset.preview_data)
    operation = request.get('operation')
    column = request.get('column')
    
    if operation == 'rename':
        new_name = request.get('new_name')
        if not column or not new_name:
            raise HTTPException(status_code=400, detail="column and new_name required")
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column {column} not found")
        df = df.rename(columns={column: new_name})
        
    elif operation == 'drop':
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column {column} not found")
        df = df.drop(columns=[column])
        
    elif operation == 'astype':
        dtype = request.get('dtype')
        if not column or not dtype:
            raise HTTPException(status_code=400, detail="column and dtype required")
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column {column} not found")
        try:
            df[column] = df[column].astype(dtype)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cannot convert: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")
    
    from app.routers.datasets import detect_columns, get_preview_data
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    await session.commit()
    
    return {"status": "success", "message": f"Applied {operation}", "columns": dataset.columns}


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
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    await session.commit()
    
    return {"status": "success", "message": f"Removed {before_count - len(df)} fuzzy duplicates", "row_count": dataset.row_count}


# Undo/Redo placeholders
@router.post("/datasets/{dataset_id}/operations/undo")
async def undo_operation(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    raise HTTPException(status_code=501, detail="Undo not yet implemented")


@router.post("/datasets/{dataset_id}/operations/redo")
async def redo_operation(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    raise HTTPException(status_code=501, detail="Redo not yet implemented")
