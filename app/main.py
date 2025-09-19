from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Initialize FastAPI app first
app = FastAPI(
    title="SIH Backend - Migrant Health System",
    description="Integrated FastAPI backend for migrant health management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "file://"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Basic routes first
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SIH Backend - Migrant Health System",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "SIH Backend is running"
    }

# Import and setup database after app initialization
try:
    from app.database import engine
    from app import models
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Import routes after database setup
    from app.routes import (
        auth_routes,
        migrant_routes,
        encounter_routes,
        consent_routes,
        integration_routes,
        analytics_routes
    )
    
    # Include routers
    app.include_router(auth_routes.router)
    app.include_router(migrant_routes.router)
    app.include_router(encounter_routes.router)
    app.include_router(consent_routes.router)
    app.include_router(integration_routes.router)
    app.include_router(analytics_routes.router)
    
except Exception as e:
    print(f"Warning: Some features may not be available due to import error: {e}")

# Add OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
