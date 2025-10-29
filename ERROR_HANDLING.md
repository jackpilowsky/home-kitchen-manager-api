# Error Handling Documentation

## Overview
The Home Kitchen Manager API implements comprehensive error handling with standardized error responses, proper HTTP status codes, detailed logging, and graceful error recovery.

## Error Response Format

All API errors follow a consistent JSON structure:

```json
{
  "error": {
    "message": "Human-readable error description",
    "error_code": "MACHINE_READABLE_ERROR_CODE",
    "error_type": "category_of_error",
    "context": {
      "field": "field_name",
      "value": "invalid_value",
      "additional_info": "..."
    },
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "path": "/api/v1/shopping-lists/",
    "method": "POST"
  }
}
```

## Error Categories

### 1. Validation Errors (422)
**Error Type**: `validation`
**Common Codes**: `VALIDATION_ERROR`, `REQUIRED_FIELD_MISSING`

Triggered by:
- Invalid request data format
- Missing required fields
- Field type mismatches
- Business rule violations

**Example**:
```json
{
  "error": {
    "message": "Validation failed",
    "error_code": "VALIDATION_ERROR",
    "error_type": "validation",
    "context": {
      "validation_errors": [
        {
          "field": "email",
          "message": "field required",
          "type": "value_error.missing"
        }
      ]
    }
  }
}
```

### 2. Authentication Errors (401)
**Error Type**: `authentication`
**Common Codes**: `INVALID_CREDENTIALS`, `TOKEN_EXPIRED`, `INVALID_TOKEN`, `INACTIVE_USER`

Triggered by:
- Invalid username/password
- Expired JWT tokens
- Malformed tokens
- Inactive user accounts

**Examples**:
```json
{
  "error": {
    "message": "Invalid username or password",
    "error_code": "INVALID_CREDENTIALS",
    "error_type": "authentication"
  }
}
```

```json
{
  "error": {
    "message": "Token has expired",
    "error_code": "TOKEN_EXPIRED",
    "error_type": "authentication"
  }
}
```

### 3. Authorization Errors (403)
**Error Type**: `authorization`
**Common Codes**: `ACCESS_DENIED`, `KITCHEN_ACCESS_DENIED`, `SHOPPING_LIST_ACCESS_DENIED`

Triggered by:
- Accessing resources owned by other users
- Insufficient permissions
- Attempting unauthorized operations

**Example**:
```json
{
  "error": {
    "message": "Access denied to kitchen 123",
    "error_code": "KITCHEN_ACCESS_DENIED",
    "error_type": "authorization",
    "context": {
      "resource": "Kitchen",
      "action": "access",
      "kitchen_id": 123
    }
  }
}
```

### 4. Not Found Errors (404)
**Error Type**: `not_found`
**Common Codes**: `RESOURCE_NOT_FOUND`

Triggered by:
- Requesting non-existent resources
- Invalid resource IDs

**Example**:
```json
{
  "error": {
    "message": "Kitchen with ID 999 not found",
    "error_code": "RESOURCE_NOT_FOUND",
    "error_type": "not_found",
    "context": {
      "resource": "Kitchen",
      "identifier": 999
    }
  }
}
```

### 5. Conflict Errors (409)
**Error Type**: `conflict`
**Common Codes**: `RESOURCE_CONFLICT`, `DUPLICATE_VALUE`

Triggered by:
- Duplicate usernames/emails
- Constraint violations
- Resource conflicts

**Example**:
```json
{
  "error": {
    "message": "Username 'john_doe' is already taken",
    "error_code": "RESOURCE_CONFLICT",
    "error_type": "conflict",
    "context": {
      "resource": "User",
      "conflict_field": "username",
      "conflict_value": "john_doe"
    }
  }
}
```

### 6. Database Errors (500)
**Error Type**: `database`
**Common Codes**: `DATABASE_ERROR`, `INTEGRITY_ERROR`

Triggered by:
- Database connection issues
- Constraint violations
- Transaction failures

**Example**:
```json
{
  "error": {
    "message": "Database operation failed",
    "error_code": "DATABASE_ERROR",
    "error_type": "database",
    "context": {
      "operation": "create_user"
    }
  }
}
```

### 7. Rate Limiting Errors (429)
**Error Type**: `rate_limit`
**Common Codes**: `RATE_LIMIT_EXCEEDED`

Triggered by:
- Too many requests in time window
- API quota exceeded

**Example**:
```json
{
  "error": {
    "message": "Rate limit exceeded",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "error_type": "rate_limit",
    "context": {
      "retry_after": 60
    }
  }
}
```

## Custom Exception Classes

### Base Exceptions
- `APIException`: Base class for all API exceptions
- `ValidationException`: Input validation errors
- `AuthenticationException`: Authentication failures
- `AuthorizationException`: Permission denied errors
- `ResourceNotFoundException`: Resource not found
- `ConflictException`: Resource conflicts
- `DatabaseException`: Database operation failures

