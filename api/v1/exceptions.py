from fastapi import HTTPException, status
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class APIException(HTTPException):
    """Base API exception with enhanced error details"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.error_type = error_type
        self.context = context or {}

class ValidationException(APIException):
    """Validation error with field-specific details"""
    
    def __init__(
        self,
        detail: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            error_type="validation",
            context={
                "field": field,
                "value": value,
                **(context or {})
            }
        )

class AuthenticationException(APIException):
    """Authentication-related errors"""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: str = "AUTH_FAILED",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            error_type="authentication",
            context=context,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationException(APIException):
    """Authorization/permission errors"""
    
    def __init__(
        self,
        detail: str = "Access denied",
        error_code: str = "ACCESS_DENIED",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            error_type="authorization",
            context={
                "resource": resource,
                "action": action,
                **(context or {})
            }
        )

class ResourceNotFoundException(APIException):
    """Resource not found errors"""
    
    def __init__(
        self,
        resource: str,
        identifier: Optional[Any] = None,
        detail: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        if not detail:
            detail = f"{resource} not found"
            if identifier:
                detail += f" with ID: {identifier}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND",
            error_type="not_found",
            context={
                "resource": resource,
                "identifier": identifier,
                **(context or {})
            }
        )

class ConflictException(APIException):
    """Resource conflict errors (duplicate, constraint violations)"""
    
    def __init__(
        self,
        detail: str,
        resource: Optional[str] = None,
        conflict_field: Optional[str] = None,
        conflict_value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="RESOURCE_CONFLICT",
            error_type="conflict",
            context={
                "resource": resource,
                "conflict_field": conflict_field,
                "conflict_value": conflict_value,
                **(context or {})
            }
        )

class BusinessLogicException(APIException):
    """Business logic validation errors"""
    
    def __init__(
        self,
        detail: str,
        error_code: str = "BUSINESS_LOGIC_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
            error_type="business_logic",
            context=context
        )

class DatabaseException(APIException):
    """Database operation errors"""
    
    def __init__(
        self,
        detail: str = "Database operation failed",
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            error_type="database",
            context={
                "operation": operation,
                **(context or {})
            }
        )

class ExternalServiceException(APIException):
    """External service integration errors"""
    
    def __init__(
        self,
        detail: str,
        service: Optional[str] = None,
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code=error_code,
            error_type="external_service",
            context={
                "service": service,
                **(context or {})
            }
        )

class RateLimitException(APIException):
    """Rate limiting errors"""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            error_type="rate_limit",
            context={
                "retry_after": retry_after,
                **(context or {})
            },
            headers=headers
        )

# Specific application exceptions
class KitchenNotFoundException(ResourceNotFoundException):
    def __init__(self, kitchen_id: int):
        super().__init__(
            resource="Kitchen",
            identifier=kitchen_id,
            detail=f"Kitchen with ID {kitchen_id} not found"
        )

class ShoppingListNotFoundException(ResourceNotFoundException):
    def __init__(self, shopping_list_id: int):
        super().__init__(
            resource="ShoppingList",
            identifier=shopping_list_id,
            detail=f"Shopping list with ID {shopping_list_id} not found"
        )

class ShoppingListItemNotFoundException(ResourceNotFoundException):
    def __init__(self, item_id: int):
        super().__init__(
            resource="ShoppingListItem",
            identifier=item_id,
            detail=f"Shopping list item with ID {item_id} not found"
        )

class UserNotFoundException(ResourceNotFoundException):
    def __init__(self, identifier: Any):
        super().__init__(
            resource="User",
            identifier=identifier,
            detail=f"User not found"
        )

class DuplicateUsernameException(ConflictException):
    def __init__(self, username: str):
        super().__init__(
            detail=f"Username '{username}' is already taken",
            resource="User",
            conflict_field="username",
            conflict_value=username
        )

class DuplicateEmailException(ConflictException):
    def __init__(self, email: str):
        super().__init__(
            detail=f"Email '{email}' is already registered",
            resource="User",
            conflict_field="email",
            conflict_value=email
        )

class InvalidCredentialsException(AuthenticationException):
    def __init__(self):
        super().__init__(
            detail="Invalid username or password",
            error_code="INVALID_CREDENTIALS"
        )

class TokenExpiredException(AuthenticationException):
    def __init__(self):
        super().__init__(
            detail="Token has expired",
            error_code="TOKEN_EXPIRED"
        )

class InvalidTokenException(AuthenticationException):
    def __init__(self, reason: Optional[str] = None):
        detail = "Invalid token"
        if reason:
            detail += f": {reason}"
        
        super().__init__(
            detail=detail,
            error_code="INVALID_TOKEN"
        )

class InactiveUserException(AuthenticationException):
    def __init__(self):
        super().__init__(
            detail="User account is inactive",
            error_code="INACTIVE_USER"
        )

class KitchenAccessDeniedException(AuthorizationException):
    def __init__(self, kitchen_id: int):
        super().__init__(
            detail=f"Access denied to kitchen {kitchen_id}",
            error_code="KITCHEN_ACCESS_DENIED",
            resource="Kitchen",
            action="access",
            context={"kitchen_id": kitchen_id}
        )

class ShoppingListAccessDeniedException(AuthorizationException):
    def __init__(self, shopping_list_id: int):
        super().__init__(
            detail=f"Access denied to shopping list {shopping_list_id}",
            error_code="SHOPPING_LIST_ACCESS_DENIED",
            resource="ShoppingList",
            action="access",
            context={"shopping_list_id": shopping_list_id}
        )

class ShoppingListItemAccessDeniedException(AuthorizationException):
    def __init__(self, item_id: int):
        super().__init__(
            detail=f"Access denied to shopping list item {item_id}",
            error_code="SHOPPING_LIST_ITEM_ACCESS_DENIED",
            resource="ShoppingListItem",
            action="access",
            context={"item_id": item_id}
        )

# Error response models for documentation
class ErrorDetail:
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.error_type = error_type
        self.context = context or {}

class ErrorResponse:
    def __init__(
        self,
        error: ErrorDetail,
        timestamp: Optional[str] = None,
        path: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        self.error = error
        self.timestamp = timestamp
        self.path = path
        self.request_id = request_id