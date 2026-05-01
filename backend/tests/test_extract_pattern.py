"""Tests for the extract-pattern operation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd


def _make_mock_dataset(data):
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.data_json = {"data": data}
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


class TestExtractPatternOperation:

    @pytest.mark.asyncio
    async def test_extract_with_capture_group(self):
        """Pattern with capture group returns group(1)."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"url": "https://example.com/page"},
            {"url": "https://foo.org/api"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "url", "pattern": r"https?://([^/]+)"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["url"] == "example.com"
        assert ds.data_json["data"][1]["url"] == "foo.org"

    @pytest.mark.asyncio
    async def test_extract_without_capture_group(self):
        """Pattern without capture group returns full match."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"text": "age: 25 years"},
            {"text": "age: 30 years"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "text", "pattern": r"\d+"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["text"] == "25"
        assert ds.data_json["data"][1]["text"] == "30"

    @pytest.mark.asyncio
    async def test_extract_email(self):
        """Extract email addresses from text."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"info": "Contact: user@example.com for details"},
            {"info": "Email: admin@foo.org please"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "info", "pattern": r"([\w.+-]+@[\w-]+\.[\w.]+)"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["info"] == "user@example.com"
        assert ds.data_json["data"][1]["info"] == "admin@foo.org"

    @pytest.mark.asyncio
    async def test_no_match_leaves_unchanged(self):
        """Values that don't match the pattern are left unchanged."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "hello world"},
            {"col": "no numbers here"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"\d+"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "no_changes"
        assert ds.data_json["data"][0]["col"] == "hello world"
        assert ds.data_json["data"][1]["col"] == "no numbers here"

    @pytest.mark.asyncio
    async def test_partial_match(self):
        """Some rows match, some don't — only matching rows are changed."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "price: $100"},
            {"col": "free item"},
            {"col": "cost: $50"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"\$(\d+)"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "100"
        assert ds.data_json["data"][1]["col"] == "free item"  # unchanged
        assert ds.data_json["data"][2]["col"] == "50"

    @pytest.mark.asyncio
    async def test_null_values_unchanged(self):
        """Null/NaN values are left unchanged."""
        from app.routers.operations import extract_pattern_value
        import numpy as np

        ds = _make_mock_dataset([
            {"col": "value: 42"},
            {"col": None},
            {"col": np.nan},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"value:\s*(\d+)"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "42"
        assert pd.isna(ds.data_json["data"][1]["col"])
        assert pd.isna(ds.data_json["data"][2]["col"])

    @pytest.mark.asyncio
    async def test_invalid_regex_returns_error(self):
        """Malformed regex pattern returns 400 error."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "some text"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(Exception) as exc_info:
                await extract_pattern_value(
                    dataset_id="ds-1",
                    request={"column": "col", "pattern": r"[invalid"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        """Case-insensitive flag works correctly."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "Hello World"},
            {"col": "HELLO WORLD"},
            {"col": "hello world"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"(hello)", "case_sensitive": False},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "Hello"
        assert ds.data_json["data"][1]["col"] == "HELLO"
        assert ds.data_json["data"][2]["col"] == "hello"

    @pytest.mark.asyncio
    async def test_case_sensitive_matching(self):
        """Case-sensitive flag (default) only matches exact case."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "Hello World"},
            {"col": "hello world"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"(hello)", "case_sensitive": True},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "Hello World"  # unchanged (case mismatch)
        assert ds.data_json["data"][1]["col"] == "hello"

    @pytest.mark.asyncio
    async def test_missing_column_returns_error(self):
        """Non-existent column returns 400 error."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "value"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(Exception) as exc_info:
                await extract_pattern_value(
                    dataset_id="ds-1",
                    request={"column": "nonexistent", "pattern": r"\d+"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_missing_pattern_returns_error(self):
        """Missing pattern returns 400 error."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "value"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(Exception) as exc_info:
                await extract_pattern_value(
                    dataset_id="ds-1",
                    request={"column": "col"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_extract_date_pattern(self):
        """Extract YYYY-MM-DD dates from text."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"log": "Event on 2024-01-15 occurred"},
            {"log": "Date: 2023-12-25 was holiday"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "log", "pattern": r"(\d{4}-\d{2}-\d{2})"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["log"] == "2024-01-15"
        assert ds.data_json["data"][1]["log"] == "2023-12-25"

    @pytest.mark.asyncio
    async def test_extract_with_row_indices(self):
        """Only specified rows are modified when row_indices is provided."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "price: $100"},
            {"col": "price: $200"},
            {"col": "price: $300"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"\$(\d+)", "row_indices": [0, 2]},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "100"
        assert ds.data_json["data"][1]["col"] == "price: $200"  # unchanged
        assert ds.data_json["data"][2]["col"] == "300"

    @pytest.mark.asyncio
    async def test_multiple_capture_groups_returns_first(self):
        """When multiple capture groups exist, group(1) is returned."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "user@domain.com"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"(\w+)@(\w+\.\w+)"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "user"

    @pytest.mark.asyncio
    async def test_empty_string_unchanged(self):
        """Empty strings that don't match are left unchanged."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "value: 42"},
            {"col": ""},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                     side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"value:\s*(\d+)"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        assert ds.data_json["data"][0]["col"] == "42"
        assert ds.data_json["data"][1]["col"] == ""

    @pytest.mark.asyncio
    async def test_new_column_creates_column(self):
        """When new_column is provided, extracted values go to a new column."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"url": "https://example.com/page"},
            {"url": "https://foo.org/api"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                     side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "url", "pattern": r"https?://([^/]+)", "new_column": "domain"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "success"
        # Original column preserved
        assert ds.data_json["data"][0]["url"] == "https://example.com/page"
        assert ds.data_json["data"][1]["url"] == "https://foo.org/api"
        # New column has extracted values
        assert ds.data_json["data"][0]["domain"] == "example.com"
        assert ds.data_json["data"][1]["domain"] == "foo.org"

    @pytest.mark.asyncio
    async def test_new_column_already_exists_returns_error(self):
        """When new_column already exists, returns 400 error."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"url": "https://example.com/page", "domain": "old"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                     side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            with pytest.raises(Exception) as exc_info:
                await extract_pattern_value(
                    dataset_id="ds-1",
                    request={"column": "url", "pattern": r"https?://([^/]+)", "new_column": "domain"},
                    current_user=MagicMock(id="u1"),
                    session=AsyncMock(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_new_column_no_match_preserves_original(self):
        """When new_column is set and no match, new column has original values."""
        from app.routers.operations import extract_pattern_value

        ds = _make_mock_dataset([
            {"col": "hello world"},
            {"col": "no numbers here"},
        ])
        with patch("app.routers.operations.get_dataset_with_owner_check",
                     side_effect=_make_owner_check(ds)), \
                _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await extract_pattern_value(
                dataset_id="ds-1",
                request={"column": "col", "pattern": r"\d+", "new_column": "extracted"},
                current_user=MagicMock(id="u1"),
                session=AsyncMock(),
            )
        assert result["status"] == "no_changes"
        # Original column unchanged
        assert ds.data_json["data"][0]["col"] == "hello world"
        assert ds.data_json["data"][1]["col"] == "no numbers here"
