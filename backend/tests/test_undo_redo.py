"""Tests for undo/redo functionality."""

import pytest
from unittest.mock import patch, MagicMock


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.routers.undo_redo import undo_operation, redo_operation


class TestUndoRedo:
    """Test undo/redo operations."""

    def test_undo_operation_is_async(self):
        """Verify undo_operation is async."""
        import inspect
        assert inspect.iscoroutinefunction(undo_operation)

    def test_redo_operation_is_async(self):
        """Verify redo_operation is async."""
        import inspect
        assert inspect.iscoroutinefunction(redo_operation)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
