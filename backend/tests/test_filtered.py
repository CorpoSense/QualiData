"""Tests for the POST /datasets/{id}/filtered endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd


SAMPLE_DATA = [
    {"name": "Alice", "city": "Paris", "country": "France"},
    {"name": "Bob", "city": "London", "country": "UK"},
    {"name": "Carol", "city": "Paris", "country": "France"},
    {"name": "Dave", "city": "Berlin", "country": "Germany"},
    {"name": "Eve", "city": "London", "country": "UK"},
]


def _make_mock_dataset(data):
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.preview_data = data
    # Use data_json as primary source (single source of truth)
    ds.data_json = {"data": data} if data else None
    ds.row_count = len(data)
    ds.columns = [{"name": k} for k in data[0].keys()] if data else []
    return ds


async def _call_filtered(dataset, filters, limit=10, page=1):
    """Helper to call the filtered endpoint."""
    from app.routers.datasets import filtered_dataset_post

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = dataset

    async def mock_execute(*args, **kwargs):
        return mock_result

    mock_session.execute = AsyncMock(side_effect=mock_execute)

    return await filtered_dataset_post(
        dataset_id="ds-1",
        filters=filters,
        limit=limit,
        page=page,
        current_user=MagicMock(id="user-1"),
        session=mock_session,
    )


class TestFilteredEndpoint:
    @pytest.mark.asyncio
    async def test_filter_by_single_column(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": "France"})
        assert result["total_matching"] == 2
        assert all(r["country"] == "France" for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_filter_by_multiple_columns(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": "UK", "city": "London"})
        assert result["total_matching"] == 2
        assert all(r["city"] == "London" for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_filter_case_insensitive(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": "france"})
        assert result["total_matching"] == 2

    @pytest.mark.asyncio
    async def test_filter_partial_match(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"name": "ali"})
        assert result["total_matching"] == 1
        assert result["preview_data"][0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_filter_no_match(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": "Japan"})
        assert result["total_matching"] == 0
        assert result["preview_data"] == []

    @pytest.mark.asyncio
    async def test_filter_empty_filters_returns_all(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {})
        assert result["total_matching"] == 5

    @pytest.mark.asyncio
    async def test_filter_pagination(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        # Filter France (2 results), page 1, limit 1
        result = await _call_filtered(ds, {"country": "France"}, limit=1, page=1)
        assert result["total_matching"] == 2
        assert len(result["preview_data"]) == 1
        assert result["preview_data"][0]["name"] == "Alice"

        # Page 2
        result2 = await _call_filtered(ds, {"country": "France"}, limit=1, page=2)
        assert len(result2["preview_data"]) == 1
        assert result2["preview_data"][0]["name"] == "Carol"

    @pytest.mark.asyncio
    async def test_filter_returns_matching_indices(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": "UK"})
        # UK is at indices 1 and 4
        assert result["matching_indices"] == [1, 4]

    @pytest.mark.asyncio
    async def test_filter_ignores_empty_values(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": "France", "city": ""})
        assert result["total_matching"] == 2  # Only country filter applies

    @pytest.mark.asyncio
    async def test_filter_empty_dataset(self):
        ds = _make_mock_dataset([])
        ds.columns = []
        result = await _call_filtered(ds, {"country": "France"})
        assert result["preview_data"] == []
        assert result["total_matching"] == 0


class TestFilteredSelectedValues:
    """Tests for the selected_values filter format in POST /filtered."""

    @pytest.mark.asyncio
    async def test_selected_values_single_column(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": {"selected_values": ["France"]}})
        assert result["total_matching"] == 2
        assert all(r["country"] == "France" for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_selected_values_multiple_values(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": {"selected_values": ["France", "Germany"]}})
        assert result["total_matching"] == 3
        assert all(r["country"] in ("France", "Germany") for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_selected_values_multiple_columns(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {
            "country": {"selected_values": ["UK"]},
            "city": {"selected_values": ["London"]},
        })
        assert result["total_matching"] == 2
        assert all(r["city"] == "London" and r["country"] == "UK" for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_selected_values_with_null(self):
        data_with_nulls = [
            {"name": "Alice", "city": "Paris"},
            {"name": "Bob", "city": None},
            {"name": "Carol", "city": "Paris"},
            {"name": "Dave", "city": None},
        ]
        ds = _make_mock_dataset(data_with_nulls)
        result = await _call_filtered(ds, {"city": {"selected_values": [None]}})
        assert result["total_matching"] == 2
        assert all(r["city"] is None for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_selected_values_with_null_and_values(self):
        data_with_nulls = [
            {"name": "Alice", "city": "Paris"},
            {"name": "Bob", "city": None},
            {"name": "Carol", "city": "London"},
            {"name": "Dave", "city": None},
        ]
        ds = _make_mock_dataset(data_with_nulls)
        result = await _call_filtered(ds, {"city": {"selected_values": [None, "Paris"]}})
        assert result["total_matching"] == 3

    @pytest.mark.asyncio
    async def test_selected_values_empty_list_returns_all(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        # Empty selected_values list should not filter (no active filter for that column)
        result = await _call_filtered(ds, {"country": {"selected_values": []}})
        assert result["total_matching"] == 5  # All rows returned

    @pytest.mark.asyncio
    async def test_selected_values_no_match(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": {"selected_values": ["Japan"]}})
        assert result["total_matching"] == 0
        assert result["preview_data"] == []

    @pytest.mark.asyncio
    async def test_selected_values_exact_match_not_substring(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        # "Fran" should NOT match "France" with selected_values (exact match)
        result = await _call_filtered(ds, {"country": {"selected_values": ["Fran"]}})
        assert result["total_matching"] == 0

    @pytest.mark.asyncio
    async def test_mixed_filter_types(self):
        """Mix selected_values and substring filters in the same request."""
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {
            "country": {"selected_values": ["France", "UK"]},  # exact match
            "name": "a",  # substring match (Alice, Carol, Dave)
        })
        # France: Alice, Carol (both have 'a' in name)
        # UK: Bob, Eve (neither has 'a' in name)
        assert result["total_matching"] == 2
        assert all(r["country"] == "France" for r in result["preview_data"])

    @pytest.mark.asyncio
    async def test_selected_values_pagination(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(
            ds, {"country": {"selected_values": ["France", "UK"]}}, limit=2, page=1
        )
        assert result["total_matching"] == 4
        assert len(result["preview_data"]) == 2

    @pytest.mark.asyncio
    async def test_selected_values_returns_matching_indices(self):
        ds = _make_mock_dataset(SAMPLE_DATA)
        result = await _call_filtered(ds, {"country": {"selected_values": ["UK"]}})
        assert result["matching_indices"] == [1, 4]

    @pytest.mark.asyncio
    async def test_selected_values_numeric_as_string(self):
        """Numeric values in selected_values should match their string representation."""
        data = [
            {"name": "Alice", "score": 85},
            {"name": "Bob", "score": 90},
            {"name": "Carol", "score": 85},
        ]
        ds = _make_mock_dataset(data)
        result = await _call_filtered(ds, {"score": {"selected_values": ["85"]}})
        assert result["total_matching"] == 2
