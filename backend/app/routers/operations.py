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


def get_dataset_with_owner_check(dataset_id: int, user_id: int, session: AsyncSession):
    result = session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    project_result = session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.owner_id == user_id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    return dataset


def save_operation(
    dataset_id: int,
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
    dataset_id: int,
    request: AddColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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
    dataset_id: int,
    request: RemoveColumnsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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
    dataset_id: int,
    request: RenameColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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
    dataset_id: int,
    request: MergeColumnsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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
    dataset_id: int,
    request: SplitColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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
    dataset_id: int,
    request: DuplicateColumnRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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
    dataset_id: int,
    request: ReorderColumnsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
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


@router.get("/datasets/{dataset_id}/operations/history")
async def get_operation_history(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    get_dataset_with_owner_check(dataset_id, current_user.id, session)
    result = await session.execute(
        select(OperationHistory)
        .where(OperationHistory.dataset_id == dataset_id)
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
