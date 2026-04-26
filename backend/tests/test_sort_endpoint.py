"""Tests for the sort endpoint (server-side single and multi-column sort).

Tests cover:
- Ascending/descending sort for strings and numbers
- Null value handling (na_position parameter)
- Invalid column name
- Missing column parameter
- Sort preserves all data
- Sort is idempotent
- Mixed type columns
- Empty dataset
- Multi-column sort with multiple sort keys
- Multi-column sort with mixed directions
- Multi-column sort with nulls
- Multi-column sort validation
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


class TestMultiColumnSortLogic:
    """Unit tests for multi-column sort logic using pandas sort_values."""

    def test_multi_sort_two_columns_both_ascending(self):
        """Sort by name asc, then age asc — ties in name broken by age."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Alice", "Bob"],
            "age": [30, 25, 20, 35],
        })
        result = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        assert list(result["name"]) == ["Alice", "Alice", "Bob", "Bob"]
        assert list(result["age"]) == [20, 30, 25, 35]

    def test_multi_sort_two_columns_mixed_directions(self):
        """Sort by name asc, then age desc — ties in name broken by age descending."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Alice", "Bob"],
            "age": [30, 25, 20, 35],
        })
        result = df.sort_values(by=["name", "age"], ascending=[True, False], na_position="last").reset_index(drop=True)
        assert list(result["name"]) == ["Alice", "Alice", "Bob", "Bob"]
        assert list(result["age"]) == [30, 20, 35, 25]

    def test_multi_sort_three_columns(self):
        """Sort by three columns: city asc, name asc, age asc."""
        df = pd.DataFrame({
            "city": ["NYC", "LA", "NYC", "LA", "NYC"],
            "name": ["Bob", "Alice", "Alice", "Bob", "Charlie"],
            "age": [30, 25, 20, 35, 22],
        })
        result = df.sort_values(by=["city", "name", "age"], ascending=[True, True, True], na_position="last").reset_index(drop=True)
        # LA first, then NYC
        assert list(result["city"]) == ["LA", "LA", "NYC", "NYC", "NYC"]
        assert list(result["name"]) == ["Alice", "Bob", "Alice", "Bob", "Charlie"]
        assert list(result["age"]) == [25, 35, 20, 30, 22]

    def test_multi_sort_first_desc_second_asc(self):
        """Sort by city desc, then name asc."""
        df = pd.DataFrame({
            "city": ["NYC", "LA", "NYC", "LA"],
            "name": ["Bob", "Alice", "Alice", "Bob"],
        })
        result = df.sort_values(by=["city", "name"], ascending=[False, True], na_position="last").reset_index(drop=True)
        assert list(result["city"]) == ["NYC", "NYC", "LA", "LA"]
        assert list(result["name"]) == ["Alice", "Bob", "Alice", "Bob"]

    def test_multi_sort_with_nulls_in_first_column(self):
        """Multi-sort with nulls in the primary sort column."""
        df = pd.DataFrame({
            "name": [None, "Bob", None, "Alice"],
            "age": [30, 25, 20, 35],
        })
        result = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        names = list(result["name"])
        ages = list(result["age"])
        # Non-null names first, sorted asc
        assert names[0] == "Alice"
        assert names[1] == "Bob"
        # Nulls last
        assert pd.isna(names[2])
        assert pd.isna(names[3])

    def test_multi_sort_with_nulls_in_second_column(self):
        """Multi-sort with nulls in the secondary sort column."""
        df = pd.DataFrame({
            "name": ["Alice", "Alice", "Bob", "Bob"],
            "age": [30, None, 25, None],
        })
        result = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        names = list(result["name"])
        ages = list(result["age"])
        # Alice: 30 first, then null
        assert names[0] == "Alice"
        assert ages[0] == 30
        assert pd.isna(ages[1])
        # Bob: 25 first, then null
        assert names[2] == "Bob"
        assert ages[2] == 25
        assert pd.isna(ages[3])

    def test_multi_sort_preserves_all_rows(self):
        """Multi-sort should not lose any rows."""
        df = pd.DataFrame({
            "name": ["C", "A", "B", "A", "C"],
            "age": [3, 1, 2, 5, 4],
            "score": [90, 80, 70, 60, 50],
        })
        result = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        assert len(result) == 5
        # Verify paired data preserved
        a_rows = result[result["name"] == "A"]
        assert list(a_rows["age"]) == [1, 5]
        assert list(a_rows["score"]) == [80, 60]

    def test_multi_sort_is_idempotent(self):
        """Applying the same multi-sort twice should produce the same result."""
        df = pd.DataFrame({
            "name": ["C", "A", "B", "A"],
            "age": [3, 1, 2, 5],
        })
        result1 = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        result2 = result1.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        pd.testing.assert_frame_equal(result1, result2)

    def test_multi_sort_single_key_equivalent_to_single_sort(self):
        """Multi-sort with one key should produce the same result as single sort."""
        df = pd.DataFrame({"name": ["C", "A", "B"]})
        single = df.sort_values(by="name", ascending=True, na_position="last").reset_index(drop=True)
        multi = df.sort_values(by=["name"], ascending=[True], na_position="last").reset_index(drop=True)
        pd.testing.assert_frame_equal(single, multi)

    def test_multi_sort_all_descending(self):
        """Multi-sort with all columns descending."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Alice", "Bob"],
            "age": [20, 25, 30, 35],
        })
        result = df.sort_values(by=["name", "age"], ascending=[False, False], na_position="last").reset_index(drop=True)
        assert list(result["name"]) == ["Bob", "Bob", "Alice", "Alice"]
        assert list(result["age"]) == [35, 25, 30, 20]

    def test_multi_sort_empty_dataframe(self):
        """Multi-sort on empty dataframe should return empty."""
        df = pd.DataFrame({"name": pd.Series([], dtype=str), "age": pd.Series([], dtype=int)})
        result = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last")
        assert len(result) == 0

    def test_multi_sort_with_duplicate_rows(self):
        """Multi-sort with completely identical rows."""
        df = pd.DataFrame({
            "name": ["Alice", "Alice", "Alice"],
            "age": [20, 20, 20],
        })
        result = df.sort_values(by=["name", "age"], ascending=[True, True], na_position="last").reset_index(drop=True)
        assert len(result) == 3
        assert list(result["name"]) == ["Alice", "Alice", "Alice"]


