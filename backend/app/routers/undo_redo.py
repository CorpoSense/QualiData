"""Undo/Redo operations for datasets."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.db.models import User, Dataset, Project
from app.db.models.project import OperationHistory
from app.routers.auth import get_current_active_user


router = APIRouter()


@router.post(
    "/datasets/{dataset_id}/operations/undo", response_model=dict
)
async def undo_operation(
    dataset_id: str,
    request: dict | None = None,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Undo the last operation on a dataset by restoring from before_snapshot."""
    # Get dataset with ownership check
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.owner_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the last applied operation that hasn't been undone
    op_result = await session.execute(
        select(OperationHistory)
        .where(
            OperationHistory.project_id == dataset.project_id,
            OperationHistory.is_applied is True,
            OperationHistory.is_undone is False,
        )
        .order_by(OperationHistory.created_at.desc())
        .limit(1)
    )
    operation = op_result.scalar_one_or_none()

    if not operation:
        return {"status": "success", "message": "No operations to undo"}

    # Restore from before_snapshot
    if operation.before_snapshot:
        if "columns" in operation.before_snapshot:
            dataset.columns = operation.before_snapshot.get("columns")
        if "preview_data" in operation.before_snapshot:
            dataset.preview_data = operation.before_snapshot.get("preview_data")
        if "row_count" in operation.before_snapshot:
            dataset.row_count = operation.before_snapshot.get(
                "row_count", len(dataset.preview_data) if dataset.preview_data else 0
            )

    # Mark as undone
    operation.is_undone = True

    await session.commit()

    return {"status": "success", "message": f"Undone: {operation.operation_type}"}


@router.post(
    "/datasets/{dataset_id}/operations/redo", response_model=dict
)
async def redo_operation(
    dataset_id: str,
    request: dict | None = None,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Redo the last undone operation on a dataset by restoring from after_snapshot."""
    # Get dataset with ownership check
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.owner_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the last undone operation (is_undone = True)
    op_result = await session.execute(
        select(OperationHistory)
        .where(
            OperationHistory.project_id == dataset.project_id,
            OperationHistory.is_undone is True,
        )
        .order_by(OperationHistory.created_at.desc())
        .limit(1)
    )
    operation = op_result.scalar_one_or_none()

    if not operation:
        return {"status": "success", "message": "No operations to redo"}

    # Restore from after_snapshot
    if operation.after_snapshot:
        if "columns" in operation.after_snapshot:
            dataset.columns = operation.after_snapshot.get("columns")
        if "preview_data" in operation.after_snapshot:
            dataset.preview_data = operation.after_snapshot.get("preview_data")
        if "row_count" in operation.after_snapshot:
            dataset.row_count = operation.after_snapshot.get(
                "row_count", len(dataset.preview_data) if dataset.preview_data else 0
            )

    # Mark as applied (not undone)
    operation.is_undone = False

    await session.commit()

    return {"status": "success", "message": f"Redone: {operation.operation_type}"}
