"""Shared utility functions for dataset operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Dataset
from app.db.models.project import OperationHistory


async def save_operation(
    dataset_id: str,
    operation_type: str,
    params: dict,
    before: dict,
    after: dict,
    session: AsyncSession,
):
    """
    Save an operation to the history table.
    
    This function properly handles UUID types for PostgreSQL.
    It queries the dataset to get its actual UUID id and project_id.
    """
    # Get dataset to get proper UUID id
    result = await session.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        return
    
    op = OperationHistory(
        project_id=dataset.project_id,
        dataset_id=dataset.id,  # Use dataset.id which is UUID
        operation_type=operation_type,
        operation_name=operation_type,  # Required field
        operation_params=params,
        before_snapshot=before,
        after_snapshot=after,
        is_applied=True,
        is_undone=False,
    )
    session.add(op)
