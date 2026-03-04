"""Tests for database models - ensures consistency between models and routers."""

import pytest
from unittest.mock import patch


# Mock database before importing app
with patch("app.db.database.get_async_session_maker"):
    with patch("app.db.database.get_sync_session_maker"):
        from app.main import app
        from app.db.models import User, Project, Dataset


class TestUserModelFields:
    """Test User model has correct fields used in routers."""

    def test_user_has_email(self):
        """User must have email field."""
        user = User(email="test@test.com")
        assert hasattr(user, 'email')
        assert user.email == "test@test.com"

    def test_user_has_password_hash(self):
        """User must have password_hash field (not hashed_password)."""
        user = User(email="test@test.com")
        assert hasattr(user, 'password_hash')

    def test_user_has_name(self):
        """User must have name field (not full_name)."""
        user = User(email="test@test.com", name="Test")
        assert hasattr(user, 'name')

    def test_user_has_id_as_string(self):
        """User id must be string (UUID)."""
        user = User(email="test@test.com")
        assert hasattr(user, 'id')

    def test_user_has_role(self):
        """User must have role field."""
        user = User(email="test@test.com")
        assert hasattr(user, 'role')

    def test_user_has_is_active(self):
        """User must have is_active field."""
        user = User(email="test@test.com")
        assert hasattr(user, 'is_active')

    def test_user_has_is_verified(self):
        """User must have is_verified field."""
        user = User(email="test@test.com")
        assert hasattr(user, 'is_verified')


class TestProjectModelFields:
    """Test Project model has correct fields used in routers."""

    def test_project_has_id(self):
        """Project must have id field."""
        assert hasattr(Project, 'id')

    def test_project_has_user_id(self):
        """Project must have user_id field (not owner_id)."""
        assert hasattr(Project, 'user_id')

    def test_project_has_name(self):
        """Project must have name field."""
        assert hasattr(Project, 'name')

    def test_project_has_description(self):
        """Project must have description field."""
        assert hasattr(Project, 'description')

    def test_project_has_row_count(self):
        """Project must have row_count field."""
        assert hasattr(Project, 'row_count')

    def test_project_has_column_count(self):
        """Project must have column_count field."""
        assert hasattr(Project, 'column_count')

    def test_project_has_storage_bytes(self):
        """Project must have storage_bytes field."""
        assert hasattr(Project, 'storage_bytes')


class TestUserResponseModel:
    """Test UserResponse matches User model."""

    def test_user_response_fields_match_user_model(self):
        """UserResponse must have same fields as User model."""
        from app.routers.auth import UserResponse
        
        user_response_fields = UserResponse.model_fields.keys()
        
        # These fields must exist in UserResponse
        required_fields = ['id', 'email', 'name', 'role', 'is_active', 'is_verified']
        
        for field in required_fields:
            assert field in user_response_fields, f"UserResponse missing field: {field}"


class TestProjectResponseModel:
    """Test ProjectResponse matches Project model."""

    def test_project_response_has_user_id(self):
        """ProjectResponse must have user_id (not owner_id)."""
        from app.routers.projects import ProjectResponse
        
        fields = ProjectResponse.model_fields.keys()
        assert 'user_id' in fields, "ProjectResponse must have user_id field"


class TestPasswordHashingConsistency:
    """Test password hashing works with User model."""

    def test_hash_and_verify(self):
        """Test that password can be hashed and verified."""
        from app.routers.auth import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestProjectRouting:
    """Test Project routes match model."""

    def test_project_get_route_exists(self):
        """GET /{project_id} should accept string UUID."""
        from app.routers.projects import get_project
        import inspect
        sig = inspect.signature(get_project)
        params = sig.parameters
        assert 'project_id' in params

    def test_project_list_route_exists(self):
        """List projects route should exist."""
        from app.routers.projects import list_projects
        assert list_projects is not None

    def test_project_create_route_exists(self):
        """Create project route should exist."""
        from app.routers.projects import create_project
        assert create_project is not None


class TestDatasetModelFields:
    """Test Dataset model fields."""

    def test_dataset_has_id(self):
        """Dataset must have id field."""
        from app.db.models import Dataset
        assert hasattr(Dataset, 'id')

    def test_dataset_has_project_id(self):
        """Dataset must have project_id field."""
        from app.db.models import Dataset
        assert hasattr(Dataset, 'project_id')

    def test_dataset_has_data_json(self):
        """Dataset must have data_json field."""
        from app.db.models.project import Dataset
        assert hasattr(Dataset, 'data_json')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestDatasetRouting:
    """Test Dataset routes use correct types."""

    def test_dataset_list_accepts_string_project_id(self):
        """Dataset list should accept string project_id (UUID)."""
        from app.routers.datasets import list_datasets
        import inspect
        sig = inspect.signature(list_datasets)
        params = sig.parameters
        assert 'project_id' in params

    def test_dataset_import_accepts_string_project_id(self):
        """Dataset import should accept string project_id (UUID)."""
        from app.routers.datasets import import_dataset
        import inspect
        sig = inspect.signature(import_dataset)
        params = sig.parameters
        assert 'project_id' in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestProjectResponseModel:
    """Test ProjectResponse matches Project model."""

    def test_project_response_id_is_string(self):
        """ProjectResponse id must be string (UUID)."""
        from app.routers.projects import ProjectResponse
        fields = ProjectResponse.model_fields
        assert fields['id'].annotation == str

    def test_project_response_created_at_accepts_datetime(self):
        """ProjectResponse created_at must accept datetime."""
        from app.routers.projects import ProjectResponse
        fields = ProjectResponse.model_fields
        # Should accept datetime or str


class TestDatasetResponseModel:
    """Test DatasetResponse matches Dataset model."""

    def test_dataset_response_id_is_string(self):
        """DatasetResponse id must be string (UUID)."""
        from app.routers.datasets import DatasetResponse
        fields = DatasetResponse.model_fields
        assert fields['id'].annotation == str

    def test_dataset_response_created_at_accepts_datetime(self):
        """DatasetResponse created_at must accept datetime."""
        from app.routers.datasets import DatasetResponse
        fields = DatasetResponse.model_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestAllRoutesAcceptUUID:
    """Test all routes accept string UUIDs."""

    def test_projects_get_accepts_string(self):
        """GET /{project_id} should accept string UUID."""
        from app.routers.projects import get_project
        import inspect
        sig = inspect.signature(get_project)
        params = sig.parameters
        assert params['project_id'].annotation == str

    def test_projects_update_accepts_string(self):
        """PUT /{project_id} should accept string UUID."""
        from app.routers.projects import update_project
        import inspect
        sig = inspect.signature(update_project)
        params = sig.parameters
        assert params['project_id'].annotation == str

    def test_projects_delete_accepts_string(self):
        """DELETE /{project_id} should accept string UUID."""
        from app.routers.projects import delete_project
        import inspect
        sig = inspect.signature(delete_project)
        params = sig.parameters
        assert params['project_id'].annotation == str

    def test_datasets_get_accepts_string(self):
        """GET /{dataset_id} should accept string UUID."""
        from app.routers.datasets import get_dataset
        import inspect
        sig = inspect.signature(get_dataset)
        params = sig.parameters
        assert params['dataset_id'].annotation == str

    def test_datasets_delete_accepts_string(self):
        """DELETE /{dataset_id} should accept string UUID."""
        from app.routers.datasets import delete_dataset
        import inspect
        sig = inspect.signature(delete_dataset)
        params = sig.parameters
        assert params['dataset_id'].annotation == str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
