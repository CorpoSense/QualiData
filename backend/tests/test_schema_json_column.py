"""Test to verify schema_json column exists in projects table."""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import Session

# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.db.models import Project


class TestSchemaJsonColumn:
    """Test that schema_json column exists in projects table."""

    def test_project_model_has_schema_json(self):
        """Project model must have schema_json field."""
        assert hasattr(Project, 'schema_json'), "Project model must have schema_json field"

    def test_schema_json_is_json_type(self):
        """schema_json field must be JSON type."""
        # Check that the column is defined as JSON
        column = Project.__table__.columns['schema_json']
        assert column is not None, "schema_json column must exist in Project model"
        # The type should be JSON or similar
        assert 'JSON' in str(type(column.type)), f"schema_json should be JSON type, got {type(column.type)}"

    def test_schema_json_is_nullable(self):
        """schema_json field must be nullable."""
        column = Project.__table__.columns['schema_json']
        assert column.nullable is True, "schema_json column must be nullable"

    def test_schema_json_can_be_set(self):
        """schema_json field can be set with a dictionary."""
        # Create a mock project with schema_json
        project = Project(
            id="test-id",
            user_id="user-id",
            name="Test Project",
            schema_json={"columns": ["col1", "col2"], "types": {"col1": "string"}}
        )
        
        assert project.schema_json == {"columns": ["col1", "col2"], "types": {"col1": "string"}}

    def test_schema_json_can_be_none(self):
        """schema_json field can be None."""
        project = Project(
            id="test-id",
            user_id="user-id",
            name="Test Project",
            schema_json=None
        )
        
        assert project.schema_json is None


class TestSchemaJsonInDatabase:
    """Test that schema_json column exists in actual database."""

    def test_schema_json_column_exists_in_table(self):
        """schema_json column must exist in projects table definition."""
        # Get the table columns from the model
        columns = Project.__table__.columns
        column_names = [col.name for col in columns]
        
        assert 'schema_json' in column_names, f"schema_json must be in projects table columns. Found: {column_names}"

    def test_schema_json_column_position(self):
        """schema_json column should be after storage_bytes."""
        columns = list(Project.__table__.columns)
        column_names = [col.name for col in columns]
        
        # Find positions
        storage_bytes_idx = column_names.index('storage_bytes')
        schema_json_idx = column_names.index('schema_json')
        
        # schema_json should come after storage_bytes
        assert schema_json_idx > storage_bytes_idx, \
            f"schema_json (index {schema_json_idx}) should come after storage_bytes (index {storage_bytes_idx})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])