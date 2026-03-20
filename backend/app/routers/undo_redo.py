"""Undo/Redo operations for datasets."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, cast, String
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
    """Undo an operation on a dataset by restoring from before_snapshot.

    If operation_id is provided in request body, undo that specific operation.
    Otherwise, undo the last applied operation.
    """
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
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the operation to undo
    operation_id = (request or {}).get("operation_id")

    if operation_id:
        op_result = await session.execute(
            select(OperationHistory).where(
                OperationHistory.id == operation_id,
                cast(OperationHistory.dataset_id, String) == dataset_id,
            )
        )
        operation = op_result.scalar_one_or_none()
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")
        if operation.is_undone:
            raise HTTPException(status_code=400, detail="Operation already undone")
    else:
        # Find the last applied operation that hasn't been undone
        op_result = await session.execute(
            select(OperationHistory)
            .where(
                cast(OperationHistory.dataset_id, String) == dataset_id,
                OperationHistory.is_applied == True,
                OperationHistory.is_undone == False,
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

    return {"status": "success", "message": f"Undone: {operation.operation_type}", "operation_id": operation.id}


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
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the last undone operation for this dataset
    op_result = await session.execute(
        select(OperationHistory)
        .where(
            cast(OperationHistory.dataset_id, String) == dataset_id,
            OperationHistory.is_undone == True,
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


@router.post("/datasets/{dataset_id}/operations/undo-batch")
async def undo_batch(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Undo multiple operations by ID. Processes in reverse chronological order."""
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    operation_ids = request.get("operation_ids", [])
    if not operation_ids:
        raise HTTPException(status_code=400, detail="operation_ids is required")

    # Fetch all requested operations, ordered newest first
    ops_result = await session.execute(
        select(OperationHistory)
        .where(
            OperationHistory.id.in_(operation_ids),
            cast(OperationHistory.dataset_id, String) == dataset_id,
            OperationHistory.is_undone == False,
        )
        .order_by(OperationHistory.created_at.desc())
    )
    operations = ops_result.scalars().all()

    if not operations:
        return {"status": "success", "message": "No operations to undo", "undone": []}

    # Undo in reverse chronological order
    # The last operation's before_snapshot becomes the dataset state
    last_op = operations[0]  # newest (first in desc order)
    if last_op.before_snapshot:
        if "columns" in last_op.before_snapshot:
            dataset.columns = last_op.before_snapshot.get("columns")
        if "preview_data" in last_op.before_snapshot:
            dataset.preview_data = last_op.before_snapshot.get("preview_data")
        if "row_count" in last_op.before_snapshot:
            dataset.row_count = last_op.before_snapshot.get(
                "row_count", len(dataset.preview_data) if dataset.preview_data else 0
            )

    undone_ids = []
    for op in operations:
        op.is_undone = True
        undone_ids.append(op.id)

    await session.commit()

    return {
        "status": "success",
        "message": f"Undone {len(undone_ids)} operation(s)",
        "undone": undone_ids,
    }
