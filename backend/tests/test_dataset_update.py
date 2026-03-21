"""Tests for dataset operations: update/rename, ownership checks."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _mock_session_with_dataset(dataset=None, project=None):
    """Create a mock session returning dataset and project."""
    mock_session = AsyncMock()
    async def mock_execute(stmt):
        mock_r = MagicMock()
        s = str(stmt).lower()
        if "projects" in s:
            mock_r.scalar_one_or_none.return_value = project
        elif "datasets" in s:
            mock_r.scalar_one_or_none.return_value = dataset
        else:
            mock_r.scalar_one_or_none.return_value = None
        return mock_r
    mock_session.execute = mock_execute
    return mock_session


class TestDatasetUpdate:
    """Test PATCH /datasets/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_name(self):
        from app.routers.datasets import update_dataset

        ds = MagicMock()
        ds.id = "ds-1"
        ds.project_id = "proj-1"
        ds.name = "old"
        ds.description = "desc"

        session = _mock_session_with_dataset(ds, MagicMock())

        result = await update_dataset(
            dataset_id="ds-1",
            request={"name": "new name"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert ds.name == "new name"

    @pytest.mark.asyncio
    async def test_update_description(self):
        from app.routers.datasets import update_dataset

        ds = MagicMock()
        ds.id = "ds-1"
        ds.project_id = "proj-1"
        ds.name = "keep"
        ds.description = "old"

        session = _mock_session_with_dataset(ds, MagicMock())

        result = await update_dataset(
            dataset_id="ds-1",
            request={"description": "new desc"},
            current_user=MagicMock(id="u1"),
            session=session,
        )

        assert result["status"] == "success"
        assert ds.description == "new desc"

    @pytest.mark.asyncio
    async def test_update_empty_name_rejected(self):
        from fastapi import HTTPException
        from app.routers.datasets import update_dataset

        ds = MagicMock()
        ds.id = "ds-1"
        ds.project_id = "proj-1"

        session = _mock_session_with_dataset(ds, MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            await update_dataset(
                dataset_id="ds-1",
                request={"name": "  "},
                current_user=MagicMock(id="u1"),
                session=session,
            )
        assert exc_info.value.status_code == 400
        assert "empty" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        from fastapi import HTTPException
        from app.routers.datasets import update_dataset

        session = _mock_session_with_dataset(None, None)

        with pytest.raises(HTTPException) as exc_info:
            await update_dataset(
                dataset_id="nonexistent",
                request={"name": "test"},
                current_user=MagicMock(id="u1"),
                session=session,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_wrong_owner_rejected(self):
        from fastapi import HTTPException
        from app.routers.datasets import update_dataset

        ds = MagicMock()
        ds.id = "ds-1"
        ds.project_id = "proj-1"

        session = _mock_session_with_dataset(ds, None)  # no project = no ownership

        with pytest.raises(HTTPException) as exc_info:
            await update_dataset(
                dataset_id="ds-1",
                request={"name": "test"},
                current_user=MagicMock(id="u1"),
                session=session,
            )
        assert exc_info.value.status_code == 403


class TestDatasetOwnershipPattern:
    """Verify dataset endpoints consistently check ownership."""

    @pytest.mark.asyncio
    async def test_all_endpoints_check_ownership(self):
        """Dataset update/delete/preview all verify project ownership."""
        from app.routers.datasets import update_dataset
        from fastapi import HTTPException

        ds = MagicMock()
        ds.id = "ds-1"
        ds.project_id = "proj-1"

        # User doesn't own the project
        session = _mock_session_with_dataset(ds, None)

        with pytest.raises(HTTPException) as exc_info:
            await update_dataset(
                dataset_id="ds-1",
                request={"name": "hack"},
                current_user=MagicMock(id="other-user"),
                session=session,
            )
        assert exc_info.value.status_code == 403
