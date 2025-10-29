from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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