from fastapi import FastAPI
from api.v1.routes import router as v1_router
from api.v1.auth_routes import router as auth_router
from api.v1.search_routes import router as search_router

# --- App setup ---
app = FastAPI(
    title="Home Kitchen Manager API", 
    version="1.0.0",
    description="A comprehensive API for managing kitchen shopping lists and items"
)

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
