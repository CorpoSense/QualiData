"""Before/After comparison for operations."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, OperationHistory, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["comparison"])


class ComparisonResponse(BaseModel):
    status: str
    operation_id: str
    operation_type: str
    before_columns: list[dict]
    after_columns: list[dict]
    changes_summary: dict[str, Any]


@router.get(
    "/datasets/{dataset_id}/compare/{operation_id}",
    response_model=ComparisonResponse,
)
async def compare_operation(
    dataset_id: str,
    operation_id: str,  # Changed from int to str (UUID)
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get before/after comparison for an operation."""
    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Get operation - use dataset.project_id to get operations for this dataset
    op_result = await session.execute(
        select(OperationHistory).where(
            OperationHistory.id == operation_id,
            OperationHistory.project_id == dataset.project_id,
        )
    )
    operation = op_result.scalar_one_or_none()

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    before = operation.before_snapshot or {}
    after = operation.after_snapshot or {}

    # Calculate changes summary
    changes = {
        "columns_added": [],
        "columns_removed": [],
        "columns_renamed": [],
        "rows_changed": 0,
    }

    before_cols = set(c["name"] for c in before.get("columns", []))
    after_cols = set(c["name"] for c in after.get("columns", []))

    changes["columns_added"] = list(after_cols - before_cols)
    changes["columns_removed"] = list(before_cols - after_cols)

    # Check for renamed columns
    before_cols_list = {c["name"]: c for c in before.get("columns", [])}
    after_cols_list = {c["name"]: c for c in after.get("columns", [])}

    for col_name in before_cols & after_cols:
        if before_cols_list[col_name] != after_cols_list[col_name]:
            changes["columns_renamed"].append({"from": col_name, "to": col_name})

    if "row_count" in before and "row_count" in after:
        changes["rows_changed"] = after["row_count"] - before.get("row_count", 0)

    return ComparisonResponse(
        status="success",
        operation_id=operation.id,
        operation_type=operation.operation_type,
        before_columns=before.get("columns", []),
        after_columns=after.get("columns", []),
        changes_summary=changes,
    )


@router.get("/datasets/{dataset_id}/history/{limit}", response_model=list[dict])
async def get_operation_history_summary(
    dataset_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get summary of recent operations."""
    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Get operations - filter by dataset_id to show only this dataset's history
    ops_result = await session.execute(
        select(OperationHistory)
        .where(cast(OperationHistory.dataset_id, String) == dataset_id)
        .order_by(OperationHistory.created_at.desc())
        .limit(limit)
    )
    operations = ops_result.scalars().all()

    return [
        {
            "id": op.id,
            "type": op.operation_type,
            "params": op.operation_params,
            "created_at": op.created_at.isoformat() if op.created_at else None,
            "is_undone": op.is_undone,
        }
        for op in operations
    ]
