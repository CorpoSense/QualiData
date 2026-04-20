"""Tests for row-filtered operations - applying operations to selected rows only."""

import pytest
import pandas as pd


class TestHelperFunctions:
    """Test helper functions for row filtering."""

    def test_filter_df_by_indices_valid(self):
        """Test filtering DataFrame with valid indices."""
        from app.routers.operations import filter_df_by_indices
        
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': ['a', 'b', 'c', 'd', 'e']})
        result = filter_df_by_indices(df, [0, 2, 4])
        
        assert len(result) == 3
        assert result['a'].tolist() == [1, 3, 5]
        assert result['b'].tolist() == ['a', 'c', 'e']

    def test_filter_df_by_indices_empty(self):
        """Test filtering with empty indices returns original."""
        from app.routers.operations import filter_df_by_indices
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = filter_df_by_indices(df, [])
        
        assert len(result) == 3

    def test_filter_df_by_indices_none(self):
        """Test filtering with None returns original."""
        from app.routers.operations import filter_df_by_indices
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = filter_df_by_indices(df, None)
        
        assert len(result) == 3

    def test_filter_df_by_indices_out_of_bounds(self):
        """Test filtering with out-of-bounds indices."""
        from app.routers.operations import filter_df_by_indices
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        result = filter_df_by_indices(df, [0, 5, 10])
        
        # Should only include valid indices
        assert len(result) == 1

    def test_filter_df_by_indices_single_row(self):
        """Test filtering single row."""
        from app.routers.operations import filter_df_by_indices
        
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
        result = filter_df_by_indices(df, [2])
        
        assert len(result) == 1
        assert result['a'].tolist() == [3]

    def test_apply_operation_to_filtered_rows(self):
        """Test applying operation to filtered rows."""
        from app.routers.operations import apply_operation_to_filtered_rows
        
        df = pd.DataFrame({'name': ['alice', 'bob', 'charlie', 'david', 'eve']})
        
        def uppercase_op(filtered_df):
            filtered_df['name'] = filtered_df['name'].str.upper()
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [0, 2, 4], uppercase_op)
        
        assert count == 3
        # Rows 0, 2, 4 should be uppercase
        assert result['name'].tolist() == ['ALICE', 'bob', 'CHARLIE', 'david', 'EVE']

    def test_apply_operation_to_all_rows(self):
        """Test applying operation to all rows when no indices provided."""
        from app.routers.operations import apply_operation_to_filtered_rows
        
        df = pd.DataFrame({'name': ['alice', 'bob', 'charlie']})
        
        def uppercase_op(filtered_df):
            filtered_df['name'] = filtered_df['name'].str.upper()
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, None, uppercase_op)
        
        assert count == 3
        assert result['name'].tolist() == ['ALICE', 'BOB', 'CHARLIE']

    def test_apply_operation_preserves_order(self):
        """Test that row order is preserved after operation."""
        from app.routers.operations import apply_operation_to_filtered_rows
        
        df = pd.DataFrame({'id': [1, 2, 3, 4, 5], 'val': ['a', 'b', 'c', 'd', 'e']})
        
        def modify_op(filtered_df):
            filtered_df['val'] = filtered_df['val'] + '_mod'
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [1, 3], modify_op)
        
        # Original order should be preserved
        assert result['id'].tolist() == [1, 2, 3, 4, 5]
        # Only modified rows should have _mod
        assert result['val'].tolist() == ['a', 'b_mod', 'c', 'd_mod', 'e']

    def test_apply_operation_empty_indices(self):
        """Test applying operation with empty indices."""
        from app.routers.operations import apply_operation_to_filtered_rows
        
        df = pd.DataFrame({'val': ['a', 'b', 'c']})
        
        def modify_op(filtered_df):
            filtered_df['val'] = filtered_df['val'].str.upper()
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [], modify_op)
        
        # Empty indices should apply to all rows (original behavior)
        assert count == 3

    def test_string_operation_row_filtering(self):
        """Integration test: string operation with row filtering."""
        from app.routers.operations import filter_df_by_indices, apply_operation_to_filtered_rows
        
        # Simulate dataset with mixed case names
        df = pd.DataFrame({
            'name': ['ALICE', 'bob', 'CHARLIE', 'david', 'EVE']
        })
        
        # Apply lowercase only to rows 1 and 3
        def lowercase_op(filtered_df):
            filtered_df['name'] = filtered_df['name'].str.lower()
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [1, 3], lowercase_op)
        
        assert count == 2
        # Only rows 1 and 3 should be lowercase
        assert result['name'].tolist() == ['ALICE', 'bob', 'CHARLIE', 'david', 'EVE']

    def test_numeric_operation_row_filtering(self):
        """Integration test: numeric operation with row filtering."""
        from app.routers.operations import filter_df_by_indices, apply_operation_to_filtered_rows
        
        df = pd.DataFrame({
            'value': [10, 20, 30, 40, 50]
        })
        
        # Double only rows 0, 2, 4
        def double_op(filtered_df):
            filtered_df['value'] = filtered_df['value'] * 2
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [0, 2, 4], double_op)
        
        assert count == 3
        # Only rows 0, 2, 4 should be doubled
        assert result['value'].tolist() == [20, 20, 60, 40, 100]

    def test_datetime_operation_row_filtering(self):
        """Integration test: datetime operation with row filtering."""
        from app.routers.operations import filter_df_by_indices, apply_operation_to_filtered_rows
        
        df = pd.DataFrame({
            'date': ['2024-01-15', '2024-02-20', '2024-03-25', '2024-04-30', '2024-05-05']
        })
        df['date'] = pd.to_datetime(df['date'])
        original_dates = df['date'].copy()
        
        # Add 1 year to rows 0, 2, 4
        def add_year_op(filtered_df):
            filtered_df['date'] = filtered_df['date'] + pd.DateOffset(years=1)
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [0, 2, 4], add_year_op)
        
        assert count == 3
        # Check that only specified rows were modified
        assert result['date'].iloc[0].year == 2025  # row 0 modified
        assert result['date'].iloc[1].year == 2024  # row 1 not modified
        assert result['date'].iloc[2].year == 2025  # row 2 modified
        assert result['date'].iloc[3].year == 2024  # row 3 not modified
        assert result['date'].iloc[4].year == 2025  # row 4 modified

    def test_find_replace_row_filtering(self):
        """Integration test: find/replace with row filtering."""
        from app.routers.operations import filter_df_by_indices, apply_operation_to_filtered_rows
        
        df = pd.DataFrame({
            'city': ['NYC', 'LA', 'NYC', 'SF', 'LA']
        })
        
        # Replace 'NYC' with 'NEW YORK' only in certain rows 
        # (simulating by applying to filtered rows then combining)
        def replace_op(filtered_df):
            filtered_df['city'] = filtered_df['city'].replace('NYC', 'NEW YORK')
            return filtered_df
        
        result, count = apply_operation_to_filtered_rows(df, [0, 2], replace_op)
        
        assert count == 2
        # Only rows 0, 2 should have replacement
        assert result['city'].tolist() == ['NEW YORK', 'LA', 'NEW YORK', 'SF', 'LA']
