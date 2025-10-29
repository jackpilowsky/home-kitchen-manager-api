from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from .database import get_db
from .validation import (
    validate_shopping_list_id,
    validate_shopping_list_item_id,
    validate_kitchen_id,
    validate_pagination,
    validate_shopping_list_name,
    validate_shopping_list_description,
    validate_item_name,
    validate_item_quantity,
    validate_shopping_list_ownership,
    validate_item_belongs_to_list
)

router = APIRouter()

# Shopping List routes
@router.post("/shopping-lists/", response_model=schemas.ShoppingList, status_code=status.HTTP_201_CREATED)
def create_shopping_list(shopping_list: schemas.ShoppingListCreate, db: Session = Depends(get_db)):
    # Validate input data
    validated_name = validate_shopping_list_name(shopping_list.name)
    validated_description = validate_shopping_list_description(shopping_list.description)
    validated_kitchen_id = validate_kitchen_id(shopping_list.kitchen_id)
    
    db_shopping_list = models.ShoppingList(
        name=validated_name,
        description=validated_description,
        kitchen_id=validated_kitchen_id
    )
    db.add(db_shopping_list)
    db.commit()
    db.refresh(db_shopping_list)
    return db_shopping_list

@router.get("/shopping-lists/", response_model=List[schemas.ShoppingList])
def list_shopping_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Validate pagination parameters
    validated_skip, validated_limit = validate_pagination(skip, limit)
    
    shopping_lists = db.query(models.ShoppingList).offset(validated_skip).limit(validated_limit).all()
    return shopping_lists

@router.get("/shopping-lists/{shopping_list_id}", response_model=schemas.ShoppingList)
def get_shopping_list(shopping_list: models.ShoppingList = Depends(validate_shopping_list_id)):
    return shopping_list

@router.put("/shopping-lists/{shopping_list_id}", response_model=schemas.ShoppingList)
def update_shopping_list(
    shopping_list_update: schemas.ShoppingListUpdate,
    shopping_list: models.ShoppingList = Depends(validate_shopping_list_id),
    db: Session = Depends(get_db)
):
    update_data = shopping_list_update.dict(exclude_unset=True)
    
    # Validate each field that's being updated
    if 'name' in update_data:
        update_data['name'] = validate_shopping_list_name(update_data['name'])
    if 'description' in update_data:
        update_data['description'] = validate_shopping_list_description(update_data['description'])
    if 'kitchen_id' in update_data:
        update_data['kitchen_id'] = validate_kitchen_id(update_data['kitchen_id'])
    
    for field, value in update_data.items():
        setattr(shopping_list, field, value)
    
    db.commit()
    db.refresh(shopping_list)
    return shopping_list

@router.delete("/shopping-lists/{shopping_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list(
    shopping_list: models.ShoppingList = Depends(validate_shopping_list_id),
    db: Session = Depends(get_db)
):
    db.delete(shopping_list)
    db.commit()
    return None

# Shopping List Item routes
@router.post("/shopping-list-items/", response_model=schemas.ShoppingListItem, status_code=status.HTTP_201_CREATED)
def create_shopping_list_item(item: schemas.ShoppingListItemCreate, db: Session = Depends(get_db)):
    # Validate input data
    validated_name = validate_item_name(item.name)
    validated_quantity = validate_item_quantity(item.quantity)
    
    # Validate that shopping list exists
    shopping_list = validate_shopping_list_id(item.shopping_list_id, db)
    
    db_item = models.ShoppingListItem(
        name=validated_name,
        quantity=validated_quantity,
        shopping_list_id=shopping_list.id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/shopping-list-items/", response_model=List[schemas.ShoppingListItem])
def list_shopping_list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Validate pagination parameters
    validated_skip, validated_limit = validate_pagination(skip, limit)
    
    items = db.query(models.ShoppingListItem).offset(validated_skip).limit(validated_limit).all()
    return items

@router.get("/shopping-list-items/{item_id}", response_model=schemas.ShoppingListItem)
def get_shopping_list_item(item: models.ShoppingListItem = Depends(validate_shopping_list_item_id)):
    return item

@router.put("/shopping-list-items/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(
    item_update: schemas.ShoppingListItemUpdate,
    item: models.ShoppingListItem = Depends(validate_shopping_list_item_id),
    db: Session = Depends(get_db)
):
    update_data = item_update.dict(exclude_unset=True)
    
    # Validate each field that's being updated
    if 'name' in update_data:
        update_data['name'] = validate_item_name(update_data['name'])
    if 'quantity' in update_data:
        update_data['quantity'] = validate_item_quantity(update_data['quantity'])
    if 'shopping_list_id' in update_data:
        # Validate that the new shopping list exists
        validate_shopping_list_id(update_data['shopping_list_id'], db)
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/shopping-list-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list_item(
    item: models.ShoppingListItem = Depends(validate_shopping_list_item_id),
    db: Session = Depends(get_db)
):
    db.delete(item)
    db.commit()
    return None