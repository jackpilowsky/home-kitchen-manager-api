import pytest
from fastapi.testclient import TestClient
from api.v1.exceptions import (
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ConflictException
)

def test_validation_error_response(client: TestClient):
    """Test validation error response format"""
    # Test with invalid data
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "",  # Invalid: empty username
            "email": "invalid-email",  # Invalid: bad email format
            "password": "weak"  # Invalid: weak password
        }
    )
    
    assert response.status_code == 422
    data = response.json()
    
    # Check error response structure
    assert "error" in data
    assert "message" in data["error"]
    assert "error_code" in data["error"]
    assert "error_type" in data["error"]
    assert "timestamp" in data["error"]
    assert "request_id" in data["error"]
    
    assert data["error"]["error_type"] == "validation"

def test_authentication_error_response(client: TestClient):
    """Test authentication error response"""
    # Test with invalid credentials
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    
    assert data["error"]["error_type"] == "authentication"
    assert data["error"]["error_code"] == "INVALID_CREDENTIALS"

def test_authorization_error_response(client: TestClient, auth_headers, db_session):
    """Test authorization error response"""
    from api.v1.models import Kitchen, User
    from auth import create_user
    
    # Create another user and their kitchen
    other_user = create_user("otheruser", "other@example.com", "Password123", db=db_session)
    other_kitchen = Kitchen(name="Other Kitchen", owner_id=other_user.id)
    db_session.add(other_kitchen)
    db_session.commit()
    
    # Try to access other user's kitchen
    response = client.get(f"/api/v1/auth/kitchens/{other_kitchen.id}", headers=auth_headers)
    
    assert response.status_code == 403
    data = response.json()
    
    assert data["error"]["error_type"] == "authorization"
    assert data["error"]["error_code"] == "KITCHEN_ACCESS_DENIED"

def test_not_found_error_response(client: TestClient, auth_headers):
    """Test not found error response"""
    # Try to access non-existent kitchen
    response = client.get("/api/v1/auth/kitchens/99999", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    
    assert data["error"]["error_type"] == "not_found"
    assert data["error"]["error_code"] == "RESOURCE_NOT_FOUND"

def test_conflict_error_response(client: TestClient, test_user):
    """Test conflict error response"""
    # Try to register with existing username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",  # Same as test_user
            "email": "newemail@example.com",
            "password": "NewPassword123"
        }
    )
    
    assert response.status_code == 409
    data = response.json()
    
    assert data["error"]["error_type"] == "conflict"
    assert data["error"]["error_code"] == "RESOURCE_CONFLICT"

def test_invalid_token_error(client: TestClient):
    """Test invalid token error response"""
    # Use invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/users/me", headers=headers)
    
    assert response.status_code == 401
    data = response.json()
    
    assert data["error"]["error_type"] == "authentication"
    assert data["error"]["error_code"] == "INVALID_TOKEN"

def test_expired_token_simulation(client: TestClient):
    """Test expired token handling"""
    # This would require creating an expired token, which is complex
    # For now, we'll test with a malformed token that triggers JWT error
    headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired"}
    response = client.get("/api/v1/auth/users/me", headers=headers)
    
    assert response.status_code == 401
    data = response.json()
    
    assert data["error"]["error_type"] == "authentication"

def test_missing_authorization_header(client: TestClient):
    """Test missing authorization header"""
    response = client.get("/api/v1/auth/users/me")
    
    assert response.status_code == 401
    data = response.json()
    
    assert data["error"]["error_type"] == "authentication"

def test_invalid_request_method(client: TestClient):
    """Test invalid HTTP method"""
    response = client.patch("/api/v1/auth/users/me")  # PATCH not allowed
    
    assert response.status_code == 405
    data = response.json()
    
    assert data["error"]["error_code"] == "METHOD_NOT_ALLOWED"

def test_invalid_json_payload(client: TestClient):
    """Test invalid JSON in request body"""
    response = client.post(
        "/api/v1/auth/register",
        data="invalid json",  # Not JSON
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 422

def test_missing_required_fields(client: TestClient):
    """Test missing required fields"""
    response = client.post(
        "/api/v1/auth/register",
        json={}  # Missing all required fields
    )
    
    assert response.status_code == 422
    data = response.json()
    
    assert data["error"]["error_type"] == "validation"
    assert "validation_errors" in data["error"]["context"]

def test_invalid_field_types(client: TestClient):
    """Test invalid field types"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": 123,  # Should be string
            "email": "valid@example.com",
            "password": "ValidPassword123"
        }
    )
    
    assert response.status_code == 422
    data = response.json()
    
    assert data["error"]["error_type"] == "validation"

def test_error_response_includes_request_info(client: TestClient):
    """Test that error responses include request information"""
    response = client.get("/api/v1/auth/users/me")
    
    assert response.status_code == 401
    data = response.json()
    
    # Check that request info is included
    assert "path" in data["error"]
    assert "method" in data["error"]
    assert data["error"]["path"] == "/api/v1/auth/users/me"
    assert data["error"]["method"] == "GET"

def test_error_response_has_unique_request_id(client: TestClient):
    """Test that each error response has a unique request ID"""
    response1 = client.get("/api/v1/auth/users/me")
    response2 = client.get("/api/v1/auth/users/me")
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Request IDs should be different
    assert data1["error"]["request_id"] != data2["error"]["request_id"]

def test_parameter_validation_errors(client: TestClient, auth_headers):
    """Test parameter validation in query strings"""
    # Test invalid pagination parameters
    response = client.get("/api/v1/shopping-lists/?skip=-1&limit=0", headers=auth_headers)
    
    assert response.status_code == 422
    data = response.json()
    
    assert data["error"]["error_type"] == "validation"

def test_database_constraint_error_handling(client: TestClient, test_user, auth_headers, db_session):
    """Test database constraint error handling"""
    from api.v1.models import Kitchen
    
    # Create a kitchen
    kitchen = Kitchen(name="Test Kitchen", owner_id=test_user.id)
    db_session.add(kitchen)
    db_session.commit()
    
    # Try to create shopping list with non-existent kitchen
    response = client.post(
        "/api/v1/shopping-lists/",
        headers=auth_headers,
        json={
            "name": "Test List",
            "kitchen_id": 99999  # Non-existent kitchen
        }
    )
    
    # Should handle the foreign key constraint error gracefully
    assert response.status_code in [400, 404, 500]  # Depending on validation order

def test_large_request_handling(client: TestClient, auth_headers):
    """Test handling of oversized requests"""
    # Create a very long name
    long_name = "x" * 1000
    
    response = client.post(
        "/api/v1/shopping-lists/",
        headers=auth_headers,
        json={
            "name": long_name,
            "kitchen_id": 1
        }
    )
    
    # Should be handled gracefully (either validation error or success with truncation)
    assert response.status_code in [201, 422]

def test_concurrent_request_error_handling(client: TestClient):
    """Test error handling under concurrent requests"""
    # This is a basic test - in practice you'd use threading or async
    responses = []
    
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "concurrent_user",
                "email": "concurrent@example.com", 
                "password": "Password123"
            }
        )
        responses.append(response)
    
    # First should succeed, others should fail with conflict
    success_count = sum(1 for r in responses if r.status_code == 201)
    conflict_count = sum(1 for r in responses if r.status_code == 409)
    
    assert success_count == 1
    assert conflict_count == 4