import pytest
from fastapi.testclient import TestClient

def test_user_registration(client: TestClient):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "first_name": "New",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["is_active"] is True
    assert "hashed_password" not in data

def test_user_registration_duplicate_username(client: TestClient, test_user):
    """Test user registration with duplicate username"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",  # Same as test_user
            "email": "different@example.com",
            "password": "NewPassword123"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_user_registration_duplicate_email(client: TestClient, test_user):
    """Test user registration with duplicate email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "differentuser",
            "email": "test@example.com",  # Same as test_user
            "password": "NewPassword123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_user_registration_weak_password(client: TestClient):
    """Test user registration with weak password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "weak"  # Too weak
        }
    )
    assert response.status_code == 422

def test_user_login_success(client: TestClient, test_user):
    """Test successful user login"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_user_login_invalid_credentials(client: TestClient, test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/users/me")
    assert response.status_code == 401

def test_update_current_user(client: TestClient, auth_headers):
    """Test updating current user info"""
    response = client.put(
        "/api/v1/auth/users/me",
        headers=auth_headers,
        json={
            "first_name": "Updated",
            "last_name": "Name"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"