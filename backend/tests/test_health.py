import pytest
from unittest.mock import patch


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app
        from fastapi.testclient import TestClient


client = TestClient(app)


def test_health_check():
    """Test the health check endpoint returns ok status."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["service"] == "MasterDataCleaner API"


def test_health_check_timestamp_is_iso_format():
    """Test that timestamp is in ISO format."""
    response = client.get("/api/health")
    data = response.json()

    # Should be parseable as ISO format
    from datetime import datetime

    datetime.fromisoformat(data["timestamp"])
