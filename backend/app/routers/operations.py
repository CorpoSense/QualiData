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


def filter_df_by_indices(df: pd.DataFrame, indices: list[int] | None) -> pd.DataFrame:
    """Filter DataFrame to include only specified row indices.
    
    Args:
        df: Input DataFrame
        indices: List of row indices to keep. If None, returns original df.
    
    Returns:
        DataFrame filtered to specified indices
    """
    if not indices:
        return df
    # Validate indices are within range
    valid_indices = [i for i in indices if 0 <= i < len(df)]
    if not valid_indices:
        return df
    return df.iloc[valid_indices].copy()


def apply_operation_to_filtered_rows(
    df: pd.DataFrame,
    indices: list[int] | None,
    operation_fn: callable
) -> tuple[pd.DataFrame, int]:
    """Apply an operation to filtered rows only, then merge back.
    
    Args:
        df: Full DataFrame
        indices: List of row indices to apply operation to. If None, applies to all.
        operation_fn: Function that takes df and returns modified df
    
    Returns:
        Tuple of (modified DataFrame, count of modified rows)
    """
    if not indices:
        # Apply to all rows
        modified_df = operation_fn(df)
        return modified_df, len(df)
    
    # Validate indices
    valid_indices = [i for i in indices if 0 <= i < len(df)]
    if not valid_indices:
        return df, 0
    
    # Split into filtered and non-filtered
    filtered_df = df.iloc[valid_indices].copy()
    non_filtered_indices = [i for i in range(len(df)) if i not in valid_indices]
    non_filtered_df = df.iloc[non_filtered_indices].copy() if non_filtered_indices else pd.DataFrame()
    
    # Apply operation to filtered only
    modified_filtered = operation_fn(filtered_df)
    
    # Merge back - preserve original order
    result_rows = []
    for i in range(len(df)):
        if i in valid_indices:
            # Find this index in valid_indices to get corresponding modified row
            idx_pos = valid_indices.index(i)
            result_rows.append(modified_filtered.iloc[idx_pos])
        else:
            result_rows.append(df.iloc[i])
    
    result_df = pd.DataFrame(result_rows)
    result_df = result_df.reset_index(drop=True)
    
    return result_df, len(valid_indices)


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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    if request.formula:
        if request.formula.startswith("row_number"):
            df[request.column_name] = range(1, len(df) + 1)
        elif request.formula.startswith("constant:"):
            df[request.column_name] = request.formula.replace("constant:", "")
        else:
            raise HTTPException(status_code=400, detail="Invalid formula")
    else:
        df[request.column_name] = request.default_value or None
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}
    await save_operation(dataset_id, "add_column", request.model_dump(), before, after, session)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    missing = [c for c in request.columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    df = df.drop(columns=request.columns)
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}
    await save_operation(dataset_id, "remove_columns", request.model_dump(), before, after, session)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    if request.old_name not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.old_name}' not found"
        )
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    df = df.rename(columns={request.old_name: request.new_name})
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns}
    await save_operation(dataset_id, "rename_column", request.model_dump(), before, after, session)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    missing = [c for c in request.columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    df[request.new_column] = (
        df[request.columns].astype(str).agg(request.delimiter.join, axis=1)
    )
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns}
    # PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    # await save_operation(dataset_id, "merge_columns", request.dict(), before, after, session)
    await save_operation(dataset_id, "merge_columns", request.model_dump(), before, after, session)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    split_data = (
        df[request.column].astype(str).str.split(request.delimiter, expand=True)
    )
    for i, col_name in enumerate(request.new_columns):
        df[col_name] = split_data[i] if i < len(split_data.columns) else None
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns}
    # PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    # await save_operation(dataset_id, "split_column", request.dict(), before, after, session)
    await save_operation(dataset_id, "split_column", request.model_dump(), before, after, session)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    if request.source_column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.source_column}' not found"
        )
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    df[request.new_column] = df[request.source_column]
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns}
    await save_operation(
        dataset_id, "duplicate_column", request.model_dump(), before, after, session
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    df = pd.DataFrame(dataset.data_json["data"])
    if set(df.columns) != set(request.columns):
        raise HTTPException(status_code=400, detail="Column mismatch")
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    df = df[request.columns]
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns}
    await save_operation(
        # PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
        # dataset_id, "reorder_columns", request.dict(), before, after, session
        dataset_id, "reorder_columns", request.model_dump(), before, after, session
    )
    await session.commit()
    return OperationResponse(
        status="success", message="Columns reordered", columns=dataset.columns
    )


class ReorderRowsRequest(BaseModel):
    indices: list[int]
    direction: str  # "up" or "down"


