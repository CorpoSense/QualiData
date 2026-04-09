"""Tests for pivot table service and API endpoints."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import app from conftest (already patched)
from tests.conftest import app

from app.services.pivot_service import PivotService

client = TestClient(app)


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "category": ["A", "B", "A", "B", "C", "A", "B", "C", "A", "B", "A", "B", "C", "A", "B", "C", "A", "B", "C", "A", "B", "C", "A", "B", "C"],
        "status": ["active", "inactive", "active", "active", "inactive", "active", "inactive", "active", "active", "inactive", "active", "inactive", "active", "active", "inactive", "active", "inactive", "active", "active", "inactive", "active", "inactive", "active", "active", "inactive"],
        "region": ["North", "South", "North", "South", "East", "North", "South", "East", "North", "South", "North", "South", "East", "North", "South", "East", "North", "South", "East", "North", "South", "East", "North", "South", "East"],
        "price": [10.5, 20.3, 15.2, 25.1, 30.0, 12.5, 22.3, 35.0, 18.2, 28.1, 11.5, 21.3, 16.2, 26.1, 31.0, 13.5, 23.3, 36.0, 19.2, 29.1, 14.5, 24.3, 17.2, 27.1, 32.0],
        "quantity": [100, 200, 150, 250, 300, 120, 220, 350, 180, 280, 110, 210, 160, 260, 310, 130, 230, 360, 190, 290, 140, 240, 170, 270, 320],
        "value": [1050, 4060, 2280, 6275, 9000, 1500, 4906, 12250, 3276, 7868, 1150, 4260, 2380, 6475, 9200, 1600, 5106, 12650, 3476, 8068, 1250, 4460, 2480, 6675, 9400],
    })


@pytest.fixture
def df_with_nulls():
    """Create a DataFrame with null values for testing."""
    return pd.DataFrame({
        "category": ["A", "B", None, "B", "C", "A", None, "C", "A", "B"],
        "status": ["active", "inactive", "active", None, "inactive", "active", "inactive", "active", None, "inactive"],
        "price": [10.5, None, 15.2, 25.1, 30.0, 12.5, 22.3, None, 18.2, 28.1],
        "quantity": [100, 200, None, 250, 300, 120, 220, 350, None, 280],
    })


class TestPivotService:
    """Tests for PivotService class."""

    def test_detect_column_type_categorical(self, sample_df):
        """Test categorical column detection."""
        service = PivotService(sample_df)
        assert service.detect_column_type("category") == "categorical"
        assert service.detect_column_type("status") == "categorical"
        assert service.detect_column_type("region") == "categorical"

    def test_detect_column_type_continuous(self, sample_df):
        """Test continuous column detection."""
        service = PivotService(sample_df)
        assert service.detect_column_type("price") == "continuous"
        assert service.detect_column_type("quantity") == "continuous"
        assert service.detect_column_type("value") == "continuous"

    def test_detect_column_type_with_custom_threshold(self, sample_df):
        """Test categorical detection with custom unique threshold."""
        service = PivotService(sample_df)
        # With threshold 2, price column (25 unique values) is continuous
        assert service.detect_column_type("price", unique_threshold=2) == "continuous"
        # With threshold 100, all columns are categorical
        assert service.detect_column_type("price", unique_threshold=100) == "categorical"

    def test_get_column_types(self, sample_df):
        """Test getting all column types."""
        service = PivotService(sample_df)
        types = service.get_column_types()
        assert "categorical" in types
        assert "continuous" in types
        assert "datetime" in types
        assert "category" in types["categorical"]
        assert "price" in types["continuous"]

    def test_get_column_statistics(self, sample_df):
        """Test getting column statistics."""
        service = PivotService(sample_df)
        stats = service.get_column_statistics("price")
        assert stats["name"] == "price"
        assert stats["dtype"] == "float64"
        assert stats["total_rows"] == 25
        assert stats["null_count"] == 0
        assert "min" in stats
        assert "max" in stats
        assert "mean" in stats

    def test_get_column_statistics_with_nulls(self, df_with_nulls):
        """Test column statistics with null values."""
        service = PivotService(df_with_nulls)
        stats = service.get_column_statistics("price")
        assert stats["null_count"] == 2
        assert stats["null_percent"] == 20.0

    def test_create_pivot_categorical(self, sample_df):
        """Test pivot creation with categorical columns."""
        service = PivotService(sample_df)
        result = service.create_pivot(
            index_columns=["category"],
            column_columns=["status"],
            value_column="value",
            aggfunc="sum",
        )
        assert "pivot" in result
        assert "columns" in result
        assert "summary" in result
        assert result["summary"]["aggregation"] == "sum"
        assert result["summary"]["value_column"] == "value"

    def test_create_pivot_continuous_binning(self, sample_df):
        """Test pivot creation with continuous column binning."""
        service = PivotService(sample_df)
        result = service.create_pivot(
            index_columns=["price"],
            column_columns=["category"],
            value_column="quantity",
            aggfunc="sum",
            bin_continuous=True,
            bins=3,
        )
        assert "pivot" in result
        assert "price" in result["summary"]["binned_columns"]

    def test_create_pivot_continuous_no_binning(self, sample_df):
        """Test pivot creation without binning continuous columns."""
        service = PivotService(sample_df)
        result = service.create_pivot(
            index_columns=["price"],
            column_columns=["category"],
            value_column="quantity",
            aggfunc="sum",
            bin_continuous=False,
        )
        assert "pivot" in result
        assert len(result["summary"]["binned_columns"]) == 0

    def test_create_pivot_with_nulls_excluded(self, df_with_nulls):
        """Test pivot creation excluding null values."""
        service = PivotService(df_with_nulls)
        result = service.create_pivot(
            index_columns=["category"],
            column_columns=["status"],
            value_column="price",
            aggfunc="sum",
            include_nulls=False,
        )
        assert "pivot" in result
        assert result["summary"]["include_nulls"] is False

    def test_create_pivot_with_nulls_included(self, df_with_nulls):
        """Test pivot creation including null values."""
        service = PivotService(df_with_nulls)
        result = service.create_pivot(
            index_columns=["category"],
            column_columns=["status"],
            value_column="price",
            aggfunc="sum",
            include_nulls=True,
        )
        assert "pivot" in result
        assert result["summary"]["include_nulls"] is True

    def test_create_pivot_all_aggregations(self, sample_df):
        """Test all aggregation functions."""
        service = PivotService(sample_df)
        aggfuncs = ["count", "sum", "mean", "median", "min", "max", "std"]
        
        for aggfunc in aggfuncs:
            result = service.create_pivot(
                index_columns=["category"],
                column_columns=["status"],
                value_column="value",
                aggfunc=aggfunc,
            )
            assert result["summary"]["aggregation"] == aggfunc

    def test_create_pivot_invalid_column(self, sample_df):
        """Test pivot creation with invalid column."""
        service = PivotService(sample_df)
        with pytest.raises(ValueError, match="not found"):
            service.create_pivot(
                index_columns=["nonexistent"],
                column_columns=["status"],
                value_column="value",
                aggfunc="sum",
            )

    def test_create_pivot_invalid_aggfunc(self, sample_df):
        """Test pivot creation with invalid aggregation function."""
        service = PivotService(sample_df)
        with pytest.raises(ValueError, match="Invalid aggfunc"):
            service.create_pivot(
                index_columns=["category"],
                column_columns=["status"],
                value_column="value",
                aggfunc="invalid",
            )

    def test_create_pivot_non_numeric_for_sum(self, sample_df):
        """Test pivot creation with non-numeric column for sum aggregation."""
        service = PivotService(sample_df)
        with pytest.raises(ValueError, match="must be numeric"):
            service.create_pivot(
                index_columns=["category"],
                column_columns=["status"],
                value_column="status",  # Non-numeric
                aggfunc="sum",
            )

    def test_value_counts_single_column(self, sample_df):
        """Test value counts for single column."""
        service = PivotService(sample_df)
        result = service.value_counts_analysis(columns=["category"])
        assert result["columns"] == ["category"]
        assert result["normalize"] is False
        assert len(result["data"]) > 0

    def test_value_counts_multiple_columns(self, sample_df):
        """Test value counts for multiple columns."""
        service = PivotService(sample_df)
        result = service.value_counts_analysis(columns=["category", "status"])
        assert result["columns"] == ["category", "status"]
        assert len(result["data"]) > 0

    def test_value_counts_normalized(self, sample_df):
        """Test normalized value counts."""
        service = PivotService(sample_df)
        result = service.value_counts_analysis(columns=["category"], normalize=True)
        assert result["normalize"] is True
        # Sum of proportions should be approximately 1
        total = sum(item["count"] for item in result["data"])
        assert abs(total - 1.0) < 0.01

    def test_value_counts_invalid_column(self, sample_df):
        """Test value counts with invalid column."""
        service = PivotService(sample_df)
        with pytest.raises(ValueError, match="not found"):
            service.value_counts_analysis(columns=["nonexistent"])

    def test_binning_equal_width(self, sample_df):
        """Test equal width binning strategy."""
        service = PivotService(sample_df)
        result = service.create_pivot(
            index_columns=["price"],
            column_columns=["category"],
            value_column="quantity",
            aggfunc="sum",
            binning_strategy="equal_width",
            bins=3,
        )
        assert result["summary"]["binning_strategy"] == "equal_width"

    def test_binning_equal_freq(self, sample_df):
        """Test equal frequency binning strategy."""
        service = PivotService(sample_df)
        result = service.create_pivot(
            index_columns=["price"],
            column_columns=["category"],
            value_column="quantity",
            aggfunc="sum",
            binning_strategy="equal_freq",
            bins=3,
        )
        assert result["summary"]["binning_strategy"] == "equal_freq"

    def test_pivot_summary_metadata(self, sample_df):
        """Test pivot summary contains all metadata."""
        service = PivotService(sample_df)
        result = service.create_pivot(
            index_columns=["category"],
            column_columns=["status"],
            value_column="value",
            aggfunc="sum",
            bin_continuous=True,
            bins=5,
            binning_strategy="equal_width",
            include_nulls=False,
            unique_threshold=25,
        )
        summary = result["summary"]
        assert summary["total_rows"] > 0
        assert summary["total_columns"] > 0
        assert summary["aggregation"] == "sum"
        assert summary["value_column"] == "value"
        assert summary["index_columns"] == ["category"]
        assert summary["column_columns"] == ["status"]
        # binning_strategy is None when no continuous columns are binned
        assert summary["binning_strategy"] is None
        # bins is None when no continuous columns are binned
        assert summary["bins"] is None
        assert summary["include_nulls"] is False
        assert summary["unique_threshold"] == 25
        assert "column_types" in summary


class TestPivotAPI:
    """Tests for pivot API endpoints."""

    def test_create_pivot_endpoint(self):
        """Test POST /api/datasets/{dataset_id}/pivot endpoint."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.post(
                "/api/datasets/test-dataset-id/pivot",
                json={
                    "index_columns": ["category"],
                    "column_columns": ["status"],
                    "value_column": "value",
                    "aggfunc": "sum",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "pivot" in data
            assert "columns" in data
            assert "summary" in data
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_pivot_with_binning(self):
        """Test pivot creation with binning options."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                # Create more rows with varied price values for binning to work
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                    {"category": "A", "status": "active", "price": 12.5, "quantity": 120, "value": 1500},
                    {"category": "B", "status": "inactive", "price": 22.3, "quantity": 220, "value": 4906},
                    {"category": "A", "status": "active", "price": 18.2, "quantity": 180, "value": 3276},
                    {"category": "B", "status": "active", "price": 28.1, "quantity": 280, "value": 7868},
                    {"category": "C", "status": "inactive", "price": 35.0, "quantity": 350, "value": 12250},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.post(
                "/api/datasets/test-dataset-id/pivot",
                json={
                    "index_columns": ["price"],
                    "column_columns": ["category"],
                    "value_column": "quantity",
                    "aggfunc": "sum",
                    "bin_continuous": True,
                    "bins": 5,
                    "binning_strategy": "equal_width",
                    "unique_threshold": 5,  # Lower threshold to detect price as continuous
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["summary"]["binned_columns"] == ["price"]
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_pivot_invalid_dataset(self):
        """Test pivot creation with invalid dataset ID."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return None for invalid dataset
                result.scalar_one_or_none.return_value = None
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.post(
                "/api/datasets/invalid-id/pivot",
                json={
                    "index_columns": ["category"],
                    "column_columns": ["status"],
                    "value_column": "value",
                    "aggfunc": "sum",
                },
            )
            assert response.status_code == 404
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_get_pivot_columns(self):
        """Test GET /api/datasets/{dataset_id}/pivot/columns endpoint."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.get(
                "/api/datasets/test-dataset-id/pivot/columns",
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "categorical" in data
            assert "continuous" in data
            assert "datetime" in data
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_get_pivot_columns_with_threshold(self):
        """Test column types with custom unique threshold."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.get(
                "/api/datasets/test-dataset-id/pivot/columns?unique_threshold=10",
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_value_counts_endpoint(self):
        """Test POST /api/datasets/{dataset_id}/pivot/value-counts endpoint."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.post(
                "/api/datasets/test-dataset-id/pivot/value-counts",
                json={
                    "columns": ["category"],
                    "normalize": False,
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["columns"] == ["category"]
            assert "data" in data
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_value_counts_normalized(self):
        """Test normalized value counts."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies
        from app.routers.auth import get_current_active_user
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.post(
                "/api/datasets/test-dataset-id/pivot/value-counts",
                json={
                    "columns": ["category"],
                    "normalize": True,
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["normalize"] is True
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_pivot_unauthorized(self):
        """Test pivot endpoint without authentication."""
        # Create mock session
        mock_session = MagicMock()
        
        # Mock the execute method to return appropriate results
        async def mock_execute(query):
            result = MagicMock()
            query_str = str(query)
            if "dataset" in query_str.lower():
                # Return a mock dataset with columns matching test requests
                mock_dataset = MagicMock()
                mock_dataset.id = "test-dataset-id"
                mock_dataset.project_id = "test-project-id"
                mock_dataset.row_count = 1000
                mock_dataset.data_json = {"data": [
                    {"category": "A", "status": "active", "price": 10.5, "quantity": 100, "value": 1050},
                    {"category": "B", "status": "inactive", "price": 20.3, "quantity": 200, "value": 4060},
                    {"category": "A", "status": "active", "price": 15.2, "quantity": 150, "value": 2280},
                    {"category": "B", "status": "active", "price": 25.1, "quantity": 250, "value": 6275},
                    {"category": "C", "status": "inactive", "price": 30.0, "quantity": 300, "value": 9000},
                ]}
                mock_dataset.data_json = {"data": mock_dataset.data_json["data"]}
                mock_dataset.columns = [
                    {"name": "category", "dtype": "str"},
                    {"name": "status", "dtype": "str"},
                    {"name": "price", "dtype": "float"},
                    {"name": "quantity", "dtype": "int"},
                    {"name": "value", "dtype": "int"},
                ]
                result.scalar_one_or_none.return_value = mock_dataset
            elif "project" in query_str.lower():
                # Return a mock project
                mock_project = MagicMock()
                mock_project.id = "test-project-id"
                mock_project.user_id = "test-user-id"
                result.scalar_one_or_none.return_value = mock_project
            return result
        
        mock_session.execute = mock_execute
        
        # Override dependencies - only session, not auth
        from app.routers.datasets import get_async_session
        
        app.dependency_overrides[get_async_session] = lambda: mock_session
        
        try:
            response = client.post(
                "/api/datasets/test-dataset-id/pivot",
                json={
                    "index_columns": ["category"],
                    "column_columns": ["status"],
                    "value_column": "value",
                    "aggfunc": "sum",
                },
            )
            assert response.status_code == 401
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
