# Filtering and Search Features

## Overview
The Home Kitchen Manager API now includes comprehensive filtering and search functionality across all entities (Kitchens, Shopping Lists, and Shopping List Items).

## Features Implemented

### 🔍 **Advanced Filtering**

#### Shopping Lists
- **Name filtering**: Partial match on shopping list names
- **Kitchen filtering**: Filter by specific kitchen ID
- **Date range filtering**: Filter by creation date range
- **Has items filtering**: Filter lists that have/don't have items
- **Search**: Full-text search across name and description fields

#### Shopping List Items
- **Name filtering**: Partial match on item names
- **Shopping list filtering**: Filter by specific shopping list ID
- **Kitchen filtering**: Filter items by kitchen (through shopping list)
- **Quantity filtering**: Partial match on quantity text
- **Date range filtering**: Filter by creation date range
- **Search**: Full-text search across name and quantity fields

#### Kitchens
- **Name filtering**: Partial match on kitchen names
- **Date range filtering**: Filter by creation date range
- **Search**: Full-text search across name and description fields

### 📊 **Pagination & Sorting**

#### Pagination
- **Configurable page size**: 1-1000 items per page
- **Skip/offset support**: Navigate through large datasets
- **Metadata included**: Total count, page info, has_next/has_prev flags
- **Performance optimized**: Efficient database queries

#### Sorting
- **Multiple sort fields**: name, created_at, updated_at
- **Sort direction**: Ascending or descending
- **Default sorting**: Most recent items first

### 🔎 **Global Search**

#### Multi-Entity Search
- **Cross-entity search**: Search across kitchens, shopping lists, and items simultaneously
- **Relevance-based results**: Results organized by entity type
- **Ownership filtering**: Only searches user's own data

#### Search Suggestions
- **Auto-complete**: Get suggestions based on partial queries
- **Category-specific**: Filter suggestions by entity type
- **Real-time**: Fast response for interactive UIs

#### Recent Items
- **Activity tracking**: Get recently created/updated items
- **Multi-category**: Recent items across all entity types
- **Configurable limits**: Control number of recent items returned

### 📈 **Analytics & Statistics**

#### Usage Statistics
- **Entity counts**: Total kitchens, shopping lists, and items
- **List analysis**: Lists with items vs empty lists
- **User-specific**: Statistics scoped to current user's data

## API Endpoints

### Shopping Lists
```
GET /api/v1/shopping-lists/
Parameters:
- skip: int (0+) - Items to skip for pagination
- limit: int (1-1000) - Items per page
- name: str - Filter by name (partial match)
- kitchen_id: int - Filter by kitchen ID
- search: str - Search in name and description
- date_from: date - Filter from date (YYYY-MM-DD)
- date_to: date - Filter to date (YYYY-MM-DD)
- has_items: bool - Filter by whether list has items
- sort_by: str - Sort field (name, created_at, updated_at)
- sort_order: str - Sort direction (asc, desc)
```

### Shopping List Items
```
GET /api/v1/shopping-list-items/
Parameters:
- skip: int (0+) - Items to skip for pagination
- limit: int (1-1000) - Items per page
- name: str - Filter by item name (partial match)
- shopping_list_id: int - Filter by shopping list ID
- kitchen_id: int - Filter by kitchen ID
- quantity_contains: str - Filter by quantity text
- search: str - Search in name and quantity
- date_from: date - Filter from date (YYYY-MM-DD)
- date_to: date - Filter to date (YYYY-MM-DD)
- sort_by: str - Sort field (name, quantity, created_at, updated_at)
- sort_order: str - Sort direction (asc, desc)
```

### Kitchens
```
GET /api/v1/auth/kitchens/
Parameters:
- skip: int (0+) - Items to skip for pagination
- limit: int (1-1000) - Items per page
- name: str - Filter by name (partial match)
- search: str - Search in name and description
- date_from: date - Filter from date (YYYY-MM-DD)
- date_to: date - Filter to date (YYYY-MM-DD)
- sort_by: str - Sort field (name, created_at, updated_at)
- sort_order: str - Sort direction (asc, desc)
```

### Global Search
```
GET /api/v1/search/global?q={search_term}
GET /api/v1/search/suggestions?q={partial_term}
GET /api/v1/search/recent
GET /api/v1/search/stats
```

## Response Format

### Paginated Response
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 50,
  "pages": 3,
  "has_next": true,
  "has_prev": false
}
```

### Global Search Response
```json
{
  "query": "search term",
  "results": {
    "kitchens": {
      "items": [...],
      "total": 5
    },
    "shopping_lists": {
      "items": [...],
      "total": 12
    },
    "shopping_list_items": {
      "items": [...],
      "total": 25
    }
  }
}
```

## Usage Examples

### Filter shopping lists by name
```
GET /api/v1/shopping-lists/?name=Grocery
```

### Search across all fields
```
GET /api/v1/shopping-lists/?search=weekly food
```

### Filter by date range
```
GET /api/v1/shopping-lists/?date_from=2024-01-01&date_to=2024-01-31
```

### Paginated results with sorting
```
GET /api/v1/shopping-lists/?skip=20&limit=10&sort_by=name&sort_order=asc
```

### Global search
```
GET /api/v1/search/global?q=milk
```

### Get search suggestions
```
GET /api/v1/search/suggestions?q=app&category=items
```

## Security Features

- **Ownership filtering**: Users can only search/filter their own data
- **Input validation**: All parameters validated for type and range
- **SQL injection protection**: Parameterized queries prevent injection
- **Rate limiting ready**: Pagination limits prevent resource abuse

## Performance Optimizations

- **Database indexes**: Optimized queries with proper indexing
- **Efficient joins**: Minimal database queries for ownership validation
- **Pagination limits**: Maximum 1000 items per request
- **Query optimization**: Filtered queries before pagination for efficiency

## Testing

Comprehensive test suite includes:
- Filter parameter validation
- Search functionality across all entities
- Pagination metadata accuracy
- Sorting behavior verification
- Cross-user access prevention
- Performance boundary testing