### Specific Exceptions
- `KitchenNotFoundException`
- `ShoppingListNotFoundException`
- `ShoppingListItemNotFoundException`
- `UserNotFoundException`
- `DuplicateUsernameException`
- `DuplicateEmailException`
- `InvalidCredentialsException`
- `TokenExpiredException`
- `InvalidTokenException`
- `InactiveUserException`

## Error Handling Flow

1. **Exception Occurs**: Application code raises specific exception
2. **Exception Handler**: FastAPI routes to appropriate handler
3. **Error Processing**: Handler creates standardized error response
4. **Logging**: Error details logged with context
5. **Response**: Client receives formatted error response

## Logging

### Log Levels
- **ERROR**: System errors, exceptions, failures
- **WARNING**: Authentication failures, authorization denials
- **INFO**: Successful operations, request completion
- **DEBUG**: Detailed operation information

### Log Categories
- **api.v1**: API operation logs
- **auth**: Authentication and authorization logs
- **database**: Database operation logs
- **security**: Security-related events
- **performance**: Performance monitoring

### Log Format
```
2024-01-01 12:00:00 - api.v1.routes - ERROR - Authentication failed for user: john_doe
```

### Structured Logging
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "ERROR",
  "logger": "api.v1.routes",
  "message": "Authentication failed",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": 123,
  "error_code": "INVALID_CREDENTIALS",
  "path": "/api/v1/auth/token",
  "method": "POST"
}
```

## Error Recovery Strategies

### Database Errors
- Automatic transaction rollback
- Connection retry with exponential backoff
- Graceful degradation for non-critical operations

### Authentication Errors
- Clear error messages without exposing system details
- Rate limiting for brute force protection
- Secure token refresh mechanisms

### Validation Errors
- Detailed field-level error information
- Input sanitization and normalization
- Client-side validation guidance

## Client Error Handling

### Recommended Client Patterns

```javascript
// Example client error handling
async function apiCall(endpoint, data) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new APIError(errorData.error);
    }
    
    return await response.json();
  } catch (error) {
    handleAPIError(error);
  }
}

function handleAPIError(error) {
  switch (error.error_code) {
    case 'TOKEN_EXPIRED':
      // Refresh token and retry
      refreshToken();
      break;
    case 'VALIDATION_ERROR':
      // Show field-specific errors
      showValidationErrors(error.context.validation_errors);
      break;
    case 'RATE_LIMIT_EXCEEDED':
      // Wait and retry
      setTimeout(() => retry(), error.context.retry_after * 1000);
      break;
    default:
      // Show generic error message
      showError(error.message);
  }
}
```

### Error Code Handling Matrix

| Error Code | Client Action | Retry? | User Message |
|------------|---------------|--------|--------------|
| `VALIDATION_ERROR` | Show field errors | No | "Please check your input" |
| `INVALID_CREDENTIALS` | Clear form | No | "Invalid username or password" |
| `TOKEN_EXPIRED` | Refresh token | Yes | "Session expired, please wait" |
| `ACCESS_DENIED` | Redirect/disable | No | "You don't have permission" |
| `RESOURCE_NOT_FOUND` | Update UI state | No | "Item not found" |
| `RATE_LIMIT_EXCEEDED` | Wait and retry | Yes | "Too many requests, please wait" |
| `DATABASE_ERROR` | Retry with backoff | Yes | "Service temporarily unavailable" |

## Monitoring and Alerting

### Key Metrics
- Error rate by endpoint
- Error rate by error type
- Response time percentiles
- Authentication failure rate
- Database error frequency

### Alert Conditions
- Error rate > 5% for 5 minutes
- Authentication failure rate > 10% for 2 minutes
- Database errors > 1% for 1 minute
- Response time P95 > 2 seconds for 5 minutes

### Health Checks
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "authentication": "healthy",
    "external_services": "healthy"
  },
  "metrics": {
    "uptime": 86400,
    "requests_per_minute": 150,
    "error_rate": 0.02
  }
}
```

## Testing Error Scenarios

### Unit Tests
- Exception raising and handling
- Error response format validation
- Logging verification

### Integration Tests
- End-to-end error flows
- Database constraint violations
- Authentication/authorization failures

### Load Tests
- Error handling under high load
- Rate limiting behavior
- Resource exhaustion scenarios

## Security Considerations

### Error Information Disclosure
- Never expose internal system details
- Sanitize error messages for external consumption
- Log detailed information internally only

### Rate Limiting
- Implement progressive delays for repeated failures
- Track failure patterns by IP/user
- Automatic blocking for suspicious activity

### Audit Logging
- Log all authentication attempts
- Track authorization failures
- Monitor for unusual error patterns

## Best Practices

### For Developers
1. Use specific exception types
2. Include relevant context in exceptions
3. Log errors with appropriate levels
4. Test error scenarios thoroughly
5. Document error conditions

### For API Consumers
1. Handle all documented error codes
2. Implement exponential backoff for retries
3. Show user-friendly error messages
4. Log errors for debugging
5. Monitor error rates and patterns

### For Operations
1. Set up comprehensive monitoring
2. Configure appropriate alerts
3. Regularly review error logs
4. Test error recovery procedures
5. Maintain error handling documentation