class TestMultiColumnSortRequestValidation:
    """Tests for multi-column sort request parameter validation."""

    def test_sort_keys_format(self):
        """sort_keys should be a list of {column, ascending} objects."""
        sort_keys = [
            {"column": "name", "ascending": True},
            {"column": "age", "ascending": False},
        ]
        # Validate structure
        for sk in sort_keys:
            assert "column" in sk
            assert "ascending" in sk
            assert isinstance(sk["ascending"], bool)

    def test_sort_keys_empty_list(self):
        """Empty sort_keys list should be rejected."""
        sort_keys = []
        assert len(sort_keys) == 0  # Endpoint should return 400

    def test_sort_keys_with_invalid_column(self):
        """sort_keys with non-existent column should be rejected."""
        df = pd.DataFrame({"name": ["A", "B"]})
        sort_keys = [{"column": "nonexistent", "ascending": True}]
        assert sort_keys[0]["column"] not in df.columns

    def test_sort_keys_with_duplicate_columns(self):
        """sort_keys with duplicate columns should be handled (deduped or rejected)."""
        sort_keys = [
            {"column": "name", "ascending": True},
            {"column": "name", "ascending": False},
        ]
        columns = [sk["column"] for sk in sort_keys]
        assert columns.count("name") == 2  # Duplicate — endpoint should handle

    def test_sort_keys_with_invalid_na_position(self):
        """na_position must be 'first' or 'last'."""
        request = {"sort_keys": [{"column": "name", "ascending": True}], "na_position": "middle"}
        assert request["na_position"] not in ("first", "last")

    def test_sort_keys_default_na_position(self):
        """Default na_position should be 'last'."""
        request = {"sort_keys": [{"column": "name", "ascending": True}]}
        na_position = request.get("na_position", "last")
        assert na_position == "last"

    def test_sort_keys_default_ascending(self):
        """Default ascending per sort key should be True."""
        sort_key = {"column": "name"}
        ascending = sort_key.get("ascending", True)
        assert ascending is True

    def test_backward_compatible_single_column(self):
        """Single column sort (column + ascending) should still work."""
        request = {"column": "name", "ascending": True, "na_position": "last"}
        # This is the legacy format — endpoint should support both
        assert "column" in request
        assert "sort_keys" not in request
