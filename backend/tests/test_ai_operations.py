"""Tests for AI operations endpoints.

Catches runtime errors like undefined variables (NameError) that
would only surface when the endpoint is actually called.
"""

import json
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

    @pytest.mark.asyncio
    async def test_add_column_from_source(self, mock_dataset, mock_session, mock_agent_config):
        """Add a new column copied from an existing one."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        original_cols = list(df.columns)

        content = '{"operation": "add_column", "column": "full_name", "source": "first_name"}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Add a full_name column from first_name",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )

        assert result.status == "success"
        assert "full_name" in df.columns
        assert df["full_name"].iloc[0] == "John"
        # Original columns unchanged
        for c in original_cols:
            assert c in df.columns

    @pytest.mark.asyncio
    async def test_add_column_with_default(self, mock_dataset, mock_session, mock_agent_config):
        """Add a new column with a default value."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)

        content = '{"operation": "add_column", "column": "country", "default": "Unknown"}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_structural_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Add country column",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                session=mock_session,
            )

        assert result.status == "success"
        assert "country" in df.columns
        assert all(df["country"] == "Unknown")


class TestAiDataClean:
    """Test _ai_data_clean with row-based format."""

    @pytest.mark.asyncio
    async def test_data_clean_no_nameerror(self, mock_dataset, mock_session, mock_agent_config):
        """Verify data clean doesn't raise NameError for dataset_id."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        content = '{"rows": [{"first_name": "JOHN", "last_name": "DOE", "age": 30}]}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_data_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="Uppercase names",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                batch_size=10, session=mock_session,
            )
        assert result.status == "success"
        assert df["first_name"].iloc[0] == "JOHN"

    @pytest.mark.asyncio
    async def test_data_clean_null_matching(self, mock_dataset, mock_session, mock_agent_config):
        """AI returning null values must match pandas NaN/None."""
        import pandas as pd
        import numpy as np

        data = [
            {"joined_date": "2024-01-15", "name": "Alice"},
            {"joined_date": None, "name": "Bob"},
            {"joined_date": np.nan, "name": "Carol"},
        ]
        df = pd.DataFrame(data)

        content = '{"rows": [{"joined_date": "2024-01-15", "name": "Alice"}, {"joined_date": "1970-01-01", "name": "Bob"}, {"joined_date": "1970-01-01", "name": "Carol"}]}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_data_clean(
                df=df, dataset=mock_dataset, columns=["joined_date"],
                instruction="normalize dates, fill nulls with 1970",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                batch_size=10, session=mock_session,
            )

        assert result.status == "success"
        assert df["joined_date"].iloc[1] == "1970-01-01"
        assert df["joined_date"].iloc[2] == "1970-01-01"

    @pytest.mark.asyncio
    async def test_derive_from_context(self, mock_dataset, mock_session, mock_agent_config):
        """AI can derive values for one column based on another column."""
        import pandas as pd

        data = [
            {"city": "London", "country": "N/A"},
            {"city": "Paris", "country": "N/A"},
            {"city": "Tokyo", "country": "N/A"},
        ]
        df = pd.DataFrame(data)

        content = '{"rows": [{"city": "London", "country": "UK"}, {"city": "Paris", "country": "France"}, {"city": "Tokyo", "country": "Japan"}]}'
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_data_clean(
                df=df, dataset=mock_dataset, columns=["country"],
                instruction="fill country based on city",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                batch_size=10, session=mock_session,
            )

        assert result.status == "success"
        assert df["country"].tolist() == ["UK", "France", "Japan"]
        # City column unchanged
        assert df["city"].tolist() == ["London", "Paris", "Tokyo"]

    @pytest.mark.asyncio
    async def test_no_changes_returns_no_changes(self, mock_dataset, mock_session, mock_agent_config):
        """If AI returns same values, status is no_changes."""
        import pandas as pd

        df = pd.DataFrame(mock_dataset.preview_data)
        # AI returns exact same data
        content = json.dumps({"rows": df.head(10).to_dict("records")}, default=str)
        with _LLM_PATCH(content), _SAVE_PATCH:
            result = await _ai_data_clean(
                df=df, dataset=mock_dataset, columns=["first_name"],
                instruction="do nothing",
                provider=AIProvider.OPENAI, agent_config=mock_agent_config,
                batch_size=10, session=mock_session,
            )

        assert result.status == "no_changes"
