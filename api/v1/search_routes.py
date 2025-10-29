from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import date
import math

from . import schemas, models
from .database import get_db
from .validation import validate_bearer_token
from .filters import filter_kitchens, filter_shopping_lists, filter_shopping_list_items

router = APIRouter()

@router.get("/search/global", response_model=Dict[str, Any])
def global_search(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return per category"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """Global search across all user's data"""
    results = {}
    
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Search kitchens
    kitchen_query = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id)
    filtered_kitchens = filter_kitchens(kitchen_query, search=q, sort_by="name", sort_order="asc")
    kitchen_results = filtered_kitchens.offset(skip).limit(limit).all()
    
    # Search shopping lists
    shopping_list_query = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    )
    filtered_shopping_lists = filter_shopping_lists(
        shopping_list_query, 
        search=q, 
        kitchen_ids=kitchen_ids,
        sort_by="name", 
        sort_order="asc"
    )
    shopping_list_results = filtered_shopping_lists.offset(skip).limit(limit).all()
    
    # Search shopping list items
    user_shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).all()
    shopping_list_ids = [sl.id for sl in user_shopping_lists]
    
    item_query = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.shopping_list_id.in_(shopping_list_ids)
    )
    filtered_items = filter_shopping_list_items(
        item_query, 
        search=q, 
        shopping_list_ids=shopping_list_ids,
        sort_by="name", 
        sort_order="asc"
    )
    item_results = filtered_items.offset(skip).limit(limit).all()
    
    return {
        "query": q,
        "results": {
            "kitchens": {
                "items": [schemas.Kitchen.from_orm(k) for k in kitchen_results],
                "total": filtered_kitchens.count()
            },
            "shopping_lists": {
                "items": [schemas.ShoppingList.from_orm(sl) for sl in shopping_list_results],
                "total": filtered_shopping_lists.count()
            },
            "shopping_list_items": {
                "items": [schemas.ShoppingListItem.from_orm(item) for item in item_results],
                "total": filtered_items.count()
            }
        }
    }

@router.get("/search/suggestions", response_model=List[str])
def search_suggestions(
    q: str = Query(..., min_length=1, description="Search query for suggestions"),
    category: Optional[str] = Query(None, description="Category to search (kitchens, shopping_lists, items)"),
    limit: int = Query(10, ge=1, le=50, description="Number of suggestions to return"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """Get search suggestions based on partial query"""
    suggestions = set()
    
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    if not category or category == "kitchens":
        # Get kitchen name suggestions
        kitchen_names = db.query(models.Kitchen.name).filter(
            models.Kitchen.owner_id == current_user.id,
            models.Kitchen.name.ilike(f"%{q}%")
        ).limit(limit).all()
        suggestions.update([name[0] for name in kitchen_names])
    
    if not category or category == "shopping_lists":
        # Get shopping list name suggestions
        sl_names = db.query(models.ShoppingList.name).filter(
            models.ShoppingList.kitchen_id.in_(kitchen_ids),
            models.ShoppingList.name.ilike(f"%{q}%")
        ).limit(limit).all()
        suggestions.update([name[0] for name in sl_names])
    
    if not category or category == "items":
        # Get shopping list item name suggestions
        user_shopping_lists = db.query(models.ShoppingList).filter(
            models.ShoppingList.kitchen_id.in_(kitchen_ids)
        ).all()
        shopping_list_ids = [sl.id for sl in user_shopping_lists]
        
        item_names = db.query(models.ShoppingListItem.name).filter(
            models.ShoppingListItem.shopping_list_id.in_(shopping_list_ids),
            models.ShoppingListItem.name.ilike(f"%{q}%")
        ).limit(limit).all()
        suggestions.update([name[0] for name in item_names])
    
    return sorted(list(suggestions))[:limit]

@router.get("/search/recent", response_model=Dict[str, Any])
def recent_items(
    limit: int = Query(10, ge=1, le=50, description="Number of recent items per category"),
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """Get recently created/updated items"""
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Recent kitchens
    recent_kitchens = db.query(models.Kitchen).filter(
        models.Kitchen.owner_id == current_user.id
    ).order_by(models.Kitchen.updated_at.desc()).limit(limit).all()
    
    # Recent shopping lists
    recent_shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).order_by(models.ShoppingList.updated_at.desc()).limit(limit).all()
    
    # Recent shopping list items
    user_shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).all()
    shopping_list_ids = [sl.id for sl in user_shopping_lists]
    
    recent_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.shopping_list_id.in_(shopping_list_ids)
    ).order_by(models.ShoppingListItem.updated_at.desc()).limit(limit).all()
    
    return {
        "recent": {
            "kitchens": [schemas.Kitchen.from_orm(k) for k in recent_kitchens],
            "shopping_lists": [schemas.ShoppingList.from_orm(sl) for sl in recent_shopping_lists],
            "shopping_list_items": [schemas.ShoppingListItem.from_orm(item) for item in recent_items]
        }
    }

@router.get("/search/stats", response_model=Dict[str, Any])
def search_stats(
    current_user: models.User = Depends(validate_bearer_token),
    db: Session = Depends(get_db)
):
    """Get search and usage statistics"""
    # Get user's kitchen IDs for ownership filtering
    user_kitchens = db.query(models.Kitchen).filter(models.Kitchen.owner_id == current_user.id).all()
    kitchen_ids = [kitchen.id for kitchen in user_kitchens]
    
    # Count totals
    total_kitchens = len(user_kitchens)
    
    total_shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).count()
    
    user_shopping_lists = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids)
    ).all()
    shopping_list_ids = [sl.id for sl in user_shopping_lists]
    
    total_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.shopping_list_id.in_(shopping_list_ids)
    ).count()
    
    # Get lists with items vs empty lists
    lists_with_items = db.query(models.ShoppingList).filter(
        models.ShoppingList.kitchen_id.in_(kitchen_ids),
        models.ShoppingList.items.any()
    ).count()
    
    empty_lists = total_shopping_lists - lists_with_items
    
    return {
        "totals": {
            "kitchens": total_kitchens,
            "shopping_lists": total_shopping_lists,
            "shopping_list_items": total_items
        },
        "breakdown": {
            "lists_with_items": lists_with_items,
            "empty_lists": empty_lists
        }
    }