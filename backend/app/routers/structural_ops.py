"""Structural error fixing operations."""

from typing import Optional

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
    columns: Optional[list[dict]] = None


@router.post(
    "/api/datasets/{dataset_id}/operations/fix-case", response_model=OperationResponse
)
async def fix_case(
    dataset_id: int,
    column: str,
    case: str = "title",  # lower, upper, title, sentence
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Fix case inconsistencies in a column."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    if case == "lower":
        df[column] = df[column].astype(str).str.lower().str.strip()
    elif case == "upper":
        df[column] = df[column].astype(str).str.upper().str.strip()
    elif case == "title":
        df[column] = df[column].astype(str).str.title().str.strip()
    elif case == "sentence":
        df[column] = df[column].astype(str).str.capitalize().str.strip()
    else:
        raise HTTPException(status_code=400, detail=f"Invalid case: {case}")

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id, "fix_case", {"column": column, "case": case}, before, after, session
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Fixed case to '{case}' in '{column}'",
        columns=dataset.columns,
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/trim-whitespace",
    response_model=OperationResponse,
)
async def trim_whitespace(
    dataset_id: int,
    columns: Optional[list[str]] = None,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Trim whitespace from string columns."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    cols = columns if columns else df.columns.tolist()
    trimmed_cols = []

    for col in cols:
        if col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip()
                trimmed_cols.append(col)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id, "trim_whitespace", {"columns": cols}, before, after, session
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Trimmed whitespace from {len(trimmed_cols)} columns",
        columns=dataset.columns,
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/fix-typos", response_model=OperationResponse
)
async def fix_typos(
    dataset_id: int,
    column: str,
    mappings: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Fix typos using a mapping dictionary."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Apply mappings
    df[column] = df[column].astype(str).replace(mappings)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id,
        "fix_typos",
        {"column": column, "mappings": mappings},
        before,
        after,
        session,
    )
    await session.commit()

    return OperationResponse(
        status="success", message=f"Fixed typos in '{column}'", columns=dataset.columns
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/standardize-values",
    response_model=OperationResponse,
)
async def standardize_values(
    dataset_id: int,
    column: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Standardize common value variations."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Common standardizations
    mappings = {
        "yes": "Yes",
        "y": "Yes",
        "Y": "Yes",
        "YES": "Yes",
        "true": "Yes",
        "True": "Yes",
        "TRUE": "Yes",
        "1": "Yes",
        "no": "No",
        "n": "No",
        "N": "No",
        "NO": "No",
        "false": "No",
        "False": "No",
        "FALSE": "No",
        "0": "No",
        "male": "Male",
        "m": "Male",
        "M": "Male",
        "female": "Female",
        "f": "Female",
        "F": "Female",
    }

    # Check if column might be boolean-like
    unique_vals = df[column].astype(str).str.lower().unique()
    if any(v in mappings for v in unique_vals):
        df[column] = df[column].astype(str).replace(mappings)

    from app.routers.datasets import detect_columns, get_preview_data

    before = {"columns": dataset.columns}
    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    after = {"columns": dataset.columns}

    save_operation(
        dataset_id, "standardize_values", {"column": column}, before, after, session
    )
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Standardized values in '{column}'",
        columns=dataset.columns,
    )
