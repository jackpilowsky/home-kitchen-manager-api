import pytest
from fastapi.testclient import TestClient
from api.v1.permissions import OwnershipValidator, PermissionError
from api.v1.models import Kitchen, ShoppingList, ShoppingListItem

def test_kitchen_ownership_validation(db_session, test_user):
    """Test kitchen ownership validation"""
    # Create a kitchen owned by test_user
    kitchen = Kitchen(name="Test Kitchen", owner_id=test_user.id)
    db_session.add(kitchen)
    db_session.commit()
    db_session.refresh(kitchen)
    
    # Should succeed for owner
    result = OwnershipValidator.validate_kitchen_ownership(kitchen.id, test_user.id, db_session)
    assert result.id == kitchen.id
    
    # Should fail for non-owner
    with pytest.raises(PermissionError):
        OwnershipValidator.validate_kitchen_ownership(kitchen.id, 99999, db_session)

def test_shopping_list_ownership_validation(db_session, test_user, test_kitchen, test_shopping_list):
    """Test shopping list ownership validation"""
    # Should succeed for owner
    result = OwnershipValidator.validate_shopping_list_ownership(test_shopping_list.id, test_user.id, db_session)
    assert result.id == test_shopping_list.id
    
    # Should fail for non-owner
    with pytest.raises(PermissionError):
        OwnershipValidator.validate_shopping_list_ownership(test_shopping_list.id, 99999, db_session)

def test_shopping_list_item_ownership_validation(db_session, test_user, test_shopping_list):
    """Test shopping list item ownership validation"""
    # Create an item
    item = ShoppingListItem(
        name="Test Item",
        quantity="1 piece",
        shopping_list_id=test_shopping_list.id
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    
    # Should succeed for owner
    result = OwnershipValidator.validate_shopping_list_item_ownership(item.id, test_user.id, db_session)
    assert result.id == item.id
    
    # Should fail for non-owner
    with pytest.raises(PermissionError):
        OwnershipValidator.validate_shopping_list_item_ownership(item.id, 99999, db_session)

def test_get_user_resources(db_session, test_user, test_kitchen, test_shopping_list):
    """Test getting user's accessible resources"""
    # Create an item
    item = ShoppingListItem(
        name="Test Item",
        quantity="1 piece",
        shopping_list_id=test_shopping_list.id
    )
    db_session.add(item)
    db_session.commit()
    
    # Test getting user's kitchens
    kitchens = OwnershipValidator.get_user_kitchens(test_user.id, db_session)
    assert len(kitchens) >= 1
    assert test_kitchen.id in [k.id for k in kitchens]
    
    # Test getting user's shopping lists
    shopping_lists = OwnershipValidator.get_user_shopping_lists(test_user.id, db_session)
    assert len(shopping_lists) >= 1
    assert test_shopping_list.id in [sl.id for sl in shopping_lists]
    
    # Test getting user's shopping list items
    items = OwnershipValidator.get_user_shopping_list_items(test_user.id, db_session)
    assert len(items) >= 1
    assert item.id in [i.id for i in items]

def test_cross_user_access_denied(client: TestClient, db_session):
    """Test that users cannot access each other's resources"""
    from auth import create_user, create_access_token
    
    # Create two users
    user1 = create_user("user1", "user1@example.com", "Password123", db=db_session)
    user2 = create_user("user2", "user2@example.com", "Password123", db=db_session)
    
    # User1 creates a kitchen
    kitchen1 = Kitchen(name="User1 Kitchen", owner_id=user1.id)
    db_session.add(kitchen1)
    db_session.commit()
    db_session.refresh(kitchen1)
    
    # User2 tries to access User1's kitchen
    token2 = create_access_token(data={"sub": user2.username})
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    response = client.get(f"/api/v1/auth/kitchens/{kitchen1.id}", headers=headers2)
    assert response.status_code == 404  # Should not find kitchen owned by another user