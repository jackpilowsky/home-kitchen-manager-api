from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from .database import get_db
from .validation import (
    validate_bearer_token,
    validate_shopping_list_id,
    validate_shopping_list_item_id,
    validate_authenticated_shopping_list_access,
    validate_authenticated_shopping_list_item_access
)

router = APIRouter()

# Shopping List routes
@router.post("/shopping-lists/", response_model=schemas.ShoppingList, status_code=status.HTTP_201_CREATED)
def create_shopping_list(
    shopping_list: schemas.ShoppingListCreate,
    current_user: dict = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    db_shopping_list = models.ShoppingList(**shopping_list.dict())
    db.add(db_shopping_list)
    db.commit()
    db.refresh(db_shopping_list)
    return db_shopping_list

@router.get("/shopping-lists/", response_model=List[schemas.ShoppingList])
def list_shopping_lists(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    shopping_lists = db.query(models.ShoppingList).offset(skip).limit(limit).all()
    return shopping_lists

@router.get("/shopping-lists/{shopping_list_id}", response_model=schemas.ShoppingList)
def get_shopping_list(
    shopping_list: models.ShoppingList = Depends(validate_authenticated_shopping_list_access)
):
    return shopping_list

@router.put("/shopping-lists/{shopping_list_id}", response_model=schemas.ShoppingList)
def update_shopping_list(
    shopping_list_update: schemas.ShoppingListUpdate,
    shopping_list: models.ShoppingList = Depends(validate_authenticated_shopping_list_access),
    db: Session = Depends(get_db)
):
    update_data = shopping_list_update.dict(exclude_unset=True)
    
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
    item: schemas.ShoppingListItemCreate,
    current_user: dict = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    # Validate that shopping list exists
    shopping_list = validate_shopping_list_id(item.shopping_list_id, db)
    
    db_item = models.ShoppingListItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/shopping-list-items/", response_model=List[schemas.ShoppingListItem])
def list_shopping_list_items(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    items = db.query(models.ShoppingListItem).offset(skip).limit(limit).all()
    return items

@router.get("/shopping-list-items/{item_id}", response_model=schemas.ShoppingListItem)
def get_shopping_list_item(
    item: models.ShoppingListItem = Depends(validate_authenticated_shopping_list_item_access)
):
    return item

@router.put("/shopping-list-items/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(
    item_update: schemas.ShoppingListItemUpdate,
    item: models.ShoppingListItem = Depends(validate_authenticated_shopping_list_item_access),
    db: Session = Depends(get_db)
):
    update_data = item_update.dict(exclude_unset=True)
    
    # Validate that the new shopping list exists if being updated
    if 'shopping_list_id' in update_data:
        validate_shopping_list_id(update_data['shopping_list_id'], db)
    
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