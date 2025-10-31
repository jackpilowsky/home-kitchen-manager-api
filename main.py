from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import asyncio
import logging

from api.v1.routes import router as v1_router
from api.v1.auth_routes import router as auth_router
from api.v1.search_routes import router as search_router
from api.v1.health_routes import router as health_router
from api.v1.dashboard_routes import router as dashboard_router
from api.v1.inventory_routes import router as inventory_router
from api.v1.exceptions import APIException
from api.v1.error_handlers import (
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from api.v1.monitoring import MonitoringMiddleware, system_metrics_task
from logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Home Kitchen Manager API starting up")
    
    # Start background tasks
    metrics_task = asyncio.create_task(system_metrics_task())
    
    try:
        yield
    finally:
        logger.info("Home Kitchen Manager API shutting down")
        # Cancel background tasks
        metrics_task.cancel()
        try:
            await metrics_task
        except asyncio.CancelledError:
            pass

# --- App setup ---
app = FastAPI(
    title="Home Kitchen Manager API", 
    version="1.0.0",
    description="""
    ## Home Kitchen Manager API

    A comprehensive REST API for managing kitchen operations including:
    
    ### 🏠 **Kitchen Management**
    - Create and manage multiple kitchens
    - User-based kitchen ownership and access control
    
    ### 📝 **Shopping Lists**
    - Create, update, and manage shopping lists
    - Add items with quantities, notes, and categories
    - Mark items as purchased or pending
    - Share lists between kitchen members
    
    ### 📦 **Inventory Management**
    - **Pantry Items** - Track dry goods and non-perishables
    - **Refrigerator Items** - Manage fresh and chilled products  
    - **Freezer Items** - Monitor frozen goods and long-term storage
    - UPC code support for easy product identification
    - Flexible quantity tracking with custom units
    
    ### 🔍 **Advanced Search & Filtering**
    - Full-text search across all items and lists
    - Filter by categories, kitchens, dates, and status
    - Sort by multiple criteria with pagination
    
    ### 👥 **User Authentication & Authorization**
    - JWT-based authentication system
    - Role-based access control
    - Kitchen-based ownership validation
    
    ### 📊 **Monitoring & Health**
    - System health checks and metrics
    - Performance monitoring dashboard
    - Error tracking and logging
    
    ### 🛡️ **Security Features**
    - Input validation and sanitization
    - Rate limiting and CORS support
    - Comprehensive error handling
    
    ---
    
    **Base URL:** `/api/v1`
    
    **Authentication:** Bearer Token (JWT)
    
    **Response Format:** JSON
    """,
    contact={
        "name": "Home Kitchen Manager API",
        "email": "support@kitchenmanager.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8001",
            "description": "Development server"
        },
        {
            "url": "https://api.kitchenmanager.com",
            "description": "Production server"
        }
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Register error handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes
app.include_router(
    auth_router, 
    prefix="/api/v1/auth", 
    tags=["🔐 Authentication"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Access forbidden"}
    }
)
app.include_router(
    v1_router, 
    prefix="/api/v1", 
    tags=["📝 Shopping Lists"],
    responses={
        404: {"description": "Resource not found"},
        422: {"description": "Validation error"}
    }
)
app.include_router(
    inventory_router, 
    prefix="/api/v1", 
    tags=["📦 Inventory Management"],
    responses={
        404: {"description": "Item not found"},
        422: {"description": "Validation error"}
    }
)
app.include_router(
    search_router, 
    prefix="/api/v1", 
    tags=["🔍 Search & Filtering"],
    responses={
        400: {"description": "Invalid search parameters"}
    }
)
app.include_router(
    health_router, 
    prefix="/api/v1", 
    tags=["🏥 Health & Status"]
)
app.include_router(
    dashboard_router, 
    prefix="/api/v1", 
    tags=["📊 Monitoring & Analytics"]
)

@app.get(
    "/",
    summary="API Welcome",
    description="Welcome endpoint with API information and navigation links",
    response_description="API welcome message with navigation links",
    tags=["🏠 General"]
)
def read_root():
    """
    ## Welcome to Home Kitchen Manager API
    
    This endpoint provides basic information about the API and navigation links.
    
    ### Available Resources:
    - **Documentation**: Interactive API docs at `/docs`
    - **Alternative Docs**: ReDoc documentation at `/redoc`
    - **Health Check**: System status at `/api/v1/health`
    - **OpenAPI Schema**: Raw schema at `/api/v1/openapi.json`
    
    ### Quick Start:
    1. Register a new user at `/api/v1/auth/register`
    2. Login to get access token at `/api/v1/auth/login`
    3. Create a kitchen at `/api/v1/kitchens/`
    4. Start managing your shopping lists and inventory!
    """
    return {
        "message": "Welcome to Home Kitchen Manager API",
        "version": "1.0.0",
        "description": "A comprehensive API for managing kitchen operations",
        "documentation": {
            "interactive_docs": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/api/v1/openapi.json"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "authentication": "/api/v1/auth",
            "kitchens": "/api/v1/kitchens",
            "shopping_lists": "/api/v1/shopping-lists",
            "inventory": {
                "pantry": "/api/v1/pantry-items",
                "refrigerator": "/api/v1/refrigerator-items", 
                "freezer": "/api/v1/freezer-items"
            },
            "search": "/api/v1/search",
            "monitoring": "/api/v1/dashboard"
        },
        "features": [
            "Multi-kitchen management",
            "Shopping list organization", 
            "Comprehensive inventory tracking",
            "Advanced search and filtering",
            "User authentication and authorization",
            "Real-time monitoring and health checks"
        ]
    }
