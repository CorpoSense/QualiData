"""Tests for the extract-json operation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd


def _make_mock_dataset(data):
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.preview_data = data
    ds.row_count = len(data)
    ds.columns = [{"name": k} for k in data[0].keys()] if data else []
    return ds


def _make_owner_check(dataset):
    async def fake_check(ds_id, user_id, session):
        return dataset
    return fake_check


_DETECT_PATCH = patch("app.routers.datasets.detect_columns", return_value=[])
_PREVIEW_PATCH = patch(
    "app.routers.datasets.get_preview_data",
    side_effect=lambda df: df.to_dict("records"),
)
_SAVE_PATCH = patch("app.routers.operations.save_operation", new_callable=AsyncMock)


class TestExtractJsonOperation:

    @pytest.mark.asyncio
    async def test_extract_simple_key(self):
        from app.routers.operations import extract_json_value

        ds = _make_mock_dataset([
            {"country": '{"country": "USA"}'},
            {"country": '{"country": "France"}'},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_json_value(
                dataset_id="ds-1",
                request={"column": "country", "key": "country"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.preview_data[0]["country"] == "USA"
        assert ds.preview_data[1]["country"] == "France"

    @pytest.mark.asyncio
    async def test_extract_nested_key(self):
        from app.routers.operations import extract_json_value

        ds = _make_mock_dataset([
            {"info": '{"data": {"value": 42}}'},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_json_value(
                dataset_id="ds-1",
                request={"column": "info", "key": "data.value"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.preview_data[0]["info"] == 42

    @pytest.mark.asyncio
    async def test_non_json_values_unchanged(self):
        from app.routers.operations import extract_json_value

        ds = _make_mock_dataset([
            {"country": '{"country": "USA"}'},
            {"country": "not json"},
            {"country": ""},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_json_value(
                dataset_id="ds-1",
                request={"column": "country", "key": "country"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.preview_data[0]["country"] == "USA"
        assert ds.preview_data[1]["country"] == "not json"  # unchanged
        assert ds.preview_data[2]["country"] == ""  # unchanged

    @pytest.mark.asyncio
    async def test_missing_key_unchanged(self):
        from app.routers.operations import extract_json_value

        ds = _make_mock_dataset([
            {"col": '{"name": "Alice"}'},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_json_value(
                dataset_id="ds-1",
                request={"column": "col", "key": "age"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "no_changes"
        assert ds.preview_data[0]["col"] == '{"name": "Alice"}'  # unchanged

    @pytest.mark.asyncio
    async def test_null_values_unchanged(self):
        from app.routers.operations import extract_json_value
        import numpy as np

        ds = _make_mock_dataset([
            {"col": '{"v": 1}'},
            {"col": None},
            {"col": np.nan},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_json_value(
                dataset_id="ds-1",
                request={"column": "col", "key": "v"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.preview_data[0]["col"] == 1
        assert pd.isna(ds.preview_data[1]["col"])  # None becomes NaN through pandas
