from typing import Optional, List, Any
from sqlalchemy.orm import Query
from sqlalchemy import or_, and_, func
from datetime import datetime, date
from . import models

class BaseFilter:
    """Base class for filtering functionality"""
    
    def __init__(self, query: Query):
        self.query = query
    
    def apply_text_search(self, search_term: Optional[str], *fields) -> Query:
        """Apply text search across multiple fields"""
        if not search_term:
            return self.query
        
        search_conditions = []
        for field in fields:
            search_conditions.append(field.ilike(f"%{search_term}%"))
        
        return self.query.filter(or_(*search_conditions))
    
    def apply_date_range(self, date_from: Optional[date], date_to: Optional[date], date_field) -> Query:
        """Apply date range filtering"""
        if date_from:
            self.query = self.query.filter(date_field >= date_from)
        if date_to:
            # Add one day to include the entire end date
            end_date = datetime.combine(date_to, datetime.max.time())
            self.query = self.query.filter(date_field <= end_date)
        return self.query
    
    def apply_pagination(self, skip: int = 0, limit: int = 100) -> Query:
        """Apply pagination with validation"""
        # Validate pagination parameters
        skip = max(0, skip)
        limit = min(max(1, limit), 1000)  # Max 1000 items per page
        
        return self.query.offset(skip).limit(limit)

class KitchenFilter(BaseFilter):
    """Filtering for Kitchen entities"""
    
    def filter_by_name(self, name: Optional[str]) -> 'KitchenFilter':
        """Filter kitchens by name (partial match)"""
        if name:
            self.query = self.query.filter(models.Kitchen.name.ilike(f"%{name}%"))
        return self
    
    def filter_by_owner(self, owner_id: Optional[int]) -> 'KitchenFilter':
        """Filter kitchens by owner"""
        if owner_id:
            self.query = self.query.filter(models.Kitchen.owner_id == owner_id)
        return self
    
    def search(self, search_term: Optional[str]) -> 'KitchenFilter':
        """Search across kitchen name and description"""
        if search_term:
            self.query = self.apply_text_search(
                search_term,
                models.Kitchen.name,
                models.Kitchen.description
            )
        return self
    
    def filter_by_date_range(self, date_from: Optional[date], date_to: Optional[date]) -> 'KitchenFilter':
        """Filter by creation date range"""
        self.query = self.apply_date_range(date_from, date_to, models.Kitchen.created_at)
        return self

class ShoppingListFilter(BaseFilter):
    """Filtering for ShoppingList entities"""
    
    def filter_by_name(self, name: Optional[str]) -> 'ShoppingListFilter':
        """Filter shopping lists by name (partial match)"""
        if name:
            self.query = self.query.filter(models.ShoppingList.name.ilike(f"%{name}%"))
        return self
    
    def filter_by_kitchen(self, kitchen_id: Optional[int]) -> 'ShoppingListFilter':
        """Filter shopping lists by kitchen"""
        if kitchen_id:
            self.query = self.query.filter(models.ShoppingList.kitchen_id == kitchen_id)
        return self
    
    def filter_by_kitchen_ids(self, kitchen_ids: Optional[List[int]]) -> 'ShoppingListFilter':
        """Filter shopping lists by multiple kitchen IDs"""
        if kitchen_ids:
            self.query = self.query.filter(models.ShoppingList.kitchen_id.in_(kitchen_ids))
        return self
    
    def search(self, search_term: Optional[str]) -> 'ShoppingListFilter':
        """Search across shopping list name and description"""
        if search_term:
            self.query = self.apply_text_search(
                search_term,
                models.ShoppingList.name,
                models.ShoppingList.description
            )
        return self
    
    def filter_by_date_range(self, date_from: Optional[date], date_to: Optional[date]) -> 'ShoppingListFilter':
        """Filter by creation date range"""
        self.query = self.apply_date_range(date_from, date_to, models.ShoppingList.created_at)
        return self
    
    def filter_by_has_items(self, has_items: Optional[bool]) -> 'ShoppingListFilter':
        """Filter by whether shopping list has items"""
        if has_items is not None:
            if has_items:
                self.query = self.query.filter(models.ShoppingList.items.any())
            else:
                self.query = self.query.filter(~models.ShoppingList.items.any())
        return self

class ShoppingListItemFilter(BaseFilter):
    """Filtering for ShoppingListItem entities"""
    
    def filter_by_name(self, name: Optional[str]) -> 'ShoppingListItemFilter':
        """Filter items by name (partial match)"""
        if name:
            self.query = self.query.filter(models.ShoppingListItem.name.ilike(f"%{name}%"))
        return self
    
    def filter_by_shopping_list(self, shopping_list_id: Optional[int]) -> 'ShoppingListItemFilter':
        """Filter items by shopping list"""
        if shopping_list_id:
            self.query = self.query.filter(models.ShoppingListItem.shopping_list_id == shopping_list_id)
        return self
    
    def filter_by_shopping_list_ids(self, shopping_list_ids: Optional[List[int]]) -> 'ShoppingListItemFilter':
        """Filter items by multiple shopping list IDs"""
        if shopping_list_ids:
            self.query = self.query.filter(models.ShoppingListItem.shopping_list_id.in_(shopping_list_ids))
        return self
    
    def filter_by_kitchen(self, kitchen_id: Optional[int]) -> 'ShoppingListItemFilter':
        """Filter items by kitchen (through shopping list)"""
        if kitchen_id:
            self.query = self.query.join(models.ShoppingList).filter(
                models.ShoppingList.kitchen_id == kitchen_id
            )
        return self
    
    def filter_by_quantity_contains(self, quantity_text: Optional[str]) -> 'ShoppingListItemFilter':
        """Filter items by quantity text (partial match)"""
        if quantity_text:
            self.query = self.query.filter(models.ShoppingListItem.quantity.ilike(f"%{quantity_text}%"))
        return self
    
    def search(self, search_term: Optional[str]) -> 'ShoppingListItemFilter':
        """Search across item name and quantity"""
        if search_term:
            self.query = self.apply_text_search(
                search_term,
                models.ShoppingListItem.name,
                models.ShoppingListItem.quantity
            )
        return self
    
    def filter_by_date_range(self, date_from: Optional[date], date_to: Optional[date]) -> 'ShoppingListItemFilter':
        """Filter by creation date range"""
        self.query = self.apply_date_range(date_from, date_to, models.ShoppingListItem.created_at)
        return self

