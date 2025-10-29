from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import math

from . import schemas, models
from .database import get_db
from .validation import (
    validate_bearer_token,
    validate_authenticated_pantry_item_access,
    validate_authenticated_pantry_item_creation,
    validate_authenticated_pantry_item_update,
    validate_authenticated_refrigerator_item_access,
    validate_authenticated_refrigerator_item_creation,
    validate_authenticated_refrigerator_item_update,
    validate_authenticated_freezer_item_access,
    validate_authenticated_freezer_item_creation,
    validate_authenticated_freezer_item_update
)

router = APIRouter()

# Pantry Item routes
@router.post("/pantry-items/", response_model=schemas.PantryItem, status_code=status.HTTP_201_CREATED)
def create_pantry_item(
    validated_data: schemas.PantryItemCreate = Depends(validate_authenticated_pantry_item_creation),
    db: Session = Depends(get_db)
):
    """Create a new pantry item"""
    db_item = models.PantryItem(**validated_data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/pantry-items/", response_model=schemas.PaginatedPantryItemsResponse)
def list_pantry_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    name: Optional[str] = Query(None, description="Filter by item name (partial match)"),
    kitchen_id: Optional[int] = Query(None, description="Filter by kitchen ID"),
    quantity_type: Optional[str] = Query(None, description="Filter by quantity type"),
    upc: Optional[str] = Query(None, description="Filter by UPC code"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, created_at, updated_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """List pantry items with filtering and pagination"""
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Base query with ownership filtering
    base_query = db.query(models.PantryItem).filter(models.PantryItem.kitchen_id.in_(kitchen_ids))
    
    # Apply filters
    if name:
        base_query = base_query.filter(models.PantryItem.name.ilike(f"%{name}%"))
    if kitchen_id:
        base_query = base_query.filter(models.PantryItem.kitchen_id == kitchen_id)
    if quantity_type:
        base_query = base_query.filter(models.PantryItem.quantity_type.ilike(f"%{quantity_type}%"))
    if upc:
        base_query = base_query.filter(models.PantryItem.upc == upc)
    if search:
        base_query = base_query.filter(
            models.PantryItem.name.ilike(f"%{search}%") |
            models.PantryItem.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
    if sort_by == "name":
        sort_field = models.PantryItem.name
    elif sort_by == "updated_at":
        sort_field = models.PantryItem.updated_at
    else:
        sort_field = models.PantryItem.created_at
    
    if sort_order == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())
    
    # Get total count
    total = base_query.count()
    
    # Apply pagination
    items = base_query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return schemas.PaginatedPantryItemsResponse(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/pantry-items/{item_id}", response_model=schemas.PantryItem)
def get_pantry_item(
    item: models.PantryItem = Depends(validate_authenticated_pantry_item_access)
):
    """Get a specific pantry item"""
    return item

@router.put("/pantry-items/{item_id}", response_model=schemas.PantryItem)
def update_pantry_item(
    item_id: int,
    item_update: schemas.PantryItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a pantry item"""
    item, validated_update = validate_authenticated_pantry_item_update(
        item_id, item_update, db=db
    )
    
    update_data = validated_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/pantry-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pantry_item(
    item: models.PantryItem = Depends(validate_authenticated_pantry_item_access),
    db: Session = Depends(get_db)
):
    """Delete a pantry item"""
    db.delete(item)
    db.commit()
    return None

# Refrigerator Item routes
@router.post("/refrigerator-items/", response_model=schemas.RefrigeratorItem, status_code=status.HTTP_201_CREATED)
def create_refrigerator_item(
    validated_data: schemas.RefrigeratorItemCreate = Depends(validate_authenticated_refrigerator_item_creation),
    db: Session = Depends(get_db)
):
    """Create a new refrigerator item"""
    db_item = models.RefrigeratorItem(**validated_data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/refrigerator-items/", response_model=schemas.PaginatedRefrigeratorItemsResponse)
def list_refrigerator_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    name: Optional[str] = Query(None, description="Filter by item name (partial match)"),
    kitchen_id: Optional[int] = Query(None, description="Filter by kitchen ID"),
    quantity_type: Optional[str] = Query(None, description="Filter by quantity type"),
    upc: Optional[str] = Query(None, description="Filter by UPC code"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, created_at, updated_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """List refrigerator items with filtering and pagination"""
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Base query with ownership filtering
    base_query = db.query(models.RefrigeratorItem).filter(models.RefrigeratorItem.kitchen_id.in_(kitchen_ids))
    
    # Apply filters
    if name:
        base_query = base_query.filter(models.RefrigeratorItem.name.ilike(f"%{name}%"))
    if kitchen_id:
        base_query = base_query.filter(models.RefrigeratorItem.kitchen_id == kitchen_id)
    if quantity_type:
        base_query = base_query.filter(models.RefrigeratorItem.quantity_type.ilike(f"%{quantity_type}%"))
    if upc:
        base_query = base_query.filter(models.RefrigeratorItem.upc == upc)
    if search:
        base_query = base_query.filter(
            models.RefrigeratorItem.name.ilike(f"%{search}%") |
            models.RefrigeratorItem.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
    if sort_by == "name":
        sort_field = models.RefrigeratorItem.name
    elif sort_by == "updated_at":
        sort_field = models.RefrigeratorItem.updated_at
    else:
        sort_field = models.RefrigeratorItem.created_at
    
    if sort_order == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())
    
    # Get total count
    total = base_query.count()
    
    # Apply pagination
    items = base_query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return schemas.PaginatedRefrigeratorItemsResponse(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/refrigerator-items/{item_id}", response_model=schemas.RefrigeratorItem)
def get_refrigerator_item(
    item: models.RefrigeratorItem = Depends(validate_authenticated_refrigerator_item_access)
):
    """Get a specific refrigerator item"""
    return item

@router.put("/refrigerator-items/{item_id}", response_model=schemas.RefrigeratorItem)
def update_refrigerator_item(
    item_id: int,
    item_update: schemas.RefrigeratorItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a refrigerator item"""
    item, validated_update = validate_authenticated_refrigerator_item_update(
        item_id, item_update, db=db
    )
    
    update_data = validated_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/refrigerator-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_refrigerator_item(
    item: models.RefrigeratorItem = Depends(validate_authenticated_refrigerator_item_access),
    db: Session = Depends(get_db)
):
    """Delete a refrigerator item"""
    db.delete(item)
    db.commit()
    return None

# Freezer Item routes
@router.post("/freezer-items/", response_model=schemas.FreezerItem, status_code=status.HTTP_201_CREATED)
def create_freezer_item(
    validated_data: schemas.FreezerItemCreate = Depends(validate_authenticated_freezer_item_creation),
    db: Session = Depends(get_db)
):
    """Create a new freezer item"""
    db_item = models.FreezerItem(**validated_data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/freezer-items/", response_model=schemas.PaginatedFreezerItemsResponse)
def list_freezer_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    name: Optional[str] = Query(None, description="Filter by item name (partial match)"),
    kitchen_id: Optional[int] = Query(None, description="Filter by kitchen ID"),
    quantity_type: Optional[str] = Query(None, description="Filter by quantity type"),
    upc: Optional[str] = Query(None, description="Filter by UPC code"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, created_at, updated_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """List freezer items with filtering and pagination"""
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Base query with ownership filtering
    base_query = db.query(models.FreezerItem).filter(models.FreezerItem.kitchen_id.in_(kitchen_ids))
    
    # Apply filters
    if name:
        base_query = base_query.filter(models.FreezerItem.name.ilike(f"%{name}%"))
    if kitchen_id:
        base_query = base_query.filter(models.FreezerItem.kitchen_id == kitchen_id)
    if quantity_type:
        base_query = base_query.filter(models.FreezerItem.quantity_type.ilike(f"%{quantity_type}%"))
    if upc:
        base_query = base_query.filter(models.FreezerItem.upc == upc)
    if search:
        base_query = base_query.filter(
            models.FreezerItem.name.ilike(f"%{search}%") |
            models.FreezerItem.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
    if sort_by == "name":
        sort_field = models.FreezerItem.name
    elif sort_by == "updated_at":
        sort_field = models.FreezerItem.updated_at
    else:
        sort_field = models.FreezerItem.created_at
    
    if sort_order == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())
    
    # Get total count
    total = base_query.count()
    
    # Apply pagination
    items = base_query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return schemas.PaginatedFreezerItemsResponse(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/freezer-items/{item_id}", response_model=schemas.FreezerItem)
def get_freezer_item(
    item: models.FreezerItem = Depends(validate_authenticated_freezer_item_access)
):
    """Get a specific freezer item"""
    return item

@router.put("/freezer-items/{item_id}", response_model=schemas.FreezerItem)
def update_freezer_item(
    item_id: int,
    item_update: schemas.FreezerItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a freezer item"""
    item, validated_update = validate_authenticated_freezer_item_update(
        item_id, item_update, db=db
    )
    
    update_data = validated_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/freezer-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_freezer_item(
    item: models.FreezerItem = Depends(validate_authenticated_freezer_item_access),
    db: Session = Depends(get_db)
):
    """Delete a freezer item"""
    db.delete(item)
    db.commit()
    return None