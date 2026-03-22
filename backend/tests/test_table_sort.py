"""Tests for table sort logic (mirrors DataTable multi-sort behavior)."""

import pytest


def multi_sort(items, sort_keys):
    """Sort items by multiple keys. Each key is {key, dir} where dir is 'asc' or 'desc'.
    Mirrors the JavaScript sortedItems computed property in DataTable.vue."""
    if not sort_keys:
        return items
    result = list(items)
    result.sort(key=lambda row: _sort_key(row, sort_keys))
    return result


def _sort_key(row, sort_keys):
    """Build a composite sort key from multiple sort entries."""
    keys = []
    for entry in sort_keys:
        key = entry["key"]
        is_desc = entry["dir"] == "desc"
        val = row.get(key)
        if val is None:
            # None always sorts last
            keys.append((1, 0))
        elif isinstance(val, (int, float)):
            # For desc, negate the number
            keys.append((0, -val if is_desc else val))
        else:
            s = str(val).lower()
            # For desc, we can't simply negate strings, so we use a wrapper
            keys.append((0, _NegatedStr(s) if is_desc else s))
    return keys


class _NegatedStr:
    """Wrapper that reverses string comparison order."""
    def __init__(self, val):
        self.val = val
    def __lt__(self, other):
        if isinstance(other, _NegatedStr):
            return self.val > other.val
        return self.val > str(other)
    def __eq__(self, other):
        if isinstance(other, _NegatedStr):
            return self.val == other.val
        return self.val == str(other)


class TestSingleSort:
    """Test single-column sorting (multi_sort with one key)."""

    def test_sort_ascending_strings(self):
        items = [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}]
        result = multi_sort(items, [{"key": "name", "dir": "asc"}])
        assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie"]

    def test_sort_descending_strings(self):
        items = [{"name": "Alice"}, {"name": "Charlie"}, {"name": "Bob"}]
        result = multi_sort(items, [{"key": "name", "dir": "desc"}])
        assert [r["name"] for r in result] == ["Charlie", "Bob", "Alice"]

    def test_sort_ascending_numbers(self):
        items = [{"age": 30}, {"age": 10}, {"age": 20}]
        result = multi_sort(items, [{"key": "age", "dir": "asc"}])
        assert [r["age"] for r in result] == [10, 20, 30]

    def test_sort_descending_numbers(self):
        items = [{"age": 10}, {"age": 30}, {"age": 20}]
        result = multi_sort(items, [{"key": "age", "dir": "desc"}])
        assert [r["age"] for r in result] == [30, 20, 10]

    def test_sort_null_values_last(self):
        items = [{"name": None}, {"name": "Bob"}, {"name": "Alice"}]
        result = multi_sort(items, [{"key": "name", "dir": "asc"}])
        assert [r["name"] for r in result] == ["Alice", "Bob", None]

    def test_empty_sort_keys_returns_original(self):
        items = [{"name": "Z"}, {"name": "A"}]
        result = multi_sort(items, [])
        assert [r["name"] for r in result] == ["Z", "A"]


class TestMultiSort:
    """Test multi-column sorting."""

    def test_sort_by_two_columns(self):
        items = [
            {"city": "Paris", "name": "Bob"},
            {"city": "London", "name": "Alice"},
            {"city": "Paris", "name": "Alice"},
            {"city": "London", "name": "Bob"},
        ]
        result = multi_sort(items, [
            {"key": "city", "dir": "asc"},
            {"key": "name", "dir": "asc"},
        ])
        assert [(r["city"], r["name"]) for r in result] == [
            ("London", "Alice"), ("London", "Bob"),
            ("Paris", "Alice"), ("Paris", "Bob"),
        ]

    def test_sort_mixed_directions(self):
        items = [
            {"city": "Paris", "age": 30},
            {"city": "London", "age": 25},
            {"city": "Paris", "age": 20},
            {"city": "London", "age": 35},
        ]
        result = multi_sort(items, [
            {"key": "city", "dir": "asc"},
            {"key": "age", "dir": "desc"},
        ])
        assert [(r["city"], r["age"]) for r in result] == [
            ("London", 35), ("London", 25),
            ("Paris", 30), ("Paris", 20),
        ]

    def test_sort_three_columns(self):
        items = [
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 1, "c": 2},
            {"a": 1, "b": 1, "c": 1},
            {"a": 2, "b": 1, "c": 1},
        ]
        result = multi_sort(items, [
            {"key": "a", "dir": "asc"},
            {"key": "b", "dir": "asc"},
            {"key": "c", "dir": "asc"},
        ])
        assert [(r["a"], r["b"], r["c"]) for r in result] == [
            (1, 1, 1), (1, 1, 2), (1, 2, 3), (2, 1, 1),
        ]

    def test_preserves_original_order_when_no_sort(self):
        items = [{"id": 3}, {"id": 1}, {"id": 2}]
        result = multi_sort(items, [])
        assert [r["id"] for r in result] == [3, 1, 2]


class TestSortEdgeCases:
    """Edge cases for sorting."""

    def test_empty_list(self):
        assert multi_sort([], [{"key": "name", "dir": "asc"}]) == []

    def test_single_item(self):
        items = [{"name": "Only"}]
        result = multi_sort(items, [{"key": "name", "dir": "asc"}])
        assert len(result) == 1
        assert result[0]["name"] == "Only"

    def test_all_same_values(self):
        items = [{"name": "A"}, {"name": "A"}, {"name": "A"}]
        result = multi_sort(items, [{"key": "name", "dir": "asc"}])
        assert len(result) == 3

    def test_mixed_types_as_strings(self):
        items = [{"val": "10"}, {"val": "2"}, {"val": "100"}]
        result = multi_sort(items, [{"key": "val", "dir": "asc"}])
        # String sort: "10" < "100" < "2"
        assert [r["val"] for r in result] == ["10", "100", "2"]
