"""Tests for dataset import/export."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import get_app_routes

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app


client = TestClient(app)


class TestDatasetRoutes:
    """Test dataset import/export routes."""

    def test_import_endpoint_exists(self):
        """Test that import endpoint exists."""
        response = client.post("/api/datasets/import/single", data={"project_id": 1})
        # Should fail auth, not 404
        assert response.status_code in [401, 422, 500]

    def test_import_endpoint_requires_project_id(self):
        """Test that import endpoint requires project_id in form data."""
        # Send request without project_id - should fail validation (after auth)
        response = client.post("/api/datasets/import/single", data={})
        # Should return 401 (auth) or 422 (validation error) - never 200
        assert response.status_code in [401, 422]
        # If validation error, verify it's about project_id
        if response.status_code == 422:
            assert "project_id" in response.text

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

        df = pd.DataFrame(
            {"name": ["Alice", "Bob"], "age": [25, 30], "score": [85.5, 92.0]}
        )

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

        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})

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

        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "active": [True, False, True],
                "created": ["2024-01-01", "2024-01-02", "2024-01-03"],
            }
        )

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
        response = client.post("/api/projects", json={"name": "Test Project"})
        assert response.status_code in [401, 422, 500]


class TestAuthRoutes:
    """Test authentication routes - check route exists."""

    def test_routes_exist(self):
        """Test auth routes are registered."""
        routes = get_app_routes(app)
        assert "/api/auth/register" in routes
        assert "/api/auth/login" in routes
        assert "/api/auth/me" in routes


class TestPreviewColumnNormalization:
    """Test that preview endpoint handles legacy string-format columns."""

    def test_normalize_columns_from_strings(self):
        from app.routers.datasets import _normalize_columns
        result = _normalize_columns(["age", "name", "city"])
        assert len(result) == 3
        assert all(isinstance(c, dict) for c in result)
        assert result[0] == {"name": "age", "dtype": "string"}
        assert result[1] == {"name": "name", "dtype": "string"}

    def test_normalize_columns_from_dicts(self):
        from app.routers.datasets import _normalize_columns
        input_cols = [{"name": "age", "dtype": "integer"}, {"name": "name", "dtype": "string"}]
        result = _normalize_columns(input_cols)
        assert result == input_cols

    def test_normalize_columns_empty(self):
        from app.routers.datasets import _normalize_columns
        assert _normalize_columns([]) == []
        assert _normalize_columns(None) == []


class TestMergeDatasets:
    """Test the merge-datasets endpoint."""

    @pytest.mark.asyncio
    async def test_merge_requires_two_datasets(self):
        from app.routers.datasets import merge_datasets
        from fastapi import HTTPException

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await merge_datasets(
                request={"project_id": "p1", "dataset_ids": ["d1"], "name": "Merged"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert exc_info.value.status_code == 400
        assert "At least 2" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_merge_requires_project_id(self):
        from app.routers.datasets import merge_datasets
        from fastapi import HTTPException

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await merge_datasets(
                request={"dataset_ids": ["d1", "d2"], "name": "Merged"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_merge_union_strategy(self):
        """Union keeps all columns from all datasets."""
        from app.routers.datasets import merge_datasets
        import pandas as pd

        ds1 = MagicMock()
        ds1.id = "d1"
        ds1.name = "Dataset 1"
        ds1.preview_data.data_json = {"data": [{"name": "Alice", "age": 30}]}
        ds1.data_json = {"data": [{"name": "Alice", "age": 30}]}
        ds1.columns = [{"name": "name", "dtype": "string"}, {"name": "age", "dtype": "integer"}]
        ds1.row_count = 1

        ds2 = MagicMock()
        ds2.id = "d2"
        ds2.name = "Dataset 2"
        ds2.preview_data.data_json = {"data": [{"name": "Bob", "city": "Paris"}]}
        ds2.data_json = {"data": [{"name": "Bob", "city": "Paris"}]}
        ds2.columns = [{"name": "name", "dtype": "string"}, {"name": "city", "dtype": "string"}]
        ds2.row_count = 1

        mock_project = MagicMock()
        mock_project.row_count = 0

        async def mock_execute(query):
            q_str = str(query)
            r = MagicMock()
            if "project" in q_str.lower() and "user" in q_str.lower():
                r.scalar_one_or_none.return_value = mock_project
            elif "dataset" in q_str.lower():
                # Return different datasets based on call order
                if not hasattr(mock_execute, '_call_count'):
                    mock_execute._call_count = 0
                mock_execute._call_count += 1
                if mock_execute._call_count <= 2:
                    r.scalar_one_or_none.return_value = ds1 if mock_execute._call_count == 1 else ds2
                else:
                    r.scalar_one_or_none.return_value = mock_project
            else:
                r.scalar_one_or_none.return_value = mock_project
            return r

        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        mock_session.refresh = AsyncMock()

        result = await merge_datasets(
            request={"project_id": "p1", "dataset_ids": ["d1", "d2"], "name": "Merged", "strategy": "union"},
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "success"
        assert result["row_count"] == 2
        assert result["column_count"] == 3  # name, age, city

    @pytest.mark.asyncio
    async def test_merge_intersection_strategy(self):
        """Intersection keeps only common columns."""
        from app.routers.datasets import merge_datasets

        ds1 = MagicMock()
        ds1.id = "d1"
        ds1.name = "DS1"
        ds1.preview_data.data_json = {"data": [{"name": "Alice", "age": 30}]}
        ds1.data_json = {"data": [{"name": "Alice", "age": 30}]}
        ds1.columns = [{"name": "name"}, {"name": "age"}]
        ds1.row_count = 1

        ds2 = MagicMock()
        ds2.id = "d2"
        ds2.name = "DS2"
        ds2.data_json = {"data": [{"name": "Bob", "age": 25}]}
        ds2.columns = [{"name": "name"}, {"name": "age"}]
        ds2.row_count = 1

        mock_project = MagicMock()
        mock_project.row_count = 0

        call_count = [0]

        async def mock_execute(query):
            q_str = str(query)
            r = MagicMock()
            if "project" in q_str.lower() and "user" in q_str.lower():
                r.scalar_one_or_none.return_value = mock_project
            elif "dataset" in q_str.lower():
                call_count[0] += 1
                r.scalar_one_or_none.return_value = ds1 if call_count[0] == 1 else ds2
            else:
                r.scalar_one_or_none.return_value = mock_project
            return r

        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        mock_session.refresh = AsyncMock()

        result = await merge_datasets(
            request={"project_id": "p1", "dataset_ids": ["d1", "d2"], "name": "Merged", "strategy": "intersection"},
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "success"
        assert result["column_count"] == 2  # only name, age

    @pytest.mark.asyncio
    async def test_merge_strict_returns_graceful_error(self):
        """Strict mode with mismatched columns returns failed status, not exception."""
        from app.routers.datasets import merge_datasets

        ds1 = MagicMock()
        ds1.id = "d1"
        ds1.name = "DS1"
        ds1.preview_data.data_json = {"data": [{"name": "Alice", "age": 30}]}
        ds1.data_json = {"data": [{"name": "Alice", "age": 30}]}
        ds1.columns = [{"name": "name"}, {"name": "age"}]
        ds1.row_count = 1

        ds2 = MagicMock()
        ds2.id = "d2"
        ds2.name = "DS2"
        ds2.preview_data.data_json = {"data": [{"name": "Bob", "city": "Paris"}]}
        ds2.data_json = {"data": [{"name": "Bob", "city": "Paris"}]}
        ds2.columns = [{"name": "name"}, {"name": "city"}]
        ds2.row_count = 1

        mock_project = MagicMock()
        mock_project.row_count = 0

        call_count = [0]

        async def mock_execute(query):
            q_str = str(query)
            r = MagicMock()
            if "project" in q_str.lower() and "user" in q_str.lower():
                r.scalar_one_or_none.return_value = mock_project
            elif "dataset" in q_str.lower():
                call_count[0] += 1
                r.scalar_one_or_none.return_value = ds1 if call_count[0] == 1 else ds2
            else:
                r.scalar_one_or_none.return_value = mock_project
            return r

        mock_session = AsyncMock()
        mock_session.execute = mock_execute

        result = await merge_datasets(
            request={"project_id": "p1", "dataset_ids": ["d1", "d2"], "name": "Merged", "strategy": "strict"},
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "failed"
        assert "Column mismatch" in result["message"]
        assert "missing" in result["message"].lower() or "extra" in result["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
