"""Undo/Redo operations for datasets."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.db.models import User, Dataset, Project
from app.db.models.project import OperationHistory
from app.routers.auth import get_current_active_user


router = APIRouter()


def _restore_snapshot(dataset: Dataset, snapshot: dict | None) -> None:
    """Restore dataset state from a before/after snapshot.

    Handles both the modern snapshot format (``{"data": [...]}``) and the
    legacy format (``{"preview_data": [...]}``) written by older operation
    endpoints. Preserves the ``charts`` key in ``data_json`` so that chart
    configurations are not destroyed on undo/redo.
    """
    if not snapshot:
        return

    # Restore columns
    if "columns" in snapshot:
        dataset.columns = snapshot.get("columns")

    # Restore data_json. Prefer the full "data" key; fall back to the legacy
    # "preview_data" key for history records written by older endpoints.
    data = snapshot.get("data")
    if data is None:
        data = snapshot.get("preview_data")

    if data is not None:
        # Preserve existing charts (and any other keys) in data_json.
        existing = dataset.data_json if isinstance(dataset.data_json, dict) else {}
        new_data_json = {**existing, "data": data}
        dataset.data_json = new_data_json

    # Restore row_count
    if "row_count" in snapshot:
        dataset.row_count = snapshot.get(
            "row_count", len(data) if data is not None else dataset.row_count
        )
    elif data is not None:
        dataset.row_count = len(data)


async def _get_owned_dataset(
    dataset_id: str, current_user: User, session: AsyncSession
) -> Dataset:
    """Fetch dataset and verify ownership via project."""
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
    return dataset


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
    dataset = await _get_owned_dataset(dataset_id, current_user, session)

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
    _restore_snapshot(dataset, operation.before_snapshot)

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
    dataset = await _get_owned_dataset(dataset_id, current_user, session)

    # Find the operation to redo
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
        if not operation.is_undone:
            raise HTTPException(status_code=400, detail="Operation not undone")
    else:
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
    _restore_snapshot(dataset, operation.after_snapshot)

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
    dataset = await _get_owned_dataset(dataset_id, current_user, session)

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
    _restore_snapshot(dataset, last_op.before_snapshot)

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


@router.post("/datasets/{dataset_id}/operations/redo-batch")
async def redo_batch(
    dataset_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Redo multiple operations by ID. Processes in chronological order."""
    dataset = await _get_owned_dataset(dataset_id, current_user, session)

    operation_ids = request.get("operation_ids", [])
    if not operation_ids:
        raise HTTPException(status_code=400, detail="operation_ids is required")

    # Fetch all requested operations, ordered oldest first (chronological order)
    ops_result = await session.execute(
        select(OperationHistory)
        .where(
            OperationHistory.id.in_(operation_ids),
            cast(OperationHistory.dataset_id, String) == dataset_id,
            OperationHistory.is_undone == True,
        )
        .order_by(OperationHistory.created_at.asc())
    )
    operations = ops_result.scalars().all()

    if not operations:
        return {"status": "success", "message": "No operations to redo", "redone": []}

    # Redo in chronological order
    # The first operation's after_snapshot becomes the dataset state
    first_op = operations[0]  # oldest (first in asc order)
    _restore_snapshot(dataset, first_op.after_snapshot)

    redone_ids = []
    for op in operations:
        op.is_undone = False
        redone_ids.append(op.id)

    await session.commit()

    return {
        "status": "success",
        "message": f"Redone {len(redone_ids)} operation(s)",
        "redone": redone_ids,
    }
