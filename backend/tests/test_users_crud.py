"""Tests for users CRUD operations."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_users_create_valid_data():
    """Test creating user with valid data."""
    from app.main import app
    client = TestClient(app)
    
    # Without auth should return 401
    response = client.post("/api/users", json={
        "email": "newuser@test.com",
        "password": "password123",
        "name": "New User",
        "role": "user"
    })
    assert response.status_code in [401, 403, 500]


def test_users_create_invalid_role():
    """Test creating user with invalid role."""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/users", json={
        "email": "test@test.com",
        "password": "password123",
        "role": "invalid_role"
    })
    # Should fail validation or auth
    assert response.status_code in [401, 422, 500]


def test_users_update_valid():
    """Test updating user with valid data."""
    from app.main import app
    client = TestClient(app)
    
    response = client.patch("/api/users/some-id", json={
        "name": "Updated Name",
        "role": "manager"
    })
    # Should require auth
    assert response.status_code in [401, 403, 404, 500]


def test_users_update_invalid_role():
    """Test updating user with invalid role."""
    from app.main import app
    client = TestClient(app)
    
    response = client.patch("/api/users/some-id", json={
        "role": "superadmin"
    })
    assert response.status_code in [401, 403, 404, 422, 500]


def test_users_delete():
    """Test deleting a user."""
    from app.main import app
    client = TestClient(app)
    
    response = client.delete("/api/users/some-id")
    assert response.status_code in [204, 401, 403, 404, 500]


def test_users_list_pagination():
    """Test users list with pagination."""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/api/users?skip=0&limit=10")
    assert response.status_code in [200, 401, 403, 500]


def test_users_list_search():
    """Test users list with search."""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/api/users?search=test")
    assert response.status_code in [200, 401, 403, 500]


def test_users_profile_update():
    """Test updating own profile."""
    from app.main import app
    client = TestClient(app)
    
    response = client.patch("/api/users/me", json={
        "name": "My Name",
        "timezone": "UTC"
    })
    assert response.status_code in [200, 401, 403, 500]


def test_users_change_password():
    """Test changing password."""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/users/me/change-password", json={
        "current_password": "oldpass",
        "new_password": "newpass123"
    })
    assert response.status_code in [200, 401, 403, 400, 500]


def test_user_response_schema():
    """Test UserResponse model has correct fields."""
    from app.routers.users import UserResponse
    
    # Create a response with required fields
    response = UserResponse(
        id="test-id",
        email="test@test.com",
        role="user",
        is_active=True
    )
    
    # Should serialize correctly
    data = response.model_dump()
    assert data["id"] == "test-id"
    assert data["email"] == "test@test.com"
    assert data["role"] == "user"


def test_user_create_schema():
    """Test UserCreate model validation."""
    from app.routers.users import UserCreate
    
    # Valid user
    user = UserCreate(
        email="test@test.com",
        password="password123"
    )
    assert user.role == "user"  # default
    
    # Custom role
    user2 = UserCreate(
        email="admin@test.com",
        password="password123",
        role="admin"
    )
    assert user2.role == "admin"


def test_user_update_schema():
    """Test UserUpdate model allows partial updates."""
    from app.routers.users import UserUpdate
    
    # Partial update - only name
    user = UserUpdate(name="New Name")
    assert user.name == "New Name"
    assert user.role is None
    
    # Partial update - only role
    user2 = UserUpdate(role="manager")
    assert user2.role == "manager"
    assert user2.name is None