@router.post(
    "/datasets/{dataset_id}/operations/reorder-rows",
    response_model=OperationResponse,
)
async def reorder_rows(
    dataset_id: str,
    request: ReorderRowsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Move selected rows one step up or down."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    total = len(dataset.data_json["data"])
    indices = sorted(request.indices)

    if not indices:
        raise HTTPException(status_code=400, detail="No indices provided")
    if any(i < 0 or i >= total for i in indices):
        raise HTTPException(status_code=400, detail="Index out of range")

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}

    rows = list(dataset.data_json["data"])

    # Group adjacent indices into contiguous blocks
    indices_set = set(indices)
    blocks = []
    block = []
    for i in sorted(indices):
        if block and i != block[-1] + 1:
            blocks.append(block)
            block = []
        block.append(i)
    if block:
        blocks.append(block)

    if request.direction == "up":
        # Move each block up by one (process blocks left to right)
        for b in blocks:
            if b[0] > 0 and (b[0] - 1) not in indices_set:
                # Swap: the row above goes to the bottom of the block
                above = b[0] - 1
                displaced = rows[above]
                rows[above] = rows[b[0]]
                for j in range(1, len(b)):
                    rows[b[j - 1]] = rows[b[j]]
                rows[b[-1]] = displaced
    elif request.direction == "down":
        # Move each block down by one (process blocks right to left)
        for b in reversed(blocks):
            if b[-1] < total - 1 and (b[-1] + 1) not in indices_set:
                # Swap: the row below goes to the top of the block
                below = b[-1] + 1
                displaced = rows[below]
                rows[below] = rows[b[-1]]
                for j in range(len(b) - 2, -1, -1):
                    rows[b[j + 1]] = rows[b[j]]
                rows[b[0]] = displaced
    else:
        raise HTTPException(status_code=400, detail="Direction must be 'up' or 'down'")

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    df = pd.DataFrame(rows)
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns}
    await save_operation(
        # PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
        # dataset_id, "reorder_rows", request.dict(), before, after, session
        dataset_id, "reorder_rows", request.model_dump(), before, after, session
    )
    await session.commit()
    return OperationResponse(
        status="success", message="Rows reordered", columns=dataset.columns
    )


