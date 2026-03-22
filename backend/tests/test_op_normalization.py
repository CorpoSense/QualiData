"""Tests for operation name normalization (frontend → backend mapping).

Prevents regressions where frontend sends hyphenated operation names
but backend expects underscored or abbreviated names."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd


def _make_mock_dataset(data: list[dict]):
    ds = MagicMock()
    ds.id = "test-ds-id"
    ds.project_id = "test-project-id"
    ds.preview_data = data
    ds.row_count = len(data)
    ds.columns = [{"field": k, "label": k} for k in data[0].keys()] if data else []
    return ds


def _make_owner_check(dataset):
    async def fake_check(ds_id, user_id, session):
        return dataset
    return fake_check


_DETECT_PATCH = patch("app.routers.datasets.detect_columns", return_value=[])
_PREVIEW_PATCH = patch("app.routers.datasets.get_preview_data", side_effect=lambda df: df.to_dict("records"))
_SAVE_PATCH = patch("app.routers.operations.save_operation", new_callable=AsyncMock)


SAMPLE_DATA = [
    {"name": "Alice", "age": 30, "score": 85.5, "joined": "2024-01-15"},
    {"name": "Bob", "age": 25, "score": 92.3, "joined": "2024-06-20"},
]


class TestDatetimeOperationsNormalization:
    """Test that datetime-operations accepts hyphenated names from frontend."""

    @pytest.mark.asyncio
    async def test_parse_datetime_hyphenated(self):
        from app.routers.operations import datetime_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="test-ds-id",
                request={"columns": ["joined"], "operation": "parse-datetime"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_extract_year_hyphenated(self):
        from app.routers.operations import datetime_operations

        # Need actual datetime data for extract operations
        data = [
            {"name": "Alice", "joined": pd.Timestamp("2024-01-15")},
            {"name": "Bob", "joined": pd.Timestamp("2023-06-20")},
        ]
        dataset = _make_mock_dataset(data)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="test-ds-id",
                request={"columns": ["joined"], "operation": "extract-year"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_extract_month_hyphenated(self):
        from app.routers.operations import datetime_operations

        data = [
            {"name": "Alice", "joined": pd.Timestamp("2024-01-15")},
        ]
        dataset = _make_mock_dataset(data)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="test-ds-id",
                request={"columns": ["joined"], "operation": "extract-month"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_parse_datetime_underscore_still_works(self):
        """Underscore format should still work for backward compat."""
        from app.routers.operations import datetime_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="test-ds-id",
                request={"columns": ["joined"], "operation": "parse_datetime"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_unknown_datetime_op_raises(self):
        from app.routers.operations import datetime_operations
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(HTTPException) as exc_info:
                await datetime_operations(
                    dataset_id="test-ds-id",
                    request={"columns": ["joined"], "operation": "invalid-op"},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400
        assert "unknown operation" in exc_info.value.detail


class TestStringOperationsNormalization:
    """Test that string-operations accepts names from frontend."""

    @pytest.mark.asyncio
    async def test_strip(self):
        from app.routers.operations import string_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await string_operations(
                dataset_id="test-ds-id",
                request={"columns": ["name"], "operation": "strip"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_upper(self):
        from app.routers.operations import string_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await string_operations(
                dataset_id="test-ds-id",
                request={"columns": ["name"], "operation": "upper"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_title(self):
        from app.routers.operations import string_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await string_operations(
                dataset_id="test-ds-id",
                request={"columns": ["name"], "operation": "title"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"


class TestNumericOperationsAcceptsFrontendNames:
    """Test that numeric operations accept names from frontend."""

    @pytest.mark.asyncio
    async def test_round(self):
        from app.routers.operations import numeric_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await numeric_operations(
                dataset_id="test-ds-id",
                request={"columns": ["score"], "operation": "round", "decimals": 0},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_normalize(self):
        from app.routers.operations import numeric_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await numeric_operations(
                dataset_id="test-ds-id",
                request={"columns": ["score"], "operation": "normalize"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_standardize(self):
        from app.routers.operations import numeric_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await numeric_operations(
                dataset_id="test-ds-id",
                request={"columns": ["score"], "operation": "standardize"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_robust_scale(self):
        from app.routers.operations import numeric_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await numeric_operations(
                dataset_id="test-ds-id",
                request={"columns": ["score"], "operation": "robust_scale"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
