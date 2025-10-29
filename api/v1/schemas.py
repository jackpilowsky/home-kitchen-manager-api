from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime
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
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
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
    kitchens: List["Kitchen"] = []
    
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

# Update forward references
ShoppingList.model_rebuild()