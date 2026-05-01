"""Tests for structural operations: add_column, rename, drop, astype."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd


def _make_mock_dataset(data: list[dict]):
    """Create a mock dataset from list of dicts."""
    ds = MagicMock()
    ds.id = "test-ds-id"
    ds.project_id = "test-project-id"
    ds.data_json = {"data": data}
    ds.row_count = len(data)
    ds.columns = [{"name": k, "dtype": "string"} for k in data[0].keys()] if data else []
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
_SAVE_PATCH_EXTRA = patch("app.routers.operations_extra.save_operation", new_callable=AsyncMock)


def _make_sync_owner_check(dataset):
    """Patch get_dataset_with_owner_check (sync version in operations_extra) to return our mock."""
    def fake_check(ds_id, user_id, session):
        return dataset
    return fake_check


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
        preview = dataset.data_json["data"]
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
        preview = dataset.data_json["data"]
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
        preview = dataset.data_json["data"]
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
        assert "full_name" in dataset.data_json["data"][0]
        assert "name" not in dataset.data_json["data"][0]


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
        assert list(dataset.data_json["data"][0].keys()) == ["name", "city", "age"]

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
        assert list(dataset.data_json["data"][0].keys()) == ["age", "name", "city"]

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
        row = dataset.data_json["data"][0]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        row = dataset.data_json["data"][1]
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
        assert len(dataset.data_json["data"]) == 3
        assert dataset.data_json["data"][2]["name"] == "Carol"

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
        assert len(dataset.data_json["data"]) == 4

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
        assert len(dataset.data_json["data"]) == 4

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
        row = dataset.data_json["data"][2]
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
        row = dataset.data_json["data"][2]
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
        assert dataset.data_json["data"][0]["name"] == "Alice"

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
        assert dataset.data_json["data"][0]["name"] == "ALICE"

    @pytest.mark.asyncio
    async def test_import_recipe_snapshot_uses_dicts_not_strings(self):
        """Before snapshot should contain column dicts, not plain strings (for undo)."""
        from app.routers.operations import import_recipe, ImportRecipeRequest

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()
        saved_snapshots = []

        async def capture_save(*args, **kwargs):
            if len(args) >= 5:
                saved_snapshots.append(args[3])  # before_snapshot

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             patch("app.routers.operations.save_operation", side_effect=capture_save), \
             _DETECT_PATCH, _PREVIEW_PATCH:
            await import_recipe(
                dataset_id="test-ds-id",
                request=ImportRecipeRequest(operations=[
                    {"operation": "string-operations", "column": "name", "params": {"operation": "upper"}},
                ]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert len(saved_snapshots) == 1
        snapshot_cols = saved_snapshots[0]["columns"]
        # Each column should be a dict with 'name' and 'dtype', not a plain string
        assert all(isinstance(c, dict) for c in snapshot_cols)
        assert all("name" in c and "dtype" in c for c in snapshot_cols)


class TestMergeColumnsOperation:
    """Test the merge-columns operation."""

    @pytest.mark.asyncio
    async def test_merge_columns_with_delimiter(self):
        from app.routers.operations import merge_columns, MergeColumnsRequest

        dataset = _make_mock_dataset([
            {"first": "John", "last": "Doe"},
            {"first": "Jane", "last": "Smith"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await merge_columns(
                dataset_id="test-ds-id",
                request=MergeColumnsRequest(columns=["first", "last"], new_column="full_name", delimiter=" "),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "full_name" in dataset.data_json["data"][0]
        assert dataset.data_json["data"][0]["full_name"] == "John Doe"
        assert dataset.data_json["data"][1]["full_name"] == "Jane Smith"

    @pytest.mark.asyncio
    async def test_merge_columns_no_delimiter(self):
        from app.routers.operations import merge_columns, MergeColumnsRequest

        dataset = _make_mock_dataset([
            {"area": "555", "number": "1234"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await merge_columns(
                dataset_id="test-ds-id",
                request=MergeColumnsRequest(columns=["area", "number"], new_column="phone", delimiter=""),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert dataset.data_json["data"][0]["phone"] == "5551234"

    @pytest.mark.asyncio
    async def test_merge_columns_missing_raises(self):
        from app.routers.operations import merge_columns, MergeColumnsRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await merge_columns(
                    dataset_id="test-ds-id",
                    request=MergeColumnsRequest(columns=["name", "missing_col"], new_column="merged", delimiter=" "),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400


class TestSplitColumnOperation:
    """Test the split-column operation."""

    @pytest.mark.asyncio
    async def test_split_column_by_delimiter(self):
        from app.routers.operations import split_column, SplitColumnRequest

        dataset = _make_mock_dataset([
            {"full_name": "John Doe"},
            {"full_name": "Jane Smith"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await split_column(
                dataset_id="test-ds-id",
                request=SplitColumnRequest(column="full_name", delimiter=" ", new_columns=["first", "last"]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert dataset.data_json["data"][0]["first"] == "John"
        assert dataset.data_json["data"][0]["last"] == "Doe"
        assert dataset.data_json["data"][1]["first"] == "Jane"
        assert dataset.data_json["data"][1]["last"] == "Smith"

    @pytest.mark.asyncio
    async def test_split_column_missing_raises(self):
        from app.routers.operations import split_column, SplitColumnRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await split_column(
                    dataset_id="test-ds-id",
                    request=SplitColumnRequest(column="nonexistent", delimiter=" ", new_columns=["a", "b"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_split_column_extra_parts_fill_null(self):
        """When split produces fewer parts than new columns, extras get None."""
        from app.routers.operations import split_column, SplitColumnRequest

        dataset = _make_mock_dataset([
            {"name": "John"},  # No delimiter, only 1 part
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await split_column(
                dataset_id="test-ds-id",
                request=SplitColumnRequest(column="name", delimiter=" ", new_columns=["first", "last"]),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert dataset.data_json["data"][0]["first"] == "John"
        assert dataset.data_json["data"][0]["last"] is None


class TestFuzzyDedupeRequiresColumn:
    """Test that fuzzy-dedupe requires a column parameter."""

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_missing_column_raises(self):
        from app.routers.operations import fuzzy_dedupe
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await fuzzy_dedupe(
                    dataset_id="test-ds-id",
                    request={"threshold": 0.8},  # No column!
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400
        assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_none_column_raises(self):
        """Explicit None column should also fail."""
        from app.routers.operations import fuzzy_dedupe
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await fuzzy_dedupe(
                    dataset_id="test-ds-id",
                    request={"column": None, "threshold": 0.8},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400


class TestFuzzyDedupeNewParameters:
    """Test the new matching_type and mode parameters for fuzzy-dedupe."""

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_invalid_matching_type_raises(self):
        """Invalid matching_type should raise 400."""
        from app.routers.operations import fuzzy_dedupe
        from fastapi import HTTPException

        dataset = _make_mock_dataset([{"name": "Alice"}, {"name": "Bob"}])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await fuzzy_dedupe(
                    dataset_id="test-ds-id",
                    request={"column": "name", "threshold": 0.8, "matching_type": "invalid"},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400
        assert "matching_type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_invalid_mode_raises(self):
        """Invalid mode should raise 400."""
        from app.routers.operations import fuzzy_dedupe
        from fastapi import HTTPException

        dataset = _make_mock_dataset([{"name": "Alice"}, {"name": "Bob"}])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await fuzzy_dedupe(
                    dataset_id="test-ds-id",
                    request={"column": "name", "threshold": 0.8, "mode": "invalid"},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400
        assert "mode" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_permutation_matching(self):
        """Permutation matching should match word order differences."""
        from app.routers.operations import fuzzy_dedupe

        dataset = _make_mock_dataset([
            {"name": "John Smith"},
            {"name": "Smith John"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await fuzzy_dedupe(
                dataset_id="test-ds-id",
                request={"column": "name", "threshold": 0.5, "matching_type": "permutation", "mode": "delete"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        # One row should be removed (they're similar under permutation matching)
        assert result["row_count"] == 1

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_merge_first_mode(self):
        """Merge first mode should keep all rows but update values to first occurrence."""
        from app.routers.operations import fuzzy_dedupe

        dataset = _make_mock_dataset([
            {"name": "John"},
            {"name": "John"},
            {"name": "jon"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await fuzzy_dedupe(
                dataset_id="test-ds-id",
                request={"column": "name", "threshold": 0.8, "matching_type": "standard", "mode": "merge_first"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        # All rows kept, but values merged to first
        assert result["row_count"] == 3
        names = [r["name"] for r in dataset.data_json["data"]]
        assert all(n == "John" for n in names)

    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_merge_most_frequent_mode(self):
        """Merge most frequent mode should consolidate to most common value."""
        from app.routers.operations import fuzzy_dedupe

        # Use similar strings that will cluster together
        dataset = _make_mock_dataset([
            {"name": "John"},  # This will be clustered with the others
            {"name": "Jon"},   # Similar to John
            {"name": "John"},  # This is the most frequent
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await fuzzy_dedupe(
                dataset_id="test-ds-id",
                request={"column": "name", "threshold": 0.8, "matching_type": "standard", "mode": "merge_most_frequent"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        # All 3 rows kept, but values merged to most frequent (which was "John" at index 2)
        assert result["row_count"] == 3
        names = [r["name"] for r in dataset.data_json["data"]]
        # Most frequent in cluster was "John", so all should be "John"
        assert all(n == "John" for n in names)

    
    @pytest.mark.asyncio
    async def test_fuzzy_dedupe_default_parameters(self):
        """Default parameters should be 'standard' matching_type and 'delete' mode."""
        from app.routers.operations import fuzzy_dedupe
        
        dataset = _make_mock_dataset([
            {"name": "Alice"},
            {"name": "Alice"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await fuzzy_dedupe(
                dataset_id="test-ds-id",
                request={"column": "name", "threshold": 0.8},  # No matching_type or mode
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result["status"] == "success"
        # Should delete the duplicate (default mode='delete')
        assert result["row_count"] == 1


class TestEncodingOperations:
    """Test ML/feature engineering encoding operations."""

    @pytest.mark.asyncio
    async def test_one_hot_encoding(self):
        from app.routers.operations import encoding_operations

        dataset = _make_mock_dataset([
            {"name": "Alice", "color": "red"},
            {"name": "Bob", "color": "blue"},
            {"name": "Carol", "color": "red"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await encoding_operations(
                dataset_id="test-ds-id",
                request={"column": "color", "operation": "one_hot"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "color_blue" in dataset.data_json["data"][0]
        assert "color_red" in dataset.data_json["data"][0]
        assert dataset.data_json["data"][0]["color_red"] == 1

    @pytest.mark.asyncio
    async def test_label_encoding(self):
        from app.routers.operations import encoding_operations

        dataset = _make_mock_dataset([
            {"name": "Alice", "grade": "A"},
            {"name": "Bob", "grade": "C"},
            {"name": "Carol", "grade": "B"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await encoding_operations(
                dataset_id="test-ds-id",
                request={"column": "grade", "operation": "label"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "grade_encoded" in dataset.data_json["data"][0]
        # A=0, B=1, C=2 (sorted)
        assert dataset.data_json["data"][0]["grade_encoded"] == 0  # A
        assert dataset.data_json["data"][1]["grade_encoded"] == 2  # C

    @pytest.mark.asyncio
    async def test_value_mapping(self):
        from app.routers.operations import encoding_operations

        dataset = _make_mock_dataset([
            {"name": "Alice", "status": "Y"},
            {"name": "Bob", "status": "N"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await encoding_operations(
                dataset_id="test-ds-id",
                request={"column": "status", "operation": "map", "mapping": {"Y": "Yes", "N": "No"}},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert dataset.data_json["data"][0]["status"] == "Yes"
        assert dataset.data_json["data"][1]["status"] == "No"

    @pytest.mark.asyncio
    async def test_binning(self):
        from app.routers.operations import encoding_operations

        dataset = _make_mock_dataset([
            {"name": "A", "score": 10},
            {"name": "B", "score": 50},
            {"name": "C", "score": 90},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)), \
             _SAVE_PATCH, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await encoding_operations(
                dataset_id="test-ds-id",
                request={"column": "score", "operation": "bin", "n_bins": 3, "strategy": "equal_width"},
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

        assert result.status == "success"
        assert "score_binned" in dataset.data_json["data"][0]

    @pytest.mark.asyncio
    async def test_encoding_missing_column_raises(self):
        from app.routers.operations import encoding_operations
        from fastapi import HTTPException

        dataset = _make_mock_dataset([{"name": "Alice"}])
        mock_session = AsyncMock()

        with patch("app.routers.operations.get_dataset_with_owner_check",
                    side_effect=_make_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await encoding_operations(
                    dataset_id="test-ds-id",
                    request={"column": "nonexistent", "operation": "label"},
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
        assert exc_info.value.status_code == 400


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
        assert dataset.data_json["data"][0]["name"] == "Bob"

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
        assert dataset.data_json["data"][0]["name"] == "Alice"

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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
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
        names = [r["name"] for r in dataset.data_json["data"]]
        assert names == ["B", "D"]
    
    
    class TestDetectType:
        """Test the detect-type endpoint and detect_column_type helper."""
    
        @pytest.mark.asyncio
        async def test_detect_integer_column(self):
            """Detects integer type for a string column with numeric values."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "age": "30"},
                {"name": "Bob", "age": "25"},
                {"name": "Carol", "age": "35"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["age"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["column"] == "age"
            assert col_result["suggested_type"] == "integer"
            assert col_result["confidence"] >= 0.8
            assert "integer" in col_result["type_scores"]
            assert col_result["type_scores"]["integer"] >= 0.8
    
        @pytest.mark.asyncio
        async def test_detect_boolean_column(self):
            """Detects boolean type for a column with true/false values."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "active": "true"},
                {"name": "Bob", "active": "false"},
                {"name": "Carol", "active": "yes"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["active"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["suggested_type"] == "boolean"
            assert col_result["confidence"] >= 0.8
    
        @pytest.mark.asyncio
        async def test_detect_datetime_column(self):
            """Detects datetime type for a column with date strings."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "created": "2024-01-15"},
                {"name": "Bob", "created": "2024-02-20"},
                {"name": "Carol", "created": "2024-03-10"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["created"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["suggested_type"] == "datetime"
            assert col_result["confidence"] >= 0.8
    
        @pytest.mark.asyncio
        async def test_detect_string_fallback(self):
            """Falls back to string for mixed data."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "mixed": "hello"},
                {"name": "Bob", "mixed": "42"},
                {"name": "Carol", "mixed": "world"},
                {"name": "Dave", "mixed": "true"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["mixed"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            # Mixed data should not suggest a specific type with high confidence
            assert col_result["suggested_type"] == "string"
    
        @pytest.mark.asyncio
        async def test_detect_multiple_columns(self):
            """Detects types for multiple columns at once."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "age": "30", "active": "true"},
                {"name": "Bob", "age": "25", "active": "false"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["age", "active"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            assert len(result["columns"]) == 2
            assert result["columns"][0]["column"] == "age"
            assert result["columns"][1]["column"] == "active"
    
        @pytest.mark.asyncio
        async def test_detect_type_missing_column_raises(self):
            """Detecting type for a non-existent column raises 400."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
            from fastapi import HTTPException
    
            dataset = _make_mock_dataset(SAMPLE_DATA)
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                with pytest.raises(HTTPException) as exc_info:
                    await detect_type(
                        dataset_id="test-ds-id",
                        request=DetectTypeRequest(columns=["nonexistent"]),
                        current_user=MagicMock(id="user-1"),
                        session=mock_session,
                    )
            assert exc_info.value.status_code == 400
    
        @pytest.mark.asyncio
        async def test_detect_type_with_nulls(self):
            """Type detection handles null values gracefully."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "age": "30"},
                {"name": "Bob", "age": None},
                {"name": "Carol", "age": "35"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["age"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["null_count"] == 1
            assert col_result["suggested_type"] == "integer"
    
        @pytest.mark.asyncio
        async def test_detect_float_column(self):
            """Detects float type for a column with decimal values."""
            from app.routers.operations_extra import detect_type, DetectTypeRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "score": "3.14"},
                {"name": "Bob", "score": "2.71"},
                {"name": "Carol", "score": "1.41"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await detect_type(
                    dataset_id="test-ds-id",
                    request=DetectTypeRequest(columns=["score"]),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            # Float should be suggested (integers are also valid floats, but float has decimals)
            assert col_result["suggested_type"] in ("float", "integer")
            assert col_result["type_scores"]["float"] >= 0.8
    
    
    class TestChangeTypePreview:
        """Test the change-type-preview endpoint."""
    
        @pytest.mark.asyncio
        async def test_preview_string_to_integer(self):
            """Preview shows before/after for string→integer conversion."""
            from app.routers.operations_extra import change_type_preview, ChangeTypePreviewRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "age": "30"},
                {"name": "Bob", "age": "25"},
                {"name": "Carol", "age": "N/A"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await change_type_preview(
                    dataset_id="test-ds-id",
                    request=ChangeTypePreviewRequest(
                        columns=["age"], target_type="integer", sample_rows=3
                    ),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["column"] == "age"
            assert col_result["target_type"] == "integer"
            assert len(col_result["preview"]) == 3
            # First two should convert fine
            assert col_result["preview"][0]["changed"] is True
            assert col_result["preview"][0]["error"] is False
            # "N/A" should be an error
            assert col_result["preview"][2]["error"] is True
            assert col_result["total_errors"] == 1
    
        @pytest.mark.asyncio
        async def test_preview_with_data_loss_warnings(self):
            """Preview warns about float→integer precision loss."""
            from app.routers.operations_extra import change_type_preview, ChangeTypePreviewRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "score": 3.14},
                {"name": "Bob", "score": 2.71},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await change_type_preview(
                    dataset_id="test-ds-id",
                    request=ChangeTypePreviewRequest(
                        columns=["score"], target_type="integer", sample_rows=2
                    ),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert len(col_result["data_loss_warnings"]) > 0
            assert any("Precision loss" in w for w in col_result["data_loss_warnings"])
    
        @pytest.mark.asyncio
        async def test_preview_string_to_datetime(self):
            """Preview shows before/after for string→datetime conversion."""
            from app.routers.operations_extra import change_type_preview, ChangeTypePreviewRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "created": "2024-01-15"},
                {"name": "Bob", "created": "not-a-date"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await change_type_preview(
                    dataset_id="test-ds-id",
                    request=ChangeTypePreviewRequest(
                        columns=["created"], target_type="datetime", sample_rows=2
                    ),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["total_errors"] == 1
    
        @pytest.mark.asyncio
        async def test_preview_invalid_target_type(self):
            """Preview with invalid target type raises 400."""
            from app.routers.operations_extra import change_type_preview, ChangeTypePreviewRequest
            from fastapi import HTTPException
    
            dataset = _make_mock_dataset(SAMPLE_DATA)
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                with pytest.raises(HTTPException) as exc_info:
                    await change_type_preview(
                        dataset_id="test-ds-id",
                        request=ChangeTypePreviewRequest(
                            columns=["age"], target_type="unknown_type"
                        ),
                        current_user=MagicMock(id="user-1"),
                        session=mock_session,
                    )
            assert exc_info.value.status_code == 400
    
        @pytest.mark.asyncio
        async def test_preview_no_errors(self):
            """Preview with clean data shows no errors."""
            from app.routers.operations_extra import change_type_preview, ChangeTypePreviewRequest
    
            dataset = _make_mock_dataset([
                {"name": "Alice", "age": "30"},
                {"name": "Bob", "age": "25"},
            ])
            mock_session = AsyncMock()
    
            with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                        side_effect=_make_sync_owner_check(dataset)):
                result = await change_type_preview(
                    dataset_id="test-ds-id",
                    request=ChangeTypePreviewRequest(
                        columns=["age"], target_type="integer", sample_rows=2
                    ),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
    
            assert result["status"] == "success"
            col_result = result["columns"][0]
            assert col_result["total_errors"] == 0
    
    
class TestEnhancedChangeType:
    """Test the enhanced change-type endpoint with error_handling and fallback_value."""

    @pytest.mark.asyncio
    async def test_change_type_coerce_default(self):
        """Default coerce mode converts invalid values to null (backward compatible)."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "N/A"},
            {"name": "Carol", "age": "35"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)), \
                _SAVE_PATCH_EXTRA, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await change_type(
                dataset_id="test-ds-id",
                request=ChangeTypeRequest(column="age", target_type="integer"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

            assert result.status == "success"
            # "N/A" should become null
            data = dataset.data_json["data"]
            assert data[0]["age"] == 30
            assert data[1]["age"] is None or pd.isna(data[1]["age"])
            assert data[2]["age"] == 35

    @pytest.mark.asyncio
    async def test_change_type_fallback(self):
        """Fallback mode replaces invalid values with fallback_value."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "N/A"},
            {"name": "Carol", "age": "35"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)), \
                _SAVE_PATCH_EXTRA, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await change_type(
                dataset_id="test-ds-id",
                request=ChangeTypeRequest(
                    column="age", target_type="integer",
                    error_handling="fallback", fallback_value=0
                ),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

            assert result.status == "success"
            data = dataset.data_json["data"]
            assert data[0]["age"] == 30
            assert data[1]["age"] == 0  # fallback value
            assert data[2]["age"] == 35

    @pytest.mark.asyncio
    async def test_change_type_raise_mode(self):
        """Raise mode fails the entire operation if any value cannot convert."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "N/A"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await change_type(
                    dataset_id="test-ds-id",
                    request=ChangeTypeRequest(
                        column="age", target_type="integer",
                        error_handling="raise"
                    ),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
            assert exc_info.value.status_code == 400
            assert "cannot be converted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_change_type_category(self):
        """Category type conversion works."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "status": "active"},
            {"name": "Bob", "status": "inactive"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)), \
                _SAVE_PATCH_EXTRA, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await change_type(
                dataset_id="test-ds-id",
                request=ChangeTypeRequest(column="status", target_type="category"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

            assert result.status == "success"

    @pytest.mark.asyncio
    async def test_change_type_boolean_smart_conversion(self):
        """Boolean conversion maps common boolean strings."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "active": "yes"},
            {"name": "Bob", "active": "no"},
            {"name": "Carol", "active": "true"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)), \
                _SAVE_PATCH_EXTRA, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await change_type(
                dataset_id="test-ds-id",
                request=ChangeTypeRequest(column="active", target_type="boolean"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

            assert result.status == "success"
            data = dataset.data_json["data"]
            assert data[0]["active"] is True
            assert data[1]["active"] is False
            assert data[2]["active"] is True

    @pytest.mark.asyncio
    async def test_change_type_invalid_error_handling(self):
        """Invalid error_handling value raises 400."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await change_type(
                    dataset_id="test-ds-id",
                    request=ChangeTypeRequest(
                        column="age", target_type="integer",
                        error_handling="invalid_mode"
                    ),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
            assert exc_info.value.status_code == 400
            assert "error_handling" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_change_type_invalid_target_type(self):
        """Invalid target type raises 400."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest
        from fastapi import HTTPException

        dataset = _make_mock_dataset(SAMPLE_DATA)
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)):
            with pytest.raises(HTTPException) as exc_info:
                await change_type(
                    dataset_id="test-ds-id",
                    request=ChangeTypeRequest(column="age", target_type="unknown"),
                    current_user=MagicMock(id="user-1"),
                    session=mock_session,
                )
            assert exc_info.value.status_code == 400
            assert "Unknown target type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_change_type_message_includes_error_count(self):
        """Success message includes error count when conversions fail."""
        from app.routers.operations_extra import change_type, ChangeTypeRequest

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "N/A"},
        ])
        mock_session = AsyncMock()

        with patch("app.routers.operations_extra.get_dataset_with_owner_check",
                    side_effect=_make_sync_owner_check(dataset)), \
                _SAVE_PATCH_EXTRA, _DETECT_PATCH, _PREVIEW_PATCH:
            result = await change_type(
                dataset_id="test-ds-id",
                request=ChangeTypeRequest(column="age", target_type="integer"),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )

            assert result.status == "success"
            assert "1 value(s)" in result.message
            assert "null" in result.message

class TestDetectColumnTypeHelper:
    """Test the detect_column_type helper function directly."""

    def test_detect_empty_column(self):
        """Empty column defaults to string."""
        import pandas as pd
        from app.routers.operations_extra import detect_column_type

        s = pd.Series([], dtype=object)
        result = detect_column_type(s)
        assert result["suggested_type"] == "string"
        assert result["total_rows"] == 0

    def test_detect_all_null_column(self):
        """All-null column defaults to string."""
        import pandas as pd
        from app.routers.operations_extra import detect_column_type

        s = pd.Series([None, None, None])
        result = detect_column_type(s)
        assert result["suggested_type"] == "string"
        assert result["null_count"] == 3

    def test_detect_integer_scores(self):
        """Integer detection returns correct scores."""
        import pandas as pd
        from app.routers.operations_extra import detect_column_type

        s = pd.Series(["1", "2", "3", "4", "5"])
        result = detect_column_type(s)
        assert result["type_scores"]["integer"] == 1.0
        assert result["type_scores"]["float"] == 1.0  # integers are valid floats
        # "1" is in _BOOLEAN_VALUES, so boolean score may be > 0 for pure integer series
        assert result["type_scores"]["boolean"] < 0.5  # but should not dominate

    def test_detect_boolean_scores(self):
        """Boolean detection returns correct scores."""
        import pandas as pd
        from app.routers.operations_extra import detect_column_type

        s = pd.Series(["true", "false", "yes", "no"])
        result = detect_column_type(s)
        assert result["type_scores"]["boolean"] == 1.0
        assert result["suggested_type"] == "boolean"

    def test_detect_mixed_scores(self):
        """Mixed data returns low scores for specific types."""
        import pandas as pd
        from app.routers.operations_extra import detect_column_type

        s = pd.Series(["hello", "42", "true", "2024-01-01", "world"])
        result = detect_column_type(s)
        # No single type should dominate
        assert result["type_scores"]["integer"] < 0.8
        assert result["type_scores"]["boolean"] < 0.8
        assert result["suggested_type"] == "string"


class TestConvertColumnHelper:
    """Test the convert_column helper function directly."""

    def test_convert_to_string(self):
        """Converting to string always succeeds."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series([1, 2, 3])
        converted, errors, indices = convert_column(s, "string")
        assert errors == 0
        assert converted.tolist() == ["1", "2", "3"]

    def test_convert_to_integer_with_errors(self):
        """Converting to integer counts errors correctly."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series(["1", "2", "abc", "4"])
        converted, errors, indices = convert_column(s, "integer", "coerce")
        assert errors == 1
        assert len(indices) == 1

    def test_convert_to_integer_raise_mode(self):
        """Raise mode throws ValueError on conversion errors."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series(["1", "2", "abc"])
        with pytest.raises(ValueError):
            convert_column(s, "integer", "raise")

    def test_convert_to_integer_fallback_mode(self):
        """Fallback mode replaces errors with fallback value."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series(["1", "2", "abc", "4"])
        converted, errors, indices = convert_column(s, "integer", "fallback", 0)
        assert errors == 1
        # The error value should be replaced with 0
        assert converted.iloc[2] == 0

    def test_convert_to_boolean_smart_mapping(self):
        """Boolean conversion maps common boolean strings."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series(["yes", "no", "true", "false", "1", "0"])
        converted, errors, indices = convert_column(s, "boolean")
        assert errors == 0
        assert converted.tolist() == [True, False, True, False, True, False]

    def test_convert_to_category(self):
        """Category conversion always succeeds."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series(["a", "b", "c"])
        converted, errors, indices = convert_column(s, "category")
        assert errors == 0
        assert converted.dtype.name == "category"

    def test_convert_unknown_type_raises(self):
        """Unknown target type raises ValueError."""
        import pandas as pd
        from app.routers.operations_extra import convert_column

        s = pd.Series([1, 2, 3])
        with pytest.raises(ValueError):
            convert_column(s, "unknown_type")


class TestGenerateDataLossWarnings:
    """Test the generate_data_loss_warnings helper function."""

    def test_float_to_integer_precision_warning(self):
        """Warns about precision loss when converting float to integer."""
        import pandas as pd
        from app.routers.operations_extra import generate_data_loss_warnings

        s = pd.Series([1.5, 2.7, 3.0])
        warnings = generate_data_loss_warnings(s, "float64", "integer", 0)
        assert any("Precision loss" in w for w in warnings)

    def test_numeric_to_string_warning(self):
        """Warns about losing numeric operations when converting to string."""
        import pandas as pd
        from app.routers.operations_extra import generate_data_loss_warnings

        s = pd.Series([1, 2, 3])
        warnings = generate_data_loss_warnings(s, "int64", "string", 0)
        assert any("numeric operations" in w for w in warnings)

    def test_to_category_warning(self):
        """Warns about category limitations."""
        import pandas as pd
        from app.routers.operations_extra import generate_data_loss_warnings

        s = pd.Series(["a", "b", "c"])
        warnings = generate_data_loss_warnings(s, "object", "category", 0)
        assert any("categories" in w for w in warnings)

    def test_no_warnings_for_safe_conversion(self):
        """No warnings for safe conversions like integer to float."""
        import pandas as pd
        from app.routers.operations_extra import generate_data_loss_warnings

        s = pd.Series([1, 2, 3])
        warnings = generate_data_loss_warnings(s, "int64", "float", 0)
        assert len(warnings) == 0

    def test_error_count_warning(self):
        """Warns about conversion errors."""
        import pandas as pd
        from app.routers.operations_extra import generate_data_loss_warnings

        s = pd.Series(["1", "abc", "3"])
        warnings = generate_data_loss_warnings(s, "object", "integer", 1)
        assert any("1 of 3" in w for w in warnings)

