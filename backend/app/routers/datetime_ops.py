"""Date/time operations for datasets."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import User
from app.routers.auth import get_current_active_user
from app.routers.operations import get_dataset_with_owner_check, save_operation

router = APIRouter(tags=["dataset-operations"])


class OperationResponse(BaseModel):
    status: str
    message: str
    columns: list[dict] | None = None


@router.post(
    "/api/datasets/{dataset_id}/operations/parse-datetime",
    response_model=OperationResponse,
)
async def parse_datetime(
    dataset_id: str,
    column: str,
    input_format: str | None = None,
    output_format: str = "%Y-%m-%d %H:%M:%S",
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Parse datetime column to standard format."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    try:
        if input_format:
            df[column] = pd.to_datetime(
                df[column], format=input_format, errors="coerce"
            )
        else:
            df[column] = pd.to_datetime(df[column], errors="coerce")

        df[column] = df[column].dt.strftime(output_format)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse datetime: {str(e)}"
        )

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id,
        "parse_datetime",
        {
            "column": column,
            "input_format": input_format,
            "output_format": output_format,
        },
        before,
        after,
        session,
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Parsed '{column}' to datetime",
        columns=dataset.columns,
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/extract-datetime",
    response_model=OperationResponse,
)
async def extract_datetime_parts(
    dataset_id: str,
    column: str,
    parts: list[str] = ["year", "month", "day"],
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Extract datetime parts (year, month, day, hour, etc.) into separate columns."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Parse datetime if not already
    try:
        dt = pd.to_datetime(df[column], errors="coerce")
    except Exception:
        raise HTTPException(
            status_code=400, detail=f"Column '{column}' is not a datetime column"
        )

    valid_parts = {
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "weekday",
        "quarter",
    }
    for part in parts:
        if part not in valid_parts:
            raise HTTPException(status_code=400, detail=f"Invalid part: {part}")
        if part == "year":
            df[f"{column}_year"] = dt.dt.year
        elif part == "month":
            df[f"{column}_month"] = dt.dt.month
        elif part == "day":
            df[f"{column}_day"] = dt.dt.day
        elif part == "hour":
            df[f"{column}_hour"] = dt.dt.hour
        elif part == "minute":
            df[f"{column}_minute"] = dt.dt.minute
        elif part == "second":
            df[f"{column}_second"] = dt.dt.second
        elif part == "weekday":
            df[f"{column}_weekday"] = dt.dt.weekday
        elif part == "quarter":
            df[f"{column}_quarter"] = dt.dt.quarter

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id,
        "extract_datetime",
        {"column": column, "parts": parts},
        before,
        after,
        session,
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Extracted {parts} from '{column}'",
        columns=dataset.columns,
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/standardize-date",
    response_model=OperationResponse,
)
async def standardize_date(
    dataset_id: str,
    column: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Standardize date to YYYY-MM-DD format."""
    return await parse_datetime(
        dataset_id,
        column,
        output_format="%Y-%m-%d",
        current_user=current_user,
        session=session,
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/standardize-datetime",
    response_model=OperationResponse,
)
async def standardize_datetime(
    dataset_id: str,
    column: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Standardize datetime to YYYY-MM-DD HH:MM:SS format."""
    return await parse_datetime(
        dataset_id,
        column,
        output_format="%Y-%m-%d %H:%M:%S",
        current_user=current_user,
        session=session,
    )
