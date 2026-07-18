"""Tests for multi-undo: per-operation undo by ID and batch undo."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_mock_dataset(data=None, columns=None):
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.columns = columns if columns is not None else [{"name": "a"}]
    ds.data_json = {"data": data if data is not None else [{"a": 1}]}
    ds.row_count = len(ds.data_json["data"])
    return ds


def _make_mock_op(op_id="op-1", is_undone=False):
    op = MagicMock()
    op.id = op_id
    op.is_undone = is_undone
    op.is_applied = True
    op.before_snapshot = {"columns": [{"name": "a"}], "preview_data": [{"a": 1}]}
    op.operation_type = "test"
    return op


def _make_session_with_dataset_and_ops(dataset, ops=None, single_op=None):
    """Create a mock session that returns dataset, project, and operations."""
    mock_session = AsyncMock()

    async def mock_execute(stmt):
        mock_r = MagicMock()
        s = str(stmt)
        if "projects" in s.lower() or "Project" in s:
            mock_r.scalar_one_or_none.return_value = MagicMock()  # ownership ok
        elif "operation_history" in s.lower() or "OperationHistory" in s:
            if single_op:
                mock_r.scalar_one_or_none.return_value = single_op
            elif ops is not None:
                mock_r.scalars.return_value.all.return_value = ops
            else:
                mock_r.scalar_one_or_none.return_value = None
        elif "datasets" in s.lower() or "Dataset" in s:
            mock_r.scalar_one_or_none.return_value = dataset
        else:
            mock_r.scalar_one_or_none.return_value = None
        return mock_r

    mock_session.execute = mock_execute
    return mock_session


class TestPerOperationUndo:

    @pytest.mark.asyncio
    async def test_undo_by_id(self):
        ds = _make_mock_dataset()
        op = _make_mock_op("op-42")
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        from app.routers.undo_redo import undo_operation

        result = await undo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-42"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert op.is_undone is True
        assert result["operation_id"] == "op-42"

    @pytest.mark.asyncio
    async def test_undo_already_undone_rejected(self):
        from fastapi import HTTPException
        from app.routers.undo_redo import undo_operation

        ds = _make_mock_dataset()
        op = _make_mock_op("op-42", is_undone=True)
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        with pytest.raises(HTTPException) as exc_info:
            await undo_operation(
                dataset_id="ds-1",
                request={"operation_id": "op-42"},
                current_user=MagicMock(id="u1"),
                session=session,
            )

        assert exc_info.value.status_code == 400
        assert "already undone" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_undo_without_id_uses_last(self):
        """When no operation_id, undo the last applied operation."""
        from app.routers.undo_redo import undo_operation

        ds = _make_mock_dataset()
        op = _make_mock_op("last-op")
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        result = await undo_operation(
            dataset_id="ds-1",
            request=None,
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert op.is_undone is True


class TestBatchUndo:

    @pytest.mark.asyncio
    async def test_batch_undo(self):
        from app.routers.undo_redo import undo_batch

        ds = _make_mock_dataset()
        ops = [_make_mock_op("op-1"), _make_mock_op("op-2")]
        session = _make_session_with_dataset_and_ops(ds, ops=ops)

        result = await undo_batch(
            dataset_id="ds-1",
            request={"operation_ids": ["op-1", "op-2"]},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert len(result["undone"]) == 2
        assert all(op.is_undone for op in ops)

    @pytest.mark.asyncio
    async def test_batch_undo_empty_list_rejected(self):
        from fastapi import HTTPException
        from app.routers.undo_redo import undo_batch

        ds = _make_mock_dataset()
        session = _make_session_with_dataset_and_ops(ds, ops=[])

        with pytest.raises(HTTPException):
            await undo_batch(
                dataset_id="ds-1",
                request={"operation_ids": []},
                current_user=MagicMock(id="u1"),
                session=session,
            )


class TestRestoreSnapshot:
    """Regression tests for _restore_snapshot helper (Bug #1-#3 fixes)."""

    def test_restore_with_data_key(self):
        """Snapshot with 'data' key restores data_json correctly."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset(data=[{"a": 99}])
        snapshot = {
            "columns": [{"name": "a", "dtype": "integer"}],
            "row_count": 3,
            "data": [{"a": 1}, {"a": 2}, {"a": 3}],
        }
        _restore_snapshot(ds, snapshot)
        assert ds.data_json["data"] == [{"a": 1}, {"a": 2}, {"a": 3}]
        assert ds.columns == [{"name": "a", "dtype": "integer"}]
        assert ds.row_count == 3

    def test_restore_with_preview_data_backward_compat(self):
        """Legacy 'preview_data' key is used as fallback when 'data' is absent."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset(data=[{"a": 99}])
        snapshot = {
            "columns": [{"name": "a"}],
            "preview_data": [{"a": 10}, {"a": 20}],
        }
        _restore_snapshot(ds, snapshot)
        # preview_data should be used as the data fallback
        assert ds.data_json["data"] == [{"a": 10}, {"a": 20}]

    def test_restore_with_none_snapshot(self):
        """None snapshot does not crash (Bug #1 fix)."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset()
        original_data = ds.data_json["data"]
        original_columns = ds.columns
        _restore_snapshot(ds, None)
        # Nothing should change
        assert ds.data_json["data"] == original_data
        assert ds.columns == original_columns

    def test_restore_preserves_charts_key(self):
        """Restoring data_json preserves existing 'charts' key (Bug #3 fix)."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset(data=[{"a": 1}])
        ds.data_json = {"data": [{"a": 1}], "charts": [{"type": "bar", "id": "c1"}]}

        snapshot = {
            "columns": [{"name": "a"}],
            "data": [{"a": 100}],
        }
        _restore_snapshot(ds, snapshot)
        assert ds.data_json["data"] == [{"a": 100}]
        assert ds.data_json["charts"] == [{"type": "bar", "id": "c1"}]

    def test_restore_with_columns_only(self):
        """Snapshot with only 'columns' (no data) updates columns without crashing."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset()
        snapshot = {"columns": [{"name": "b"}]}
        _restore_snapshot(ds, snapshot)
        assert ds.columns == [{"name": "b"}]
        # data_json should remain unchanged
        assert ds.data_json["data"] == [{"a": 1}]

    def test_restore_with_empty_snapshot(self):
        """Empty dict snapshot does nothing."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset()
        _restore_snapshot(ds, {})
        assert ds.data_json["data"] == [{"a": 1}]

    def test_restore_with_data_key_priority_over_preview(self):
        """When both 'data' and 'preview_data' exist, 'data' takes priority."""
        from app.routers.undo_redo import _restore_snapshot

        ds = _make_mock_dataset(data=[{"a": 99}])
        snapshot = {
            "columns": [{"name": "a"}],
            "data": [{"a": 1}],
            "preview_data": [{"a": 2}],
        }
        _restore_snapshot(ds, snapshot)
        assert ds.data_json["data"] == [{"a": 1}]


class TestUndoRedoDataRestoration:
    """End-to-end undo/redo tests verifying data is actually restored."""

    @pytest.mark.asyncio
    async def test_undo_restores_data_from_snapshot(self):
        """Undo should restore data_json from before_snapshot."""
        from app.routers.undo_redo import undo_operation

        ds = _make_mock_dataset(data=[{"a": 1}, {"a": 2}])
        op = _make_mock_op("op-1")
        op.before_snapshot = {
            "columns": [{"name": "a"}],
            "row_count": 2,
            "data": [{"a": 1}, {"a": 2}],
        }
        op.is_undone = False
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        # Simulate data was modified (current state different from snapshot)
        ds.data_json = {"data": [{"a": 10}, {"a": 20}]}

        result = await undo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-1"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert ds.data_json["data"] == [{"a": 1}, {"a": 2}]
        assert op.is_undone is True

    @pytest.mark.asyncio
    async def test_redo_restores_data_from_snapshot(self):
        """Redo should restore data_json from after_snapshot."""
        from app.routers.undo_redo import redo_operation

        ds = _make_mock_dataset(data=[{"a": 1}, {"a": 2}])
        op = _make_mock_op("op-1", is_undone=True)
        op.after_snapshot = {
            "columns": [{"name": "a"}],
            "row_count": 2,
            "data": [{"a": 10}, {"a": 20}],
        }
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        result = await redo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-1"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert ds.data_json["data"] == [{"a": 10}, {"a": 20}]
        assert op.is_undone is False

    @pytest.mark.asyncio
    async def test_undo_with_null_snapshot_no_crash(self):
        """Undo with None before_snapshot should not crash (Bug #1 fix)."""
        from app.routers.undo_redo import undo_operation

        ds = _make_mock_dataset(data=[{"a": 1}])
        op = _make_mock_op("op-1")
        op.before_snapshot = None
        op.is_undone = False
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        result = await undo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-1"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        # data should remain unchanged since snapshot is None
        assert ds.data_json["data"] == [{"a": 1}]

    @pytest.mark.asyncio
    async def test_undo_preserves_charts(self):
        """Undo should preserve the 'charts' key in data_json."""
        from app.routers.undo_redo import undo_operation

        ds = _make_mock_dataset(data=[{"a": 1}])
        ds.data_json = {"data": [{"a": 1}], "charts": [{"type": "pie"}]}
        op = _make_mock_op("op-1")
        op.before_snapshot = {
            "columns": [{"name": "a"}],
            "data": [{"a": 100}],
        }
        op.is_undone = False
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        result = await undo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-1"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert ds.data_json["data"] == [{"a": 100}]
        assert ds.data_json["charts"] == [{"type": "pie"}]

    @pytest.mark.asyncio
    async def test_undo_redo_full_cycle(self):
        """Full undo/redo cycle: undo restores before, redo restores after."""
        from app.routers.undo_redo import undo_operation, redo_operation

        ds = _make_mock_dataset(data=[{"a": 1}])
        op = _make_mock_op("op-1")
        op.before_snapshot = {
            "columns": [{"name": "a"}],
            "row_count": 1,
            "data": [{"a": 1}],
        }
        op.after_snapshot = {
            "columns": [{"name": "a"}],
            "row_count": 1,
            "data": [{"a": 10}],
        }

        # Current state is "after" state
        ds.data_json = {"data": [{"a": 10}]}
        session = _make_session_with_dataset_and_ops(ds, single_op=op)

        # Undo
        result = await undo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-1"},
            current_user=MagicMock(id="u1"),
            session=session,
        )
        assert result["status"] == "success"
        assert ds.data_json["data"] == [{"a": 1}]
        assert op.is_undone is True

        # Redo
        session2 = _make_session_with_dataset_and_ops(ds, single_op=op)
        result2 = await redo_operation(
            dataset_id="ds-1",
            request={"operation_id": "op-1"},
            current_user=MagicMock(id="u1"),
            session=session2,
        )
        assert result2["status"] == "success"
        assert ds.data_json["data"] == [{"a": 10}]
        assert op.is_undone is False
