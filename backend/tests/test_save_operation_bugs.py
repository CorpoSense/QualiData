"""Tests to catch common bugs in operations."""

import pytest
from unittest.mock import patch


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.routers import operations, operations_extra


class TestSaveOperationBugs:
    """Tests to catch common save_operation bugs."""

    def test_all_save_operations_are_async(self):
        """Verify all save_operation functions are async."""
        import inspect
        
        # Check operations.py
        assert inspect.iscoroutinefunction(operations.save_operation), \
            "operations.save_operation should be async"
        
        # Check operations_extra.py  
        assert inspect.iscoroutinefunction(operations_extra.save_operation), \
            "operations_extra.save_operation should be async"

    def test_all_save_operation_calls_have_await(self):
        """Verify all calls to save_operation have await."""
        import inspect
        import re
        
        # Check operations.py
        ops_source = inspect.getsource(operations)
        # Use regex to find actual function calls (not the definition)
        # Look for save_operation( that's not part of "def save_operation(" or "async def save_operation("
        ops_calls = len(re.findall(r'(?<!def )(?<!async def )save_operation\s*\(', ops_source))
        ops_awaits = len(re.findall(r'await\s+save_operation\s*\(', ops_source))
        assert ops_calls == ops_awaits, \
            f"operations.py: {ops_calls} save_operation calls but only {ops_awaits} with await"
        
        # Check operations_extra.py
        extra_source = inspect.getsource(operations_extra)
        extra_calls = len(re.findall(r'(?<!def )(?<!async def )save_operation\s*\(', extra_source))
        extra_awaits = len(re.findall(r'await\s+save_operation\s*\(', extra_source))
        assert extra_calls == extra_awaits, \
            f"operations_extra.py: {extra_calls} save_operation calls but only {extra_awaits} with await"

    def test_save_operation_uses_dataset_id_from_dataset_object(self):
        """Verify save_operation uses dataset.id (UUID), not string dataset_id."""
        import inspect
        from app.utils.operations import save_operation
        
        source = inspect.getsource(save_operation)
        
        # Should use dataset.id, not dataset_id parameter
        assert 'dataset_id=dataset.id' in source, \
            "save_operation should use dataset.id (UUID)"

    def test_only_one_save_operation_implementation(self):
        """Verify there's only ONE save_operation implementation in utils."""
        # Check that save_operation exists in utils
        from app.utils import operations as utils_ops
        
        assert hasattr(utils_ops, 'save_operation'), "save_operation should be in utils"
        
        # Check that routers don't define their own
        import inspect
        from app.routers import operations, operations_extra
        
        ops_source = inspect.getsource(operations)
        extra_source = inspect.getsource(operations_extra)
        
        # They should import, not define
        assert 'from app.utils.operations import save_operation' in ops_source, \
            "operations.py should import save_operation from utils"
        assert 'from app.utils.operations import save_operation' in extra_source, \
            "operations_extra.py should import save_operation from utils"


class TestDatasetIdUsage:
    """Tests to verify dataset_id is used correctly."""

    def test_history_queries_use_cast_for_uuid_comparison(self):
        """Verify UUID comparisons use cast to avoid type errors."""
        import inspect
        from app.routers import comparison, undo_redo, operations
        
        # All files that query by dataset_id should use cast
        files = [comparison, undo_redo, operations]
        
        for module in files:
            source = inspect.getsource(module)
            # If the file uses dataset_id in queries, it should use cast
            if 'OperationHistory.dataset_id' in source:
                assert 'cast(OperationHistory.dataset_id' in source or \
                       'String)' in source, \
                    f"{module.__name__} should cast dataset_id for UUID comparison"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
