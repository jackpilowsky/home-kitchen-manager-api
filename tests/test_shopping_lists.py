import pytest
from fastapi.testclient import TestClient

def test_create_shopping_list(client: TestClient, auth_headers, test_kitchen):
    """Test creating a shopping list"""
    response = client.post(
        "/api/v1/shopping-lists/",
        headers=auth_headers,
        json={
            "name": "Grocery List",
            "description": "Weekly groceries",
            "kitchen_id": test_kitchen.id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Grocery List"
    assert data["kitchen_id"] == test_kitchen.id

def test_create_shopping_list_unauthorized(client: TestClient, test_kitchen):
    """Test creating a shopping list without authentication"""
    response = client.post(
        "/api/v1/shopping-lists/",
        json={
            "name": "Grocery List",
            "kitchen_id": test_kitchen.id
        }
    )
    assert response.status_code == 401

def test_list_shopping_lists(client: TestClient, auth_headers, test_shopping_list):
    """Test listing shopping lists"""
    response = client.get("/api/v1/shopping-lists/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(sl["name"] == "Test Shopping List" for sl in data)

def test_get_shopping_list(client: TestClient, auth_headers, test_shopping_list):
    """Test getting a specific shopping list"""
    response = client.get(f"/api/v1/shopping-lists/{test_shopping_list.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Shopping List"
    assert data["id"] == test_shopping_list.id

def test_get_shopping_list_not_found(client: TestClient, auth_headers):
    """Test getting a non-existent shopping list"""
    response = client.get("/api/v1/shopping-lists/99999", headers=auth_headers)
    assert response.status_code == 404

def test_update_shopping_list(client: TestClient, auth_headers, test_shopping_list):
    """Test updating a shopping list"""
    response = client.put(
        f"/api/v1/shopping-lists/{test_shopping_list.id}",
        headers=auth_headers,
        json={
            "name": "Updated Shopping List",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Shopping List"
    assert data["description"] == "Updated description"

def test_delete_shopping_list(client: TestClient, auth_headers, test_shopping_list):
    """Test deleting a shopping list"""
    response = client.delete(f"/api/v1/shopping-lists/{test_shopping_list.id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify shopping list is deleted
    response = client.get(f"/api/v1/shopping-lists/{test_shopping_list.id}", headers=auth_headers)
    assert response.status_code == 404

def test_create_shopping_list_item(client: TestClient, auth_headers, test_shopping_list):
    """Test creating a shopping list item"""
    response = client.post(
        "/api/v1/shopping-list-items/",
        headers=auth_headers,
        json={
            "name": "Milk",
            "quantity": "1 gallon",
            "shopping_list_id": test_shopping_list.id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Milk"
    assert data["quantity"] == "1 gallon"
    assert data["shopping_list_id"] == test_shopping_list.id

def test_list_shopping_list_items(client: TestClient, auth_headers, test_shopping_list):
    """Test listing shopping list items"""
    # First create an item
    client.post(
        "/api/v1/shopping-list-items/",
        headers=auth_headers,
        json={
            "name": "Bread",
            "quantity": "2 loaves",
            "shopping_list_id": test_shopping_list.id
        }
    )
    
    response = client.get("/api/v1/shopping-list-items/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["name"] == "Bread" for item in data)