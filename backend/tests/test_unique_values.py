"""Tests for the GET /datasets/{id}/unique-values endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock

SAMPLE_DATA = [
    {"name": "Alice", "city": "Paris", "score": 85},
    {"name": "Bob", "city": "London", "score": 90},
    {"name": "Carol", "city": "Paris", "score": 85},
    {"name": "Dave", "city": "Berlin", "score": None},
    {"name": "Eve", "city": "London", "score": 90},
    {"name": "Frank", "city": None, "score": 75},
]

SAMPLE_DATA_WITH_NULLS = [
    {"name": "Alice", "city": "Paris"},
    {"name": "Bob", "city": None},
    {"name": "Carol", "city": "Paris"},
    {"name": "Dave", "city": None},
    {"name": "Eve", "city": "London"},
]


def _make_mock_dataset(data, columns=None):
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.data_json = {"data": data} if data else None
    ds.row_count = len(data) if data else 0
    if columns:
        ds.columns = columns
    elif data:
        ds.columns = [{"name": k, "dtype": "string"} for k in data[0].keys()]
    else:
        ds.columns = []
    return ds


async def _call_unique_values(dataset, column="city", limit=500):
    """Helper to call the unique-values endpoint."""
    from app.routers.datasets import get_unique_values

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = dataset

    async def mock_execute(*args, **kwargs):
        return mock_result

    mock_session.execute = AsyncMock(side_effect=mock_execute)

    return await get_unique_values(
        dataset_id="ds-1",
        column=column,
        limit=limit,
        current_user=MagicMock(id="user-1"),
        session=mock_session,
    )


class TestUniqueValuesEndpoint:
    @pytest.mark.asyncio
    async def test_basic_unique_values(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_unique_values(ds, column="city")
        assert result["column"] == "city"
        values = result["values"]
        # Paris(2), London(2), Berlin(1), null(1)
        value_map = {v["value"]: v["count"] for v in values}
        assert value_map.get("Paris") == 2
        assert value_map.get("London") == 2
        assert value_map.get("Berlin") == 1
        # null entry
        null_entry = [v for v in values if v["value"] is None]
        assert len(null_entry) == 1
        assert null_entry[0]["count"] == 1

    @pytest.mark.asyncio
    async def test_total_unique_count(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_unique_values(ds, column="city")
        # Paris, London, Berlin, null = 4 unique
        assert result["total_unique"] == 4

    @pytest.mark.asyncio
    async def test_sorted_by_count_descending(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_unique_values(ds, column="city")
        non_null_values = [v for v in result["values"] if v["value"] is not None]
        # Should be sorted by count descending: Paris(2), London(2), Berlin(1)
        # Paris and London both have count 2, so order between them may vary
        assert non_null_values[0]["count"] >= non_null_values[1]["count"]
        assert non_null_values[1]["count"] >= non_null_values[2]["count"]

    @pytest.mark.asyncio
    async def test_null_handling(self):
        ds = _make_mock_dataset(SAMPLE_DATA_WITH_NULLS)
        result = await _call_unique_values(ds, column="city")
        null_entry = [v for v in result["values"] if v["value"] is None]
        assert len(null_entry) == 1
        assert null_entry[0]["count"] == 2  # Bob and Dave have null city

    @pytest.mark.asyncio
    async def test_numeric_column_converted_to_string(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_unique_values(ds, column="score")
        values = result["values"]
        # 85(2), 90(2), 75(1), null(1) — all as strings
        # Note: pandas converts int columns with NaN to float64, so str(85.0) = "85.0"
        value_map = {v["value"]: v["count"] for v in values if v["value"] is not None}
        assert value_map.get("85.0") == 2
        assert value_map.get("90.0") == 2
        assert value_map.get("75.0") == 1

    @pytest.mark.asyncio
    async def test_limit_parameter(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_unique_values(ds, column="city", limit=2)
        # Should return at most 2 non-null values (null is added separately)
        non_null_values = [v for v in result["values"] if v["value"] is not None]
        assert len(non_null_values) <= 2

    @pytest.mark.asyncio
    async def test_column_not_found(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        with pytest.raises(Exception) as exc_info:
            await _call_unique_values(ds, column="nonexistent")
        assert "not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_empty_dataset(self):
        ds = _make_mock_dataset([])
        ds.columns = [{"name": "city", "dtype": "string"}]
        result = await _call_unique_values(ds, column="city")
        assert result["values"] == []
        assert result["total_unique"] == 0

    @pytest.mark.asyncio
    async def test_no_data_json(self):
        ds = _make_mock_dataset(None)
        ds.data_json = None
        ds.columns = [{"name": "city", "dtype": "string"}]
        result = await _call_unique_values(ds, column="city")
        assert result["values"] == []
        assert result["total_unique"] == 0

    @pytest.mark.asyncio
    async def test_all_null_column(self):
        data = [
            {"name": "Alice", "city": None},
            {"name": "Bob", "city": None},
            {"name": "Carol", "city": None},
        ]
        ds = _make_mock_dataset(data)
        result = await _call_unique_values(ds, column="city")
        # Only null entry
        assert len(result["values"]) == 1
        assert result["values"][0]["value"] is None
        assert result["values"][0]["count"] == 3
        assert result["total_unique"] == 1

    @pytest.mark.asyncio
    async def test_single_value_column(self):
        data = [
            {"name": "Alice", "status": "active"},
            {"name": "Bob", "status": "active"},
            {"name": "Carol", "status": "active"},
        ]
        ds = _make_mock_dataset(data)
        result = await _call_unique_values(ds, column="status")
        non_null = [v for v in result["values"] if v["value"] is not None]
        assert len(non_null) == 1
        assert non_null[0]["value"] == "active"
        assert non_null[0]["count"] == 3
