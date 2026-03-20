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
