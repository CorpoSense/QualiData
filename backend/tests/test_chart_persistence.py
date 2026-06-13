"""Tests for chart persistence endpoints."""

import os
import re
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_async_session
from app.routers.auth import get_current_active_user

client = TestClient(app)


# --- Simple chart class (avoids MagicMock attribute quirks) ---

class FakeChart:
    def __init__(self, chart_id="chart-1", dataset_id="ds-1", sort_order=0):
        self.id = chart_id
        self.dataset_id = dataset_id
        self.sort_order = sort_order
        self.config = {
            "chartType": "bar",
            "xAxis": "col_a",
            "yAxis": "col_b",
            "aggregation": "sum",
            "colorPalette": "default",
            "title": "My Bar Chart",
            "showLegend": True,
            "showGrid": True,
        }
        self.meta = {"title": "My Bar Chart"}
        self.created_at = datetime(2026, 1, 1)


# --- Helpers ---

def _mock_user():
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.is_active = True
    return user


def _mock_dataset(dataset_id="ds-1", project_id="proj-1"):
    ds = MagicMock()
    ds.id = dataset_id
    ds.project_id = project_id
    ds.row_count = 100
    ds.columns = [{"name": "col_a"}, {"name": "col_b"}]
    return ds


def _mock_project(project_id="proj-1", user_id="test-user-id"):
    p = MagicMock()
    p.id = project_id
    p.user_id = user_id
    return p


def _build_session(dataset=None, project=None, chart=None):
    """Build a mock session with deterministic query routing."""
    session = MagicMock()

    async def execute(query):
        result = MagicMock()
        q = str(query).lower()

        table_match = re.search(r'\b(?:from|into)\s+(\w+)', q)
        table_name = table_match.group(1) if table_match else ""

        if table_name == "datasets":
            result.scalar_one_or_none.return_value = dataset
        elif table_name == "projects":
            result.scalar_one_or_none.return_value = project
        elif table_name == "charts":
            if isinstance(chart, list):
                result.scalars.return_value.all.return_value = chart
            elif chart is not None:
                result.scalar_one_or_none.return_value = chart
            else:
                result.scalar_one_or_none.return_value = None
                result.scalars.return_value.all.return_value = []
        else:
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []

        return result

    session.execute = AsyncMock(side_effect=execute)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = MagicMock()

    def _refresh_side_effect(obj):
        """Simulate refresh by returning None (no-op for tests)."""
        pass

    session.refresh = AsyncMock(side_effect=_refresh_side_effect)
    return session


def _setup(dataset=None, project=None, chart=None):
    """Set up dependency overrides."""
    app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
    app.dependency_overrides[get_async_session] = lambda: _build_session(
        dataset=dataset, project=project, chart=chart
    )


def _teardown():
    app.dependency_overrides.clear()


# --- Tests ---

class TestListCharts:
    def test_requires_auth(self):
        res = client.get("/api/datasets/ds-1/charts")
        assert res.status_code == 401

    def test_empty(self):
        _setup(dataset=_mock_dataset(), project=_mock_project(), chart=[])
        try:
            res = client.get("/api/datasets/ds-1/charts")
            assert res.status_code == 200
            assert res.json()["charts"] == []
        finally:
            _teardown()

    def test_returns_saved(self):
        chart = FakeChart()
        _setup(dataset=_mock_dataset(), project=_mock_project(), chart=[chart])
        try:
            res = client.get("/api/datasets/ds-1/charts")
            assert res.status_code == 200
            charts = res.json()["charts"]
            assert len(charts) == 1
            assert charts[0]["config"]["chartType"] == "bar"
        finally:
            _teardown()


