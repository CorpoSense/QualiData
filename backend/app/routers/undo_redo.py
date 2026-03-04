"""Undo/Redo operations for datasets."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, OperationHistory, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["dataset-operations"])


class OperationResponse(BaseModel):
    status: str
    message: str


def get_dataset_with_owner_check(dataset_id: str, user_id: str, session: AsyncSession):
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


@router.post(
    "/api/datasets/{dataset_id}/operations/undo", response_model=OperationResponse
)
async def undo_operation(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Undo the last operation on a dataset."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    # Find the last applied operation that hasn't been undone
    result = await session.execute(
        select(OperationHistory)
        .where(
            OperationHistory.dataset_id == dataset_id,
            OperationHistory.is_applied is True,
            OperationHistory.is_undone is False,
        )
        .order_by(OperationHistory.created_at.desc())
        .limit(1)
    )
    operation = result.scalar_one_or_none()

    if not operation:
        return OperationResponse(status="success", message="No operations to undo")

    # Restore from before_snapshot
    if operation.before_snapshot:
        if "columns" in operation.before_snapshot:
            dataset.columns = operation.before_snapshot.get("columns")
        if "data" in operation.before_snapshot:
            dataset.preview_data = operation.before_snapshot.get("data")
        if "row_count" in operation.before_snapshot:
            dataset.row_count = operation.before_snapshot.get(
                "row_count", len(dataset.preview_data) if dataset.preview_data else 0
            )

    # Mark as undone
    operation.is_undone = False  # Keep as applied but mark for redo

    await session.commit()

    return OperationResponse(
        status="success", message=f"Undone: {operation.operation_type}"
    )


@router.post(
    "/api/datasets/{dataset_id}/operations/redo", response_model=OperationResponse
)
async def redo_operation(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Redo the last undone operation on a dataset."""
    dataset = get_dataset_with_owner_check(dataset_id, current_user.id, session)

    # Find the last undone operation
    result = await session.execute(
        select(OperationHistory)
        .where(
            OperationHistory.dataset_id == dataset_id,
            OperationHistory.is_applied is True,
            OperationHistory.is_undone is False,
        )
        .order_by(OperationHistory.created_at.desc())
        .limit(1)
    )
    operation = result.scalar_one_or_none()

    if not operation:
        return OperationResponse(status="success", message="No operations to redo")

    # Restore from after_snapshot
    if operation.after_snapshot:
        if "columns" in operation.after_snapshot:
            dataset.columns = operation.after_snapshot.get("columns")
        if "data" in operation.after_snapshot:
            dataset.preview_data = operation.after_snapshot.get("data")
        if "row_count" in operation.after_snapshot:
            dataset.row_count = operation.after_snapshot.get(
                "row_count", len(dataset.preview_data) if dataset.preview_data else 0
            )

    await session.commit()

    return OperationResponse(
        status="success", message=f"Redone: {operation.operation_type}"
    )
