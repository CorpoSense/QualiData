"""Missing values operations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import User
from app.routers.auth import get_current_active_user
from app.routers.operations import get_dataset_with_owner_check, save_operation

router = APIRouter(tags=["dataset-operations"])


class FillNaRequest(BaseModel):
    columns: list[str] | None = None  # If None, fill all columns
    value: str | None = None  # Value to fill with
    method: str = "constant"  # constant, mean, median, mode, forward, backward, drop


class OperationResponse(BaseModel):
    status: str
    message: str
    columns: list[dict] | None = None
    row_count: int | None = None


@router.post(
    "/datasets/{dataset_id}/operations/fillna", response_model=OperationResponse
)
async def fill_na(
    dataset_id: str,
    request: FillNaRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Fill missing values in dataset."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)
    before_count = df.isna().sum().sum()

    # Select columns to fill
    cols = request.columns if request.columns else df.columns.tolist()

    for col in cols:
        if col not in df.columns:
            continue

        if request.method == "constant":
            fill_value = request.value if request.value is not None else ""
            df[col] = df[col].fillna(fill_value)
        elif request.method == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif request.method == "median":
            df[col] = df[col].fillna(df[col].median())
        elif request.method == "mode":
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
        elif request.method == "forward":
            df[col] = df[col].fillna(method="ffill")
        elif request.method == "backward":
            df[col] = df[col].fillna(method="bfill")
        elif request.method == "drop":
            df = df.dropna(subset=[col])
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown method: {request.method}"
            )

    after_count = df.isna().sum().sum()
    filled_count = before_count - after_count

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "row_count": len(dataset.preview_data)}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}

    save_operation(dataset_id, "fillna", request.dict(), before, after, session)
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Filled {filled_count} missing values using {request.method}",
        columns=dataset.columns,
        row_count=len(df),
    )


@router.post(
    "/datasets/{dataset_id}/operations/dropna", response_model=OperationResponse
)
async def drop_na(
    dataset_id: str,
    columns: list[str] | None = None,
    how: str = "any",  # any or all
    thresh: int | None = None,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Drop rows with missing values."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)
    before_count = len(df)

    if thresh:
        df = df.dropna(thresh=thresh)
    else:
        df = df.dropna(how=how, subset=columns)

    rows_dropped = before_count - len(df)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns, "row_count": before_count}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df)}

    save_operation(
        dataset_id,
        "dropna",
        {"columns": columns, "how": how, "thresh": thresh},
        before,
        after,
        session,
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Dropped {rows_dropped} rows with missing values",
        columns=dataset.columns,
        row_count=len(df),
    )


@router.post(
    "/datasets/{dataset_id}/operations/string-operations",
    response_model=OperationResponse,
)
async def string_operations(
    dataset_id: str,
    column: str,
    operation: str,  # strip, upper, lower, title, capitalize
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply string operations to columns."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    if operation == "strip":
        df[column] = df[column].astype(str).str.strip()
    elif operation == "upper":
        df[column] = df[column].astype(str).str.upper()
    elif operation == "lower":
        df[column] = df[column].astype(str).str.lower()
    elif operation == "title":
        df[column] = df[column].astype(str).str.title()
    elif operation == "capitalize":
        df[column] = df[column].astype(str).str.capitalize()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id,
        "string_operations",
        {"column": column, "operation": operation},
        before,
        after,
        session,
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Applied '{operation}' to column '{column}'",
        columns=dataset.columns,
    )
