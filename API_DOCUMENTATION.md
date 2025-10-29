# Home Kitchen Manager API Documentation

## Overview

The Home Kitchen Manager API is a comprehensive REST API designed to help users manage their kitchen operations efficiently. It provides endpoints for managing kitchens, shopping lists, inventory items, and user authentication.

## Base Information

- **Base URL**: `http://localhost:8000/api/v1`
- **Authentication**: JWT Bearer Token
- **Content Type**: `application/json`
- **API Version**: 1.0.0

## Quick Start

### 1. Authentication

First, register a new user and obtain an access token:

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'

# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

### 2. Create a Kitchen

```bash
curl -X POST "http://localhost:8000/api/v1/kitchens/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Kitchen",
    "description": "Main family kitchen"
  }'
```

### 3. Create a Shopping List

```bash
curl -X POST "http://localhost:8000/api/v1/shopping-lists/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Groceries",
    "description": "Weekly grocery shopping list",
    "kitchen_id": 1
  }'
```

## API Endpoints

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get access token |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user profile |

### 🏠 Kitchens

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/kitchens/` | List user's kitchens |
| POST | `/kitchens/` | Create a new kitchen |
| GET | `/kitchens/{id}` | Get kitchen details |
| PUT | `/kitchens/{id}` | Update kitchen |
| DELETE | `/kitchens/{id}` | Delete kitchen |

### 📝 Shopping Lists

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shopping-lists/` | List shopping lists |
| POST | `/shopping-lists/` | Create shopping list |
| GET | `/shopping-lists/{id}` | Get shopping list |
| PUT | `/shopping-lists/{id}` | Update shopping list |
| DELETE | `/shopping-lists/{id}` | Delete shopping list |

### 📋 Shopping List Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shopping-lists/{id}/items/` | List items in shopping list |
| POST | `/shopping-lists/{id}/items/` | Add item to shopping list |
| PUT | `/shopping-list-items/{id}` | Update shopping list item |
| DELETE | `/shopping-list-items/{id}` | Delete shopping list item |

### 📦 Inventory Management

#### Pantry Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pantry-items/` | List pantry items |
| POST | `/pantry-items/` | Create pantry item |
| GET | `/pantry-items/{id}` | Get pantry item |
| PUT | `/pantry-items/{id}` | Update pantry item |
| DELETE | `/pantry-items/{id}` | Delete pantry item |

#### Refrigerator Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/refrigerator-items/` | List refrigerator items |
| POST | `/refrigerator-items/` | Create refrigerator item |
| GET | `/refrigerator-items/{id}` | Get refrigerator item |
| PUT | `/refrigerator-items/{id}` | Update refrigerator item |
| DELETE | `/refrigerator-items/{id}` | Delete refrigerator item |

#### Freezer Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/freezer-items/` | List freezer items |
| POST | `/freezer-items/` | Create freezer item |
| GET | `/freezer-items/{id}` | Get freezer item |
| PUT | `/freezer-items/{id}` | Update freezer item |
| DELETE | `/freezer-items/{id}` | Delete freezer item |

### 🔍 Search & Filtering

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/` | Global search across all items |
| GET | `/search/shopping-lists/` | Search shopping lists |
| GET | `/search/items/` | Search shopping list items |
| GET | `/search/inventory/` | Search inventory items |

### 🏥 Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health/` | Basic health check |
| GET | `/health/detailed/` | Detailed health status |
| GET | `/dashboard/metrics/` | System metrics |
| GET | `/dashboard/stats/` | Usage statistics |

## Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `size`: Items per page (default: 50, max: 1000)

### Filtering
- `kitchen_id`: Filter by kitchen ID
- `name`: Filter by name (partial match)
- `category`: Filter by category
- `status`: Filter by status
- `quantity_type`: Filter by quantity type (inventory items)
- `upc`: Filter by UPC code (inventory items)

### Sorting
- `sort_by`: Field to sort by (name, created_at, updated_at)
- `sort_order`: Sort direction (asc, desc)

### Search
- `q`: Search query for full-text search
- `search_in`: Fields to search in (name, description, notes)

## Response Format

### Success Response
```json
{
  "data": [...],
  "metadata": {
    "total": 100,
    "page": 1,
    "size": 50,
    "pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": ["Field is required"]
    }
  }
}
```

## Data Models

### User
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Kitchen
```json
{
  "id": 1,
  "name": "My Kitchen",
  "description": "Main family kitchen",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Shopping List
```json
{
  "id": 1,
  "name": "Weekly Groceries",
  "description": "Weekly grocery shopping list",
  "kitchen_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "items_count": 5,
  "completed_items": 2
}
```

### Shopping List Item
```json
{
  "id": 1,
  "name": "Milk",
  "description": "2% milk",
  "quantity": "1 gallon",
  "category": "Dairy",
  "notes": "Organic preferred",
  "is_purchased": false,
  "shopping_list_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Inventory Item (Pantry/Refrigerator/Freezer)
```json
{
  "id": 1,
  "name": "Rice",
  "description": "Basmati rice",
  "quantity": "5",
  "quantity_type": "lbs",
  "upc": "1234567890123",
  "kitchen_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication required or failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `DUPLICATE_ERROR` | Resource already exists |
| `DATABASE_ERROR` | Database operation failed |
| `INTERNAL_ERROR` | Internal server error |

## Rate Limiting

- **Rate Limit**: 100 requests per minute per IP
- **Burst Limit**: 20 requests per second
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Security

### Authentication
- JWT tokens with 30-minute expiration
- Refresh tokens for extended sessions
- Secure password hashing with bcrypt

### Authorization
- Kitchen-based ownership validation
- User can only access their own resources
- Role-based permissions (future enhancement)

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection headers
- CORS configuration

## Examples

### Complete Workflow Example

```bash
# 1. Register and login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secure_password123"}' \
  | jq -r '.access_token')

# 2. Create kitchen
KITCHEN_ID=$(curl -s -X POST "http://localhost:8000/api/v1/kitchens/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Kitchen", "description": "Main kitchen"}' \
  | jq -r '.id')

# 3. Create shopping list
LIST_ID=$(curl -s -X POST "http://localhost:8000/api/v1/shopping-lists/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Groceries\", \"kitchen_id\": $KITCHEN_ID}" \
  | jq -r '.id')

# 4. Add items to shopping list
curl -X POST "http://localhost:8000/api/v1/shopping-lists/$LIST_ID/items/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Milk", "quantity": "1 gallon", "category": "Dairy"}'

# 5. Add pantry item
curl -X POST "http://localhost:8000/api/v1/pantry-items/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Rice\", \"quantity\": \"5\", \"quantity_type\": \"lbs\", \"kitchen_id\": $KITCHEN_ID}"

# 6. Search items
curl -G "http://localhost:8000/api/v1/search/" \
  -H "Authorization: Bearer $TOKEN" \
  -d "q=milk" \
  -d "kitchen_id=$KITCHEN_ID"
```

## Interactive Documentation

Visit the following URLs for interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

## Support

For questions, issues, or feature requests:
- **Email**: support@kitchenmanager.com
- **Documentation**: Available at `/docs` endpoint
- **Health Status**: Check `/api/v1/health` for system status