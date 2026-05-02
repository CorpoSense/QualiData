"""Pivot table service for data analysis and reporting."""

from typing import Any, Optional
import pandas as pd
import numpy as np


class PivotService:
    """Service for creating pivot tables and frequency analysis."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with a pandas DataFrame."""
        self.df = df.copy()

    def detect_column_type(
        self, column: str, unique_threshold: int = 20
    ) -> str:
        """
        Detect if a column is categorical or continuous.

        Args:
            column: Column name to analyze
            unique_threshold: Maximum unique values to consider as categorical (default: 20)

        Returns:
            'categorical' or 'continuous'
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        col_data = self.df[column]

        # Check if object type (strings, mixed types)
        if col_data.dtype == "object":
            return "categorical"

        # Check unique count
        try:
            unique_count = col_data.nunique()
        except TypeError:
            # Unhashable types - treat as categorical
            return "categorical"

        # Low cardinality = categorical
        if unique_count <= unique_threshold:
            return "categorical"

        # Numeric with high cardinality = continuous
        if pd.api.types.is_numeric_dtype(col_data):
            return "continuous"

        # Default to categorical for other types
        return "categorical"

    def get_column_types(self, unique_threshold: int = 20) -> dict[str, list[str]]:
        """
        Get all columns categorized by type.

        Args:
            unique_threshold: Maximum unique values to consider as categorical

        Returns:
            Dictionary with 'categorical', 'continuous', and 'datetime' keys
        """
        result = {"categorical": [], "continuous": [], "datetime": []}

        for col in self.df.columns:
            col_type = self.detect_column_type(col, unique_threshold)

            # Check for datetime
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                result["datetime"].append(col)
            else:
                result[col_type].append(col)

        return result

    def get_column_statistics(self, column: str) -> dict[str, Any]:
        """
        Get statistics for a column.

        Args:
            column: Column name

        Returns:
            Dictionary with column statistics
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        col_data = self.df[column]
        stats = {
            "name": column,
            "dtype": str(col_data.dtype),
            "total_rows": len(col_data),
            "null_count": int(col_data.isna().sum()),
            "null_percent": round(
                (col_data.isna().sum() / len(col_data)) * 100, 2
            )
            if len(col_data) > 0
            else 0,
        }

        # Unique count (handle unhashable types)
        try:
            stats["unique_count"] = int(col_data.nunique())
        except TypeError:
            try:
                stats["unique_count"] = int(col_data.astype(str).nunique())
            except Exception:
                stats["unique_count"] = 0

        # Numeric stats
        if pd.api.types.is_numeric_dtype(col_data):
            stats.update(
                {
                    "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                    "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                    "mean": float(col_data.mean()) if not pd.isna(col_data.mean()) else None,
                    "median": float(col_data.median())
                    if not pd.isna(col_data.median())
                    else None,
                    "std": float(col_data.std()) if not pd.isna(col_data.std()) else None,
                }
            )

        # Top values for categorical
        if stats["unique_count"] < 50:
            try:
                value_counts = col_data.value_counts().head(10)
                stats["top_values"] = [
                    {"value": str(v), "count": int(c)} for v, c in value_counts.items()
                ]
            except TypeError:
                # Unhashable types
                stats["top_values"] = []

        return stats

    def create_pivot(
        self,
        index_columns: list[str],
        column_columns: list[str],
        value_column: str,
        aggfunc: str = "count",
        bin_continuous: bool = True,
        bins: int = 10,
        binning_strategy: str = "equal_width",
        include_nulls: bool = False,
        unique_threshold: int = 20,
    ) -> dict[str, Any]:
        """
        Create a pivot table from the DataFrame.

        Args:
            index_columns: Columns to use as rows (index)
            column_columns: Columns to use as columns
            value_column: Column to aggregate
            aggfunc: Aggregation function (count, sum, mean, median, min, max, std)
            bin_continuous: Whether to bin continuous columns
            bins: Number of bins for continuous columns
            binning_strategy: Binning strategy ('equal_width' or 'equal_freq')
            include_nulls: Whether to include null values in aggregation
            unique_threshold: Threshold for categorical detection

        Returns:
            Dictionary with pivot data and metadata
        """
        # Validate inputs
        all_columns = index_columns + column_columns + [value_column]
        for col in all_columns:
            if col not in self.df.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame")

        # Validate aggfunc
        valid_aggfuncs = ["count", "sum", "mean", "median", "min", "max", "std"]
        if aggfunc not in valid_aggfuncs:
            raise ValueError(
                f"Invalid aggfunc '{aggfunc}'. Must be one of {valid_aggfuncs}"
            )

        # Check if value column is numeric for certain aggfuncs
        if aggfunc in ["sum", "mean", "median", "std"]:
            if not pd.api.types.is_numeric_dtype(self.df[value_column]):
                raise ValueError(
                    f"Column '{value_column}' must be numeric for aggregation function '{aggfunc}'"
                )

        df = self.df.copy()

        # Handle nulls
        if not include_nulls:
            df = df.dropna(subset=[value_column])

        # Pre-validate: check if continuous columns are used as column axes
        # without binning, which would produce an enormous pivot table
        for col in column_columns:
            col_type = self.detect_column_type(col, unique_threshold)
            if col_type == "continuous" and not bin_continuous:
                raise ValueError(
                    f"Column '{col}' is continuous (numerical with many unique values). "
                    f"Using it as a column header without binning would create too many columns. "
                    f"Please enable 'Bin continuous columns' or choose a categorical column instead."
                )

        # Bin continuous columns if needed
        binned_columns = []
        bin_failures = []
        if bin_continuous:
            for col in index_columns + column_columns:
                col_type = self.detect_column_type(col, unique_threshold)
                if col_type == "continuous":
                    bin_col_name = f"{col}_bin"
                    try:
                        if binning_strategy == "equal_freq":
                            df[bin_col_name] = pd.qcut(
                                df[col], q=bins, duplicates="drop"
                            )
                        else:  # equal_width
                            df[bin_col_name] = pd.cut(df[col], bins=bins)
                        binned_columns.append((col, bin_col_name))
                    except Exception as e:
                        # If binning fails, record the failure
                        bin_failures.append((col, str(e)))

        # If binning failed for any column used as column axis, raise an error
        # (unlike index columns, column axis with raw continuous values produces
        # an unmanageable number of columns)
        for col, err_msg in bin_failures:
            if col in column_columns:
                raise ValueError(
                    f"Failed to bin continuous column '{col}' for use as column header: {err_msg}. "
                    f"Try using a different binning strategy or choose a categorical column instead."
                )

        # Replace continuous columns with binned versions
        final_index = []
        for col in index_columns:
            binned = next((b for b in binned_columns if b[0] == col), None)
            final_index.append(binned[1] if binned else col)

        final_columns = []
        for col in column_columns:
            binned = next((b for b in binned_columns if b[0] == col), None)
            final_columns.append(binned[1] if binned else col)

        # Create pivot table
        try:
            pivot_df = df.pivot_table(
                index=final_index,
                columns=final_columns,
                values=value_column,
                aggfunc=aggfunc,
                observed=False,
                fill_value=0 if aggfunc == "count" else np.nan,
            )
        except Exception as e:
            raise ValueError(f"Failed to create pivot table: {str(e)}")

        # Convert to serializable format
        pivot_data = pivot_df.reset_index()

        # Convert interval values in data cells to strings for JSON serialization
        for col in pivot_data.columns:
            if len(pivot_data) > 0:
                first_val = pivot_data[col].iloc[0]
                if hasattr(first_val, "left") and hasattr(first_val, "right"):
                    pivot_data[col] = pivot_data[col].astype(str)

        # Convert interval objects in column names to strings for JSON serialization
        # When continuous columns are binned and used as column axes, the MultiIndex
        # column names contain Interval objects which are not JSON-serializable
        new_columns = []
        for col in pivot_data.columns:
            if isinstance(col, tuple):
                # MultiIndex column: convert each element
                new_columns.append(tuple(
                    str(c) if hasattr(c, "left") and hasattr(c, "right") else c
                    for c in col
                ))
            elif hasattr(col, "left") and hasattr(col, "right"):
                new_columns.append(str(col))
            else:
                new_columns.append(col)
        pivot_data.columns = new_columns

        # Calculate summary statistics
        summary = {
            "total_rows": len(pivot_df),
            "total_columns": len(pivot_df.columns),
            "aggregation": aggfunc,
            "value_column": value_column,
            "index_columns": index_columns,
            "column_columns": column_columns,
            "binned_columns": [b[0] for b in binned_columns],
            "binning_strategy": binning_strategy if binned_columns else None,
            "bins": bins if binned_columns else None,
            "include_nulls": include_nulls,
            "unique_threshold": unique_threshold,
        }

        # Add column type information
        column_types = {}
        for col in index_columns + column_columns:
            column_types[col] = self.detect_column_type(col, unique_threshold)
        summary["column_types"] = column_types

        return {
            "pivot": pivot_data.to_dict(orient="records"),
            "columns": list(pivot_data.columns),
            "summary": summary,
        }

    def value_counts_analysis(
        self, columns: list[str], normalize: bool = False
    ) -> dict[str, Any]:
        """
        Perform frequency analysis on columns.

        Args:
            columns: Columns to analyze
            normalize: Whether to return proportions instead of counts

        Returns:
            Dictionary with value counts data
        """
        # Validate columns
        for col in columns:
            if col not in self.df.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame")

        if len(columns) == 1:
            # Single column value counts
            col = columns[0]
            try:
                vc = self.df[col].value_counts(normalize=normalize)
                result = [
                    {"value": str(v), "count": int(c) if not normalize else float(c)}
                    for v, c in vc.items()
                ]
            except TypeError:
                # Unhashable types - convert to string
                vc = self.df[col].astype(str).value_counts(normalize=normalize)
                result = [
                    {"value": str(v), "count": int(c) if not normalize else float(c)}
                    for v, c in vc.items()
                ]
        else:
            # Multi-column frequency
            try:
                grouped = self.df.groupby(columns).size().reset_index(name="count")
                if normalize:
                    total = grouped["count"].sum()
                    grouped["count"] = grouped["count"] / total
                result = grouped.to_dict(orient="records")
            except Exception as e:
                raise ValueError(f"Failed to compute value counts: {str(e)}")

        return {
            "columns": columns,
            "normalize": normalize,
            "data": result,
        }
