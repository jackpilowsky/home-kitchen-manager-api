from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models

class PermissionError(HTTPException):
    def __init__(self, detail: str = "Permission denied", status_code: int = 403):
        super().__init__(status_code=status_code, detail=detail)

class OwnershipValidator:
    """Centralized ownership validation for all resources"""
    
    @staticmethod
    def validate_kitchen_ownership(kitchen_id: int, user_id: int, db: Session) -> models.Kitchen:
        """Validate that user owns the kitchen"""
        kitchen = db.query(models.Kitchen).filter(
            models.Kitchen.id == kitchen_id,
            models.Kitchen.owner_id == user_id
        ).first()
        
        if not kitchen:
            raise PermissionError("Kitchen not found or access denied")
        
        return kitchen
    
    @staticmethod
    def validate_shopping_list_ownership(shopping_list_id: int, user_id: int, db: Session) -> models.ShoppingList:
        """Validate that user owns the shopping list through kitchen ownership"""
        shopping_list = db.query(models.ShoppingList).join(models.Kitchen).filter(
            models.ShoppingList.id == shopping_list_id,
            models.Kitchen.owner_id == user_id
        ).first()
        
        if not shopping_list:
            raise PermissionError("Shopping list not found or access denied")
        
        return shopping_list
    
    @staticmethod
    def validate_shopping_list_item_ownership(item_id: int, user_id: int, db: Session) -> models.ShoppingListItem:
        """Validate that user owns the shopping list item through kitchen ownership"""
        item = db.query(models.ShoppingListItem).join(
            models.ShoppingList
        ).join(models.Kitchen).filter(
            models.ShoppingListItem.id == item_id,
            models.Kitchen.owner_id == user_id
        ).first()
        
        if not item:
            raise PermissionError("Shopping list item not found or access denied")
        
        return item
    
    @staticmethod
    def validate_user_can_access_kitchen(kitchen_id: int, user_id: int, db: Session) -> bool:
        """Check if user can access a kitchen (for future role-based access)"""
        kitchen = db.query(models.Kitchen).filter(
            models.Kitchen.id == kitchen_id,
            models.Kitchen.owner_id == user_id
        ).first()
        
        return kitchen is not None
    
    @staticmethod
    def get_user_kitchens(user_id: int, db: Session) -> list[models.Kitchen]:
        """Get all kitchens accessible to the user"""
        return db.query(models.Kitchen).filter(models.Kitchen.owner_id == user_id).all()
    
    @staticmethod
    def get_user_shopping_lists(user_id: int, db: Session) -> list[models.ShoppingList]:
        """Get all shopping lists accessible to the user"""
        return db.query(models.ShoppingList).join(models.Kitchen).filter(
            models.Kitchen.owner_id == user_id
        ).all()
    
    @staticmethod
    def get_user_shopping_list_items(user_id: int, db: Session) -> list[models.ShoppingListItem]:
        """Get all shopping list items accessible to the user"""
        return db.query(models.ShoppingListItem).join(
            models.ShoppingList
        ).join(models.Kitchen).filter(
            models.Kitchen.owner_id == user_id
        ).all()

# Convenience functions for common operations
def ensure_kitchen_access(kitchen_id: int, user: models.User, db: Session) -> models.Kitchen:
    """Ensure user has access to kitchen, return kitchen if valid"""
    return OwnershipValidator.validate_kitchen_ownership(kitchen_id, user.id, db)

def ensure_shopping_list_access(shopping_list_id: int, user: models.User, db: Session) -> models.ShoppingList:
    """Ensure user has access to shopping list, return shopping list if valid"""
    return OwnershipValidator.validate_shopping_list_ownership(shopping_list_id, user.id, db)

def ensure_shopping_list_item_access(item_id: int, user: models.User, db: Session) -> models.ShoppingListItem:
    """Ensure user has access to shopping list item, return item if valid"""
    return OwnershipValidator.validate_shopping_list_item_ownership(item_id, user.id, db)