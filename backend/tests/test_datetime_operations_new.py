"""Tests for datetime_operations with new features: error_handling, fallback_value, new_column, formats, row_indices."""

import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch


def _make_mock_dataset(data):
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.data_json = {"data": data}
    ds.row_count = len(data)
    ds.columns = [{"name": k, "dtype": "string"} for k in data[0].keys()] if data else []
    return ds


def _make_owner_check(dataset):
    async def fake_check(ds_id, user_id, session):
        return dataset
    return fake_check


_DETECT_PATCH = patch("app.routers.datasets.detect_columns", return_value=[])
_PREVIEW_PATCH = patch("app.routers.datasets.get_preview_data", side_effect=lambda df: df.to_dict("records"))
_SAVE_PATCH = patch("app.routers.operations.save_operation", new_callable=AsyncMock)


# ─── Backward compatibility ────────────────────────────────────────────────

class TestDatetimeOperationsBackwardCompat:
    """Ensure existing behavior is preserved."""

    @pytest.mark.asyncio
    async def test_parse_datetime_default_coerce(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([
            {"date": "2024-01-15", "name": "Alice"},
            {"date": "not-a-date", "name": "Bob"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={"columns": ["date"], "operation": "parse-datetime"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "success"
        # Unparseable value should be NaT (coerced to null)
        assert pd.isna(ds.data_json["data"][1]["date"])

    @pytest.mark.asyncio
    async def test_extract_year_default(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([
            {"date": pd.Timestamp("2024-01-15"), "name": "Alice"},
            {"date": pd.Timestamp("2023-06-20"), "name": "Bob"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={"columns": ["date"], "operation": "extract-year"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert ds.data_json["data"][0]["date"] == 2024
        assert ds.data_json["data"][1]["date"] == 2023

    @pytest.mark.asyncio
    async def test_hyphenated_op_names(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([{"date": "2024-01-15"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={"columns": ["date"], "operation": "parse-datetime"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"


# ─── Error handling ─────────────────────────────────────────────────────────

class TestDatetimeErrorHandling:
    """Test error_handling parameter."""

    @pytest.mark.asyncio
    async def test_raise_fails_on_error(self):
        from app.routers.operations import datetime_operations
        from fastapi import HTTPException

        ds = _make_mock_dataset([{"date": "not-a-date"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(HTTPException) as exc_info:
                await datetime_operations(
                    dataset_id="ds-1",
                    request={"columns": ["date"], "operation": "parse-datetime", "error_handling": "raise"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_fallback_replaces_errors(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([
            {"date": "2024-01-15"},
            {"date": "not-a-date"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={
                    "columns": ["date"],
                    "operation": "parse-datetime",
                    "error_handling": "fallback",
                    "fallback_value": "1970-01-01",
                },
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert result["message"] == "Applied parse_datetime to 1 column(s). 1 value(s) could not be parsed and were set to fallback value"

    @pytest.mark.asyncio
    async def test_invalid_error_handling_returns_400(self):
        from app.routers.operations import datetime_operations
        from fastapi import HTTPException

        ds = _make_mock_dataset([{"date": "2024-01-15"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(HTTPException) as exc_info:
                await datetime_operations(
                    dataset_id="ds-1",
                    request={"columns": ["date"], "operation": "parse-datetime", "error_handling": "invalid"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_fallback_without_value_returns_400(self):
        from app.routers.operations import datetime_operations
        from fastapi import HTTPException

        ds = _make_mock_dataset([{"date": "2024-01-15"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(HTTPException) as exc_info:
                await datetime_operations(
                    dataset_id="ds-1",
                    request={"columns": ["date"], "operation": "parse-datetime", "error_handling": "fallback"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400


# ─── New column ─────────────────────────────────────────────────────────────

class TestDatetimeNewColumn:
    """Test new_column parameter."""

    @pytest.mark.asyncio
    async def test_new_column_preserves_original(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([{"date": "2024-01-15"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={"columns": ["date"], "operation": "parse-datetime", "new_column": "parsed_date"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        # Original preserved
        assert ds.data_json["data"][0]["date"] == "2024-01-15"
        # New column has parsed value
        assert ds.data_json["data"][0]["parsed_date"] is not None

    @pytest.mark.asyncio
    async def test_new_column_already_exists_returns_400(self):
        from app.routers.operations import datetime_operations
        from fastapi import HTTPException

        ds = _make_mock_dataset([{"date": "2024-01-15", "parsed_date": "old"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(HTTPException) as exc_info:
                await datetime_operations(
                    dataset_id="ds-1",
                    request={"columns": ["date"], "operation": "parse-datetime", "new_column": "parsed_date"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_new_column_with_batch_returns_400(self):
        from app.routers.operations import datetime_operations
        from fastapi import HTTPException

        ds = _make_mock_dataset([
            {"date1": "2024-01-15", "date2": "2024-06-20"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(HTTPException) as exc_info:
                await datetime_operations(
                    dataset_id="ds-1",
                    request={"columns": ["date1", "date2"], "operation": "parse-datetime", "new_column": "parsed"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400


# ─── Formats ────────────────────────────────────────────────────────────────

class TestDatetimeFormats:
    """Test input_format and output_format parameters."""

    @pytest.mark.asyncio
    async def test_parse_with_input_format(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([{"date": "15/01/2024"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={
                    "columns": ["date"],
                    "operation": "parse-datetime",
                    "input_format": "%d/%m/%Y",
                },
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        # Should be parsed to 2024-01-15
        assert "2024-01-15" in str(ds.data_json["data"][0]["date"])

    @pytest.mark.asyncio
    async def test_parse_with_output_format(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([{"date": "2024-01-15"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={
                    "columns": ["date"],
                    "operation": "parse-datetime",
                    "output_format": "%d/%m/%Y",
                },
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert ds.data_json["data"][0]["date"] == "15/01/2024"

    @pytest.mark.asyncio
    async def test_parse_with_both_formats(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([{"date": "15/01/2024"}])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={
                    "columns": ["date"],
                    "operation": "parse-datetime",
                    "input_format": "%d/%m/%Y",
                    "output_format": "%Y-%m-%d",
                },
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert ds.data_json["data"][0]["date"] == "2024-01-15"


# ─── Row indices ────────────────────────────────────────────────────────────

class TestDatetimeRowIndices:
    """Test row_indices parameter."""

    @pytest.mark.asyncio
    async def test_row_indices_applied(self):
        from app.routers.operations import datetime_operations

        ds = _make_mock_dataset([
            {"date": "2024-01-15"},
            {"date": "2023-06-20"},
            {"date": "2022-12-25"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await datetime_operations(
                dataset_id="ds-1",
                request={
                    "columns": ["date"],
                    "operation": "extract-year",
                    "row_indices": [0, 2],
                },
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        # Row 0 and 2 should be extracted, row 1 should be unchanged
        assert ds.data_json["data"][0]["date"] == 2024
        assert ds.data_json["data"][1]["date"] == "2023-06-20"  # unchanged
        assert ds.data_json["data"][2]["date"] == 2022


# ─── Import recipe ──────────────────────────────────────────────────────────

class TestDatetimeImportRecipe:
    """Test datetime operations via import-recipe."""

    @pytest.mark.asyncio
    async def test_import_recipe_parse_datetime(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest

        ds = _make_mock_dataset([{"date": "2024-01-15"}])
        req = ImportRecipeRequest(operations=[
            {
                "operation": "datetime-operations",
                "column": "date",
                "params": {"operation": "parse-datetime"},
            }
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="ds-1",
                request=req,
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "success"
        # The value should now be in datetime format
        assert "2024-01-15" in str(ds.data_json["data"][0]["date"])

    @pytest.mark.asyncio
    async def test_import_recipe_extract_year(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest

        ds = _make_mock_dataset([
            {"date": pd.Timestamp("2024-06-15")},
        ])
        req = ImportRecipeRequest(operations=[
            {
                "operation": "datetime_operations",
                "column": "date",
                "params": {"operation": "extract_year"},
            }
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check", side_effect=_make_owner_check(ds)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="ds-1",
                request=req,
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )

        assert result["status"] == "success"
        assert ds.data_json["data"][0]["date"] == 2024
