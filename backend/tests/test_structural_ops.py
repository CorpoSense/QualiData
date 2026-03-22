"""Tests for structural operations: add_column, rename, drop, astype."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd


def _make_mock_dataset(data: list[dict]):
    """Create a mock dataset from list of dicts."""
    ds = MagicMock()
    ds.id = "test-ds-id"
    ds.project_id = "test-project-id"
    ds.preview_data = data
    ds.row_count = len(data)
    ds.columns = [{"field": k, "label": k} for k in data[0].keys()] if data else []
    return ds


def _make_owner_check(dataset):
    """Patch get_dataset_with_owner_check to return our mock."""
    async def fake_check(ds_id, user_id, session):
        return dataset
    return fake_check


SAMPLE_DATA = [
    {"name": "Alice", "age": 30, "city": "Paris"},
    {"name": "Bob", "age": 25, "city": "London"},
]

# detect_columns and get_preview_data are imported locally inside
# structural_operations, so patch them at their source module.
_DETECT_PATCH = patch("app.routers.datasets.detect_columns", return_value=[])
_PREVIEW_PATCH = patch(
    "app.routers.datasets.get_preview_data",
    side_effect=lambda df: df.to_dict("records"),
)
_SAVE_PATCH = patch("app.routers.operations.save_operation", new_callable=AsyncMock)


class TestAddColumnOperation:
    """Test the add_column structural operation."""

    @pytest.mark.asyncio
    async def test_add_column_with_default_value(self):
        """Adding a column with a default value fills all rows."""
        from app.routers.operations import structural_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await structural_operations(
                dataset_id="test-ds-id",
                request={"operation": "add_column", "new_name": "country", "default_value": "Unknown"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        preview = dataset.preview_data
        assert "country" in preview[0]
        assert all(row["country"] == "Unknown" for row in preview)

    @pytest.mark.asyncio
    async def test_add_column_copies_from_source(self):
        """Adding a column with source copies values from existing column."""
        from app.routers.operations import structural_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await structural_operations(
                dataset_id="test-ds-id",
                request={"operation": "add_column", "new_name": "country", "source": "city"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        preview = dataset.preview_data
        assert "country" in preview[0]
        assert preview[0]["country"] == "Paris"
        assert preview[0]["city"] == "Paris"

    @pytest.mark.asyncio
    async def test_add_column_rejects_duplicate_name(self):
        """Adding a column with an existing name should fail."""
        from app.routers.operations import structural_operations
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await structural_operations(
                    dataset_id="test-ds-id",
                    request={"operation": "add_column", "new_name": "city"},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_add_column_requires_name(self):
        """Adding a column without new_name should fail."""
        from app.routers.operations import structural_operations
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await structural_operations(
                    dataset_id="test-ds-id",
                    request={"operation": "add_column"},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_add_column_empty_default(self):
        """Adding a column with empty default fills with empty string."""
        from app.routers.operations import structural_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await structural_operations(
                dataset_id="test-ds-id",
                request={"operation": "add_column", "new_name": "notes", "default_value": ""},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        preview = dataset.preview_data
        assert "notes" in preview[0]
        assert preview[0]["notes"] == ""


class TestExistingStructuralOps:
    """Quick sanity checks that existing operations still work."""

    @pytest.mark.asyncio
    async def test_rename_still_works(self):
        from app.routers.operations import structural_operations

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await structural_operations(
                dataset_id="test-ds-id",
                request={"operation": "rename", "column": "name", "new_name": "full_name"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        assert "full_name" in dataset.preview_data[0]
        assert "name" not in dataset.preview_data[0]


class TestReorderColumnsOperation:
    """Test the reorder-columns operation."""

    @pytest.mark.asyncio
    async def test_reorder_shifts_selected_one_step_left(self):
        """Shifting selected columns one step left reorders correctly."""
        from app.routers.operations import reorder_columns, ReorderColumnsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_columns(
                dataset_id="test-ds-id",
                request=ReorderColumnsRequest(columns=["name", "city", "age"]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert list(dataset.preview_data[0].keys()) == ["name", "city", "age"]

    @pytest.mark.asyncio
    async def test_reorder_shifts_selected_one_step_right(self):
        """Shifting selected columns one step right reorders correctly."""
        from app.routers.operations import reorder_columns, ReorderColumnsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_columns(
                dataset_id="test-ds-id",
                request=ReorderColumnsRequest(columns=["age", "name", "city"]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert list(dataset.preview_data[0].keys()) == ["age", "name", "city"]

    @pytest.mark.asyncio
    async def test_reorder_preserves_data(self):
        """Reordering columns does not lose or corrupt row data."""
        from app.routers.operations import reorder_columns, ReorderColumnsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_columns(
                dataset_id="test-ds-id",
                request=ReorderColumnsRequest(columns=["city", "age", "name"]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        row = dataset.preview_data[0]
        assert row["name"] == "Alice"
        assert row["age"] == 30
        assert row["city"] == "Paris"

    @pytest.mark.asyncio
    async def test_reorder_rejects_column_mismatch(self):
        """Reorder with wrong column set raises 400."""
        from app.routers.operations import reorder_columns, ReorderColumnsRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await reorder_columns(
                    dataset_id="test-ds-id",
                    request=ReorderColumnsRequest(columns=["name", "age"]),  # missing "city"
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )

        assert exc_info.value.status_code == 400
        assert "mismatch" in exc_info.value.detail.lower()


class TestReorderRowsOperation:
    """Test the reorder-rows operation."""

    @pytest.mark.asyncio
    async def test_move_single_row_up(self):
        """Moving one row up swaps it with the row above."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[2], direction="up"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "C", "B", "D"]

    @pytest.mark.asyncio
    async def test_move_single_row_down(self):
        """Moving one row down swaps it with the row below."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[1], direction="down"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "C", "B", "D"]

    @pytest.mark.asyncio
    async def test_move_multiple_rows_up(self):
        """Moving non-adjacent rows up shifts each by one step."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            # Select rows at indices 2 and 4 (C and E), move up
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[2, 4], direction="up"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "C", "B", "E", "D"]

    @pytest.mark.asyncio
    async def test_move_multiple_rows_down(self):
        """Moving non-adjacent rows down shifts each by one step."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            # Select rows at indices 0 and 2 (A and C), move down
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[0, 2], direction="down"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["B", "A", "D", "C", "E"]

    @pytest.mark.asyncio
    async def test_move_first_row_up_is_noop(self):
        """Moving the first row up is a no-op (row stays in place)."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[0], direction="up"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_move_last_row_down_is_noop(self):
        """Moving the last row down is a no-op (row stays in place)."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[2], direction="down"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_move_adjacent_selected_rows_up(self):
        """Adjacent selected rows move as a block up."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            # Select rows 1,2 (B,C) — adjacent. Move up.
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[1, 2], direction="up"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["B", "C", "A", "D"]

    @pytest.mark.asyncio
    async def test_reorder_preserves_row_data(self):
        """Reordering rows does not corrupt cell data."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Carol", "age": 35},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await reorder_rows(
                dataset_id="test-ds-id",
                request=ReorderRowsRequest(indices=[2], direction="up"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        row = dataset.preview_data[1]
        assert row["name"] == "Carol"
        assert row["age"] == 35

    @pytest.mark.asyncio
    async def test_reorder_invalid_index_rejected(self):
        """Out-of-range index raises 400."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset([{"name": "A"}, {"name": "B"}])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await reorder_rows(
                    dataset_id="test-ds-id",
                    request=ReorderRowsRequest(indices=[5], direction="up"),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_reorder_invalid_direction_rejected(self):
        """Invalid direction raises 400."""
        from app.routers.operations import reorder_rows, ReorderRowsRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset([{"name": "A"}, {"name": "B"}])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await reorder_rows(
                    dataset_id="test-ds-id",
                    request=ReorderRowsRequest(indices=[0], direction="left"),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )

        assert exc_info.value.status_code == 400


