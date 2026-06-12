"""Tests for the chart-data endpoint and helper functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app

from app.routers.datasets import (
    _apply_agg,
    _apply_chart_filters,
    _compute_chart_aggregation,
    _compute_chart_bubble,
    _compute_chart_histogram,
    _compute_chart_scatter,
    ChartDataRequest,
)


client = TestClient(app)


class TestApplyAgg:
    """Test the _apply_agg helper function."""

    def test_sum(self):
        assert _apply_agg([1, 2, 3, 4], "sum") == 10

    def test_avg(self):
        assert _apply_agg([1, 2, 3, 4], "avg") == 2.5

    def test_count(self):
        assert _apply_agg([1, 2, 3, 4], "count") == 4

    def test_min(self):
        assert _apply_agg([5, 2, 8, 1], "min") == 1

    def test_max(self):
        assert _apply_agg([5, 2, 8, 1], "max") == 8

    def test_empty_returns_zero(self):
        assert _apply_agg([], "sum") == 0
        assert _apply_agg([], "avg") == 0
        assert _apply_agg([], "count") == 0

    def test_unknown_method_defaults_to_sum(self):
        assert _apply_agg([1, 2, 3], "unknown") == 6


class TestApplyChartFilters:
    """Test the _apply_chart_filters helper function."""

    def test_no_filters_returns_all(self):
        data = [{"city": "NYC"}, {"city": "LA"}]
        result = _apply_chart_filters(data, None)
        assert len(result) == 2

    def test_empty_filters_returns_all(self):
        data = [{"city": "NYC"}, {"city": "LA"}]
        result = _apply_chart_filters(data, {})
        assert len(result) == 2

    def test_substring_filter(self):
        data = [
            {"city": "New York"},
            {"city": "Los Angeles"},
            {"city": "New Orleans"},
        ]
        result = _apply_chart_filters(data, {"city": "new"})
        assert len(result) == 2  # New York, New Orleans

    def test_selected_values_filter(self):
        data = [
            {"city": "NYC", "revenue": 100},
            {"city": "LA", "revenue": 200},
            {"city": "Chicago", "revenue": 300},
        ]
        result = _apply_chart_filters(data, {"city": {"selected_values": ["NYC", "LA"]}})
        assert len(result) == 2

    def test_selected_values_with_null(self):
        data = [
            {"city": "NYC"},
            {"city": None},
            {"city": "LA"},
        ]
        result = _apply_chart_filters(data, {"city": {"selected_values": [None, "NYC"]}})
        assert len(result) == 2

    def test_multiple_filters_are_and_combined(self):
        data = [
            {"city": "NYC", "category": "A"},
            {"city": "NYC", "category": "B"},
            {"city": "LA", "category": "A"},
        ]
        result = _apply_chart_filters(data, {
            "city": {"selected_values": ["NYC"]},
            "category": {"selected_values": ["A"]},
        })
        assert len(result) == 1
        assert result[0]["city"] == "NYC"
        assert result[0]["category"] == "A"


class TestComputeChartAggregation:
    """Test the _compute_chart_aggregation helper function."""

    sample_data = [
        {"city": "NYC", "revenue": 100, "category": "A"},
        {"city": "NYC", "revenue": 200, "category": "B"},
        {"city": "LA", "revenue": 150, "category": "A"},
        {"city": "LA", "revenue": 50, "category": "B"},
        {"city": "Chicago", "revenue": 300, "category": "A"},
    ]

    def test_empty_data(self):
        result = _compute_chart_aggregation([], "city", "revenue", "sum")
        assert result["labels"] == []
        assert result["datasets"][0]["data"] == []

    def test_empty_x_column(self):
        result = _compute_chart_aggregation(self.sample_data, "", "revenue", "sum")
        assert result["labels"] == []

    def test_sum_aggregation(self):
        result = _compute_chart_aggregation(self.sample_data, "city", "revenue", "sum")
        labels = result["labels"]
        nyc_idx = labels.index("NYC")
        la_idx = labels.index("LA")
        chi_idx = labels.index("Chicago")
        assert result["datasets"][0]["data"][nyc_idx] == 300  # 100 + 200
        assert result["datasets"][0]["data"][la_idx] == 200  # 150 + 50
        assert result["datasets"][0]["data"][chi_idx] == 300

    def test_avg_aggregation(self):
        result = _compute_chart_aggregation(self.sample_data, "city", "revenue", "avg")
        nyc_idx = result["labels"].index("NYC")
        assert result["datasets"][0]["data"][nyc_idx] == 150  # (100+200)/2

    def test_count_aggregation(self):
        result = _compute_chart_aggregation(self.sample_data, "city", "revenue", "count")
        nyc_idx = result["labels"].index("NYC")
        assert result["datasets"][0]["data"][nyc_idx] == 2

    def test_count_without_y_column(self):
        result = _compute_chart_aggregation(self.sample_data, "city", "", "count")
        nyc_idx = result["labels"].index("NYC")
        assert result["datasets"][0]["data"][nyc_idx] == 2

    def test_grouped_aggregation(self):
        result = _compute_chart_aggregation(
            self.sample_data, "city", "revenue", "sum", "category"
        )
        assert len(result["datasets"]) == 2  # A and B
        cat_a = next(ds for ds in result["datasets"] if ds["label"] == "A")
        cat_b = next(ds for ds in result["datasets"] if ds["label"] == "B")
        assert cat_a is not None
        assert cat_b is not None

    def test_null_handling_exclude(self):
        data = [
            {"city": "NYC", "revenue": 100},
            {"city": "NYC", "revenue": None},
            {"city": "LA", "revenue": 200},
        ]
        result = _compute_chart_aggregation(data, "city", "revenue", "sum", null_handling="exclude")
        nyc_idx = result["labels"].index("NYC")
        assert result["datasets"][0]["data"][nyc_idx] == 100

    def test_null_handling_zero_includes_null_rows(self):
        data = [
            {"city": "NYC", "revenue": 100},
            {"city": "NYC", "revenue": None},
            {"city": "LA", "revenue": 200},
        ]
        result = _compute_chart_aggregation(data, "city", "revenue", "sum", null_handling="zero")
        nyc_idx = result["labels"].index("NYC")
        # None becomes 0.0 in "zero" mode, so NYC sum = 100 + 0 = 100
        assert result["datasets"][0]["data"][nyc_idx] == 100.0


class TestComputeChartHistogram:
    """Test the _compute_chart_histogram helper function."""

    def test_empty_data(self):
        result = _compute_chart_histogram([], "age")
        assert result["labels"] == []
        assert result["data"] == []

    def test_empty_column(self):
        result = _compute_chart_histogram([{"name": "Alice"}], "age")
        assert result["labels"] == []
        assert result["data"] == []

    def test_histogram_bins(self):
        data = [
            {"age": 10}, {"age": 15}, {"age": 20},
            {"age": 25}, {"age": 30},
        ]
        result = _compute_chart_histogram(data, "age", 5)
        assert len(result["labels"]) == 5
        assert len(result["data"]) == 5
        total = sum(result["data"])
        assert total == 5

    def test_single_value(self):
        data = [{"age": 25}, {"age": 25}, {"age": 25}]
        result = _compute_chart_histogram(data, "age", 5)
        total = sum(result["data"])
        assert total == 3

    def test_null_handling_exclude(self):
        data = [{"age": 10}, {"age": None}, {"age": 20}]
        result = _compute_chart_histogram(data, "age", 5, null_handling="exclude")
        total = sum(result["data"])
        assert total == 2


class TestComputeChartScatter:
    """Test the _compute_chart_scatter helper function."""

    def test_empty_data(self):
        result = _compute_chart_scatter([], "x", "y")
        assert result["datasets"][0]["data"] == []
        assert result["total_points"] == 0

    def test_scatter_points(self):
        data = [
            {"x": 1, "y": 10},
            {"x": 2, "y": 20},
            {"x": 3, "y": 30},
        ]
        result = _compute_chart_scatter(data, "x", "y")
        assert len(result["datasets"][0]["data"]) == 3
        assert result["total_points"] == 3
        assert result["displayed_points"] == 3

    def test_downsampling(self):
        # Create 100 data points, max 10
        data = [{"x": i, "y": i * 2} for i in range(100)]
        result = _compute_chart_scatter(data, "x", "y", max_points=10)
        assert result["displayed_points"] == 10
        assert result["total_points"] == 100
        assert result["warning"] is not None
        assert "downsampled" in result["warning"]

    def test_no_downsampling_when_under_limit(self):
        data = [{"x": i, "y": i * 2} for i in range(5)]
        result = _compute_chart_scatter(data, "x", "y", max_points=10)
        assert result["displayed_points"] == 5
        assert result["warning"] is None

    def test_null_handling_exclude(self):
        data = [
            {"x": 1, "y": 10},
            {"x": None, "y": 20},
            {"x": 3, "y": None},
            {"x": 4, "y": 40},
        ]
        result = _compute_chart_scatter(data, "x", "y", null_handling="exclude")
        assert len(result["datasets"][0]["data"]) == 2  # Only (1,10) and (4,40)


class TestComputeChartBubble:
    """Test the _compute_chart_bubble helper function."""

    def test_empty_data(self):
        result = _compute_chart_bubble([], "x", "y")
        assert result["datasets"][0]["data"] == []

    def test_empty_columns(self):
        result = _compute_chart_bubble([{"a": 1}], "", "y")
        assert result["datasets"][0]["data"] == []

    def test_bubble_points_without_size(self):
        data = [
            {"x": 1, "y": 10},
            {"x": 2, "y": 20},
            {"x": 3, "y": 30},
        ]
        result = _compute_chart_bubble(data, "x", "y")
        assert len(result["datasets"][0]["data"]) == 3
        assert result["total_points"] == 3
        # Without size column, radius should be default 8.0
        for pt in result["datasets"][0]["data"]:
            assert pt["r"] == 8.0
            assert "x" in pt
            assert "y" in pt

    def test_bubble_points_with_size(self):
        data = [
            {"x": 1, "y": 10, "pop": 100},
            {"x": 2, "y": 20, "pop": 200},
            {"x": 3, "y": 30, "pop": 300},
        ]
        result = _compute_chart_bubble(data, "x", "y", "pop")
        assert len(result["datasets"][0]["data"]) == 3
        # Radius should be normalized to 5-30 range
        radii = [pt["r"] for pt in result["datasets"][0]["data"]]
        assert min(radii) >= 5
        assert max(radii) <= 30

    def test_bubble_null_handling_exclude(self):
        data = [
            {"x": 1, "y": 10},
            {"x": None, "y": 20},
            {"x": 3, "y": None},
            {"x": 4, "y": 40},
        ]
        result = _compute_chart_bubble(data, "x", "y", null_handling="exclude")
        assert len(result["datasets"][0]["data"]) == 2

    def test_bubble_label_with_size(self):
        data = [{"x": 1, "y": 10, "pop": 100}]
        result = _compute_chart_bubble(data, "x", "y", "pop")
        assert "pop" in result["datasets"][0]["label"]

    def test_bubble_label_without_size(self):
        data = [{"x": 1, "y": 10}]
        result = _compute_chart_bubble(data, "x", "y")
        assert "x" in result["datasets"][0]["label"]


class TestChartDataEndpoint:
    """Test the chart-data API endpoint."""

    def test_endpoint_requires_auth(self):
        """Test that chart-data endpoint requires authentication."""
        response = client.post("/api/datasets/test-id/chart-data", json={
            "chart_type": "bar",
            "x_column": "city",
            "y_column": "revenue",
            "aggregation": "sum",
        })
        assert response.status_code in [401, 403, 422, 500]

    def test_chart_data_request_model(self):
        """Test ChartDataRequest model validation."""
        req = ChartDataRequest(
            chart_type="bar",
            x_column="city",
            y_column="revenue",
            aggregation="sum",
        )
        assert req.chart_type == "bar"
        assert req.x_column == "city"
        assert req.y_column == "revenue"
        assert req.aggregation == "sum"
        assert req.group_by == ""
        assert req.null_handling == "exclude"
        assert req.histogram_bins == 10
        assert req.filters is None
        assert req.scatter_max_points == 5000
        assert req.size_column == ""

    def test_chart_data_request_bubble(self):
        """Test ChartDataRequest model for bubble chart type."""
        req = ChartDataRequest(
            chart_type="bubble",
            x_column="gdp",
            y_column="life_expectancy",
            size_column="population",
        )
        assert req.chart_type == "bubble"
        assert req.size_column == "population"

    def test_chart_data_request_with_filters(self):
        """Test ChartDataRequest model with filters."""
        req = ChartDataRequest(
            chart_type="bar",
            x_column="city",
            y_column="revenue",
            aggregation="sum",
            filters={"country": {"selected_values": ["France"]}},
        )
        assert req.filters is not None
        assert "country" in req.filters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