# Sorting functionality
class SortOptions:
    """Sorting options for different entities"""
    
    KITCHEN_SORT_FIELDS = {
        'name': models.Kitchen.name,
        'created_at': models.Kitchen.created_at,
        'updated_at': models.Kitchen.updated_at,
    }
    
    SHOPPING_LIST_SORT_FIELDS = {
        'name': models.ShoppingList.name,
        'created_at': models.ShoppingList.created_at,
        'updated_at': models.ShoppingList.updated_at,
    }
    
    SHOPPING_LIST_ITEM_SORT_FIELDS = {
        'name': models.ShoppingListItem.name,
        'quantity': models.ShoppingListItem.quantity,
        'created_at': models.ShoppingListItem.created_at,
        'updated_at': models.ShoppingListItem.updated_at,
    }
    
    @staticmethod
    def apply_sorting(query: Query, sort_by: Optional[str], sort_order: Optional[str], sort_fields: dict) -> Query:
        """Apply sorting to query"""
        if not sort_by or sort_by not in sort_fields:
            # Default sorting by created_at desc
            sort_by = 'created_at'
            sort_order = 'desc'
        
        field = sort_fields[sort_by]
        
        if sort_order and sort_order.lower() == 'desc':
            query = query.order_by(field.desc())
        else:
            query = query.order_by(field.asc())
        
        return query

# Convenience functions for easy use in routes
def filter_kitchens(query: Query, **filters) -> Query:
    """Apply filters to kitchen query"""
    kitchen_filter = KitchenFilter(query)
    
    if 'name' in filters:
        kitchen_filter = kitchen_filter.filter_by_name(filters['name'])
    if 'owner_id' in filters:
        kitchen_filter = kitchen_filter.filter_by_owner(filters['owner_id'])
    if 'search' in filters:
        kitchen_filter = kitchen_filter.search(filters['search'])
    if 'date_from' in filters or 'date_to' in filters:
        kitchen_filter = kitchen_filter.filter_by_date_range(
            filters.get('date_from'), filters.get('date_to')
        )
    
    # Apply sorting
    query = SortOptions.apply_sorting(
        kitchen_filter.query,
        filters.get('sort_by'),
        filters.get('sort_order'),
        SortOptions.KITCHEN_SORT_FIELDS
    )
    
    return query

def filter_shopping_lists(query: Query, **filters) -> Query:
    """Apply filters to shopping list query"""
    sl_filter = ShoppingListFilter(query)
    
    if 'name' in filters:
        sl_filter = sl_filter.filter_by_name(filters['name'])
    if 'kitchen_id' in filters:
        sl_filter = sl_filter.filter_by_kitchen(filters['kitchen_id'])
    if 'kitchen_ids' in filters:
        sl_filter = sl_filter.filter_by_kitchen_ids(filters['kitchen_ids'])
    if 'search' in filters:
        sl_filter = sl_filter.search(filters['search'])
    if 'date_from' in filters or 'date_to' in filters:
        sl_filter = sl_filter.filter_by_date_range(
            filters.get('date_from'), filters.get('date_to')
        )
    if 'has_items' in filters:
        sl_filter = sl_filter.filter_by_has_items(filters['has_items'])
    
    # Apply sorting
    query = SortOptions.apply_sorting(
        sl_filter.query,
        filters.get('sort_by'),
        filters.get('sort_order'),
        SortOptions.SHOPPING_LIST_SORT_FIELDS
    )
    
    return query

def filter_shopping_list_items(query: Query, **filters) -> Query:
    """Apply filters to shopping list item query"""
    item_filter = ShoppingListItemFilter(query)
    
    if 'name' in filters:
        item_filter = item_filter.filter_by_name(filters['name'])
    if 'shopping_list_id' in filters:
        item_filter = item_filter.filter_by_shopping_list(filters['shopping_list_id'])
    if 'shopping_list_ids' in filters:
        item_filter = item_filter.filter_by_shopping_list_ids(filters['shopping_list_ids'])
    if 'kitchen_id' in filters:
        item_filter = item_filter.filter_by_kitchen(filters['kitchen_id'])
    if 'quantity_contains' in filters:
        item_filter = item_filter.filter_by_quantity_contains(filters['quantity_contains'])
    if 'search' in filters:
        item_filter = item_filter.search(filters['search'])
    if 'date_from' in filters or 'date_to' in filters:
        item_filter = item_filter.filter_by_date_range(
            filters.get('date_from'), filters.get('date_to')
        )
    
    # Apply sorting
    query = SortOptions.apply_sorting(
        item_filter.query,
        filters.get('sort_by'),
        filters.get('sort_order'),
        SortOptions.SHOPPING_LIST_ITEM_SORT_FIELDS
    )
    
    return query