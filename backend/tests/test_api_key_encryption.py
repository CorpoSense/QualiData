"""Tests for API key encryption in agent CRUD and AI operations."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.crypto import encrypt_value, decrypt_value


# --- Crypto unit tests ---

class TestCrypto:
    """Test encrypt/decrypt round-trip."""

    SECRET = "test-secret-key-for-unit-tests"

    def test_encrypt_decrypt_roundtrip(self):
        original = "sk-abc123def456ghi789"
        encrypted = encrypt_value(original, self.SECRET)
        decrypted = decrypt_value(encrypted, self.SECRET)
        assert decrypted == original

    def test_encrypted_is_not_plaintext(self):
        original = "sk-my-api-key"
        encrypted = encrypt_value(original, self.SECRET)
        assert encrypted != original
        assert "sk-my-api-key" not in encrypted

    def test_different_secrets_fail(self):
        original = "sk-secret-value"
        encrypted = encrypt_value(original, "secret-A")
        with pytest.raises(Exception):
            decrypt_value(encrypted, "secret-B")

    def test_empty_string_roundtrip(self):
        encrypted = encrypt_value("", self.SECRET)
        assert decrypt_value(encrypted, self.SECRET) == ""

    def test_unicode_roundtrip(self):
        original = "clé-api-française-🔑"
        encrypted = encrypt_value(original, self.SECRET)
        assert decrypt_value(encrypted, self.SECRET) == original


# --- Agent create encrypts api_key ---

def _make_mock_user():
    user = MagicMock()
    user.id = "user-1"
    return user


class TestAgentCreateEncryption:
    """Test that creating an agent encrypts the api_key."""

    @pytest.mark.asyncio
    async def test_create_agent_encrypts_api_key(self):
        from app.routers.agents import create_agent

        mock_session = AsyncMock()
        mock_session.refresh = AsyncMock()

        agent_in = MagicMock()
        agent_in.model_dump.return_value = {
            "name": "Test Agent",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "system_prompt": None,
            "prompt_template": None,
            "description": None,
            "is_template": False,
            "is_builtin": False,
            "api_key": "sk-plaintext-key-123",
            "base_url": None,
        }

        with patch("app.routers.agents.get_settings") as mock_settings, \
             patch("app.routers.agents.Agent") as MockAgent:
            mock_settings.return_value.secret_key = "test-secret"
            mock_agent = MagicMock()
            mock_agent.id = "agent-1"
            mock_agent.user_id = "user-1"
            mock_agent.name = "Test Agent"
            mock_agent.provider = "openai"
            mock_agent.model = "gpt-4o-mini"
            mock_agent.temperature = 0.3
            mock_agent.system_prompt = None
            mock_agent.prompt_template = None
            mock_agent.description = None
            mock_agent.is_template = False
            mock_agent.is_builtin = False
            mock_agent.base_url = None
            mock_agent.api_key = None  # Will be set by constructor
            mock_agent.created_at = None
            mock_agent.updated_at = None
            MockAgent.return_value = mock_agent

            await create_agent(
                agent_in=agent_in,
                current_user=_make_mock_user(),
                session=mock_session,
            )

            # Verify Agent was called with an encrypted key, not plaintext
            call_kwargs = MockAgent.call_args[1]
            stored_key = call_kwargs["api_key"]
            assert stored_key != "sk-plaintext-key-123"
            # Verify the stored key can be decrypted back
            assert decrypt_value(stored_key, "test-secret") == "sk-plaintext-key-123"

    @pytest.mark.asyncio
    async def test_create_agent_without_key_stores_none(self):
        from app.routers.agents import create_agent

        mock_session = AsyncMock()
        mock_session.refresh = AsyncMock()

        agent_in = MagicMock()
        agent_in.model_dump.return_value = {
            "name": "No Key Agent",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "system_prompt": None,
            "prompt_template": None,
            "description": None,
            "is_template": False,
            "is_builtin": False,
            "api_key": None,
            "base_url": None,
        }

        with patch("app.routers.agents.get_settings") as mock_settings, \
             patch("app.routers.agents.Agent") as MockAgent:
            mock_settings.return_value.secret_key = "test-secret"
            mock_agent = MagicMock()
            MockAgent.return_value = mock_agent

            await create_agent(
                agent_in=agent_in,
                current_user=_make_mock_user(),
                session=mock_session,
            )

            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["api_key"] is None


# --- Agent update encrypts api_key ---

class TestAgentUpdateEncryption:
    """Test that updating an agent's api_key encrypts it."""

    @pytest.mark.asyncio
    async def test_update_agent_encrypts_api_key(self):
        from app.routers.agents import update_agent

        mock_session = AsyncMock()
        existing_agent = MagicMock()
        existing_agent.api_key = "old-encrypted-key"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_agent
        mock_session.execute = AsyncMock(return_value=mock_result)

        agent_in = MagicMock()
        # Make model_dump(exclude_unset=True) work
        agent_in.model_dump = MagicMock(return_value={"api_key": "sk-new-plaintext-key"})

        with patch("app.routers.agents.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = "test-secret"

            await update_agent(
                agent_id="agent-1",
                agent_in=agent_in,
                current_user=_make_mock_user(),
                session=mock_session,
            )

            # Verify the agent's api_key was set to an encrypted value
            stored_key = existing_agent.api_key
            assert stored_key != "sk-new-plaintext-key"
            assert decrypt_value(stored_key, "test-secret") == "sk-new-plaintext-key"


# --- AI operations decrypt api_key ---

class TestAiOperationsDecryption:
    """Test that _get_agent_config decrypts the api_key."""

    @pytest.mark.asyncio
    async def test_get_agent_config_decrypts_api_key(self):
        from app.routers.ai_operations import _get_agent_config

        secret = "test-secret-key"
        original_key = "sk-real-openai-key-456"
        encrypted_key = encrypt_value(original_key, secret)

        mock_agent = MagicMock()
        mock_agent.provider = "openai"
        mock_agent.model = "gpt-4o-mini"
        mock_agent.temperature = 0.3
        mock_agent.system_prompt = "You are helpful."
        mock_agent.api_key = encrypted_key
        mock_agent.base_url = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.config.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = secret

            config = await _get_agent_config("agent-1", "user-1", mock_session)

            assert config["api_key"] == original_key

    @pytest.mark.asyncio
    async def test_get_agent_config_handles_plain_text_key(self):
        """Legacy plain-text keys should still work (decrypt fails, use as-is)."""
        from app.routers.ai_operations import _get_agent_config

        mock_agent = MagicMock()
        mock_agent.provider = "openai"
        mock_agent.model = "gpt-4o-mini"
        mock_agent.temperature = 0.3
        mock_agent.system_prompt = None
        mock_agent.api_key = "sk-legacy-plain-text-key"
        mock_agent.base_url = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.config.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = "some-secret"

            config = await _get_agent_config("agent-1", "user-1", mock_session)

            # Should fall back to the plain text key
            assert config["api_key"] == "sk-legacy-plain-text-key"

    @pytest.mark.asyncio
    async def test_get_agent_config_handles_none_key(self):
        """Agent with no api_key should return None."""
        from app.routers.ai_operations import _get_agent_config

        mock_agent = MagicMock()
        mock_agent.provider = "ollama"
        mock_agent.model = "llama3.2"
        mock_agent.temperature = 0.3
        mock_agent.system_prompt = None
        mock_agent.api_key = None
        mock_agent.base_url = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        config = await _get_agent_config("agent-1", "user-1", mock_session)
        assert config["api_key"] is None

    @pytest.mark.asyncio
    async def test_get_agent_config_no_agent_id_returns_defaults(self):
        """No agent_id returns default config dict."""
        from app.routers.ai_operations import _get_agent_config

        mock_session = AsyncMock()

        config = await _get_agent_config(None, "user-1", mock_session)
        # _get_agent_config returns a default dict when agent_id is None
        assert config is not None
        assert config["provider"] == "openai"
        assert config["api_key"] is None
        assert config["search_engine_id"] is None
