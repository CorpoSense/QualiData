"""Tests for AI operations endpoints.

Catches runtime errors like undefined variables (NameError) that
would only surface when the endpoint is actually called.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.routers.ai_operations import _ai_structural_clean, _ai_data_clean
from app.services.ai_provider import AIProvider


@pytest.fixture
def mock_dataset():
    """Create a mock dataset with test data."""
    ds = MagicMock()
    ds.id = "test-dataset-id"
    ds.columns = [
        {"field": "first_name", "label": "first_name", "dtype": "object"},
        {"field": "last_name", "label": "last_name", "dtype": "object"},
        {"field": "age", "label": "age", "dtype": "int64"},
    ]
    ds.preview_data = [
        {"first_name": "John", "last_name": "Doe", "age": 30},
        {"first_name": "Jane", "last_name": "Smith", "age": 25},
    ]
    ds.row_count = 2
    return ds


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_agent_config():
    return {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": None,
        "api_key": None,
    }


def _make_llm_mock(json_content: str):
    """Helper to create a mocked LLM that returns given JSON content."""
    mock_response = MagicMock()
    mock_response.content = json_content
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = mock_response
    return mock_llm


# save_operation is imported locally inside the functions, so we must
# patch it at its source module.
_SAVE_PATCH = patch(
    "app.routers.operations.save_operation", new_callable=AsyncMock
)
_LLM_PATCH = lambda j: patch(
    "app.routers.ai_operations.get_chat_model",
    return_value=_make_llm_mock(j),
)


class TestAiStructuralClean:
    """Test _ai_structural_clean for NameError and other bugs."""

    @pytest.mark.asyncio
    async def test_rename_no_nameerror(self, mock_dataset, mock_session, mock_agent_config):
        """Verify rename operation doesn't raise NameError for dataset_id."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        with _LLM_PATCH('{"operation": "rename", "renames": {"first_name": "fname"}}'), \
             _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Rename first_name to fname",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )
        assert result.status == "success"
        assert any(r["from"] == "first_name" and r["to"] == "fname" for r in result.results)

    @pytest.mark.asyncio
    async def test_drop_no_nameerror(self, mock_dataset, mock_session, mock_agent_config):
        """Verify drop operation doesn't raise NameError."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        with _LLM_PATCH('{"operation": "drop", "columns": ["age"]}'), _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["age"],
                instruction="Drop the age column",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_alternate_keys_accepted(self, mock_dataset, mock_session, mock_agent_config):
        """AI using 'action' instead of 'operation' should still work."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        with _LLM_PATCH('{"action": "rename", "renames": {"first_name": "fname"}}'), \
             _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Rename first_name to fname",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_unknown_operation_returns_no_changes(self, mock_dataset, mock_session, mock_agent_config):
        """Unknown operation type should return no_changes, not crash."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        with _LLM_PATCH('{"operation": "sort_by_magic"}'), _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Sort by magic",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )
        assert result.status == "no_changes"
        assert result.results[0]["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_multiple_operations(self, mock_dataset, mock_session, mock_agent_config):
        """Multiple operations in one response."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        content = '{"operations": [{"operation": "rename", "renames": {"first_name": "fname"}}, {"operation": "astype", "columns": ["age"], "dtype": "float"}]}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["first_name", "age"],
                instruction="Rename and change type",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )
        assert result.status == "success"
        assert len(result.results) == 2


class TestAiDataClean:
    """Test _ai_data_clean for NameError and other bugs."""

    @pytest.mark.asyncio
    async def test_data_clean_no_nameerror(self, mock_dataset, mock_session, mock_agent_config):
        """Verify data clean doesn't raise NameError for dataset_id."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        content = '{"operations": [{"column": "first_name", "transformations": [{"original": "John", "cleaned": "JOHN"}]}]}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_data_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Uppercase names",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                batch_size=10, session=mock_session,
            )
        assert result.status == "success"
