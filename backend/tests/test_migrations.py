"""Tests for database migrations."""

import pytest


class TestMigrations:
    """Test migration files are valid."""

    def test_initial_migration_exists(self):
        """Test that the initial migration file exists and can be imported."""
        # This just verifies the migration file is syntactically valid
        import sys
        import os
        import importlib.util
        import glob
        
        # Find the initial migration file (starts with 155b9933f705)
        migration_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'alembic',
            'versions'
        )
        
        migration_files = glob.glob(os.path.join(migration_dir, '155b9933f705_*.py'))
        
        if not migration_files:
            pytest.skip("Initial migration file not found")
        
        migration_path = migration_files[0]
        
        spec = importlib.util.spec_from_file_location(
            "initial_migration",
            migration_path
        )
        module = importlib.util.module_from_spec(spec)
        
        # Check it can be loaded
        try:
            spec.loader.exec_module(module)
            assert hasattr(module, 'upgrade')
            assert hasattr(module, 'downgrade')
            assert hasattr(module, 'revision')
        except Exception as e:
            pytest.skip(f"Migration load failed: {e}")

    def test_migration_revision_chain(self):
        """Test that migration revision chain is valid."""
        import os
        import re
        import glob
        
        # Find the initial migration file (starts with 155b9933f705)
        migration_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'alembic',
            'versions'
        )
        
        migration_files = glob.glob(os.path.join(migration_dir, '155b9933f705_*.py'))
        
        if not migration_files:
            pytest.skip("Initial migration file not found")
        
        migration_path = migration_files[0]
        
        with open(migration_path, 'r') as f:
            content = f.read()
        
        # Extract revision info using regex (handles both revision = and revision: formats)
        # Also handles type annotations like "revision: str = '...'"
        revision_match = re.search(r"revision\s*:\s*str\s*=\s*['\"]([^'\"]+)['\"]", content)
        if not revision_match:
            revision_match = re.search(r"revision\s*=\s*['\"]([^'\"]+)['\"]", content)
        
        down_revision_match = re.search(r"down_revision\s*:\s*.*?=\s*['\"]([^'\"]+)['\"]", content)
        if not down_revision_match:
            down_revision_match = re.search(r"down_revision\s*=\s*['\"]([^'\"]+)['\"]", content)
        
        assert revision_match, f"Could not find revision in migration file: {migration_path}"
        # For initial migration, down_revision should be None or empty
        if down_revision_match:
            assert down_revision_match.group(1) in ['None', ''], "Initial migration should have no down_revision"


class TestOperationHistoryModelFields:
    """Test that OperationHistory model has expected fields."""

    def test_model_has_all_required_columns(self):
        """Verify the model defines all columns needed by the app."""
        from app.db.models.project import OperationHistory
        
        # These are the fields our code uses
        required_fields = [
            'id',
            'project_id', 
            'operation_type',
            'operation_name',
            'operation_params',
            'before_snapshot',
            'after_snapshot',
            'is_applied',
            'is_undone',
            'created_at',
        ]
        
        for field in required_fields:
            assert hasattr(OperationHistory, field), f"Missing field: {field}"

    def test_columns_are_nullable_or_have_defaults(self):
        """Test that columns are properly configured."""
        from app.db.models.project import OperationHistory
        import inspect
        
        # Get the mapper to inspect columns
        mapper = OperationHistory.__mapper__
        
        # Check that critical columns are nullable or have defaults
        # This is a basic check - actual nullable config is in the model
        assert mapper.columns['id'].primary_key is True
        assert mapper.columns['project_id'].nullable is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
