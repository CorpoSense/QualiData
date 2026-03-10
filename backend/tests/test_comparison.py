"""Tests for comparison API endpoints."""

from unittest.mock import patch

import pytest


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.routers.comparison import compare_operation, ComparisonResponse


class TestComparisonEndpoint:
    """Test comparison endpoint."""

    def test_compare_operation_accepts_string_id(self):
        """Verify compare_operation accepts string UUID for operation_id."""
        import inspect
        
        # Get function signature
        sig = inspect.signature(compare_operation)
        params = sig.parameters
        
        # operation_id should be string (UUID), not int
        assert 'operation_id' in params
        assert params['operation_id'].annotation == str, \
            f"operation_id should be str (UUID), got {params['operation_id'].annotation}"

    def test_compare_endpoint_route_is_correct(self):
        """Verify the route uses correct path parameters."""
        from app.routers.comparison import router
        
        # Find the compare route
        routes = [r for r in router.routes if hasattr(r, 'path') and 'compare' in r.path]
        assert len(routes) > 0, "No compare route found"
        
        route = routes[0]
        # The path should have {operation_id} as a parameter
        assert '{operation_id}' in route.path


class TestOperationHistoryId:
    """Test that operation history uses string IDs."""

    def test_operation_history_id_is_string(self):
        """Verify OperationHistory uses string (UUID) for id."""
        from app.db.models.project import OperationHistory
        
        # Check the id column type
        id_column = OperationHistory.__mapper__.columns['id']
        assert id_column.type.python_type == str, \
            f"OperationHistory.id should be str (UUID), got {id_column.type.python_type}"


class TestComparisonResponse:
    """Test ComparisonResponse model."""

    def test_operation_id_is_string_in_response(self):
        """Verify ComparisonResponse uses string operation_id, not int."""
        # Check that the model has operation_id as str
        assert ComparisonResponse.model_fields['operation_id'].annotation == str, \
            "ComparisonResponse.operation_id should be str"

    def test_comparison_response_validation_with_uuid(self):
        """Test that ComparisonResponse can validate with UUID string."""
        # Create a valid response with UUID operation_id
        response = ComparisonResponse(
            status="success",
            operation_id="6de25b0f-57e8-4306-9e94-870225303a58",
            operation_type="string_operations",
            before_columns=[],
            after_columns=[],
            changes_summary={}
        )
        
        # Verify it was created successfully
        assert response.status == "success"
        assert response.operation_id == "6de25b0f-57e8-4306-9e94-870225303a58"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
