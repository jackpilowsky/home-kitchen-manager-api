from __future__ import annotations
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Union, Any
from datetime import datetime, date
import re

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 30:
            raise ValueError('Password must be no more than 30 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        # Ensure password is within bcrypt's byte limit when encoded
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too complex (exceeds 72 bytes when encoded)')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Kitchen schemas
class KitchenBase(BaseModel):
    name: str
    description: Optional[str] = None

class KitchenCreate(KitchenBase):
    pass

class KitchenUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Kitchen(KitchenBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    shopping_lists: List["ShoppingList"] = []
    
    class Config:
        from_attributes = True

# Shopping List schemas
class ShoppingListBase(BaseModel):
    name: str
    description: Optional[str] = None
    kitchen_id: int

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    kitchen_id: Optional[int] = None

class ShoppingList(ShoppingListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List["ShoppingListItem"] = []
    
    class Config:
        from_attributes = True

# Shopping List Item schemas
class ShoppingListItemBase(BaseModel):
    name: str
    quantity: str
    shopping_list_id: int

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    shopping_list_id: Optional[int] = None

class ShoppingListItem(ShoppingListItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Filter and Search schemas
class KitchenFilters(BaseModel):
    name: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

class ShoppingListFilters(BaseModel):
    name: Optional[str] = None
    kitchen_id: Optional[int] = None
    search: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    has_items: Optional[bool] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

class ShoppingListItemFilters(BaseModel):
    name: Optional[str] = None
    shopping_list_id: Optional[int] = None
    kitchen_id: Optional[int] = None
    quantity_contains: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

# Pagination response schema
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedKitchensResponse(BaseModel):
    items: List[Kitchen]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedShoppingListsResponse(BaseModel):
    items: List[ShoppingList]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedShoppingListItemsResponse(BaseModel):
    items: List[ShoppingListItem]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

# Pantry Item schemas
class PantryItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: Optional[str] = None
    quantity_type: Optional[str] = None
    upc: Optional[str] = None
    kitchen_id: int

class PantryItemCreate(PantryItemBase):
    pass

class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    quantity_type: Optional[str] = None
    upc: Optional[str] = None
    kitchen_id: Optional[int] = None

class PantryItem(PantryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Refrigerator Item schemas
class RefrigeratorItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: Optional[str] = None
    quantity_type: Optional[str] = None
    upc: Optional[str] = None
    kitchen_id: int

class RefrigeratorItemCreate(RefrigeratorItemBase):
    pass

class RefrigeratorItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    quantity_type: Optional[str] = None
    upc: Optional[str] = None
    kitchen_id: Optional[int] = None

class RefrigeratorItem(RefrigeratorItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Freezer Item schemas
class FreezerItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: Optional[str] = None
    quantity_type: Optional[str] = None
    upc: Optional[str] = None
    kitchen_id: int

class FreezerItemCreate(FreezerItemBase):
    pass

class FreezerItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    quantity_type: Optional[str] = None
    upc: Optional[str] = None
    kitchen_id: Optional[int] = None

class FreezerItem(FreezerItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Paginated response schemas for new items
class PaginatedPantryItemsResponse(BaseModel):
    items: List[PantryItem]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedRefrigeratorItemsResponse(BaseModel):
    items: List[RefrigeratorItem]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedFreezerItemsResponse(BaseModel):
    items: List[FreezerItem]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

# Update forward references
ShoppingList.model_rebuild()