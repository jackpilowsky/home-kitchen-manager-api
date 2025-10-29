from sqlalchemy.orm import Session
from . import models
from .exceptions import (
    KitchenNotFoundException,
    ShoppingListNotFoundException,
    ShoppingListItemNotFoundException,
    KitchenAccessDeniedException,
    ShoppingListAccessDeniedException,
    ShoppingListItemAccessDeniedException
)

class OwnershipValidator:
    """Centralized ownership validation for all resources"""
    
    @staticmethod
    def validate_kitchen_ownership(kitchen_id: int, user_id: int, db: Session) -> models.Kitchen:
        """Validate that user owns the kitchen"""
        # First check if kitchen exists
        kitchen = db.query(models.Kitchen).filter(models.Kitchen.id == kitchen_id).first()
        if not kitchen:
            raise KitchenNotFoundException(kitchen_id)
        
        # Then check ownership
        if kitchen.owner_id != user_id:
            raise KitchenAccessDeniedException(kitchen_id)
        
        return kitchen
    
    @staticmethod
    def validate_shopping_list_ownership(shopping_list_id: int, user_id: int, db: Session) -> models.ShoppingList:
        """Validate that user owns the shopping list through kitchen ownership"""
        # First check if shopping list exists
        shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == shopping_list_id).first()
        if not shopping_list:
            raise ShoppingListNotFoundException(shopping_list_id)
        
        # Then check ownership through kitchen
        kitchen = db.query(models.Kitchen).filter(models.Kitchen.id == shopping_list.kitchen_id).first()
        if not kitchen or kitchen.owner_id != user_id:
            raise ShoppingListAccessDeniedException(shopping_list_id)
        
        return shopping_list
    
    @staticmethod
    def validate_shopping_list_item_ownership(item_id: int, user_id: int, db: Session) -> models.ShoppingListItem:
        """Validate that user owns the shopping list item through kitchen ownership"""
        # First check if item exists
        item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
        if not item:
            raise ShoppingListItemNotFoundException(item_id)
        
        # Then check ownership through shopping list and kitchen
        shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == item.shopping_list_id).first()
        if not shopping_list:
            raise ShoppingListItemAccessDeniedException(item_id)
        
        kitchen = db.query(models.Kitchen).filter(models.Kitchen.id == shopping_list.kitchen_id).first()
        if not kitchen or kitchen.owner_id != user_id:
            raise ShoppingListItemAccessDeniedException(item_id)
        
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