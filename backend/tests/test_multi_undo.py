"""Tests for multi-undo: per-operation undo by ID and batch undo."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_mock_dataset():
    ds = MagicMock()
    ds.id = "ds-1"
    ds.project_id = "proj-1"
    ds.columns = [{"name": "a"}]
    ds.data_json = {"data": [{"a": 1}]}
    ds.row_count = 1
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
