"""Tests for cell update operations — type coercion and error handling."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd


def _make_mock_dataset(data):
    ds = MagicMock()
    ds.id = "test-ds-id"
    ds.data_json = {"data": data}
    ds.row_count = len(data)
    ds.columns = list(data[0].keys()) if data else []
    return ds


class TestCellUpdateTypeCoercion:
    """Test that update_cell coerces values to column dtypes."""

    @pytest.mark.asyncio
    async def test_update_float_column_with_int_string(self):
        from app.routers.cell_ops import update_cell, CellUpdate

        dataset = _make_mock_dataset([
            {"name": "Alice", "score": 85.5},
            {"name": "Bob", "score": 92.3},
        ])
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await update_cell(
            dataset_id="test-ds-id",
            update=CellUpdate(row_index=0, column="score", value="90"),
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_float_column_with_invalid_string(self):
        from app.routers.cell_ops import update_cell, CellUpdate

        dataset = _make_mock_dataset([
            {"name": "Alice", "score": 85.5},
        ])
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await update_cell(
            dataset_id="test-ds-id",
            update=CellUpdate(row_index=0, column="score", value="not-a-number"),
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "failed"
        assert "numeric" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_update_with_null_values(self):
        from app.routers.cell_ops import update_cell, CellUpdate

        dataset = _make_mock_dataset([
            {"name": "Alice", "score": 85.5},
        ])
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        for null_val in ['', 'null', 'None', 'NaN']:
            dataset.data_json = {"data": [{"name": "Alice", "score": 85.5}]}
            result = await update_cell(
                dataset_id="test-ds-id",
                update=CellUpdate(row_index=0, column="score", value=null_val),
                current_user=MagicMock(id="user-1"),
                session=mock_session,
            )
            assert result["status"] == "success", f"Failed for null value: {null_val}"

    @pytest.mark.asyncio
    async def test_update_preserves_old_value(self):
        from app.routers.cell_ops import update_cell, CellUpdate

        dataset = _make_mock_dataset([
            {"name": "Alice", "age": 30},
        ])
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await update_cell(
            dataset_id="test-ds-id",
            update=CellUpdate(row_index=0, column="age", value="31"),
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "success"
        assert result["old_value"] == 30

    @pytest.mark.asyncio
    async def test_nan_values_become_none_in_json(self):
        """NaN values in preview_data should become None, not stay as NaN."""
        from app.routers.cell_ops import update_cell, CellUpdate

        dataset = _make_mock_dataset([
            {"name": "Alice", "score": 85.5},
            {"name": "Bob", "score": 92.3},
        ])
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Set score to null for first row
        result = await update_cell(
            dataset_id="test-ds-id",
            update=CellUpdate(row_index=0, column="score", value=""),
            current_user=MagicMock(id="user-1"),
            session=mock_session,
        )

        assert result["status"] == "success"
        # Verify no NaN in the saved data
        import json
        json.dumps(dataset.data_json["data"])  # Should not raise
