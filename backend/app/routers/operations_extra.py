"""Additional dataset operations - filter, sort, deduplicate, find-replace, type conversion."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, OperationHistory, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["dataset-operations"])


# Operation schemas
class FilterRowsRequest(BaseModel):
    column: str
    operator: str  # eq, neq, gt, gte, lt, lte, contains, startswith, endswith, isnull, notnull
    value: Any | None = None


class SortDataRequest(BaseModel):
    column: str
    ascending: bool = True


class RemoveDuplicatesRequest(BaseModel):
    columns: list[str] | None = None  # If None, use all columns


class FindReplaceRequest(BaseModel):
    column: str
    find: str
    replace: str
    use_regex: bool = False


class ChangeTypeRequest(BaseModel):
    column: str
    target_type: str  # string, integer, float, boolean, datetime


class OperationResponse(BaseModel):
    status: str
    message: str
    columns: list[dict] | None = None
    row_count: int | None = None


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


def apply_filter(df, column: str, operator: str, value: Any):
    """Apply filter operator to dataframe."""
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    col = df[column]

    if operator == "eq":
        return df[col == value]
    elif operator == "neq":
        return df[col != value]
    elif operator == "gt":
        return df[col > value]
    elif operator == "gte":
        return df[col >= value]
    elif operator == "lt":
        return df[col < value]
    elif operator == "lte":
        return df[col <= value]
    elif operator == "contains":
        return df[col.astype(str).str.contains(str(value), na=False)]
    elif operator == "startswith":
        return df[col.astype(str).str.startswith(str(value), na=False)]
    elif operator == "endswith":
        return df[col.astype(str).str.endswith(str(value), na=False)]
    elif operator == "isnull":
        return df[col.isnull()]
    elif operator == "notnull":
        return df[col.notnull()]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operator: {operator}")


# Routes
@router.post(
    "/datasets/{dataset_id}/operations/filter-rows", response_model=OperationResponse
)
async def filter_rows(
    dataset_id: int,
    request: FilterRowsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)
    before_row_count = len(df)

    df = apply_filter(df, request.column, request.operator, request.value)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "row_count": before_row_count}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}

    save_operation(dataset_id, "filter_rows", request.dict(), before, after, session)
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Filtered to {len(df)} rows",
        columns=dataset.columns,
        row_count=len(df),
    )


@router.post(
    "/datasets/{dataset_id}/operations/sort-data", response_model=OperationResponse
)
async def sort_data(
    dataset_id: int,
    request: SortDataRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )

    df = df.sort_values(by=request.column, ascending=request.ascending)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(dataset_id, "sort_data", request.dict(), before, after, session)
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Sorted by '{request.column}'",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/remove-duplicates",
    response_model=OperationResponse,
)
async def remove_duplicates(
    dataset_id: int,
    request: RemoveDuplicatesRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)
    before_count = len(df)

    if request.columns:
        df = df.drop_duplicates(subset=request.columns)
    else:
        df = df.drop_duplicates()

    duplicates_removed = before_count - len(df)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "row_count": before_count}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}

    save_operation(
        dataset_id, "remove_duplicates", request.dict(), before, after, session
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Removed {duplicates_removed} duplicates",
        columns=dataset.columns,
        row_count=len(df),
    )


@router.post(
    "/datasets/{dataset_id}/operations/find-replace", response_model=OperationResponse
)
async def find_replace(
    dataset_id: int,
    request: FindReplaceRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )

    before_count = (df[request.column].astype(str) == request.find).sum()

    if request.use_regex:
        df[request.column] = (
            df[request.column]
            .astype(str)
            .str.replace(request.find, request.replace, regex=True)
        )
    else:
        df[request.column] = (
            df[request.column]
            .astype(str)
            .str.replace(request.find, request.replace, regex=False)
        )

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(dataset_id, "find_replace", request.dict(), before, after, session)
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Replaced {before_count} occurrences",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/change-type", response_model=OperationResponse
)
async def change_type(
    dataset_id: int,
    request: ChangeTypeRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )

    # Convert type
    try:
        if request.target_type == "string":
            df[request.column] = df[request.column].astype(str)
        elif request.target_type == "integer":
            df[request.column] = pd.to_numeric(
                df[request.column], errors="coerce"
            ).astype("Int64")
        elif request.target_type == "float":
            df[request.column] = pd.to_numeric(df[request.column], errors="coerce")
        elif request.target_type == "boolean":
            df[request.column] = df[request.column].astype(bool)
        elif request.target_type == "datetime":
            df[request.column] = pd.to_datetime(df[request.column], errors="coerce")
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown type: {request.target_type}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {str(e)}")

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(dataset_id, "change_type", request.dict(), before, after, session)
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Changed '{request.column}' to {request.target_type}",
        columns=dataset.columns,
    )
