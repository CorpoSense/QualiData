import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test the health check endpoint returns ok status."""
    response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["service"] == "MasterDataCleaner API"


@pytest.mark.asyncio
async def test_health_check_timestamp_is_iso_format(client):
    """Test that timestamp is in ISO format."""
    response = await client.get("/api/health")
    data = response.json()

    # Should be parseable as ISO format
    from datetime import datetime

    datetime.fromisoformat(data["timestamp"])
