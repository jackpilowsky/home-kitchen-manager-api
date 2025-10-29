from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
from datetime import datetime
import logging
import traceback
import uuid
from typing import Dict, Any

from .exceptions import (
    APIException,
    DatabaseException,
    ValidationException,
    ConflictException
)

logger = logging.getLogger(__name__)

def create_error_response(
    error_detail: str,
    error_code: str = "UNKNOWN_ERROR",
    error_type: str = "unknown",
    status_code: int = 500,
    context: Dict[str, Any] = None,
    request: Request = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    
    request_id = str(uuid.uuid4())
    
    error_response = {
        "error": {
            "message": error_detail,
            "error_code": error_code,
            "error_type": error_type,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    }
    
    if request:
        error_response["error"]["path"] = str(request.url.path)
        error_response["error"]["method"] = request.method
    
    # Log error for monitoring
    logger.error(
        f"API Error: {error_code} - {error_detail}",
        extra={
            "request_id": request_id,
            "error_code": error_code,
            "error_type": error_type,
            "status_code": status_code,
            "context": context,
            "path": str(request.url.path) if request else None,
            "method": request.method if request else None
        }
    )
    
    return error_response

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions"""
    
    error_response = create_error_response(
        error_detail=exc.detail,
        error_code=exc.error_code or "API_ERROR",
        error_type=exc.error_type or "api",
        status_code=exc.status_code,
        context=exc.context,
        request=request
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    
    # Map common HTTP status codes to error types
    error_type_map = {
        400: "bad_request",
        401: "authentication",
        403: "authorization",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation",
        429: "rate_limit",
        500: "internal_server_error",
        502: "bad_gateway",
        503: "service_unavailable"
    }
    
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_response = create_error_response(
        error_detail=exc.detail,
        error_code=error_code_map.get(exc.status_code, "HTTP_ERROR"),
        error_type=error_type_map.get(exc.status_code, "http"),
        status_code=exc.status_code,
        request=request
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    
    # Extract validation error details
    validation_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    error_response = create_error_response(
        error_detail="Validation failed",
        error_code="VALIDATION_ERROR",
        error_type="validation",
        status_code=422,
        context={"validation_errors": validation_errors},
        request=request
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    
    error_detail = "Database operation failed"
    error_code = "DATABASE_ERROR"
    context = {}
    
    # Handle specific SQLAlchemy exceptions
    if isinstance(exc, IntegrityError):
        error_detail = "Data integrity constraint violation"
        error_code = "INTEGRITY_ERROR"
        
        # Extract constraint information if available
        if hasattr(exc, 'orig') and exc.orig:
            orig_error = str(exc.orig)
            if "UNIQUE constraint failed" in orig_error:
                error_detail = "Duplicate value detected"
                error_code = "DUPLICATE_VALUE"
            elif "FOREIGN KEY constraint failed" in orig_error:
                error_detail = "Referenced resource not found"
                error_code = "FOREIGN_KEY_ERROR"
            elif "NOT NULL constraint failed" in orig_error:
                error_detail = "Required field is missing"
                error_code = "REQUIRED_FIELD_MISSING"
    
    # Log the full exception for debugging
    logger.error(
        f"Database error: {error_code}",
        exc_info=True,
        extra={
            "error_code": error_code,
            "exception_type": type(exc).__name__,
            "path": str(request.url.path),
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        error_detail=error_detail,
        error_code=error_code,
        error_type="database",
        status_code=500,
        context=context,
        request=request
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    # Log the full exception with traceback
    logger.error(
        f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={
            "exception_type": type(exc).__name__,
            "path": str(request.url.path),
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Don't expose internal error details in production
    error_detail = "An unexpected error occurred"
    
    error_response = create_error_response(
        error_detail=error_detail,
        error_code="INTERNAL_SERVER_ERROR",
        error_type="internal",
        status_code=500,
        request=request
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

# Error response schemas for OpenAPI documentation
ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Invalid request parameters",
                        "error_code": "BAD_REQUEST",
                        "error_type": "bad_request",
                        "context": {},
                        "timestamp": "2024-01-01T12:00:00.000Z",
                        "request_id": "123e4567-e89b-12d3-a456-426614174000",
                        "path": "/api/v1/shopping-lists/",
                        "method": "GET"
                    }
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Authentication failed",
                        "error_code": "UNAUTHORIZED",
                        "error_type": "authentication",
                        "context": {},
                        "timestamp": "2024-01-01T12:00:00.000Z",
                        "request_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        }
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Access denied",
                        "error_code": "FORBIDDEN",
                        "error_type": "authorization",
                        "context": {"resource": "Kitchen", "action": "access"},
                        "timestamp": "2024-01-01T12:00:00.000Z",
                        "request_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Resource not found",
                        "error_code": "NOT_FOUND",
                        "error_type": "not_found",
                        "context": {"resource": "ShoppingList", "identifier": 123},
                        "timestamp": "2024-01-01T12:00:00.000Z",
                        "request_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        }
    },
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Validation failed",
                        "error_code": "VALIDATION_ERROR",
                        "error_type": "validation",
                        "context": {
                            "validation_errors": [
                                {
                                    "field": "name",
                                    "message": "field required",
                                    "type": "value_error.missing"
                                }
                            ]
                        },
                        "timestamp": "2024-01-01T12:00:00.000Z",
                        "request_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "An unexpected error occurred",
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "error_type": "internal",
                        "context": {},
                        "timestamp": "2024-01-01T12:00:00.000Z",
                        "request_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        }
    }
}