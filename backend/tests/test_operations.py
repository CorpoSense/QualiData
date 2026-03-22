"""Tests for operations including save_operation."""

from unittest.mock import MagicMock, patch, AsyncMock

import pytest


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.db.models.project import OperationHistory
        from app.routers.operations import save_operation


class TestSaveOperation:
    """Test save_operation function."""

    @pytest.mark.asyncio
    async def test_save_operation_creates_history_record(self):
        """Test that save_operation creates an OperationHistory record."""
        # Test the one in utils (the single source of truth)
        from app.utils.operations import save_operation
        
        # Create mock session with async execute
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(project_id="project-123", id="uuid-456")
        
        # Make execute return a coroutine that resolves to the result
        async def mock_execute(*args, **kwargs):
            return mock_result
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        mock_session.add = MagicMock()

        # Call save_operation (now async)
        await save_operation(
            dataset_id="dataset-456",
            operation_type="string_operations",
            params={"operation": "uppercase", "columns": ["name", "email"]},
            before={"columns": [{"name": "name"}, {"name": "email"}], "row_count": 100},
            after={"columns": [{"name": "name"}, {"name": "email"}], "row_count": 100},
            session=mock_session,
        )

        # Verify session.add was called with OperationHistory
        mock_session.add.assert_called_once()
        call_args = mock_session.add.call_args[0][0]
        
        # Verify the OperationHistory was created with correct fields
        assert isinstance(call_args, OperationHistory)
        assert call_args.project_id == "project-123"
        assert call_args.dataset_id == "uuid-456"
        assert call_args.operation_type == "string_operations"
        assert call_args.operation_params == {"operation": "uppercase", "columns": ["name", "email"]}

    @pytest.mark.asyncio
    async def test_save_operation_handles_missing_dataset(self):
        """Test that save_operation handles missing dataset gracefully."""
        # Create mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Dataset not found
        
        async def mock_execute(*args, **kwargs):
            return mock_result
        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Call save_operation - should not raise
        await save_operation(
            dataset_id="nonexistent-dataset",
            operation_type="string_operations",
            params={},
            before={},
            after={},
            session=mock_session,
        )

        # Verify session.add was NOT called
        mock_session.add.assert_not_called()


class TestOperationHistoryModel:
    """Test OperationHistory model fields."""

    def test_operation_history_has_required_fields(self):
        """Test that OperationHistory has all required fields."""
        # Check that the model has the expected attributes
        assert hasattr(OperationHistory, 'id')
        assert hasattr(OperationHistory, 'project_id')
        assert hasattr(OperationHistory, 'operation_type')
        assert hasattr(OperationHistory, 'operation_name')
        assert hasattr(OperationHistory, 'operation_params')
        assert hasattr(OperationHistory, 'before_snapshot')
        assert hasattr(OperationHistory, 'after_snapshot')
        assert hasattr(OperationHistory, 'is_applied')
        assert hasattr(OperationHistory, 'is_undone')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestDeleteOperationHistory:
    """Test DELETE /datasets/{id}/operations/{op_id}."""

    @pytest.mark.asyncio
    async def test_delete_undone_operation(self):
        from app.routers.operations import delete_operation_history

        dataset = MagicMock()
        dataset.id = "ds-1"
        dataset.project_id = "proj-1"

        op = MagicMock()
        op.id = "op-1"
        op.is_undone = True

        mock_session = AsyncMock()

        async def mock_execute(stmt):
            mock_r = MagicMock()
            s = str(stmt)
            if "projects" in s.lower():
                mock_r.scalar_one_or_none.return_value = MagicMock()
            elif "operation_history" in s.lower():
                mock_r.scalar_one_or_none.return_value = op
            elif "datasets" in s.lower():
                mock_r.scalar_one_or_none.return_value = dataset
            return mock_r

        mock_session.execute = mock_execute

        result = await delete_operation_history(
            dataset_id="ds-1",
            operation_id="op-1",
            current_user=MagicMock(id="u1"),
            session=mock_session,
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_active_operation_rejected(self):
        from fastapi import HTTPException
        from app.routers.operations import delete_operation_history

        dataset = MagicMock()
        dataset.id = "ds-1"
        dataset.project_id = "proj-1"

        op = MagicMock()
        op.id = "op-1"
        op.is_undone = False  # not undone

        mock_session = AsyncMock()

        async def mock_execute(stmt):
            mock_r = MagicMock()
            s = str(stmt)
            if "projects" in s.lower():
                mock_r.scalar_one_or_none.return_value = MagicMock()
            elif "operation_history" in s.lower():
                mock_r.scalar_one_or_none.return_value = op
            elif "datasets" in s.lower():
                mock_r.scalar_one_or_none.return_value = dataset
            return mock_r

        mock_session.execute = mock_execute

        with pytest.raises(HTTPException) as exc_info:
            await delete_operation_history(
                dataset_id="ds-1",
                operation_id="op-1",
                current_user=MagicMock(id="u1"),
                session=mock_session,
            )

        assert exc_info.value.status_code == 400
        assert "Undo it first" in exc_info.value.detail


class TestOperationStats:
    """Test GET /operations/stats endpoint."""

    @pytest.mark.asyncio
    async def test_stats_returns_correct_structure(self):
        from app.routers.operations import get_operation_stats

        mock_session = AsyncMock()
        call_count = [0]

        async def mock_execute(stmt):
            call_count[0] += 1
            mock_r = MagicMock()
            s = str(stmt).lower()
            if "projects" in s and "operation_history" not in s:
                mock_r.fetchall.return_value = [("proj-1",)]
            elif "datasets" in s and "operation_history" not in s:
                mock_r.fetchall.return_value = [("ds-1",)]
            elif "count" in s and "operation_history" in s and "is_undone" in s:
                mock_r.scalar.return_value = 2  # undone count
            elif "count" in s and "operation_history" in s and "ai_" in s:
                mock_r.scalar.return_value = 5  # AI ops
            elif "count" in s and "operation_history" in s:
                mock_r.scalar.return_value = 10  # total
            elif "group_by" in s:
                mock_r.fetchall.return_value = [("fillna", 3), ("string-operations", 2)]
            else:
                mock_r.scalar.return_value = 0
            return mock_r

        mock_session.execute = mock_execute

        result = await get_operation_stats(
            current_user=MagicMock(id="u1"),
            session=mock_session,
        )

        assert "total" in result
        assert "ai_operations" in result
        assert "manual_operations" in result
        assert "active" in result
        assert "undone" in result
        assert "top_types" in result

    @pytest.mark.asyncio
    async def test_stats_empty_user(self):
        from app.routers.operations import get_operation_stats

        mock_session = AsyncMock()

        async def mock_execute(stmt):
            mock_r = MagicMock()
            mock_r.fetchall.return_value = []
            mock_r.scalar.return_value = 0
            return mock_r

        mock_session.execute = mock_execute

        result = await get_operation_stats(
            current_user=MagicMock(id="u1"),
            session=mock_session,
        )

        assert result["total"] == 0
        assert result["top_types"] == []
