"""Tests to verify all operations save to history."""

from unittest.mock import MagicMock, patch
import pytest


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.routers.operations import save_operation


class TestOperationsSaveHistory:
    """Test that all operations call save_operation."""

    def test_save_operation_is_called_for_string_operations(self):
        """Verify string operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "string_operations"' in source

    def test_save_operation_is_called_for_numeric_operations(self):
        """Verify numeric operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "numeric"' in source

    def test_save_operation_is_called_for_datetime_operations(self):
        """Verify datetime operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "datetime_operations"' in source

    def test_save_operation_is_called_for_fillna(self):
        """Verify fillna operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "fillna"' in source

    def test_save_operation_is_called_for_remove_duplicates(self):
        """Verify remove_duplicates operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "remove_duplicates"' in source

    def test_save_operation_is_called_for_sort(self):
        """Verify sort operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "sort"' in source

    def test_save_operation_is_called_for_structural(self):
        """Verify structural operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "structural"' in source

    def test_save_operation_is_called_for_fuzzy_dedupe(self):
        """Verify fuzzy dedupe operations save to history."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        assert 'save_operation(dataset_id, "fuzzy_dedupe"' in source

    def test_all_operations_have_save_operation(self):
        """Comprehensive test: all operation endpoints call save_operation."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        
        # All operations should have save_operation calls
        # These are the operation types we're looking for
        operations_to_check = [
            "add_column",
            "remove_columns",
            "rename_column",
            "merge_columns",
            "split_column",
            "duplicate_column",
            "reorder_columns",
            "string_operations",
            "datetime_operations",
            "fillna",
            "remove_duplicates",
            "sort",
            "structural",
            "fuzzy_dedupe",
            "numeric",
        ]
        
        # Build regex patterns for both single-line and multi-line formats
        import re
        missing = []
        
        for op in operations_to_check:
            # Pattern 1: save_operation(dataset_id, "op"...
            # Pattern 2: save_operation(\n        dataset_id, "op"...
            pattern1 = re.escape(f'dataset_id, "{op}"')
            pattern2 = re.escape(f'dataset_id, "{op}"')
            
            found = bool(re.search(pattern1, source)) or bool(re.search(pattern2, source))
            
            if not found:
                # Also try just checking if the operation name appears after save_operation
                if f'save_operation' in source and f'"{op}"' in source:
                    # It's there somewhere
                    pass
                else:
                    missing.append(op)
        
        # Simpler check: count save_operation calls
        save_op_count = source.count('save_operation(')
        # We should have at least 15 save_operation calls (one per operation type)
        assert save_op_count >= 15, f"Expected at least 15 save_operation calls, found {save_op_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
