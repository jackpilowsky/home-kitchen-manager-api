from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from . import models
from .database import get_db

class ValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

def validate_shopping_list_id(shopping_list_id: int, db: Session = Depends(get_db)) -> models.ShoppingList:
    """Validate that shopping list exists and return it"""
    if shopping_list_id <= 0:
        raise ValidationError("Shopping list ID must be a positive integer")
    
    shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == shopping_list_id).first()
    if not shopping_list:
        raise ValidationError("Shopping list not found", status_code=404)
    
    return shopping_list

def validate_shopping_list_item_id(item_id: int, db: Session = Depends(get_db)) -> models.ShoppingListItem:
    """Validate that shopping list item exists and return it"""
    if item_id <= 0:
        raise ValidationError("Shopping list item ID must be a positive integer")
    
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        raise ValidationError("Shopping list item not found", status_code=404)
    
    return item

def validate_kitchen_id(kitchen_id: int) -> int:
    """Validate kitchen ID format"""
    if kitchen_id <= 0:
        raise ValidationError("Kitchen ID must be a positive integer")
    return kitchen_id

def validate_pagination(skip: int = 0, limit: int = 100) -> tuple[int, int]:
    """Validate pagination parameters"""
    if skip < 0:
        raise ValidationError("Skip parameter must be non-negative")
    
    if limit <= 0:
        raise ValidationError("Limit parameter must be positive")
    
    if limit > 1000:
        raise ValidationError("Limit parameter cannot exceed 1000")
    
    return skip, limit

def validate_shopping_list_name(name: str) -> str:
    """Validate shopping list name"""
    if not name or not name.strip():
        raise ValidationError("Shopping list name cannot be empty")
    
    if len(name.strip()) > 200:
        raise ValidationError("Shopping list name cannot exceed 200 characters")
    
    return name.strip()

def validate_shopping_list_description(description: Optional[str]) -> Optional[str]:
    """Validate shopping list description"""
    if description is not None:
        if len(description) > 1000:
            raise ValidationError("Description cannot exceed 1000 characters")
        return description.strip() if description.strip() else None
    return None

def validate_item_name(name: str) -> str:
    """Validate shopping list item name"""
    if not name or not name.strip():
        raise ValidationError("Item name cannot be empty")
    
    if len(name.strip()) > 100:
        raise ValidationError("Item name cannot exceed 100 characters")
    
    return name.strip()

def validate_item_quantity(quantity: str) -> str:
    """Validate shopping list item quantity"""
    if not quantity or not quantity.strip():
        raise ValidationError("Item quantity cannot be empty")
    
    if len(quantity.strip()) > 50:
        raise ValidationError("Item quantity cannot exceed 50 characters")
    
    return quantity.strip()

def validate_shopping_list_ownership(shopping_list: models.ShoppingList, kitchen_id: Optional[int] = None) -> models.ShoppingList:
    """Validate that shopping list belongs to the specified kitchen (if provided)"""
    if kitchen_id is not None and shopping_list.kitchen_id != kitchen_id:
        raise ValidationError("Shopping list does not belong to the specified kitchen", status_code=403)
    
    return shopping_list

def validate_item_belongs_to_list(item: models.ShoppingListItem, shopping_list_id: Optional[int] = None) -> models.ShoppingListItem:
    """Validate that item belongs to the specified shopping list (if provided)"""
    if shopping_list_id is not None and item.shopping_list_id != shopping_list_id:
        raise ValidationError("Item does not belong to the specified shopping list", status_code=403)
    
    return item