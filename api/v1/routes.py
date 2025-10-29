from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import math
from . import schemas, models
from .database import get_db
from .filters import filter_shopping_lists, filter_shopping_list_items
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

@router.get("/shopping-lists/", response_model=schemas.PaginatedShoppingListsResponse)
def list_shopping_lists(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    kitchen_id: Optional[int] = Query(None, description="Filter by kitchen ID"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    has_items: Optional[bool] = Query(None, description="Filter by whether list has items"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, created_at, updated_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Base query with ownership filtering
    base_query = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    )
    
    # Apply filters
    filters = {
        'name': name,
        'kitchen_id': kitchen_id,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'has_items': has_items,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'kitchen_ids': kitchen_ids  # Ensure we only get user's lists
    }
    
    filtered_query = filter_shopping_lists(base_query, **filters)
    
    # Get total count for pagination
    total = filtered_query.count()
    
    # Apply pagination
    shopping_lists = filtered_query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return schemas.PaginatedShoppingListsResponse(
        items=shopping_lists,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

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

@router.get("/shopping-list-items/", response_model=schemas.PaginatedShoppingListItemsResponse)
def list_shopping_list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    name: Optional[str] = Query(None, description="Filter by item name (partial match)"),
    shopping_list_id: Optional[int] = Query(None, description="Filter by shopping list ID"),
    kitchen_id: Optional[int] = Query(None, description="Filter by kitchen ID"),
    quantity_contains: Optional[str] = Query(None, description="Filter by quantity text (partial match)"),
    search: Optional[str] = Query(None, description="Search in name and quantity"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, quantity, created_at, updated_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Get user's shopping list IDs for ownership filtering
    user_shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).all()
    shopping_list_ids = [sl.id for sl in user_shopping_lists]
    
    # Base query with ownership filtering
    base_query = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.shopping_list_id.in_(shopping_list_ids)
    )
    
    # Apply filters
    filters = {
        'name': name,
        'shopping_list_id': shopping_list_id,
        'kitchen_id': kitchen_id,
        'quantity_contains': quantity_contains,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'shopping_list_ids': shopping_list_ids  # Ensure we only get user's items
    }
    
    filtered_query = filter_shopping_list_items(base_query, **filters)
    
    # Get total count for pagination
    total = filtered_query.count()
    
    # Apply pagination
    items = filtered_query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return schemas.PaginatedShoppingListItemsResponse(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

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