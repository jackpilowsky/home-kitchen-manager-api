from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    selected_kitchen_id = Column(Integer, ForeignKey("kitchens.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    kitchens = relationship("Kitchen", back_populates="owner", foreign_keys="Kitchen.owner_id")
    selected_kitchen = relationship("Kitchen", foreign_keys=[selected_kitchen_id], post_update=True)

class Kitchen(Base):
    __tablename__ = "kitchens"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="kitchens", foreign_keys=[owner_id])
    shopping_lists = relationship("ShoppingList", back_populates="kitchen")
    pantry_items = relationship("PantryItem", back_populates="kitchen")
    refrigerator_items = relationship("RefrigeratorItem", back_populates="kitchen")
    freezer_items = relationship("FreezerItem", back_populates="kitchen")

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    kitchen_id = Column(Integer, ForeignKey("kitchens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    kitchen = relationship("Kitchen", back_populates="shopping_lists")
    items = relationship("ShoppingListItem", back_populates="shopping_list")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=False)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    shopping_list = relationship("ShoppingList", back_populates="items")

class PantryItem(Base):
    __tablename__ = "pantry_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(String(50), nullable=True)
    quantity_type = Column(String(50), nullable=True)  # e.g., "pieces", "lbs", "oz", "cups"
    upc = Column(String(20), nullable=True)  # Universal Product Code
    kitchen_id = Column(Integer, ForeignKey("kitchens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    kitchen = relationship("Kitchen", back_populates="pantry_items")

class RefrigeratorItem(Base):
    __tablename__ = "refrigerator_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(String(50), nullable=True)
    quantity_type = Column(String(50), nullable=True)  # e.g., "pieces", "lbs", "oz", "cups"
    upc = Column(String(20), nullable=True)  # Universal Product Code
    kitchen_id = Column(Integer, ForeignKey("kitchens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    kitchen = relationship("Kitchen", back_populates="refrigerator_items")

class FreezerItem(Base):
    __tablename__ = "freezer_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(String(50), nullable=True)
    quantity_type = Column(String(50), nullable=True)  # e.g., "pieces", "lbs", "oz", "cups"
    upc = Column(String(20), nullable=True)  # Universal Product Code
    kitchen_id = Column(Integer, ForeignKey("kitchens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    kitchen = relationship("Kitchen", back_populates="freezer_items")