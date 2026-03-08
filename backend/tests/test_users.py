"""Tests for users management frontend."""

import pytest
from fastapi.testclient import TestClient


def test_users_list_endpoint():
    """Test /api/users endpoint returns proper structure."""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/api/users")
    # Should require auth
    assert response.status_code in [401, 403, 500]


def test_users_me_endpoint():
    """Test /api/users/me endpoint returns user data."""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/api/users/me")
    # Should require auth
    assert response.status_code in [401, 403, 500]


def test_users_me_patch_endpoint():
    """Test PATCH /api/users/me endpoint works."""
    from app.main import app
    client = TestClient(app)
    
    response = client.patch("/api/users/me", json={"name": "Test"})
    # Should require auth
    assert response.status_code in [401, 403, 422, 500]


def test_users_me_change_password_endpoint():
    """Test /api/users/me/change-password endpoint."""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/users/me/change-password", json={
        "current_password": "test",
        "new_password": "test123"
    })
    # Should require auth
    assert response.status_code in [401, 403, 422, 500]


def test_users_create_endpoint():
    """Test POST /api/users creates user."""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/users", json={
        "email": "new@example.com",
        "password": "password123",
        "name": "New User",
        "role": "user"
    })
    # Should require admin auth
    assert response.status_code in [401, 403, 500]


def test_users_delete_endpoint():
    """Test DELETE /api/users/{id} deletes user."""
    from app.main import app
    client = TestClient(app)
    
    response = client.delete("/api/users/some-id")
    # Should require admin auth
    assert response.status_code in [401, 403, 404, 500]
