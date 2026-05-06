"""Tests for the map-values endpoint."""

import re
from unittest.mock import MagicMock, patch, AsyncMock

import pandas as pd
import pytest


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.routers.operations import map_values, MapValuesMapping, MapValuesRequest


def _make_dataset(data, columns=None):
    """Create a mock dataset with the given data."""
    dataset = MagicMock()
    dataset.id = "test-dataset-id"
    dataset.project_id = "test-project-id"
    dataset.row_count = len(data)
    dataset.data_json = {"data": data}
    if columns is None:
        df = pd.DataFrame(data)
        from app.routers.datasets import detect_columns
        dataset.columns = detect_columns(df)
    else:
        dataset.columns = columns
    return dataset


def _make_session(dataset):
    """Create a mock session that returns the dataset."""
    mock_session = MagicMock()

    async def mock_execute(stmt):
        result = MagicMock()
        s = str(stmt).lower()
        if "dataset" in s:
            result.scalar_one_or_none.return_value = dataset
        elif "project" in s:
            mock_project = MagicMock()
            mock_project.id = "test-project-id"
            mock_project.user_id = "test-user-id"
            result.scalar_one_or_none.return_value = mock_project
        return result

    mock_session.execute = AsyncMock(side_effect=mock_execute)
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()
    return mock_session


