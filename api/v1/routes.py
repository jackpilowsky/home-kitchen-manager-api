from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from .database import get_db
from .validation import (
    validate_bearer_token,
    validate_authenticated_shopping_list_access,
    validate_authenticated_shopping_list_item_access,
    validate_authenticated_shopping_list_creation,
    validate_authenticated_shopping_list_update,
    validate_authenticated_shopping_list_item_creation,
    validate_authenticated_shopping_list_item_update
)

router = APIRouter()

# Shopping List routes
@router.post("/shopping-lists/", response_model=schemas.ShoppingList, status_code=status.HTTP_201_CREATED)
def create_shopping_list(
    validated_data: schemas.ShoppingListCreate = Depends(validate_authenticated_shopping_list_creation),
    db: Session = Depends(get_db)
):
    db_shopping_list = models.ShoppingList(**validated_data.dict())
    db.add(db_shopping_list)
    db.commit()
    db.refresh(db_shopping_list)
    return db_shopping_list

@router.get("/shopping-lists/", response_model=List[schemas.ShoppingList])
def list_shopping_lists(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    # Only return shopping lists from user's kitchens
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).offset(skip).limit(limit).all()
    return shopping_lists

@router.get("/shopping-lists/{shopping_list_id}", response_model=schemas.ShoppingList)
def get_shopping_list(
    shopping_list: models.ShoppingList = Depends(validate_authenticated_shopping_list_access)
):
    return shopping_list

@router.put("/shopping-lists/{shopping_list_id}", response_model=schemas.ShoppingList)
def update_shopping_list(
    shopping_list_id: int,
    shopping_list_update: schemas.ShoppingListUpdate,
    db: Session = Depends(get_db)
):
    shopping_list, validated_update = validate_authenticated_shopping_list_update(
        shopping_list_id, shopping_list_update, db=db
    )
    
    update_data = validated_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(shopping_list, field, value)
    
    db.commit()
    db.refresh(shopping_list)
    return shopping_list

@router.delete("/shopping-lists/{shopping_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list(
    shopping_list: models.ShoppingList = Depends(validate_authenticated_shopping_list_access),
    db: Session = Depends(get_db)
):
    db.delete(shopping_list)
    db.commit()
    return None

# Shopping List Item routes
@router.post("/shopping-list-items/", response_model=schemas.ShoppingListItem, status_code=status.HTTP_201_CREATED)
def create_shopping_list_item(
    validated_data: schemas.ShoppingListItemCreate = Depends(validate_authenticated_shopping_list_item_creation),
    db: Session = Depends(get_db)
):
    db_item = models.ShoppingListItem(**validated_data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/shopping-list-items/", response_model=List[schemas.ShoppingListItem])
def list_shopping_list_items(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    # Only return items from user's kitchens
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    items = db.query(models.ShoppingListItem).join(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).offset(skip).limit(limit).all()
    return items

@router.get("/shopping-list-items/{item_id}", response_model=schemas.ShoppingListItem)
def get_shopping_list_item(
    item: models.ShoppingListItem = Depends(validate_authenticated_shopping_list_item_access)
):
    return item

@router.put("/shopping-list-items/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(
    item_id: int,
    item_update: schemas.ShoppingListItemUpdate,
    db: Session = Depends(get_db)
):
    item, validated_update = validate_authenticated_shopping_list_item_update(
        item_id, item_update, db=db
    )
    
    update_data = validated_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/shopping-list-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list_item(
    item: models.ShoppingListItem = Depends(validate_authenticated_shopping_list_item_access),
    db: Session = Depends(get_db)
):
    db.delete(item)
    db.commit()
    return None