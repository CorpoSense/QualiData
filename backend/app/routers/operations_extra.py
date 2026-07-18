"""Additional dataset operations - filter, sort, deduplicate, find-replace, type conversion."""

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, OperationHistory, Project, User
from app.routers.auth import get_current_active_user
from app.utils.operations import save_operation

router = APIRouter(tags=["dataset-operations"])

# Valid target types for change-type operations
VALID_TARGET_TYPES = ["string", "integer", "float", "boolean", "datetime", "category"]

# Boolean-like values for detection
_BOOLEAN_VALUES = {"true", "false", "yes", "no", "y", "n", "t", "f", "0", "1"}

# Regex patterns for type detection
_INTEGER_PATTERN = re.compile(r"^-?\d+$")
_FLOAT_PATTERN = re.compile(r"^-?\d+\.?\d*([eE][+-]?\d+)?$")


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
    target_type: str  # string, integer, float, boolean, datetime, category
    error_handling: str = "coerce"  # coerce, fallback, raise
    fallback_value: Any | None = None


class DetectTypeRequest(BaseModel):
    columns: list[str]


class ChangeTypePreviewRequest(BaseModel):
    columns: list[str]
    target_type: str
    error_handling: str = "coerce"  # coerce, fallback, raise
    fallback_value: Any | None = None
    sample_rows: int = 10


class OperationResponse(BaseModel):
    status: str
    message: str
    columns: list[dict] | None = None
    row_count: int | None = None


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


def detect_column_type(col_data) -> dict:
    """Analyze a column's data and return type detection results.

    Uses heuristic analysis to determine the best type for a column.
    Returns a dict with current_type, suggested_type, confidence, reason,
    type_scores, sample_values, null_count, and total_rows.
    """
    import pandas as pd

    total_rows = len(col_data)
    null_count = int(col_data.isna().sum())
    non_null = col_data.dropna()

    if total_rows == 0 or len(non_null) == 0:
        return {
            "current_type": str(col_data.dtype),
            "suggested_type": "string",
            "confidence": 1.0,
            "reason": "Empty column, defaulting to string",
            "type_scores": {"string": 1.0},
            "sample_values": [],
            "null_count": null_count,
            "total_rows": total_rows,
        }

    # Get string representations for analysis
    str_values = non_null.astype(str)
    sample_values = str_values.head(5).tolist()

    # Current dtype
    current_dtype = str(col_data.dtype)

    # Calculate scores for each type
    scores = {}

    # String: always possible (score 1.0)
    scores["string"] = 1.0

    # Boolean: all non-null values are boolean-like
    lower_values = str_values.str.lower().str.strip()
    bool_match = lower_values.isin(_BOOLEAN_VALUES)
    scores["boolean"] = float(bool_match.sum()) / len(non_null) if len(non_null) > 0 else 0.0

    # Integer: all non-null values match integer pattern
    int_match = str_values.apply(lambda x: bool(_INTEGER_PATTERN.match(str(x).strip())))
    scores["integer"] = float(int_match.sum()) / len(non_null) if len(non_null) > 0 else 0.0

    # Float: all non-null values match float pattern (includes integers)
    float_match = str_values.apply(lambda x: bool(_FLOAT_PATTERN.match(str(x).strip())))
    scores["float"] = float(float_match.sum()) / len(non_null) if len(non_null) > 0 else 0.0

    # Datetime: try parsing with pd.to_datetime
    try:
        parsed = pd.to_datetime(non_null, errors="coerce")
        datetime_valid = parsed.notna().sum()
        scores["datetime"] = float(datetime_valid) / len(non_null) if len(non_null) > 0 else 0.0
    except Exception:
        scores["datetime"] = 0.0

    # Category: low cardinality (unique < 20% of total AND unique < 50)
    unique_count = non_null.nunique()
    if total_rows > 0 and unique_count < max(50, total_rows * 0.2):
        scores["category"] = min(1.0, 1.0 - (unique_count / max(total_rows, 1)))
    else:
        scores["category"] = 0.0

    # Determine suggested type (priority: boolean > integer > float > datetime > category > string)
    # Only suggest if score >= 0.8 (80% of values match)
    type_priority = ["boolean", "integer", "float", "datetime", "category", "string"]
    suggested_type = "string"
    confidence = 1.0
    reason = "Default fallback type"

    for t in type_priority:
        score = scores.get(t, 0.0)
        if score >= 0.8:
            suggested_type = t
            confidence = round(score, 2)
            if t == "boolean":
                reason = f"{int(score * 100)}% of non-null values are boolean-like"
            elif t == "integer":
                reason = f"{int(score * 100)}% of non-null values are valid integers"
            elif t == "float":
                reason = f"{int(score * 100)}% of non-null values are valid numbers"
            elif t == "datetime":
                reason = f"{int(score * 100)}% of non-null values parse as datetime"
            elif t == "category":
                reason = f"Low cardinality: {unique_count} unique values in {total_rows} rows"
            else:
                reason = "Default string type"
            break

    # If current dtype already matches suggested, still report it
    # but note that the column may already be the right type
    return {
        "current_type": current_dtype,
        "suggested_type": suggested_type,
        "confidence": confidence,
        "reason": reason,
        "type_scores": {k: round(v, 2) for k, v in scores.items()},
        "sample_values": sample_values,
        "null_count": null_count,
        "total_rows": total_rows,
    }