class TestExactMatchMapping:
    """Test exact value mapping (no regex)."""

    @pytest.mark.asyncio
    async def test_exact_match_mapping(self):
        """Map 'USA' → 'US', 'UK' → 'United Kingdom'."""
        data = [
            {"country": "USA", "value": 1},
            {"country": "UK", "value": 2},
            {"country": "France", "value": 3},
            {"country": "USA", "value": 4},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
                MapValuesMapping(from_value="UK", to_value="United Kingdom", is_regex=False, case_sensitive=True),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        assert result["changed_count"] > 0
        # Verify data was updated
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "US"
        assert df["country"].iloc[1] == "United Kingdom"
        assert df["country"].iloc[2] == "France"  # Unchanged


class TestRegexMapping:
    """Test regex-based value mapping."""

    @pytest.mark.asyncio
    async def test_regex_mapping(self):
        """Map regex /^Neth.*/ → 'NL'."""
        data = [
            {"country": "Netherlands", "value": 1},
            {"country": "Nether", "value": 2},
            {"country": "France", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="^Neth.*", to_value="NL", is_regex=True, case_sensitive=True),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "NL"
        assert df["country"].iloc[1] == "NL"
        assert df["country"].iloc[2] == "France"


class TestMixedExactAndRegex:
    """Test combining exact and regex mappings."""

    @pytest.mark.asyncio
    async def test_mixed_exact_and_regex(self):
        """Combine exact + regex mappings."""
        data = [
            {"country": "USA", "value": 1},
            {"country": "Netherlands", "value": 2},
            {"country": "France", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
                MapValuesMapping(from_value="^Neth.*", to_value="NL", is_regex=True, case_sensitive=True),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "US"
        assert df["country"].iloc[1] == "NL"
        assert df["country"].iloc[2] == "France"


class TestMissingValueFill:
    """Test filling null values before mapping."""

    @pytest.mark.asyncio
    async def test_missing_value_fill(self):
        """Null values filled with 'Unknown'."""
        data = [
            {"country": "USA", "value": 1},
            {"country": None, "value": 2},
            {"country": "France", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
            missing_value_action="fill",
            missing_value_fill="Unknown",
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[1] == "Unknown"
        assert result["nulls_handled"] > 0


class TestMissingValueDrop:
    """Test dropping rows with null values."""

    @pytest.mark.asyncio
    async def test_missing_value_drop(self):
        """Rows with nulls dropped."""
        data = [
            {"country": "USA", "value": 1},
            {"country": None, "value": 2},
            {"country": "France", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
            missing_value_action="drop",
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert len(df) == 2
        assert result["nulls_handled"] > 0


class TestMissingValueKeep:
    """Test keeping null values unchanged."""

    @pytest.mark.asyncio
    async def test_missing_value_keep(self):
        """Nulls remain null after mapping."""
        data = [
            {"country": "USA", "value": 1},
            {"country": None, "value": 2},
            {"country": "France", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
            missing_value_action="keep",
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert pd.isna(df["country"].iloc[1])


class TestDefaultValue:
    """Test default value for unmatched non-null values."""

    @pytest.mark.asyncio
    async def test_default_value(self):
        """Unmatched values replaced with default."""
        data = [
            {"country": "USA", "value": 1},
            {"country": "UK", "value": 2},
            {"country": "France", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
            default_value="Other",
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "US"
        assert df["country"].iloc[1] == "Other"
        assert df["country"].iloc[2] == "Other"
        assert result["default_matched"] > 0


class TestCaseInsensitiveRegex:
    """Test case-insensitive regex mapping."""

    @pytest.mark.asyncio
    async def test_case_insensitive_regex(self):
        """Regex with case_sensitive=False."""
        data = [
            {"country": "usa", "value": 1},
            {"country": "USA", "value": 2},
            {"country": "UsA", "value": 3},
            {"country": "France", "value": 4},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="^usa$", to_value="United States", is_regex=True, case_sensitive=False),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "United States"
        assert df["country"].iloc[1] == "United States"
        assert df["country"].iloc[2] == "United States"
        assert df["country"].iloc[3] == "France"


class TestInvalidRegexPattern:
    """Test that invalid regex patterns return 400."""

    @pytest.mark.asyncio
    async def test_invalid_regex_pattern(self):
        """Returns 400 for invalid regex."""
        data = [{"country": "USA", "value": 1}]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="[invalid", to_value="X", is_regex=True, case_sensitive=True),
            ],
        )

        with pytest.raises(Exception) as exc_info:
            await map_values("test-dataset-id", request, user, session)
        assert exc_info.value.status_code == 400


class TestEmptyMappings:
    """Test that empty mappings list returns 400."""

    @pytest.mark.asyncio
    async def test_empty_mappings(self):
        """Returns 400 for empty mappings list."""
        data = [{"country": "USA", "value": 1}]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[],
        )

        with pytest.raises(Exception) as exc_info:
            await map_values("test-dataset-id", request, user, session)
        assert exc_info.value.status_code == 400


class TestColumnNotFound:
    """Test that non-existent column returns 400."""

    @pytest.mark.asyncio
    async def test_column_not_found(self):
        """Returns 400 for non-existent column."""
        data = [{"country": "USA", "value": 1}]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="nonexistent",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
        )

        with pytest.raises(Exception) as exc_info:
            await map_values("test-dataset-id", request, user, session)
        assert exc_info.value.status_code == 400


class TestRowIndicesFilter:
    """Test row filtering with row_indices."""

    @pytest.mark.asyncio
    async def test_row_indices_filter(self):
        """Only mapped rows are affected when row_indices specified."""
        data = [
            {"country": "USA", "value": 1},
            {"country": "USA", "value": 2},
            {"country": "USA", "value": 3},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
            row_indices=[0],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "US"
        assert df["country"].iloc[1] == "USA"
        assert df["country"].iloc[2] == "USA"


class TestNoChanges:
    """Test when no values match any mapping."""

    @pytest.mark.asyncio
    async def test_no_changes(self):
        """Returns 'no_changes' when nothing matches."""
        data = [
            {"country": "France", "value": 1},
            {"country": "Germany", "value": 2},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="US", is_regex=False, case_sensitive=True),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "no_changes"


class TestMappingToEmptyString:
    """Test mapping a value to an empty string."""

    @pytest.mark.asyncio
    async def test_mapping_to_empty_string(self):
        """Map value to empty string."""
        data = [
            {"country": "USA", "value": 1},
            {"country": "France", "value": 2},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="USA", to_value="", is_regex=False, case_sensitive=True),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == ""


class TestMultipleRegexFirstMatchWins:
    """Test that order-dependent regex mapping works (first match wins)."""

    @pytest.mark.asyncio
    async def test_multiple_regex_first_match_wins(self):
        """Order-dependent regex mapping — first match wins.

        Both patterns match "Netherlands" but the first one (^Neth.*$)
        should win because it appears first in the mappings list.
        The second pattern (^Netherlands$) should NOT be applied.
        """
        data = [
            {"country": "Netherlands", "value": 1},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        request = MapValuesRequest(
            column="country",
            mappings=[
                MapValuesMapping(from_value="^Neth.*$", to_value="NL", is_regex=True, case_sensitive=True),
                MapValuesMapping(from_value="^Netherlands$", to_value="NET", is_regex=True, case_sensitive=True),
            ],
        )

        result = await map_values("test-dataset-id", request, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        # First regex matches the full string, so value should be "NL"
        # If second regex were applied instead, it would be "NET"
        assert df["country"].iloc[0] == "NL"


class TestRecipeImport:
    """Test map-values in import-recipe handler."""

    @pytest.mark.asyncio
    async def test_recipe_import(self):
        """map-values works in import-recipe."""
        from app.routers.operations import import_recipe, ImportRecipeRequest

        data = [
            {"country": "USA", "value": 1},
            {"country": "UK", "value": 2},
            {"country": None, "value": 3},
            {"country": "France", "value": 4},
        ]
        dataset = _make_dataset(data)
        session = _make_session(dataset)
        user = MagicMock(id="test-user-id")

        recipe = ImportRecipeRequest(
            operations=[
                {
                    "operation": "map-values",
                    "column": "country",
                    "params": {
                        "mappings": [
                            {"from_value": "USA", "to_value": "US", "is_regex": False, "case_sensitive": True},
                            {"from_value": "^F.*", "to_value": "FR", "is_regex": True, "case_sensitive": True},
                        ],
                        "missing_value_action": "fill",
                        "missing_value_fill": "Unknown",
                    },
                }
            ]
        )

        result = await import_recipe("test-dataset-id", recipe, user, session)
        assert result["status"] == "success"
        df = pd.DataFrame(dataset.data_json["data"])
        assert df["country"].iloc[0] == "US"
        assert df["country"].iloc[1] == "UK"
        assert df["country"].iloc[2] == "Unknown"
        assert df["country"].iloc[3] == "FR"
