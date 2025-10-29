from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from api.v1.routes import router as v1_router
from api.v1.auth_routes import router as auth_router
from api.v1.search_routes import router as search_router
from api.v1.exceptions import APIException
from api.v1.error_handlers import (
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from logging_config import setup_logging, RequestLoggingMiddleware
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# --- App setup ---
app = FastAPI(
    title="Home Kitchen Manager API", 
    version="1.0.0",
    description="A comprehensive API for managing kitchen shopping lists and items"
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Register error handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

logger.info("Home Kitchen Manager API starting up")

# Include API routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(v1_router, prefix="/api/v1", tags=["shopping-lists"])
app.include_router(search_router, prefix="/api/v1", tags=["search"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Home Kitchen Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }
