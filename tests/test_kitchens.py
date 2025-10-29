import pytest
from fastapi.testclient import TestClient

def test_create_kitchen(client: TestClient, auth_headers):
    """Test creating a kitchen"""
    response = client.post(
        "/api/v1/auth/kitchens/",
        headers=auth_headers,
        json={
            "name": "My Kitchen",
            "description": "A beautiful kitchen"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Kitchen"
    assert data["description"] == "A beautiful kitchen"
    assert "owner_id" in data

def test_create_kitchen_unauthorized(client: TestClient):
    """Test creating a kitchen without authentication"""
    response = client.post(
        "/api/v1/auth/kitchens/",
        json={
            "name": "My Kitchen",
            "description": "A beautiful kitchen"
        }
    )
    assert response.status_code == 401

def test_list_user_kitchens(client: TestClient, auth_headers, test_kitchen):
    """Test listing user's kitchens"""
    response = client.get("/api/v1/auth/kitchens/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(kitchen["name"] == "Test Kitchen" for kitchen in data)

def test_get_kitchen(client: TestClient, auth_headers, test_kitchen):
    """Test getting a specific kitchen"""
    response = client.get(f"/api/v1/auth/kitchens/{test_kitchen.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Kitchen"
    assert data["id"] == test_kitchen.id

def test_get_kitchen_not_found(client: TestClient, auth_headers):
    """Test getting a non-existent kitchen"""
    response = client.get("/api/v1/auth/kitchens/99999", headers=auth_headers)
    assert response.status_code == 404

def test_update_kitchen(client: TestClient, auth_headers, test_kitchen):
    """Test updating a kitchen"""
    response = client.put(
        f"/api/v1/auth/kitchens/{test_kitchen.id}",
        headers=auth_headers,
        json={
            "name": "Updated Kitchen Name",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Kitchen Name"
    assert data["description"] == "Updated description"

def test_delete_kitchen(client: TestClient, auth_headers, test_kitchen):
    """Test deleting a kitchen"""
    response = client.delete(f"/api/v1/auth/kitchens/{test_kitchen.id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify kitchen is deleted
    response = client.get(f"/api/v1/auth/kitchens/{test_kitchen.id}", headers=auth_headers)
    assert response.status_code == 404