class TestCreateChart:
    def test_requires_auth(self):
        res = client.post("/api/datasets/ds-1/charts", json={"config": {}})
        assert res.status_code == 401

    def test_success(self):
        session = MagicMock()
        async def execute(q):
            result = MagicMock()
            q_str = str(q).lower()
            table_match = re.search(r'\b(?:from|into)\s+(\w+)', q_str)
            tn = table_match.group(1) if table_match else ""
            if tn == "datasets":
                result.scalar_one_or_none.return_value = _mock_dataset()
            elif tn == "projects":
                result.scalar_one_or_none.return_value = _mock_project()
            elif tn == "charts":
                # For the "last chart" query, return None (no existing charts)
                result.scalar_one_or_none.return_value = None
            return result
        session.execute = AsyncMock(side_effect=execute)
        session.add = MagicMock()
        session.commit = AsyncMock()

        async def fake_refresh(chart_obj):
            # Simulate refresh by not changing anything
            pass
        session.refresh = fake_refresh

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            payload = {
                "config": {
                    "chartType": "line", "xAxis": "date", "yAxis": "revenue",
                    "aggregation": "sum", "colorPalette": "viridis",
                },
                "meta": {"title": "Revenue"},
            }
            res = client.post("/api/datasets/ds-1/charts", json=payload)
            assert res.status_code == 201
            data = res.json()
            assert data["config"]["chartType"] == "line"
            assert "id" in data
            session.add.assert_called_once()
            session.commit.assert_called()
        finally:
            _teardown()

    def test_missing_config(self):
        _setup(dataset=_mock_dataset(), project=_mock_project())
        try:
            res = client.post("/api/datasets/ds-1/charts", json={})
            assert res.status_code == 422
        finally:
            _teardown()

    def test_dataset_not_found(self):
        _setup(dataset=None)
        try:
            res = client.post(
                "/api/datasets/ds-1/charts",
                json={"config": {"chartType": "bar", "xAxis": "a"}},
            )
            assert res.status_code == 404
        finally:
            _teardown()


class TestUpdateChart:
    def test_requires_auth(self):
        res = client.put("/api/datasets/ds-1/charts/chart-1", json={"config": {}})
        assert res.status_code == 401

    def test_success(self):
        chart = FakeChart()
        _setup(dataset=_mock_dataset(), project=_mock_project(), chart=chart)
        try:
            res = client.put(
                "/api/datasets/ds-1/charts/chart-1",
                json={"config": {"chartType": "pie", "xAxis": "col_a"}},
            )
            assert res.status_code == 200
            assert res.json()["config"]["chartType"] == "pie"
        finally:
            _teardown()

    def test_not_found(self):
        _setup(dataset=_mock_dataset(), project=_mock_project(), chart=None)
        try:
            res = client.put(
                "/api/datasets/ds-1/charts/chart-1",
                json={"config": {"chartType": "pie"}},
            )
            assert res.status_code == 404
        finally:
            _teardown()


class TestDeleteChart:
    def test_requires_auth(self):
        res = client.delete("/api/datasets/ds-1/charts/chart-1")
        assert res.status_code == 401

    def test_success(self):
        session = MagicMock()
        chart = FakeChart()
        deleted_chart = []

        async def execute(q):
            result = MagicMock()
            q_str = str(q).lower()
            table_match = re.search(r'\b(?:from|into)\s+(\w+)', q_str)
            tn = table_match.group(1) if table_match else ""
            if tn == "datasets":
                result.scalar_one_or_none.return_value = _mock_dataset()
            elif tn == "projects":
                result.scalar_one_or_none.return_value = _mock_project()
            elif tn == "charts":
                result.scalar_one_or_none.return_value = chart
            return result
        session.execute = AsyncMock(side_effect=execute)
        session.commit = AsyncMock()

        def fake_delete(obj):
            deleted_chart.append(obj)
        session.delete = fake_delete

        app.dependency_overrides[get_current_active_user] = lambda: _mock_user()
        app.dependency_overrides[get_async_session] = lambda: session
        try:
            res = client.delete("/api/datasets/ds-1/charts/chart-1")
            assert res.status_code == 204
            assert len(deleted_chart) == 1
            assert deleted_chart[0] is chart
            session.commit.assert_called()
        finally:
            _teardown()

    def test_not_found(self):
        _setup(dataset=_mock_dataset(), project=_mock_project(), chart=None)
        try:
            res = client.delete("/api/datasets/ds-1/charts/chart-1")
            assert res.status_code == 404
        finally:
            _teardown()


class TestReorderCharts:
    def test_requires_auth(self):
        res = client.put("/api/datasets/ds-1/charts/reorder", json={"chart_ids": []})
        assert res.status_code == 401

    def test_success(self):
        c1 = FakeChart(chart_id="c1", sort_order=0)
        c2 = FakeChart(chart_id="c2", sort_order=1)
        _setup(dataset=_mock_dataset(), project=_mock_project(), chart=[c1, c2])
        try:
            res = client.put(
                "/api/datasets/ds-1/charts/reorder",
                json={"chart_ids": ["c2", "c1"]},
            )
            assert res.status_code == 200
            assert c1.sort_order == 1
            assert c2.sort_order == 0
        finally:
            _teardown()