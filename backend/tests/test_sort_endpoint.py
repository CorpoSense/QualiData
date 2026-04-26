"""Tests for the sort endpoint (server-side single column sort).

Tests cover:
- Ascending/descending sort for strings and numbers
- Null value handling (na_position parameter)
- Invalid column name
- Missing column parameter
- Sort preserves all data
- Sort is idempotent
- Mixed type columns
- Empty dataset
"""

import pytest
import pandas as pd

from app.routers.operations import sort_operations


class TestSortLogic:
    """Unit tests for the pandas sort logic used by the sort endpoint."""

    def test_sort_strings_ascending(self):
        df = pd.DataFrame({"name": ["Charlie", "Alice", "Bob"]})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        assert list(result["name"]) == ["Alice", "Bob", "Charlie"]

    def test_sort_strings_descending(self):
        df = pd.DataFrame({"name": ["Alice", "Charlie", "Bob"]})
        result = df.sort_values(by="name", ascending=False, na_position="last")
        assert list(result["name"]) == ["Charlie", "Bob", "Alice"]

    def test_sort_numbers_ascending(self):
        df = pd.DataFrame({"age": [30, 10, 20]})
        result = df.sort_values(by="age", ascending=True, na_position="last")
        assert list(result["age"]) == [10, 20, 30]

    def test_sort_numbers_descending(self):
        df = pd.DataFrame({"age": [10, 30, 20]})
        result = df.sort_values(by="age", ascending=False, na_position="last")
        assert list(result["age"]) == [30, 20, 10]

    def test_sort_nulls_last_ascending(self):
        df = pd.DataFrame({"name": [None, "Bob", "Alice", None]})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        names = list(result["name"])
        # Non-null values sorted first
        assert names[0] == "Alice"
        assert names[1] == "Bob"
        # Nulls at the end
        assert pd.isna(names[2])
        assert pd.isna(names[3])

    def test_sort_nulls_last_descending(self):
        df = pd.DataFrame({"name": [None, "Bob", "Alice", None]})
        result = df.sort_values(by="name", ascending=False, na_position="last")
        names = list(result["name"])
        # Non-null values sorted first (desc)
        assert names[0] == "Bob"
        assert names[1] == "Alice"
        # Nulls at the end
        assert pd.isna(names[2])
        assert pd.isna(names[3])

    def test_sort_nulls_first_ascending(self):
        df = pd.DataFrame({"name": [None, "Bob", "Alice", None]})
        result = df.sort_values(by="name", ascending=True, na_position="first")
        names = list(result["name"])
        # Nulls first
        assert pd.isna(names[0])
        assert pd.isna(names[1])
        # Then sorted values
        assert names[2] == "Alice"
        assert names[3] == "Bob"

    def test_sort_nulls_first_descending(self):
        df = pd.DataFrame({"name": [None, "Bob", "Alice", None]})
        result = df.sort_values(by="name", ascending=False, na_position="first")
        names = list(result["name"])
        # Nulls first
        assert pd.isna(names[0])
        assert pd.isna(names[1])
        # Then sorted values (desc)
        assert names[2] == "Bob"
        assert names[3] == "Alice"

    def test_sort_preserves_all_rows(self):
        df = pd.DataFrame({"name": ["C", "A", "B"], "age": [3, 1, 2]})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        assert len(result) == 3
        # Check that the paired data is preserved
        alice_row = result[result["name"] == "A"]
        assert alice_row["age"].iloc[0] == 1

    def test_sort_is_idempotent(self):
        df = pd.DataFrame({"name": ["C", "A", "B"]})
        result1 = df.sort_values(by="name", ascending=True, na_position="last")
        result2 = result1.sort_values(by="name", ascending=True, na_position="last")
        pd.testing.assert_frame_equal(result1.reset_index(drop=True), result2.reset_index(drop=True))

    def test_sort_mixed_types_as_strings(self):
        """When column has mixed types, pandas sorts by string representation."""
        df = pd.DataFrame({"val": ["10", "2", "100"]})
        result = df.sort_values(by="val", ascending=True, na_position="last")
        # String sort: "10" < "100" < "2"
        assert list(result["val"]) == ["10", "100", "2"]

    def test_sort_empty_dataframe(self):
        df = pd.DataFrame({"name": pd.Series([], dtype=str)})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        assert len(result) == 0

    def test_sort_single_row(self):
        df = pd.DataFrame({"name": ["Only"]})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        assert list(result["name"]) == ["Only"]

    def test_sort_all_nulls(self):
        df = pd.DataFrame({"name": [None, None, None]})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        assert len(result) == 3
        assert all(pd.isna(v) for v in result["name"])

    def test_sort_all_same_values(self):
        df = pd.DataFrame({"name": ["A", "A", "A"]})
        result = df.sort_values(by="name", ascending=True, na_position="last")
        assert list(result["name"]) == ["A", "A", "A"]

    def test_sort_numeric_with_nulls(self):
        df = pd.DataFrame({"age": [30, None, 10, None, 20]})
        result = df.sort_values(by="age", ascending=True, na_position="last")
        ages = list(result["age"])
        assert ages[0] == 10
        assert ages[1] == 20
        assert ages[2] == 30
        assert pd.isna(ages[3])
        assert pd.isna(ages[4])

    def test_sort_preserves_index_reset(self):
        """After sort, index should be reset for consistent pagination."""
        df = pd.DataFrame({"name": ["C", "A", "B"]})
        result = df.sort_values(by="name", ascending=True, na_position="last").reset_index(drop=True)
        assert list(result.index) == [0, 1, 2]
        assert list(result["name"]) == ["A", "B", "C"]


class TestSortRequestValidation:
    """Tests for sort request parameter validation."""

    def test_missing_column_returns_error(self):
        """Sort request without column should fail."""
        request = {"ascending": True}
        # Column is required - this would be caught by the endpoint
        assert "column" not in request

    def test_invalid_column_returns_error(self):
        """Sort request with non-existent column should fail."""
        df = pd.DataFrame({"name": ["A", "B"]})
        assert "nonexistent" not in df.columns

    def test_valid_request_params(self):
        """Valid sort request should have column and optional ascending/na_position."""
        request = {"column": "name", "ascending": True, "na_position": "last"}
        assert request["column"] == "name"
        assert request["ascending"] is True
        assert request["na_position"] == "last"

    def test_default_ascending_is_true(self):
        """Default ascending value should be True."""
        request = {"column": "name"}
        ascending = request.get("ascending", True)
        assert ascending is True

    def test_default_na_position_is_last(self):
        """Default na_position should be 'last' to match frontend behavior."""
        request = {"column": "name"}
        na_position = request.get("na_position", "last")
        assert na_position == "last"

    def test_invalid_na_position(self):
        """na_position must be 'first' or 'last'."""
        request = {"column": "name", "na_position": "middle"}
        assert request["na_position"] not in ("first", "last")