@router.get("/datasets/{dataset_id}/operations")
async def list_operations(
    dataset_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List operations for a dataset with pagination."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)

    # Count total
    from sqlalchemy import func
    count_result = await session.execute(
        select(func.count(OperationHistory.id)).where(
            cast(OperationHistory.dataset_id, String) == dataset_id
        )
    )
    total = count_result.scalar() or 0

    result = await session.execute(
        select(OperationHistory)
        .where(cast(OperationHistory.dataset_id, String) == dataset_id)
        .order_by(OperationHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    operations = result.scalars().all()

    return {
        "operations": [
            {
                "id": op.id,
                "operation_type": op.operation_type,
                "operation_params": op.operation_params,
                "created_at": op.created_at.isoformat() if op.created_at else None,
                "is_undone": op.is_undone,
            }
            for op in operations
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


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


@router.delete("/datasets/{dataset_id}/operations/{operation_id}")
async def delete_operation_history(
    dataset_id: str,
    operation_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete an operation history record. Only undone operations can be deleted."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)

    result = await session.execute(
        select(OperationHistory).where(
            OperationHistory.id == operation_id,
            cast(OperationHistory.dataset_id, String) == dataset_id,
        )
    )
    operation = result.scalar_one_or_none()

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    if not operation.is_undone:
        raise HTTPException(
            status_code=400,
            detail="Can only delete undone operations. Undo it first.",
        )

    await session.delete(operation)
    await session.commit()

    return {"status": "success", "message": "Operation deleted"}


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
    
    Supports row filtering:
    - { "columns": ["name"], "operation": "upper", "row_indices": [0, 1, 2] }
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])

    # Support both single column and batch (multiple columns)
    column = request.get('column')
    columns = request.get('columns')
    operation = request.get('operation')
    # New: support row filtering
    row_indices = request.get('row_indices')  # Optional list of row indices

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

    # Apply operation using helper function if row_indices provided
    if row_indices:
        # Use helper to apply operation only to selected rows
        def op_func(filtered_df):
            for col in target_columns:
                # Check if column is string-compatible
                try:
                    filtered_df[col] = filtered_df[col].astype(str)
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
                        filtered_df[col] = filtered_df[col].astype(str).str.upper()
                    elif op == 'lowercase':
                        filtered_df[col] = filtered_df[col].astype(str).str.lower()
                    elif op == 'trim':
                        filtered_df[col] = filtered_df[col].astype(str).str.strip()
                    elif op == 'titlecase':
                        filtered_df[col] = filtered_df[col].astype(str).str.title()
                    elif op == 'capitalize':
                        filtered_df[col] = filtered_df[col].astype(str).str.capitalize()
                    elif op == 'remove_whitespace':
                        filtered_df[col] = filtered_df[col].astype(str).str.replace(r'\s+', '', regex=True)
                    else:
                        results.append({"column": col, "status": "skipped", "reason": f"unknown operation: {operation}"})
                        continue

                    results.append({"column": col, "status": "success", "operation": op})
                except Exception as e:
                    results.append({"column": col, "status": "error", "reason": str(e)})
            return filtered_df
        
        df, modified_count = apply_operation_to_filtered_rows(df, row_indices, op_func)
    else:
        # Original logic - apply to all rows
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

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "string_operations", request, before, after, session)
    await session.commit()

    success_count = len(successful)
    # Update message based on scope
    scope_msg = f" to {len(row_indices)} row(s)" if row_indices else ""
    msg = f"Applied {operation} to {success_count} column(s){scope_msg}"

    return {"status": "success", "message": msg, "columns": dataset.columns, "results": results}


@router.post("/datasets/{dataset_id}/operations/extract-json")
async def extract_json_value(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Extract a value from JSON strings in a column.

    Supports dot notation for nested keys: "a.b.c"
    Non-JSON values or missing keys are left unchanged.
    """
    import json as json_mod

    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    column = request.get("column")
    key = request.get("key")

    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    if not key:
        raise HTTPException(status_code=400, detail="key is required")

    # Support dot notation for nested keys
    key_parts = key.split(".")

    changed = 0

    def _extract(val):
        nonlocal changed
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return val
        s = str(val).strip()
        try:
            obj = json_mod.loads(s)
        except (json_mod.JSONDecodeError, ValueError):
            return val  # not JSON, keep original

        # Traverse nested keys
        result = obj
        for part in key_parts:
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                return val  # key not found, keep original

        changed += 1
        return result

    df[column] = df[column].apply(_extract)

    if changed == 0:
        return {"status": "no_changes", "message": f"No values extracted. Check that column contains JSON with key '{key}'.", "columns": dataset.columns}

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "extract-json", {"column": column, "key": key}, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Extracted {changed} value(s) from '{column}' using key '{key}'", "columns": dataset.columns}


@router.post("/datasets/{dataset_id}/operations/find-replace")
async def find_replace(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Find and replace values in columns. Supports plain text or regex.
    
    Supports row filtering:
    - { "columns": ["name"], "find": "foo", "replace": "bar", "row_indices": [0, 1, 2] }
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    columns = request.get("columns", [])
    find_val = request.get("find", "")
    replace_val = request.get("replace", "")
    use_regex = request.get("regex", False)
    case_sensitive = request.get("case_sensitive", True)
    row_indices = request.get("row_indices")  # Optional row filtering

    if not find_val:
        raise HTTPException(status_code=400, detail="'find' value is required")
    if not columns:
        raise HTTPException(status_code=400, detail="'columns' is required")

    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")

    changed = 0
    
    # Apply find/replace using helper function if row_indices provided
    if row_indices:
        def op_func(filtered_df):
            nonlocal changed
            local_changed = 0
            for col in columns:
                before_count = filtered_df[col].astype(str).str.contains(
                    find_val, regex=use_regex, case=case_sensitive, na=False
                ).sum()
                if use_regex:
                    filtered_df[col] = filtered_df[col].astype(str).str.replace(
                        find_val, replace_val, regex=True, case=case_sensitive
                    )
                else:
                    filtered_df[col] = filtered_df[col].astype(str).str.replace(
                        find_val, replace_val, regex=False, case=case_sensitive
                    )
                local_changed += before_count
            changed = local_changed
            return filtered_df
        
        df, _ = apply_operation_to_filtered_rows(df, row_indices, op_func)
    else:
        # Original logic - apply to all rows
        for col in columns:
            before_count = df[col].astype(str).str.contains(
                find_val, regex=use_regex, case=case_sensitive, na=False
            ).sum()
            if use_regex:
                df[col] = df[col].astype(str).str.replace(
                    find_val, replace_val, regex=True, case=case_sensitive
                )
            else:
                df[col] = df[col].astype(str).str.replace(
                    find_val, replace_val, regex=False, case=case_sensitive
                )
            changed += before_count

    if changed == 0:
        return {"status": "no_changes", "message": f"No occurrences of '{find_val}' found"}

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "find-replace", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Replaced {changed} occurrence(s)", "columns": dataset.columns}


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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])

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
        'parse-datetime': 'parse_datetime',
        'parse_datetime': 'parse_datetime',
        'year': 'extract_year',
        'extract-year': 'extract_year',
        'extract_year': 'extract_year',
        'month': 'extract_month',
        'extract-month': 'extract_month',
        'extract_month': 'extract_month',
        'day': 'extract_day',
        'extract-day': 'extract_day',
        'extract_day': 'extract_day',
        'weekday': 'extract_weekday',
        'extract-weekday': 'extract_weekday',
        'extract_weekday': 'extract_weekday',
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

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
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
        if fill_value is not None:
            before = df.isna().sum().sum()
            df = df.fillna(fill_value)
            modified = before - df.isna().sum().sum()
        else:
            raise HTTPException(status_code=400, detail="fill_value required for constant method")
    elif method in ('mean', 'median', 'mode'):
        # Apply to specified columns or all numeric columns
        target_cols = request.get('columns') or []
        if not target_cols:
            target_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if not target_cols:
            raise HTTPException(status_code=400, detail=f"No numeric columns to apply {method}")
        before = df[target_cols].isna().sum().sum()
        for col in target_cols:
            if col not in df.columns:
                continue
            if method == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif method == 'median':
                df[col] = df[col].fillna(df[col].median())
            elif method == 'mode':
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col] = df[col].fillna(mode_val.iloc[0])
        modified = before - df[target_cols].isna().sum().sum()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {method}")

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    before_count = len(df)
    df = df.drop_duplicates()
    after_count = len(df)

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": before_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    column = request.get('column')
    ascending = request.get('ascending', True)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    df = df.sort_values(by=column, ascending=ascending)

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "sort", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": f"Sorted by {column}", "columns": dataset.columns}


# ML / Feature Engineering operations
@router.post("/datasets/{dataset_id}/operations/encoding")
async def encoding_operations(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Encoding operations: one-hot, label, value mapping, binning.

    Body: { column, operation: "one_hot"|"label"|"map"|"bin", ...params }
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    column = request.get("column")
    operation = request.get("operation")

    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before = {"columns": dataset.columns, "row_count": len(df), "data": dataset.data_json["data"]}

    try:
        if operation == "one_hot":
            prefix = request.get("prefix", column)
            dummies = pd.get_dummies(df[column], prefix=prefix, dtype=int)
            df = pd.concat([df, dummies], axis=1)
            msg = f"One-hot encoded '{column}' → {len(dummies.columns)} new columns"

        elif operation == "label":
            unique_vals = df[column].dropna().unique()
            mapping = {val: i for i, val in enumerate(sorted(unique_vals, key=str))}
            df[f"{column}_encoded"] = df[column].map(mapping).astype("Int64")
            msg = f"Label encoded '{column}' → '{column}_encoded' ({len(mapping)} categories)"

        elif operation == "map":
            mapping = request.get("mapping", {})
            if not mapping:
                raise HTTPException(status_code=400, detail="Mapping dictionary required")
            df[column] = df[column].map(lambda x: mapping.get(str(x), mapping.get(x, x)))
            msg = f"Mapped values in '{column}'"

        elif operation == "bin":
            n_bins = int(request.get("n_bins", 5))
            strategy = request.get("strategy", "equal_width")
            labels = request.get("labels")
            if strategy == "equal_width":
                df[f"{column}_binned"] = pd.cut(df[column], bins=n_bins, labels=labels, duplicates="drop")
            elif strategy == "equal_freq":
                df[f"{column}_binned"] = pd.qcut(df[column], q=n_bins, labels=labels, duplicates="drop")
            else:
                raise HTTPException(status_code=400, detail=f"Unknown binning strategy: {strategy}")
            df[f"{column}_binned"] = df[f"{column}_binned"].astype(str)
            msg = f"Binned '{column}' into {n_bins} bins ({strategy})"

        else:
            raise HTTPException(status_code=400, detail=f"Unknown encoding operation: {operation}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    dataset.columns = detect_columns(df)
    dataset.row_count = len(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns, "row_count": dataset.row_count}
    await save_operation(dataset_id, f"encoding_{operation}", request, before, after, session)
    await session.commit()
    return OperationResponse(status="success", message=msg, columns=dataset.columns)


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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
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

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
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


class AddRecordsRequest(BaseModel):
    records: list[dict] | None = None
    csv_text: str | None = None


@router.post("/datasets/{dataset_id}/operations/add-records", response_model=OperationResponse)
async def add_records(
    dataset_id: str,
    request: AddRecordsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Add one or more records to a dataset.

    Accepts either:
    - records: list of dicts (JSON rows)
    - csv_text: CSV-formatted string to parse
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    if not request.records and not request.csv_text:
        raise HTTPException(status_code=400, detail="Provide 'records' or 'csv_text'")

    import io as io_mod

    df = pd.DataFrame(dataset.data_json["data"])

    if request.csv_text:
        csv_df = pd.read_csv(io_mod.StringIO(request.csv_text))
        # Align columns: keep only columns that exist in the dataset, add missing ones as null
        for col in df.columns:
            if col not in csv_df.columns:
                csv_df[col] = None
        csv_df = csv_df[df.columns]
        new_rows = csv_df.to_dict("records")
    else:
        new_rows = request.records
        # Normalize keys: keep only dataset columns, fill missing with None
        new_rows = [
            {col: row.get(col, None) for col in df.columns}
            for row in new_rows
        ]

    if not new_rows:
        raise HTTPException(status_code=400, detail="No records to add")

    before = {"columns": dataset.columns, "row_count": len(df), "data": dataset.data_json["data"]}

    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    dataset.columns = detect_columns(df)
    dataset.row_count = len(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns, "row_count": dataset.row_count}
    await save_operation(
        dataset_id, "add_records", {"count": len(new_rows)}, before, after, session
    )
    await session.commit()
    return OperationResponse(
        status="success",
        message=f"Added {len(new_rows)} record(s)",
        columns=dataset.columns,
    )


class ImportRecipeRequest(BaseModel):
    operations: list[dict]


@router.post("/datasets/{dataset_id}/operations/import-recipe")
async def import_recipe(
    dataset_id: str,
    request: ImportRecipeRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Import and apply a sequence of operations from a recipe (JSON list).

    Each operation in the recipe: {operation: "...", column: "...", params: {...}}
    Returns per-operation results: [{index, operation, status, message}, ...]
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    if not request.operations:
        raise HTTPException(status_code=400, detail="No operations provided")

    df = pd.DataFrame(dataset.data_json["data"])
    existing_columns = set(df.columns)
    results = []

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    for i, op in enumerate(request.operations):
        op_type = op.get("operation", "")
        op_column = op.get("column")
        op_columns = op.get("columns")
        op_params = op.get("params", {})

        # Validate column existence
        if op_column and op_column not in existing_columns:
            results.append({"index": i, "operation": op_type, "column": op_column, "status": "skipped", "message": f"Column '{op_column}' not found"})
            continue
        if op_columns:
            missing = [c for c in op_columns if c not in existing_columns]
            if missing:
                results.append({"index": i, "operation": op_type, "columns": op_columns, "status": "skipped", "message": f"Columns not found: {', '.join(missing)}"})
                continue

        try:
            before_snapshot = {"columns": detect_columns(df), "row_count": len(df)}

            if op_type == "fillna":
                method = op_params.get("method", "constant")
                cols = op_columns or ([op_column] if op_column else None)
                if cols:
                    for c in cols:
                        if method == "drop":
                            df = df.dropna(subset=[c])
                        elif method == "forward":
                            df[c] = df[c].ffill()
                        elif method == "backward":
                            df[c] = df[c].bfill()
                        elif method == "mean" and pd.api.types.is_numeric_dtype(df[c]):
                            df[c] = df[c].fillna(df[c].mean())
                        elif method == "median" and pd.api.types.is_numeric_dtype(df[c]):
                            df[c] = df[c].fillna(df[c].median())
                        elif method == "mode":
                            mode_val = df[c].mode()
                            if len(mode_val) > 0:
                                df[c] = df[c].fillna(mode_val.iloc[0])
                        else:
                            df[c] = df[c].fillna(op_params.get("fill_value", ""))
                else:
                    if method == "drop":
                        df = df.dropna()
                    elif method == "forward":
                        df = df.ffill()
                    elif method == "backward":
                        df = df.bfill()
                df = df.reset_index(drop=True)

            elif op_type == "remove-duplicates":
                before_count = len(df)
                df = df.drop_duplicates().reset_index(drop=True)

            elif op_type == "string-operations":
                if op_column and op_column in df.columns:
                    str_op = op_params.get("operation", "strip")
                    if str_op == "strip":
                        df[op_column] = df[op_column].astype(str).str.strip()
                    elif str_op == "lower":
                        df[op_column] = df[op_column].astype(str).str.lower()
                    elif str_op == "upper":
                        df[op_column] = df[op_column].astype(str).str.upper()
                    elif str_op == "title":
                        df[op_column] = df[op_column].astype(str).str.title()
                    elif str_op == "capitalize":
                        df[op_column] = df[op_column].astype(str).str.capitalize()

            elif op_type == "find-replace":
                cols = op_columns or ([op_column] if op_column else [])
                find_val = op_params.get("find", "")
                replace_val = op_params.get("replace", "")
                use_regex = op_params.get("regex", False)
                case_sensitive = op_params.get("case_sensitive", True)
                for c in cols:
                    if c in df.columns:
                        if use_regex:
                            df[c] = df[c].astype(str).str.replace(find_val, replace_val, regex=True, case=case_sensitive)
                        else:
                            if case_sensitive:
                                df[c] = df[c].astype(str).str.replace(find_val, replace_val, regex=False)
                            else:
                                df[c] = df[c].astype(str).str.replace(find_val, replace_val, case=False, regex=False)

            elif op_type == "extract-json":
                if op_column and op_column in df.columns:
                    key = op_params.get("key", "")
                    if key:
                        import json as json_mod
                        def extract(v):
                            try:
                                obj = json_mod.loads(str(v))
                                keys = key.split(".")
                                for k in keys:
                                    obj = obj[k]
                                return obj
                            except (json.JSONDecodeError, TypeError, KeyError):
                                return v
                        df[op_column] = df[op_column].apply(extract)

            elif op_type in ("encoding_one_hot", "encoding_label", "encoding_map", "encoding_bin", "one_hot", "label", "map", "bin"):
                # Encoding operations handled via the encoding endpoint
                # For import-recipe, apply inline
                if op_column and op_column in df.columns:
                    sub = op_type.replace("encoding_", "")
                    if sub == "one_hot":
                        prefix = op_params.get("prefix", op_column)
                        dummies = pd.get_dummies(df[op_column], prefix=prefix, dtype=int)
                        df = pd.concat([df, dummies], axis=1)
                    elif sub == "label":
                        unique_vals = df[op_column].dropna().unique()
                        mapping = {val: i for i, val in enumerate(sorted(unique_vals, key=str))}
                        df[f"{op_column}_encoded"] = df[op_column].map(mapping).astype("Int64")
                    elif sub == "map":
                        mapping = op_params.get("mapping", {})
                        df[op_column] = df[op_column].map(lambda x: mapping.get(str(x), mapping.get(x, x)))
                    elif sub == "bin":
                        n_bins = int(op_params.get("n_bins", 5))
                        strategy = op_params.get("strategy", "equal_width")
                        if strategy == "equal_width":
                            df[f"{op_column}_binned"] = pd.cut(df[op_column], bins=n_bins, duplicates="drop")
                        else:
                            df[f"{op_column}_binned"] = pd.qcut(df[op_column], q=n_bins, duplicates="drop")
                        df[f"{op_column}_binned"] = df[f"{op_column}_binned"].astype(str)

            elif op_type == "structural":
                sub_op = op_params.get("operation", op.get("operation"))
                if sub_op == "rename":
                    new_name = op_params.get("new_name", "")
                    if op_column and new_name and op_column in df.columns:
                        df = df.rename(columns={op_column: new_name})
                elif sub_op == "drop":
                    cols_to_drop = op_columns or ([op_column] if op_column else [])
                    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
                elif sub_op == "add_column":
                    new_name = op_params.get("new_name", "")
                    if new_name and new_name not in df.columns:
                        df[new_name] = op_params.get("default_value", "")
                elif sub_op == "astype":
                    dtype = op_params.get("dtype", "str")
                    cols = op_columns or ([op_column] if op_column else [])
                    for c in cols:
                        if c in df.columns:
                            try:
                                df[c] = df[c].astype(dtype)
                            except (ValueError, TypeError):
                                pass

            elif op_type == "reorder_columns":
                new_order = op_params.get("columns", op.get("columns", []))
                if new_order and set(new_order) == set(df.columns):
                    df = df[new_order]

            else:
                results.append({"index": i, "operation": op_type, "status": "skipped", "message": f"Unsupported operation type: {op_type}"})
                continue

            # Update existing columns set
            existing_columns = set(df.columns)

            # Save operation history
            after_snapshot = {"columns": list(df.columns), "row_count": len(df)}
            await save_operation(
                dataset_id, op_type, {**op_params, "column": op_column, "columns": op_columns},
                before_snapshot, after_snapshot, session
            )

            results.append({"index": i, "operation": op_type, "column": op_column, "status": "success", "message": "Applied"})

        except Exception as e:
            results.append({"index": i, "operation": op_type, "column": op_column, "status": "failed", "message": str(e)})

    # Update dataset
    dataset.columns = detect_columns(df)
    dataset.row_count = len(df)
    dataset.data_json = get_full_data_json(df)
    await session.commit()

    applied = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {
        "status": "success" if failed == 0 else "partial" if applied > 0 else "failed",
        "message": f"{applied} applied, {skipped} skipped, {failed} failed",
        "results": results,
        "columns": dataset.columns,
    }


@router.post("/datasets/{dataset_id}/operations/delete-rows")
async def delete_rows(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete rows by mode: first, last, range, or visible (by index)."""
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    total_before = len(df)
    mode = request.get("mode", "")

    if mode == "first":
        count = int(request.get("count", 1))
        if count < 1:
            raise HTTPException(status_code=400, detail="Count must be at least 1")
        if count >= total_before:
            raise HTTPException(status_code=400, detail=f"Cannot delete all rows ({count} >= {total_before}). Use a smaller count.")
        df = df.iloc[count:].reset_index(drop=True)
        msg = f"Deleted first {count} row(s)"

    elif mode == "last":
        count = int(request.get("count", 1))
        if count < 1:
            raise HTTPException(status_code=400, detail="Count must be at least 1")
        if count >= total_before:
            raise HTTPException(status_code=400, detail=f"Cannot delete all rows ({count} >= {total_before}). Use a smaller count.")
        df = df.iloc[:-count].reset_index(drop=True)
        msg = f"Deleted last {count} row(s)"

    elif mode == "range":
        start = int(request.get("start", 0))
        end = int(request.get("end", total_before))
        if start < 0 or end > total_before or start >= end:
            raise HTTPException(status_code=400, detail=f"Invalid range: start={start}, end={end}")
        if (end - start) >= total_before:
            raise HTTPException(status_code=400, detail="Cannot delete all rows. Use a smaller range.")
        df = pd.concat([df.iloc[:start], df.iloc[end:]]).reset_index(drop=True)
        msg = f"Deleted rows {start + 1}-{end} ({end - start} row(s))"

    elif mode == "visible":
        indices = request.get("indices", [])
        if not indices:
            raise HTTPException(status_code=400, detail="No indices provided")
        valid_indices = [i for i in indices if 0 <= i < total_before]
        df = df.drop(df.index[valid_indices]).reset_index(drop=True)
        msg = f"Deleted {len(valid_indices)} row(s)"

    else:
        raise HTTPException(status_code=400, detail=f"Unknown mode: {mode}")

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": total_before, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "delete-rows", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": msg, "row_count": len(df)}


# Fuzzy deduplication
@router.post("/datasets/{dataset_id}/operations/fuzzy-dedupe")
async def fuzzy_dedupe(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Fuzzy deduplication based on column similarity.
    
    Supports multiple matching algorithms and action modes:
    - matching_type: "standard" (SequenceMatcher), "permutation" (word order insensitive), "levenshtein" (edit distance)
    - mode: "delete" (remove rows), "merge_first" (update to first), "merge_most_frequent" (consolidate to most common)
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
    column = request.get('column')
    threshold = request.get('threshold', 0.8)
    matching_type = request.get('matching_type', 'standard')  # standard, permutation, levenshtein
    mode = request.get('mode', 'delete')  # delete, merge_first, merge_most_frequent

    # Validate inputs
    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column {column} not found")
    if matching_type not in ('standard', 'permutation', 'levenshtein'):
        raise HTTPException(status_code=400, detail=f"Invalid matching_type: {matching_type}. Must be 'standard', 'permutation', or 'levenshtein'.")
    if mode not in ('delete', 'merge_first', 'merge_most_frequent'):
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}. Must be 'delete', 'merge_first', or 'merge_most_frequent'.")

    from difflib import SequenceMatcher

    # Get column values as strings
    rows = df[column].astype(str).tolist()
    
    def normalize_for_matching(s, matching_type):
        """Normalize string based on matching algorithm."""
        if matching_type == 'permutation':
            # Sort words alphabetically for permutation matching
            return ' '.join(sorted(s.split()))
        elif matching_type == 'levenshtein':
            # For Levenshtein, we use the original string but compare character-level
            return s.lower()
        else:  # standard
            return s.lower()

    def calculate_similarity(s1, s2, matching_type):
        """Calculate similarity between two strings."""
        from difflib import SequenceMatcher
        if matching_type == 'levenshtein':
            # Use Levenshtein distance (character-level edit distance)
            return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
        elif matching_type == 'permutation':
            # Compare sorted word versions
            return SequenceMatcher(None, normalize_for_matching(s1, 'permutation'), normalize_for_matching(s2, 'permutation')).ratio()
        else:  # standard
            return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

    # Find clusters of similar values
    cluster_map = {}  # index -> canonical index
    processed = set()
    
    for i, row in enumerate(rows):
        if i in processed:
            continue
        # This row is the canonical for its cluster
        canonical_idx = i
        cluster = [i]
        
        for j in range(i + 1, len(rows)):
            if j in processed:
                continue
            similarity = calculate_similarity(row, rows[j], matching_type)
            if similarity > threshold:
                cluster.append(j)
                processed.add(j)
                cluster_map[j] = canonical_idx
        
        processed.add(i)
        cluster_map[i] = canonical_idx

    # Apply mode
    if mode == 'delete':
        # Keep only rows where index is the canonical (not in cluster_map as value)
        canonical_indices = set(cluster_map.values())
        to_keep = [i for i in range(len(rows)) if cluster_map.get(i, i) == i or i in canonical_indices]
        df = df.iloc[to_keep].reset_index(drop=True)
        removed = len(rows) - len(to_keep)
        msg = f"Removed {removed} fuzzy duplicates"
    
    elif mode == 'merge_first':
        # For each cluster, set all to the first occurrence value
        canonical_values = {}
        for i, row in enumerate(rows):
            canonical_idx = cluster_map.get(i, i)
            if canonical_idx not in canonical_values:
                canonical_values[canonical_idx] = row
        
        # Update values based on cluster mapping
        new_col = []
        for i in range(len(rows)):
            canonical_idx = cluster_map.get(i, i)
            new_col.append(canonical_values.get(canonical_idx, rows[i]))
        
        df[column] = new_col
        removed = sum(1 for i, row in enumerate(rows) if cluster_map.get(i, i) != i)
        msg = f"Merged {removed} values to first occurrence"
    
    elif mode == 'merge_most_frequent':
        # For each cluster, find most frequent value and use it
        # First, count all values in each cluster
        cluster_values = {}
        for i, row in enumerate(rows):
            canonical_idx = cluster_map.get(i, i)
            if canonical_idx not in cluster_values:
                cluster_values[canonical_idx] = {}
            val = row
            cluster_values[canonical_idx][val] = cluster_values[canonical_idx].get(val, 0) + 1
        
        # Find most frequent for each cluster
        canonical_values = {}
        for canonical_idx, value_counts in cluster_values.items():
            most_frequent = max(value_counts.keys(), key=lambda k: value_counts[k])
            canonical_values[canonical_idx] = most_frequent
        
        # Update values
        new_col = []
        for i in range(len(rows)):
            canonical_idx = cluster_map.get(i, i)
            new_col.append(canonical_values.get(canonical_idx, rows[i]))
        
        df[column] = new_col
        removed = sum(1 for i, row in enumerate(rows) if cluster_map.get(i, i) != i)
        msg = f"Merged {removed} values to most frequent"

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_count = dataset.row_count
    before_snapshot = {"columns": dataset.columns, "row_count": before_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "fuzzy_dedupe", request, before_snapshot, after_snapshot, session)
    await session.commit()

    return {"status": "success", "message": msg, "columns": dataset.columns, "row_count": dataset.row_count}



# Fuzzy match preview endpoint
@router.get("/datasets/{dataset_id}/operations/fuzzy-preview")
async def fuzzy_preview(
    dataset_id: str,
    column: str,
    threshold: float = 0.8,
    matching_type: str = 'standard',
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Preview unique values and their clustering for fuzzy matching.
    
    Returns unique values with frequencies and suggested clusters based on similarity algorithms.
    """
    from difflib import SequenceMatcher
    
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    
    df = pd.DataFrame(dataset.data_json["data"])
    
    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    
    if matching_type not in ('standard', 'permutation', 'levenshtein'):
        raise HTTPException(status_code=400, detail=f"Invalid matching_type: {matching_type}. Must be 'standard', 'permutation', or 'levenshtein'.")
    
    # Get value frequencies
    col_series = df[column].astype(str)
    value_counts = col_series.value_counts()
    total_unique = len(value_counts)
    unique_values = value_counts.head(limit).to_dict()
    
    # If limit reached and there are more, indicate there are more
    has_more = total_unique > limit
    
    # Calculate clusters for preview (only if we have a small enough set)
    clusters = []
    values_list = list(unique_values.keys())
    
    def calculate_similarity(s1, s2, matching_type):
        """Calculate similarity between two strings."""
        if matching_type == 'levenshtein':
            return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
        elif matching_type == 'permutation':
            s1_sorted = ' '.join(sorted(s1.lower().split()))
            s2_sorted = ' '.join(sorted(s2.lower().split()))
            return SequenceMatcher(None, s1_sorted, s2_sorted).ratio()
        else:  # standard
            return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    
    # Find clusters of similar values
    if values_list and len(values_list) <= 100:
        processed = set()
        for i, val1 in enumerate(values_list):
            if i in processed:
                continue
            cluster = [val1]
            for j in range(i + 1, len(values_list)):
                if j in processed:
                    continue
                similarity = calculate_similarity(val1, values_list[j], matching_type)
                if similarity >= threshold:
                    cluster.append(values_list[j])
                    processed.add(j)
            if len(cluster) > 1:
                clusters.append({"values": cluster, "size": len(cluster)})
            processed.add(i)
    
    return {
        "status": "success",
        "column": column,
        "total_unique": total_unique,
        "unique_values": [{"value": v, "frequency": int(f)} for v, f in unique_values.items()],
        "has_more": has_more,
        "clusters": clusters,
        "threshold": threshold,
        "matching_type": matching_type
    }


# Fuzzy advanced endpoint
@router.post("/datasets/{dataset_id}/operations/fuzzy-advanced")
async def fuzzy_advanced(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply custom value mapping for fuzzy matching with manual control.
    
    Body: { "column": "col_name", "mapping": {"value1": "target1", "value2": "target2", ...} }
    All values not in mapping are kept as-is.
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")
    
    df = pd.DataFrame(dataset.data_json["data"])
    column = request.get('column')
    mapping = request.get('mapping', {})
    
    if not column or column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    if not mapping:
        raise HTTPException(status_code=400, detail="Mapping dictionary required")
    
    # Apply mapping with custom function
    def apply_mapping(val):
        str_val = str(val)
        return mapping.get(str_val, mapping.get(val, val))
    
    before_count = len(df)
    df[column] = df[column].apply(apply_mapping)
    
    # Count how many values were changed
    changed = sum(1 for val in df[column].astype(str) if val in mapping)
    
    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": before_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}
    
    await save_operation(dataset_id, "fuzzy_advanced", request, before_snapshot, after_snapshot, session)
    await session.commit()
    
    return {
        "status": "success",
        "message": f"Mapped {changed} values in column '{column}'",
        "columns": dataset.columns,
        "row_count": dataset.row_count,
        "changed_count": changed
    }


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
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    df = pd.DataFrame(dataset.data_json["data"])
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

            elif operation == 'standardize':
                # Z-score standardization: (x - mean) / std
                col_mean = df[col].mean()
                col_std = df[col].std()
                if col_std != 0:
                    df[col] = (df[col] - col_mean) / col_std

            elif operation == 'robust_scale':
                # Robust scaling using median and IQR
                col_median = df[col].median()
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR != 0:
                    df[col] = (df[col] - col_median) / IQR

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

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json
    before_snapshot = {"columns": dataset.columns, "row_count": dataset.row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after_snapshot = {"columns": dataset.columns, "row_count": len(df), "preview_data": get_preview_data(df)}

    await save_operation(dataset_id, "numeric", request, before_snapshot, after_snapshot, session)
    await session.commit()

    success_count = len(successful)
    msg = f"Applied {operation} to {success_count} column(s)"

    return {"status": "success", "message": msg, "columns": dataset.columns, "results": results}


@router.get("/operations/stats")
async def get_operation_stats(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get operation statistics for the current user's datasets."""
    from sqlalchemy import func

    # Get all dataset IDs owned by the user
    projects_result = await session.execute(
        select(Project.id).where(Project.user_id == current_user.id)
    )
    project_ids = [r[0] for r in projects_result.fetchall()]

    if not project_ids:
        return {"total": 0, "ai_operations": 0, "manual_operations": 0, "active": 0, "undone": 0, "top_types": []}

    # Get dataset IDs for these projects
    datasets_result = await session.execute(
        select(Dataset.id).where(Dataset.project_id.in_(project_ids))
    )
    dataset_ids = [str(r[0]) for r in datasets_result.fetchall()]

    if not dataset_ids:
        return {"total": 0, "ai_operations": 0, "manual_operations": 0, "active": 0, "undone": 0, "top_types": []}

    # Count operations
    total_result = await session.execute(
        select(func.count(OperationHistory.id)).where(
            cast(OperationHistory.dataset_id, String).in_(dataset_ids)
        )
    )
    total = total_result.scalar() or 0

    # Count undone
    undone_result = await session.execute(
        select(func.count(OperationHistory.id)).where(
            cast(OperationHistory.dataset_id, String).in_(dataset_ids),
            OperationHistory.is_undone == True,
        )
    )
    undone = undone_result.scalar() or 0

    # Count AI operations
    ai_types = ["ai_clean", "ai_structural", "ai_data_clean", "ai_data_clean_batch", "ai_suggest"]
    ai_result = await session.execute(
        select(func.count(OperationHistory.id)).where(
            cast(OperationHistory.dataset_id, String).in_(dataset_ids),
            OperationHistory.operation_type.in_(ai_types),
        )
    )
    ai_count = ai_result.scalar() or 0

    # Count by type (top 5)
    type_result = await session.execute(
        select(
            OperationHistory.operation_type,
            func.count(OperationHistory.id).label("count")
        )
        .where(cast(OperationHistory.dataset_id, String).in_(dataset_ids))
        .group_by(OperationHistory.operation_type)
        .order_by(func.count(OperationHistory.id).desc())
        .limit(5)
    )
    top_types = [{"type": r[0], "count": r[1]} for r in type_result.fetchall()]

    return {
        "total": total,
        "ai_operations": ai_count,
        "manual_operations": total - ai_count,
        "active": total - undone,
        "undone": undone,
        "top_types": top_types,
    }