def convert_column(col_data, target_type: str, error_handling: str = "coerce", fallback_value: Any = None):
    """Convert a column to the target type with error handling.

    Returns (converted_series, error_count, error_indices).
    """
    import pandas as pd
    import numpy as np

    if target_type not in VALID_TARGET_TYPES:
        raise ValueError(f"Unknown target type: {target_type}. Valid types: {VALID_TARGET_TYPES}")

    if target_type == "string":
        return col_data.astype(str), 0, []

    # For numeric types, first try conversion
    if target_type == "integer":
        numeric = pd.to_numeric(col_data, errors="coerce")
        error_mask = numeric.isna() & col_data.notna()
        error_count = int(error_mask.sum())
        error_indices = col_data[error_mask].index.tolist()

        if error_handling == "raise" and error_count > 0:
            raise ValueError(f"{error_count} value(s) cannot be converted to integer")
        elif error_handling == "fallback" and fallback_value is not None:
            numeric[error_mask] = int(fallback_value) if not pd.isna(fallback_value) else pd.NA
        # coerce: leave as NA (default behavior)

        # Use float astype first then convert to Int64 to handle fractional values
        # (they get truncated, which is the expected behavior for int conversion)
        numeric = numeric.where(numeric.isna(), numeric.round(0))
        return numeric.astype("Int64"), error_count, error_indices

    elif target_type == "float":
        numeric = pd.to_numeric(col_data, errors="coerce")
        error_mask = numeric.isna() & col_data.notna()
        error_count = int(error_mask.sum())
        error_indices = col_data[error_mask].index.tolist()

        if error_handling == "raise" and error_count > 0:
            raise ValueError(f"{error_count} value(s) cannot be converted to float")
        elif error_handling == "fallback" and fallback_value is not None:
            numeric[error_mask] = float(fallback_value) if not pd.isna(fallback_value) else np.nan
        # coerce: leave as NaN (default behavior)

        return numeric, error_count, error_indices

    elif target_type == "boolean":
        # Smart boolean conversion: map common boolean strings
        str_col = col_data.astype(str).str.lower().str.strip()
        bool_map = {
            "true": True, "false": False,
            "yes": True, "no": False,
            "y": True, "n": False,
            "t": True, "f": False,
            "1": True, "0": False,
        }
        mapped = str_col.map(bool_map)
        error_mask = mapped.isna() & col_data.notna()
        error_count = int(error_mask.sum())
        error_indices = col_data[error_mask].index.tolist()

        if error_handling == "raise" and error_count > 0:
            raise ValueError(f"{error_count} value(s) cannot be converted to boolean")
        elif error_handling == "fallback" and fallback_value is not None:
            fb = bool(fallback_value) if not pd.isna(fallback_value) else False
            mapped[error_mask] = fb
        elif error_handling == "coerce":
            # For non-mappable values, use Python truthiness as fallback
            mapped[error_mask] = col_data[error_mask].astype(bool)

        return mapped, error_count, error_indices

    elif target_type == "datetime":
        parsed = pd.to_datetime(col_data, errors="coerce")
        error_mask = parsed.isna() & col_data.notna()
        error_count = int(error_mask.sum())
        error_indices = col_data[error_mask].index.tolist()

        if error_handling == "raise" and error_count > 0:
            raise ValueError(f"{error_count} value(s) cannot be converted to datetime")
        elif error_handling == "fallback" and fallback_value is not None:
            fb_val = pd.to_datetime(fallback_value, errors="coerce")
            parsed[error_mask] = fb_val
        # coerce: leave as NaT (default behavior)

        return parsed, error_count, error_indices

    elif target_type == "category":
        return col_data.astype("category"), 0, []

    # Fallback (should not reach here)
    return col_data, 0, []


