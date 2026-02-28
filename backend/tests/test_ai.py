import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest_asyncio.fixture
async def client():
    """Create an async test client."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_list_providers(client):
    """Test listing AI providers."""
    response = await client.get("/api/ai/providers")

    assert response.status_code == 200
    data = response.json()

    assert "providers" in data
    providers = data["providers"]

    # Check that we have the expected providers
    provider_names = [p["provider"] for p in providers]
    assert "openai" in provider_names
    assert "anthropic" in provider_names
    assert "google" in provider_names
    assert "ollama" in provider_names
    assert "groq" in provider_names
    assert "deepseek" in provider_names
    assert "openrouter" in provider_names  # New!


@pytest.mark.asyncio
async def test_analyze_invalid_provider(client):
    """Test that invalid provider returns 400."""
    response = await client.post(
        "/api/ai/analyze",
        json={
            "provider": "invalid_provider",
            "data_summary": "test data",
        },
    )

    assert response.status_code == 400
    assert "Invalid provider" in response.json()["detail"]
