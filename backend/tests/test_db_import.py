"""Tests for database import — handles datetime serialization."""

import pytest
import json

import pandas as pd
import numpy as np


class TestDbImportDatetime:
    """Test that datetime columns are properly serialized during import."""

    def test_timestamps_become_strings(self):
        """Timestamp columns should become plain strings after conversion."""
        from app.routers.datasets import get_preview_data

        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "joined": pd.to_datetime(["2024-01-15", "2024-02-20"]),
            "age": [30, 25],
        })

        preview = get_preview_data(df)
        # Should be serializable to JSON without error
        result = json.dumps(preview)
        parsed = json.loads(result)

        # Values should be strings, not Timestamp objects
        assert isinstance(parsed[0]["joined"], str)
        assert "2024-01-15" in parsed[0]["joined"]

    def test_nat_becomes_none(self):
        """NaT (not-a-time) values should become None."""
        from app.routers.datasets import get_preview_data

        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "joined": pd.to_datetime(["2024-01-15", pd.NaT]),
        })

        preview = get_preview_data(df)
        result = json.dumps(preview)
        parsed = json.loads(result)

        assert parsed[0]["joined"] == "2024-01-15"
        assert parsed[1]["joined"] is None

    def test_import_flow_converts_before_storing(self):
        """Simulate the full import flow: read SQL table → convert → store."""
        from app.routers.datasets import get_preview_data, detect_columns

        df = pd.DataFrame({
            "id": [1, 2],
            "created_at": pd.to_datetime(["2024-01-01 10:00:00", "2024-02-01 15:30:00"]),
            "name": ["test1", "test2"],
        })

        # Convert like the import function does
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        preview = get_preview_data(df)
        columns = detect_columns(df)

        # Everything should be JSON-serializable
        result = json.dumps({"preview_data": preview, "columns": columns})
        assert "2024-01-01" in result
        assert isinstance(preview[0]["created_at"], str)


class TestDbUrlBuilding:
    """Test _build_db_url for different database types."""

    def test_postgresql_url(self):
        from app.routers.datasets import _build_db_url
        url = _build_db_url("postgresql", "localhost", "5432", "mydb", "user", "pass")
        assert url == "postgresql+psycopg2://user:pass@localhost:5432/mydb"

    def test_postgresql_with_sslmode(self):
        from app.routers.datasets import _build_db_url
        url = _build_db_url("postgresql", "localhost", "5432", "mydb", "user", "pass", sslmode="require")
        assert "sslmode=require" in url

    def test_mysql_url(self):
        from app.routers.datasets import _build_db_url
        url = _build_db_url("mysql", "localhost", "3306", "mydb", "user", "pass")
        assert url == "mysql+pymysql://user:pass@localhost:3306/mydb"

    def test_sqlite_url(self):
        from app.routers.datasets import _build_db_url
        url = _build_db_url("sqlite", "", "", "/tmp/test.db", "", "")
        assert url == "sqlite:////tmp/test.db"

    def test_mssql_url(self):
        from app.routers.datasets import _build_db_url
        url = _build_db_url("mssql", "localhost", "1433", "mydb", "user", "pass")
        assert url == "mssql+pymssql://user:pass@localhost:1433/mydb"

    def test_unsupported_type_raises(self):
        from fastapi import HTTPException
        from app.routers.datasets import _build_db_url
        import pytest
        with pytest.raises(HTTPException):
            _build_db_url("nosql", "localhost", "27017", "db", "user", "pass")