def generate_data_loss_warnings(col_data, current_type: str, target_type: str, error_count: int) -> list[str]:
    """Generate warnings about potential data loss during type conversion."""
    import pandas as pd

    warnings = []

    if error_count > 0:
        total = len(col_data)
        warnings.append(
            f"{error_count} of {total} value(s) cannot be converted and will become null"
        )

    # Float to integer: precision loss
    if target_type == "integer" and current_type in ("float", "float64", "Float64"):
        numeric = pd.to_numeric(col_data, errors="coerce")
        fractional = numeric[numeric.notna()] != numeric[numeric.notna()].round()
        frac_count = int(fractional.sum())
        if frac_count > 0:
            warnings.append(
                f"Precision loss: {frac_count} value(s) have non-zero fractional parts that will be truncated"
            )

    # Any to boolean: non-boolean values get truthy conversion
    if target_type == "boolean" and current_type not in ("bool", "boolean"):
        warnings.append("Non-boolean values will be converted: 0/empty=False, other=True")

    # Datetime to string: loses datetime operations
    if target_type == "string" and "datetime" in current_type:
        warnings.append("Datetime objects will be converted to string representation")

    # Numeric to string: loses numeric operations
    if target_type == "string" and current_type not in ("object", "string", "category"):
        warnings.append("Numeric values will become text — numeric operations will no longer work")

    # String to category: new unseen values may cause issues
    if target_type == "category":
        warnings.append("Values will be stored as categories. New unseen values may cause issues")

    return warnings


def _safe_str(val) -> str | None:
    """Convert value to string safely, handling NaN/NaT."""
    import pandas as pd
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(val, pd.Timestamp):
        return val.isoformat() if pd.notna(val) else None
    return str(val)


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
    dataset_id: str,
    request: FilterRowsRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])
    before_row_count = len(df)

    df = apply_filter(df, request.column, request.operator, request.value)

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "row_count": before_row_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "data": dataset.data_json["data"]}

    await save_operation(dataset_id, "filter_rows", request.model_dump(), before, after, session)
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
    dataset_id: str,
    request: SortDataRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])

    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )

    df = df.sort_values(by=request.column, ascending=request.ascending)

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns, "data": dataset.data_json["data"]}

    await save_operation(dataset_id, "sort_data", request.model_dump(), before, after, session)
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
    dataset_id: str,
    request: RemoveDuplicatesRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])
    before_count = len(df)

    if request.columns:
        df = df.drop_duplicates(subset=request.columns)
    else:
        df = df.drop_duplicates()

    duplicates_removed = before_count - len(df)

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "row_count": before_count, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    dataset.row_count = len(df)
    after = {"columns": dataset.columns, "row_count": len(df), "data": dataset.data_json["data"]}

    await save_operation(
        dataset_id, "remove_duplicates", request.model_dump(), before, after, session
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
    dataset_id: str,
    request: FindReplaceRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])

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

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns, "data": dataset.data_json["data"]}

    await save_operation(dataset_id, "find_replace", request.model_dump(), before, after, session)
    await session.commit()

    return OperationResponse(
        status="success",
        message=f"Replaced {before_count} occurrences",
        columns=dataset.columns,
    )


@router.post(
    "/datasets/{dataset_id}/operations/detect-type"
)
async def detect_type(
    dataset_id: str,
    request: DetectTypeRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Detect the best type for selected columns using heuristic analysis.

    Returns current type, suggested type, confidence score, and per-type scores
    for each requested column.
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])

    results = []
    for col in request.columns:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{col}' not found")
        detection = detect_column_type(df[col])
        detection["column"] = col
        results.append(detection)

    return {"status": "success", "columns": results}


