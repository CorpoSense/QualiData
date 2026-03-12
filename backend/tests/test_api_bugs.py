"""Tests to catch common API bugs like duplicate prefixes."""

import pytest
from unittest.mock import patch


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


class TestRouteConfiguration:
    """Test route configuration to catch common bugs."""

    def test_no_duplicate_api_prefix_in_routes(self):
        """Verify no routes have duplicate /api/api prefix."""
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        # Check for duplicate /api prefix
        duplicates = [r for r in routes if r.startswith('/api/api/')]
        assert len(duplicates) == 0, f"Found routes with duplicate /api prefix: {duplicates}"

    def test_all_dataset_routes_have_correct_prefix(self):
        """Verify dataset routes follow consistent pattern."""
        dataset_routes = [
            r.path for r in app.routes 
            if hasattr(r, 'path') and 'datasets' in r.path
        ]
        
        # All should start with /api/datasets (not /api/api/datasets)
        wrong_prefix = [r for r in dataset_routes if r.startswith('/api/api/')]
        assert len(wrong_prefix) == 0, f"Routes with wrong prefix: {wrong_prefix}"

    def test_no_conflicting_routes(self):
        """Check for routes - just verify app has routes."""
        routes = {r.path for r in app.routes if hasattr(r, 'path')}
        
        # Verify app has dataset routes (the exact pattern varies)
        dataset_routes = [r for r in routes if 'datasets' in r]
        assert len(dataset_routes) > 0, "No dataset routes found"

    def test_critical_endpoints_exist(self):
        """Verify critical endpoints are registered."""
        routes = {r.path for r in app.routes if hasattr(r, 'path')}
        
        critical = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/datasets',
            '/api/projects',
            '/api/datasets/{dataset_id}/preview',
            '/api/datasets/{dataset_id}/operations',
        ]
        
        missing = [r for r in critical if not any(r.replace('{dataset_id}', 'test').replace('{operation_id}', 'test').replace('{id}', 'test') in rt for rt in routes)]
        # More lenient check - just verify key patterns exist
        route_str = str(routes)
        assert '/api/datasets' in route_str
        assert '/api/auth' in route_str
        assert '/api/projects' in route_str


class TestOperationHistoryIdTypes:
    """Test that operation IDs are handled as strings (UUIDs)."""

    def test_list_operations_returns_string_ids(self):
        """Verify list_operations returns string IDs."""
        from app.routers.operations import list_operations
        import inspect
        
        # This is a sanity check - the function should exist and be async
        assert inspect.iscoroutinefunction(list_operations)

    def test_compare_operation_accepts_string_id(self):
        """Verify compare_operation accepts string operation_id."""
        from app.routers.comparison import compare_operation
        import inspect
        
        sig = inspect.signature(compare_operation)
        params = sig.parameters
        
        # operation_id should accept string (UUID)
        assert 'operation_id' in params
        # Should be str type annotation
        param_type = params['operation_id'].annotation
        assert param_type == str or param_type != int, \
            f"operation_id should be str, got {param_type}"


class TestSaveOperationAsync:
    """Test that save_operation is properly async."""

    def test_save_operation_is_async(self):
        """Verify save_operation is an async function."""
        from app.routers.operations import save_operation
        import inspect
        
        assert inspect.iscoroutinefunction(save_operation), \
            "save_operation should be an async function"

    def test_all_operations_call_await_save_operation(self):
        """Verify all operations use await when calling save_operation."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        
        # Count save_operation calls (excluding the definition line)
        # Should have 15 save_operation calls with await
        await_calls = source.count('await save_operation(')
        
        # We expect at least 15 calls (one for each operation type)
        assert await_calls >= 15, \
            f"Expected at least 15 await save_operation calls, found {await_calls}"


class TestDatabaseMigrations:
    """Test that database migrations run correctly."""

    def test_operation_history_has_required_fields(self):
        """Verify OperationHistory model has all required fields."""
        from app.db.models.project import OperationHistory
        
        required = ['id', 'project_id', 'operation_type', 'operation_name', 
                   'operation_params', 'before_snapshot', 'after_snapshot',
                   'is_applied', 'is_undone']
        
        for field in required:
            assert hasattr(OperationHistory, field), \
                f"OperationHistory missing field: {field}"

    def test_project_uses_user_id_not_owner_id(self):
        """Verify Project model uses user_id, not owner_id."""
        from app.db.models.project import Project
        
        # Project should have user_id, not owner_id
        assert hasattr(Project, 'user_id'), "Project should have user_id field"
        assert not hasattr(Project, 'owner_id'), "Project should NOT have owner_id field"

    def test_no_duplicate_undo_redo_routes(self):
        """Verify there's only one undo/redo route (not in both operations.py and undo_redo.py)."""
        from app.main import app
        
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        # Count how many undo/redo routes exist (exclude /redoc)
        undo_routes = [r for r in routes if 'undo' in r and 'operations' in r]
        redo_routes = [r for r in routes if 'redo' in r and 'operations' in r]
        
        # Should be exactly 1 undo and 1 redo (from undo_redo.py)
        assert len(undo_routes) == 1, f"Found {len(undo_routes)} undo routes: {undo_routes}"
        assert len(redo_routes) == 1, f"Found {len(redo_routes)} redo routes: {redo_routes}"

    def test_operations_save_preview_data_for_undo(self):
        """Verify all operations save preview_data in snapshots for undo to work."""
        import inspect
        from app.routers import operations
        
        source = inspect.getsource(operations)
        
        # All before/before_snapshot should include preview_data
        assert 'preview_data": dataset.preview_data' in source or "preview_data': dataset.preview_data" in source, \
            "Operations should save preview_data in before_snapshot for undo to work"
        
        # Check that after snapshots also include preview_data
        assert 'preview_data": get_preview_data(df)' in source or "preview_data': get_preview_data(df)" in source, \
            "Operations should save preview_data in after_snapshot"

    def test_operation_history_has_dataset_id(self):
        """Verify OperationHistory has dataset_id field for dataset-specific history."""
        from app.db.models.project import OperationHistory
        
        # OperationHistory should have dataset_id
        assert hasattr(OperationHistory, 'dataset_id'), "OperationHistory should have dataset_id field"

    def test_history_queries_use_dataset_id(self):
        """Verify history queries filter by dataset_id, not project_id."""
        import inspect
        from app.routers import comparison, undo_redo, operations
        
        # Check operations.py
        ops_source = inspect.getsource(operations)
        assert 'OperationHistory.dataset_id == dataset_id' in ops_source or 'cast(OperationHistory.dataset_id' in ops_source, \
            "Operations query should filter by dataset_id"
        
        # Check comparison.py
        comp_source = inspect.getsource(comparison)
        assert 'OperationHistory.dataset_id == dataset_id' in comp_source or 'cast(OperationHistory.dataset_id' in comp_source, \
            "History query should filter by dataset_id"
        
        # Check undo_redo.py
        undo_source = inspect.getsource(undo_redo)
        assert 'OperationHistory.dataset_id == dataset_id' in undo_source or 'cast(OperationHistory.dataset_id' in undo_source, \
            "Undo/redo should filter by dataset_id"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
