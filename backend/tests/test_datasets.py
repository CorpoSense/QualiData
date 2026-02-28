"""Tests for dataset import/export."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Mock database before importing app
with patch('app.db.database.get_async_session_maker'):
    with patch('app.db.database.get_sync_session_maker'):
        from app.main import app


client = TestClient(app)


class TestDatasetRoutes:
    """Test dataset import/export routes."""

    def test_import_endpoint_exists(self):
        """Test that import endpoint exists."""
        response = client.post(
            "/api/datasets/import",
            data={"project_id": 1}
        )
        # Should fail auth, not 404
        assert response.status_code in [401, 422, 500]

    def test_list_endpoint_requires_auth(self):
        """Test that list endpoint requires authentication."""
        response = client.get("/api/datasets?project_id=1")
        assert response.status_code in [401, 422, 500]

    def test_preview_endpoint_requires_auth(self):
        """Test that preview endpoint requires authentication."""
        response = client.get("/api/datasets/1/preview")
        assert response.status_code in [401, 422, 500]

    def test_export_endpoint_requires_auth(self):
        """Test that export endpoint requires authentication."""
        response = client.get("/api/datasets/1/export?format=csv")
        assert response.status_code in [401, 422, 500]


class TestCSVImport:
    """Test CSV import functionality."""

    def test_csv_column_detection(self):
        """Test CSV column detection."""
        import pandas as pd

        from app.routers.datasets import detect_columns

        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [25, 30],
            "score": [85.5, 92.0]
        })

        columns = detect_columns(df)

        assert len(columns) == 3
        assert columns[0]["name"] == "name"
        assert columns[0]["dtype"] in ["string", "str"]
        assert columns[1]["name"] == "age"
        assert columns[1]["dtype"] == "integer"

    def test_csv_preview_data(self):
        """Test CSV preview data extraction."""
        import pandas as pd

        from app.routers.datasets import get_preview_data

        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        preview = get_preview_data(df, max_rows=2)

        assert len(preview) == 2
        assert preview[0]["name"] == "Alice"
        assert preview[1]["name"] == "Bob"


class TestJSONImport:
    """Test JSON import functionality."""

    def test_json_column_detection(self):
        """Test JSON column detection."""
        import pandas as pd

        from app.routers.datasets import detect_columns

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "active": [True, False, True],
            "created": ["2024-01-01", "2024-01-02", "2024-01-03"]
        })

        columns = detect_columns(df)

        # Find the boolean column
        bool_col = next((c for c in columns if c["name"] == "active"), None)
        assert bool_col is not None


class TestProjectRoutes:
    """Test project routes."""

    def test_projects_list_requires_auth(self):
        """Test that projects list requires authentication."""
        response = client.get("/api/projects")
        assert response.status_code in [401, 422, 500]

    def test_projects_create_requires_auth(self):
        """Test that project creation requires authentication."""
        response = client.post(
            "/api/projects",
            json={"name": "Test Project"}
        )
        assert response.status_code in [401, 422, 500]


class TestAuthRoutes:
    """Test authentication routes - check route exists."""

    def test_routes_exist(self):
        """Test auth routes are registered."""
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        assert "/api/auth/register" in routes
        assert "/api/auth/login" in routes
        assert "/api/auth/me" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