class TestAddRecordsOperation:
    """Test the add-records operation."""

    @pytest.mark.asyncio
    async def test_add_single_record(self):
        """Adding a single record appends it to the dataset."""
        from app.routers.operations import add_records, AddRecordsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await add_records(
                dataset_id="test-ds-id",
                request=AddRecordsRequest(records=[{"name": "Carol", "age": 35, "city": "Berlin"}]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "1 record(s)" in result.message
        assert len(dataset.preview_data) == 3
        assert dataset.preview_data[2]["name"] == "Carol"

    @pytest.mark.asyncio
    async def test_add_multiple_records(self):
        """Adding multiple records at once."""
        from app.routers.operations import add_records, AddRecordsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await add_records(
                dataset_id="test-ds-id",
                request=AddRecordsRequest(records=[
                    {"name": "Carol", "age": 35, "city": "Berlin"},
                    {"name": "David", "age": 28, "city": "Rome"},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "2 record(s)" in result.message
        assert len(dataset.preview_data) == 4

    @pytest.mark.asyncio
    async def test_add_record_from_csv(self):
        """Adding records from CSV text."""
        from app.routers.operations import add_records, AddRecordsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        csv_text = "name,age,city\nCarol,35,Berlin\nDavid,28,Rome"

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await add_records(
                dataset_id="test-ds-id",
                request=AddRecordsRequest(csv_text=csv_text),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "2 record(s)" in result.message
        assert len(dataset.preview_data) == 4

    @pytest.mark.asyncio
    async def test_add_record_missing_columns_filled_with_none(self):
        """Records with missing columns get None for those fields."""
        from app.routers.operations import add_records, AddRecordsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await add_records(
                dataset_id="test-ds-id",
                request=AddRecordsRequest(records=[{"name": "Carol"}]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        row = dataset.preview_data[2]
        assert row["name"] == "Carol"
        assert row.get("age") is None
        assert row.get("city") is None

    @pytest.mark.asyncio
    async def test_add_record_extra_columns_ignored(self):
        """Records with extra columns not in dataset are trimmed."""
        from app.routers.operations import add_records, AddRecordsRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await add_records(
                dataset_id="test-ds-id",
                request=AddRecordsRequest(records=[{"name": "Carol", "age": 35, "city": "Berlin", "country": "DE"}]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        row = dataset.preview_data[2]
        assert "country" not in row

    @pytest.mark.asyncio
    async def test_add_record_requires_data(self):
        """Calling with neither records nor csv_text raises 400."""
        from app.routers.operations import add_records, AddRecordsRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await add_records(
                    dataset_id="test-ds-id",
                    request=AddRecordsRequest(),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400


class TestImportRecipeOperation:
    """Test the import-recipe endpoint."""

    @pytest.mark.asyncio
    async def test_import_fillna_recipe(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": 30},
            {"name": None, "age": 25},
            {"name": "Carol", "age": None},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="test-ds-id",
                request=ImportRecipeRequest(operations=[
                    {"operation": "fillna", "column": "name", "params": {"method": "constant", "fill_value": "Unknown"}},
                    {"operation": "fillna", "column": "age", "params": {"method": "constant", "fill_value": 0}},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "success"
        assert result["results"][1]["status"] == "success"

    @pytest.mark.asyncio
    async def test_import_skips_missing_columns(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="test-ds-id",
                request=ImportRecipeRequest(operations=[
                    {"operation": "fillna", "column": "nonexistent", "params": {"method": "constant", "fill_value": "X"}},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["results"][0]["status"] == "skipped"
        assert "not found" in result["results"][0]["message"]

    @pytest.mark.asyncio
    async def test_import_string_operations(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest

        dataset = _make_mock_dataset([
            {"name": "alice", "city": "paris"},
            {"name": "bob", "city": "london"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="test-ds-id",
                request=ImportRecipeRequest(operations=[
                    {"operation": "string-operations", "column": "name", "params": {"operation": "title"}},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "success"
        assert dataset.preview_data[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_import_unsupported_operation_skipped(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="test-ds-id",
                request=ImportRecipeRequest(operations=[
                    {"operation": "unknown_op", "params": {}},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["results"][0]["status"] == "skipped"
        assert "Unsupported" in result["results"][0]["message"]

    @pytest.mark.asyncio
    async def test_import_empty_list_rejected(self):
        from app.routers.operations import import_recipe, ImportRecipeRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await import_recipe(
                    dataset_id="test-ds-id",
                    request=ImportRecipeRequest(operations=[]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_import_continues_after_failure(self):
        """A failed operation doesn't stop subsequent ones."""
        from app.routers.operations import import_recipe, ImportRecipeRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await import_recipe(
                dataset_id="test-ds-id",
                request=ImportRecipeRequest(operations=[
                    {"operation": "fillna", "column": "nonexistent", "params": {"method": "constant", "fill_value": "X"}},
                    {"operation": "string-operations", "column": "name", "params": {"operation": "upper"}},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["results"][0]["status"] == "skipped"
        assert result["results"][1]["status"] == "success"
        assert dataset.preview_data[0]["name"] == "ALICE"


class TestDeleteRowsOperation:
    """Test the delete-rows operation."""

    @pytest.mark.asyncio
    async def test_delete_first_n(self):
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "first", "count": 1},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 1
        assert dataset.preview_data[0]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_delete_last_n(self):
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "last", "count": 1},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 1
        assert dataset.preview_data[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_delete_range(self):
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}
        ])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "range", "start": 1, "end": 4},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 2
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "E"]

    @pytest.mark.asyncio
    async def test_delete_visible(self):
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}
        ])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "visible", "indices": [0, 2]},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 2
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["B", "D"]

    @pytest.mark.asyncio
    async def test_delete_all_rows_rejected(self):
        from app.routers.operations import delete_rows
        from fastapi import HTTPException
        dataset = _make_mock_dataset([{"name": "A"}])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await delete_rows(
                    dataset_id="test-ds-id",
                    request={"mode": "first", "count": 1},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400
        assert "Cannot delete all rows" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_range_all_rows_rejected(self):
        from app.routers.operations import delete_rows
        from fastapi import HTTPException
        dataset = _make_mock_dataset([{"name": "A"}, {"name": "B"}, {"name": "C"}])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await delete_rows(
                    dataset_id="test-ds-id",
                    request={"mode": "range", "start": 0, "end": 3},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_visible_all_rows_allowed(self):
        """Deleting all rows via 'visible' mode is allowed (for filter-based deletion)."""
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset([{"name": "A"}, {"name": "B"}])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "visible", "indices": [0, 1]},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 0

    @pytest.mark.asyncio
    async def test_delete_specific_indices(self):
        """Simulate multi-row selection: delete specific rows by absolute index."""
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}
        ])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            # Select rows 1 and 3 (B and D)
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "visible", "indices": [1, 3]},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 3
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["A", "C", "E"]

    @pytest.mark.asyncio
    async def test_delete_non_consecutive_indices(self):
        """Delete non-consecutive rows (simulating cross-page selection)."""
        from app.routers.operations import delete_rows
        dataset = _make_mock_dataset([
            {"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}, {"name": "E"}
        ])
        mock_session = AsyncMock()
        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await delete_rows(
                dataset_id="test-ds-id",
                request={"mode": "visible", "indices": [0, 2, 4]},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
        assert result["status"] == "success"
        assert result["row_count"] == 2
        names = [r["name"] for r in dataset.preview_data]
        assert names == ["B", "D"]
