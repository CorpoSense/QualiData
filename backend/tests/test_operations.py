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
