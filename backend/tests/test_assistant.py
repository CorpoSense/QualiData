"""Tests for the AI Assistant preflight and suggest endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_mock_user():
    user = MagicMock()
    user.id = "user-1"
    return user


class TestPreflightEndpoint:
    """Test the /assistant/ai-suggest/preflight endpoint."""

    @pytest.mark.asyncio
    async def test_preflight_requires_agent_id(self):
        from app.routers.assistant import ai_suggest_preflight
        from fastapi import HTTPException

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await ai_suggest_preflight(
                request={},
                current_user=_make_mock_user(),
                session=mock_session,
            )
        assert exc_info.value.status_code == 400
        assert "agent_id" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_preflight_returns_agent_info(self):
        from app.routers.assistant import ai_suggest_preflight

        mock_agent = MagicMock()
        mock_agent.id = "agent-1"
        mock_agent.name = "My Agent"
        mock_agent.provider = "openai"
        mock_agent.model = "gpt-4o-mini"
        mock_agent.system_prompt = "You are helpful."
        mock_agent.api_key = None
        mock_agent.base_url = None
        mock_agent.temperature = 0.3

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config:
            mock_config.return_value = {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "system_prompt": "You are helpful.",
                "api_key": None,
                "base_url": None,
            }

            result = await ai_suggest_preflight(
                request={"agent_id": "agent-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        assert result["agent_name"] == "My Agent"
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o-mini"
        assert result["system_prompt"] == "You are helpful."

    @pytest.mark.asyncio
    async def test_preflight_returns_available_operations(self):
        from app.routers.assistant import ai_suggest_preflight

        mock_agent = MagicMock()
        mock_agent.name = "Test Agent"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config:
            mock_config.return_value = {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3, "system_prompt": None, "api_key": None, "base_url": None}

            result = await ai_suggest_preflight(
                request={"agent_id": "agent-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        ops = result["available_operations"]
        assert len(ops) > 0
        op_names = [o["operation"] for o in ops]
        assert "fillna" in op_names
        assert "remove-duplicates" in op_names
        assert "find-replace" in op_names

    @pytest.mark.asyncio
    async def test_preflight_returns_prompt_presets(self):
        from app.routers.assistant import ai_suggest_preflight

        mock_agent = MagicMock()
        mock_agent.name = "Test Agent"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config:
            mock_config.return_value = {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3, "system_prompt": None, "api_key": None, "base_url": None}

            result = await ai_suggest_preflight(
                request={"agent_id": "agent-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        presets = result["prompt_presets"]
        assert len(presets) >= 3
        preset_ids = [p["id"] for p in presets]
        assert "quality" in preset_ids
        assert "formatting" in preset_ids
        assert "cleanup" in preset_ids

    @pytest.mark.asyncio
    async def test_preflight_falls_back_to_default_system_prompt(self):
        """When agent has no system_prompt, use the default."""
        from app.routers.assistant import ai_suggest_preflight

        mock_agent = MagicMock()
        mock_agent.name = "Test Agent"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config:
            mock_config.return_value = {"provider": "ollama", "model": "llama3.2", "temperature": 0.3, "system_prompt": None, "api_key": None, "base_url": None}

            result = await ai_suggest_preflight(
                request={"agent_id": "agent-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        assert "data cleaning" in result["system_prompt"].lower()


class TestAiSuggestCustomPrompts:
    """Test that ai-suggest accepts custom prompt overrides."""

    @pytest.mark.asyncio
    async def test_suggest_accepts_custom_system_prompt(self):
        """Custom system_prompt in request should be used."""
        from app.routers.assistant import ai_suggest_operations

        mock_dataset = MagicMock()
        mock_dataset.id = "ds-1"
        mock_dataset.project_id = "proj-1"
        mock_dataset.data_json = {"data": [{"name": "Alice"}, {"name": "Bob"}]}
        mock_dataset.columns = [{"name": "name"}]
        mock_dataset.description = None

        mock_project = MagicMock()

        mock_ds_result = MagicMock()
        mock_ds_result.scalar_one_or_none.return_value = mock_dataset

        mock_proj_result = MagicMock()
        mock_proj_result.scalar_one_or_none.return_value = mock_project

        call_count = [0]

        async def mock_execute(query):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_ds_result
            return mock_proj_result

        mock_session = AsyncMock()
        mock_session.execute = mock_execute

        # Capture what gets sent to the LLM
        captured_messages = []

        async def mock_invoke(messages):
            captured_messages.extend(messages)
            mock_resp = MagicMock()
            mock_resp.content = '{"suggestions": []}'
            return mock_resp

        mock_llm = MagicMock()
        mock_llm.ainvoke = mock_invoke

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config, \
             patch("app.services.ai_provider.get_chat_model", return_value=mock_llm), \
             patch("app.services.ai_provider.AIProvider"):

            mock_config.return_value = {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3, "system_prompt": None, "api_key": None, "base_url": None}

            result = await ai_suggest_operations(
                request={"dataset_id": "ds-1", "agent_id": "agent-1", "system_prompt": "Custom system prompt for testing"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        # Verify the custom system prompt was used
        from langchain_core.messages import SystemMessage
        system_msgs = [m for m in captured_messages if isinstance(m, SystemMessage)]
        assert len(system_msgs) == 1
        assert system_msgs[0].content == "Custom system prompt for testing"

    @pytest.mark.asyncio
    async def test_suggest_accepts_custom_user_prompt(self):
        """Custom user_prompt should be prepended to the context."""
        from app.routers.assistant import ai_suggest_operations

        mock_dataset = MagicMock()
        mock_dataset.id = "ds-1"
        mock_dataset.project_id = "proj-1"
        mock_dataset.data_json = {"data": [{"name": "Alice"}]}
        mock_dataset.columns = [{"name": "name"}]
        mock_dataset.description = None

        mock_project = MagicMock()

        mock_ds_result = MagicMock()
        mock_ds_result.scalar_one_or_none.return_value = mock_dataset

        mock_proj_result = MagicMock()
        mock_proj_result.scalar_one_or_none.return_value = mock_project

        call_count = [0]

        async def mock_execute(query):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_ds_result
            return mock_proj_result

        mock_session = AsyncMock()
        mock_session.execute = mock_execute

        captured_messages = []

        async def mock_invoke(messages):
            captured_messages.extend(messages)
            mock_resp = MagicMock()
            mock_resp.content = '{"suggestions": []}'
            return mock_resp

        mock_llm = MagicMock()
        mock_llm.ainvoke = mock_invoke

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config, \
             patch("app.services.ai_provider.get_chat_model", return_value=mock_llm), \
             patch("app.services.ai_provider.AIProvider"):

            mock_config.return_value = {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3, "system_prompt": None, "api_key": None, "base_url": None}

            result = await ai_suggest_operations(
                request={"dataset_id": "ds-1", "agent_id": "agent-1", "user_prompt": "Focus on the name column"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        from langchain_core.messages import HumanMessage
        human_msgs = [m for m in captured_messages if isinstance(m, HumanMessage)]
        assert len(human_msgs) == 1
        assert human_msgs[0].content.startswith("Focus on the name column")


class TestAiSuggestEndpointValidation:
    """Test ai-suggest endpoint input validation."""

    @pytest.mark.asyncio
    async def test_suggest_requires_dataset_id(self):
        from app.routers.assistant import ai_suggest_operations
        from fastapi import HTTPException

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await ai_suggest_operations(
                request={"agent_id": "agent-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )
        assert exc_info.value.status_code == 400
        assert "dataset_id" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_suggest_requires_agent_id(self):
        from app.routers.assistant import ai_suggest_operations
        from fastapi import HTTPException

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await ai_suggest_operations(
                request={"dataset_id": "ds-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )
        assert exc_info.value.status_code == 400
        assert "agent_id" in exc_info.value.detail


class TestPreflightReturnsConsistentOps:
    """Verify preflight available_operations match what AI can suggest."""

    @pytest.mark.asyncio
    async def test_preflight_ops_match_available_ops(self):
        """The available_operations in preflight should match what the AI is told about."""
        from app.routers.assistant import ai_suggest_preflight

        mock_agent = MagicMock()
        mock_agent.name = "Test Agent"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agent

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("app.routers.ai_operations._get_agent_config", new_callable=AsyncMock) as mock_config:
            mock_config.return_value = {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3, "system_prompt": None, "api_key": None, "base_url": None}

            result = await ai_suggest_preflight(
                request={"agent_id": "agent-1"},
                current_user=_make_mock_user(),
                session=mock_session,
            )

        op_names = {o["operation"] for o in result["available_operations"]}
        expected = {"fillna", "remove-duplicates", "find-replace", "extract-json", "string-operations", "fuzzy-match", "one-hot-encoding", "label-encoding", "value-mapping", "binning"}
        assert expected == op_names
