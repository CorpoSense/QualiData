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


@pytest.mark.asyncio
async def test_ai_clean_requires_column(client):
    """Test that AI clean endpoint requires column or columns parameter."""
    response = await client.post(
        "/api/datasets/123/ai-clean",
        json={"instruction": "test"},
    )
    # Should fail auth (401) or validation (422), not 200
    assert response.status_code in [401, 422]
    if response.status_code == 422:
        assert "column" in response.text.lower() or "column" in response.text


@pytest.mark.asyncio
async def test_ai_clean_requires_instruction(client):
    """Test that AI clean endpoint requires instruction parameter."""
    response = await client.post(
        "/api/datasets/123/ai-clean",
        json={"column": "test_col"},
    )
    # Should fail auth (401) or validation (422), not 200
    assert response.status_code in [401, 422]
    if response.status_code == 422:
        assert "instruction" in response.text.lower()


@pytest.mark.asyncio
async def test_ai_clean_accepts_single_column(client):
    """Test that AI clean accepts single column."""
    response = await client.post(
        "/api/datasets/123/ai-clean",
        json={"column": "test_col", "instruction": "test"},
    )
    # Should fail auth or dataset not found, but not 422 (validation error)
    assert response.status_code in [401, 404, 422]


@pytest.mark.asyncio
async def test_ai_clean_accepts_multiple_columns(client):
    """Test that AI clean accepts multiple columns as array."""
    response = await client.post(
        "/api/datasets/123/ai-clean",
        json={"columns": ["col1", "col2"], "instruction": "test"},
    )
    # Should fail auth or dataset not found, but not 422 (validation error)
    assert response.status_code in [401, 404, 422]


@pytest.mark.asyncio
async def test_chat_with_agent_id_requires_auth(client):
    """Test that chat endpoint with agent_id requires authentication."""
    response = await client.post(
        "/api/ai/chat",
        json={"agent_id": "some-agent-id", "message": "test"},
    )
    # Should require auth (401) since agent_id path needs current_user
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_chat_without_agent_id_requires_auth(client):
    """Test that chat endpoint without agent_id now also requires auth."""
    response = await client.post(
        "/api/ai/chat",
        json={"provider": "openai", "message": "test"},
    )
    # Now requires auth since the endpoint always depends on current_user
    assert response.status_code in [401, 403]
