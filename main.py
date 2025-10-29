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
    description="A comprehensive API for managing kitchen shopping lists and items",
    lifespan=lifespan
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Register error handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(v1_router, prefix="/api/v1", tags=["shopping-lists"])
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["monitoring"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Home Kitchen Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }
