"""Tests for embedded chart persistence endpoints (charts inside data_json)."""

import os
from unittest.mock import MagicMock, AsyncMock

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_async_session
from app.routers.auth import get_current_active_user

client = TestClient(app)


# --- Helpers ---


def _mock_user():
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.is_active = True
    return user


def _mock_dataset(dataset_id="ds-1", project_id="proj-1", data_json=None):
    ds = MagicMock()
    ds.id = dataset_id
    ds.project_id = project_id
    ds.row_count = 100
    ds.columns = [{"name": "col_a", "dtype": "string"}, {"name": "col_b", "dtype": "integer"}]
    ds.data_json = data_json if data_json is not None else {"data": [{"col_a": "x", "col_b": 1}]}
    return ds


def _mock_project(project_id="proj-1", user_id="test-user-id"):
    p = MagicMock()
    p.id = project_id
    p.user_id = user_id
    return p


def _build_session(dataset=None, project=None):
    """Build a mock session with deterministic query routing."""
    session = MagicMock()

    async def execute(query):
        result = MagicMock()
        q = str(query).lower()

        if "from datasets" in q or "into datasets" in q:
            result.scalar_one_or_none.return_value = dataset
        elif "from projects" in q or "into projects" in q:
            result.scalar_one_or_none.return_value = project
        else:
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []

        return result

    session.execute = AsyncMock(side_effect=execute)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = MagicMock()
    return session


_SENTINEL = object()

def _setup(dataset=_SENTINEL, project=_SENTINEL):
    """Set up dependency overrides. Pass _SENTINEL (default) for a normal dataset."""
    ds = _mock_dataset() if dataset is _SENTINEL else dataset
    proj = _mock_project() if project is _SENTINEL else project
    app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
    app.dependency_overrides[get_async_session] = lambda: _build_session(
        dataset=ds, project=proj
    )


def _teardown():
    app.dependency_overrides.clear()


# --- Tests ---


class TestListChartsEmbedded:
    def test_requires_auth(self):
        res = client.get("/api/datasets/ds-1/charts")
        assert res.status_code == 401

    def test_empty_when_no_charts_key(self):
        _setup(dataset=_mock_dataset(data_json={"data": []}))
        try:
            res = client.get("/api/datasets/ds-1/charts")
            assert res.status_code == 200
            assert res.json()["charts"] == []
        finally:
            _teardown()

    def test_returns_saved_charts(self):
        charts = [
            {"id": "c1", "config": {"chartType": "bar", "xAxis": "col_a"}, "meta": {}},
            {"id": "c2", "config": {"chartType": "line", "xAxis": "col_b"}, "meta": {}},
        ]
        _setup(dataset=_mock_dataset(data_json={"data": [], "charts": charts}))
        try:
            res = client.get("/api/datasets/ds-1/charts")
            assert res.status_code == 200
            data = res.json()
            assert len(data["charts"]) == 2
            assert data["charts"][0]["config"]["chartType"] == "bar"
            assert data["charts"][1]["config"]["chartType"] == "line"
        finally:
            _teardown()

    def test_empty_when_data_json_is_none(self):
        _setup(dataset=_mock_dataset(data_json=None))
        try:
            res = client.get("/api/datasets/ds-1/charts")
            assert res.status_code == 200
            assert res.json()["charts"] == []
        finally:
            _teardown()

    def test_dataset_not_found(self):
        _setup(dataset=None)
        try:
            res = client.get("/api/datasets/nonexistent/charts")
            assert res.status_code == 404
        finally:
            _teardown()


class TestSaveChartsEmbedded:
    def test_requires_auth(self):
        res = client.put("/api/datasets/ds-1/charts", json={"charts": []})
        assert res.status_code == 401

    def test_save_charts_to_empty_data_json(self):
        session = MagicMock()
        ds = _mock_dataset(data_json={"data": [{"col_a": "x", "col_b": 1}]})

        async def execute(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            charts = [{"config": {"chartType": "bar", "xAxis": "col_a"}, "meta": {}}]
            res = client.put("/api/datasets/ds-1/charts", json={"charts": charts})
            assert res.status_code == 200
            data = res.json()
            assert len(data["charts"]) == 1
            assert data["charts"][0]["config"]["chartType"] == "bar"
            # Verify data_json was updated
            assert "charts" in ds.data_json
            assert "data" in ds.data_json
            assert ds.data_json["data"] == [{"col_a": "x", "col_b": 1}]
            session.commit.assert_called()
        finally:
            _teardown()

    def test_replace_existing_charts(self):
        existing_charts = [{"id": "old", "config": {"chartType": "pie"}, "meta": {}}]
        ds = _mock_dataset(data_json={"data": [], "charts": existing_charts})
        session = MagicMock()

        async def execute(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            new_charts = [
                {"config": {"chartType": "line", "xAxis": "col_a"}, "meta": {}},
                {"config": {"chartType": "scatter", "xAxis": "col_b"}, "meta": {}},
            ]
            res = client.put("/api/datasets/ds-1/charts", json={"charts": new_charts})
            assert res.status_code == 200
            data = res.json()
            assert len(data["charts"]) == 2
            assert data["charts"][0]["config"]["chartType"] == "line"
        finally:
            _teardown()

    def test_clear_all_charts(self):
        existing_charts = [{"id": "c1", "config": {"chartType": "bar"}, "meta": {}}]
        ds = _mock_dataset(data_json={"data": [], "charts": existing_charts})
        session = MagicMock()

        async def execute(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            res = client.put("/api/datasets/ds-1/charts", json={"charts": []})
            assert res.status_code == 200
            data = res.json()
            assert data["charts"] == []
            assert ds.data_json["charts"] == []
        finally:
            _teardown()

    def test_preserves_data_key(self):
        original_data = [{"col_a": "hello", "col_b": 42}]
        ds = _mock_dataset(data_json={"data": original_data})
        session = MagicMock()

        async def execute(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            charts = [{"config": {"chartType": "bar", "xAxis": "col_a"}, "meta": {}}]
            res = client.put("/api/datasets/ds-1/charts", json={"charts": charts})
            assert res.status_code == 200
            # Data must be preserved
            assert ds.data_json["data"] == original_data
        finally:
            _teardown()

    def test_dataset_not_found(self):
        _setup(dataset=None)
        try:
            res = client.put("/api/datasets/nonexistent/charts", json={"charts": []})
            assert res.status_code == 404
        finally:
            _teardown()

    def test_save_empty_array(self):
        ds = _mock_dataset(data_json={"data": []})
        session = MagicMock()

        async def execute(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            res = client.put("/api/datasets/ds-1/charts", json={"charts": []})
            assert res.status_code == 200
            assert res.json()["charts"] == []
        finally:
            _teardown()

    def test_multiple_charts_preserve_order(self):
        ds = _mock_dataset(data_json={"data": []})
        session = MagicMock()

        async def execute(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            charts = [
                {"config": {"chartType": "bar", "xAxis": "a"}, "meta": {"order": 0}},
                {"config": {"chartType": "line", "xAxis": "b"}, "meta": {"order": 1}},
                {"config": {"chartType": "pie", "xAxis": "c"}, "meta": {"order": 2}},
            ]
            res = client.put("/api/datasets/ds-1/charts", json={"charts": charts})
            assert res.status_code == 200
            data = res.json()
            assert len(data["charts"]) == 3
            assert data["charts"][0]["config"]["chartType"] == "bar"
            assert data["charts"][1]["config"]["chartType"] == "line"
            assert data["charts"][2]["config"]["chartType"] == "pie"
        finally:
            _teardown()

    def test_persisted_after_read(self):
        """Regression: verify charts survive a PUT→commit→GET round-trip."""
        charts = [
            {"config": {"chartType": "bar", "xAxis": "col_a"}, "meta": {}},
        ]
        ds = _mock_dataset(data_json={"data": [{"col_a": "x"}]})

        session = MagicMock()

        # First call (PUT): update data_json with charts
        put_committed = []

        async def execute_put(query):
            result = MagicMock()
            q = str(query).lower()
            if "from datasets" in q or "into datasets" in q:
                result.scalar_one_or_none.return_value = ds
            elif "from projects" in q or "into projects" in q:
                result.scalar_one_or_none.return_value = _mock_project()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        call_count = [0]

        async def commit_side_effect():
            call_count[0] += 1
            put_committed.append(ds.data_json.copy())

        session.execute = AsyncMock(side_effect=execute_put)
        session.commit = AsyncMock(side_effect=commit_side_effect)
        session.refresh = AsyncMock()

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session

        try:
            # 1. PUT to save charts
            res = client.put("/api/datasets/ds-1/charts", json={"charts": charts})
            assert res.status_code == 200

            # 2. Verify data_json was updated in-memory
            assert "charts" in ds.data_json
            assert ds.data_json["charts"] == charts

            # 3. Verify commit was called (persistence happened)
            assert session.commit.called
            assert len(put_committed) == 1
        finally:
            _teardown()