@router.post(
    "/datasets/{dataset_id}/operations/change-type-preview"
)
async def change_type_preview(
    dataset_id: str,
    request: ChangeTypePreviewRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Preview the effect of a type change without modifying data.

    Returns before/after sample values, data loss warnings, and error counts.
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    if request.target_type not in VALID_TARGET_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown target type: {request.target_type}. Valid types: {VALID_TARGET_TYPES}",
        )

    if request.error_handling not in ("coerce", "fallback", "raise"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid error_handling: {request.error_handling}. Must be 'coerce', 'fallback', or 'raise'",
        )

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])

    results = []
    for col in request.columns:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{col}' not found")

        col_data = df[col]
        current_type = str(col_data.dtype)

        # Get sample rows for preview
        sample_size = min(request.sample_rows, len(col_data))
        sample_indices = col_data.index[:sample_size].tolist()
        sample_before = col_data.iloc[:sample_size].tolist()

        # Try conversion on the full column to count errors
        try:
            converted, error_count, error_indices = convert_column(
                col_data, request.target_type,
                request.error_handling, request.fallback_value,
            )
        except ValueError as e:
            # raise mode: report errors without modifying
            results.append({
                "column": col,
                "current_type": current_type,
                "target_type": request.target_type,
                "preview": [],
                "warnings": [str(e)],
                "data_loss_warnings": [],
                "total_errors": error_count if 'error_count' in dir() else len(col_data),
                "total_rows": len(col_data),
                "error": str(e),
            })
            continue

        # Build preview: before/after for sample rows
        sample_converted = converted.iloc[:sample_size]
        preview = []
        for i, idx in enumerate(sample_indices):
            before_val = sample_before[i]
            after_val = sample_converted.iloc[i]

            # Format for JSON serialization
            before_str = _safe_str(before_val)
            after_str = _safe_str(after_val)

            # Consider value changed if string representation differs OR type changes
            # (e.g. "30" → 30 looks same as string but type changed)
            # For object dtype, any non-string target is a type change
            is_error = idx in error_indices
            is_object_to_typed = current_type == "object" and request.target_type not in ("string", "category")
            is_typed_change = current_type != "object" and current_type != request.target_type
            type_changed = is_object_to_typed or is_typed_change
            changed = before_str != after_str or (type_changed and not is_error)

            preview.append({
                "before": before_str,
                "after": after_str,
                "changed": changed,
                "error": is_error,
                "error_reason": "Cannot convert to " + request.target_type if is_error else None,
            })

        # Generate warnings
        warnings = []
        data_loss_warnings = generate_data_loss_warnings(
            col_data, current_type, request.target_type, error_count
        )

        results.append({
            "column": col,
            "current_type": current_type,
            "target_type": request.target_type,
            "preview": preview,
            "warnings": warnings,
            "data_loss_warnings": data_loss_warnings,
            "total_errors": error_count,
            "total_rows": len(col_data),
        })

    return {"status": "success", "columns": results}


@router.post(
    "/datasets/{dataset_id}/operations/change-type", response_model=OperationResponse
)
async def change_type(
    dataset_id: str,
    request: ChangeTypeRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Change the type of a column with configurable error handling.

    Supports error_handling modes:
    - coerce: Invalid values become null (default, backward compatible)
    - fallback: Invalid values replaced with fallback_value
    - raise: Fail the entire operation if any value cannot convert

    Also supports 'category' type in addition to the original types.
    """
    dataset = await get_dataset_with_owner_check(dataset_id, current_user.id, session)
    if not dataset.data_json or "data" not in dataset.data_json:
        raise HTTPException(status_code=400, detail="No data to operate on")

    if request.target_type not in VALID_TARGET_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown target type: {request.target_type}. Valid types: {VALID_TARGET_TYPES}",
        )

    if request.error_handling not in ("coerce", "fallback", "raise"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid error_handling: {request.error_handling}. Must be 'coerce', 'fallback', or 'raise'",
        )

    import pandas as pd

    df = pd.DataFrame(dataset.data_json["data"])

    if request.column not in df.columns:
        raise HTTPException(
            status_code=400, detail=f"Column '{request.column}' not found"
        )

    current_type = str(df[request.column].dtype)

    # Convert type using the shared helper
    try:
        converted, error_count, error_indices = convert_column(
            df[request.column], request.target_type,
            request.error_handling, request.fallback_value,
        )
        df[request.column] = converted
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {str(e)}")

    from app.routers.datasets import detect_columns, get_preview_data, get_full_data_json

    before = {"columns": dataset.columns, "data": dataset.data_json["data"]}
    dataset.columns = detect_columns(df)
    dataset.data_json = get_full_data_json(df)
    after = {"columns": dataset.columns, "data": dataset.data_json["data"]}

    await save_operation(dataset_id, "change_type", request.model_dump(), before, after, session)
    await session.commit()

    # Build descriptive message
    msg = f"Changed '{request.column}' from {current_type} to {request.target_type}"
    if error_count > 0:
        if request.error_handling == "coerce":
            msg += f". {error_count} value(s) could not be converted and were set to null"
        elif request.error_handling == "fallback":
            msg += f". {error_count} value(s) could not be converted and were set to fallback value"

    return OperationResponse(
        status="success",
        message=msg,
        columns=dataset.columns,
    )
