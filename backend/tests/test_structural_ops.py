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
