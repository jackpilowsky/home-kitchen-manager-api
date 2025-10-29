from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, date
from typing import List, Optional
import math

from . import schemas, models
from .database import get_db
from .filters import filter_kitchens
from auth import authenticate_user, create_access_token, create_user, get_current_active_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        db=db
    )
    
    return user

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/users/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/users/me", response_model=schemas.User)
def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    # Check if email is being updated and if it's already taken
    if 'email' in update_data:
        existing_email = db.query(models.User).filter(
            models.User.email == update_data['email'],
            models.User.id != current_user.id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# Kitchen routes
@router.post("/kitchens/", response_model=schemas.Kitchen, status_code=status.HTTP_201_CREATED)
def create_kitchen(
    kitchen_data: schemas.KitchenCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new kitchen"""
    kitchen = models.Kitchen(
        name=kitchen_data.name,
        description=kitchen_data.description,
        owner_id=current_user.id
    )
    db.add(kitchen)
    db.commit()
    db.refresh(kitchen)
    return kitchen

@router.get("/kitchens/", response_model=schemas.PaginatedKitchensResponse)
def list_user_kitchens(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, created_at, updated_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List current user's kitchens with filtering and search"""
    # Base query with ownership filtering
    base_query = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id)
    
    # Apply filters
    filters = {
        'name': name,
        'owner_id': current_user.id,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    
    filtered_query = filter_kitchens(base_query, **filters)
    
    # Get total count for pagination
    total = filtered_query.count()
    
    # Apply pagination
    kitchens = filtered_query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return schemas.PaginatedKitchensResponse(
        items=kitchens,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/kitchens/{kitchen_id}", response_model=schemas.Kitchen)
def get_kitchen(
    kitchen_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific kitchen"""
    kitchen = db.query(models.Kitchen).filter(
        models.Kitchen.id == kitchen_id,
        models.Kitchen.owner_id == current_user.id
    ).first()
    
    if not kitchen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kitchen not found"
        )
    
    return kitchen

@router.put("/kitchens/{kitchen_id}", response_model=schemas.Kitchen)
def update_kitchen(
    kitchen_id: int,
    kitchen_update: schemas.KitchenUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a kitchen"""
    kitchen = db.query(models.Kitchen).filter(
        models.Kitchen.id == kitchen_id,
        models.Kitchen.owner_id == current_user.id
    ).first()
    
    if not kitchen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kitchen not found"
        )
    
    update_data = kitchen_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(kitchen, field, value)
    
    db.commit()
    db.refresh(kitchen)
    return kitchen

@router.delete("/kitchens/{kitchen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kitchen(
    kitchen_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a kitchen"""
    kitchen = db.query(models.Kitchen).filter(
        models.Kitchen.id == kitchen_id,
        models.Kitchen.owner_id == current_user.id
    ).first()
    
    if not kitchen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kitchen not found"
        )
    
    db.delete(kitchen)
    db.commit()
    return None