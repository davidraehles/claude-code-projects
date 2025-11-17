"""
FastAPI application entry point for Recipe & Meal Planning System.

Initializes the FastAPI app with middleware, routes, and event handlers.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage application lifecycle events.

    Startup:
        - Initialize database tables (dev only)
        - Connect to Redis event bus
        - Start background agent workers

    Shutdown:
        - Close database connections
        - Disconnect from Redis
        - Gracefully stop agents
    """
    # Import event bus
    from app.events.bus import get_event_bus

    # Startup
    print("🚀 Starting Recipe & Meal Planning System...")

    # Create tables (in production, use Alembic migrations instead)
    if os.getenv("APP_ENV") == "development":
        print("📦 Creating database tables...")
        Base.metadata.create_all(bind=engine)

    # Initialize Redis event bus
    try:
        event_bus = get_event_bus()
        await event_bus.connect()
        print("✅ Event bus connected")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Redis event bus: {e}")
        print("   Application will continue without event bus functionality")

    print("✅ Application started successfully")

    yield

    # Shutdown
    print("🛑 Shutting down application...")

    # Disconnect from Redis event bus
    try:
        event_bus = get_event_bus()
        await event_bus.disconnect()
        print("✅ Event bus disconnected")
    except Exception as e:
        print(f"⚠️  Warning during event bus shutdown: {e}")

    print("✅ Shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title="Recipe & Meal Planning API",
    description="Multi-agent system for recipe harvesting, meal planning, and grocery shopping",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics middleware
from app.monitoring.middleware import PrometheusMiddleware
app.add_middleware(PrometheusMiddleware)


# Prometheus metrics endpoint
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

@app.get("/metrics", tags=["System"])
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        Metrics in Prometheus format
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Status and version information
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "recipe-meal-planning-api"
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: Welcome message and documentation links
    """
    return {
        "message": "Recipe & Meal Planning API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The FastAPI request object
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response with 500 status
    """
    # Log the error (in production, use proper logging)
    print(f"❌ Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "True" else "An unexpected error occurred"
        }
    )


# Import and include routers
from app.api.v1 import recipes, ingredients, users, meal_plans, auth

app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["Recipes"])
app.include_router(ingredients.router, prefix="/api/v1/ingredients", tags=["Ingredients"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(meal_plans.router, prefix="/api/v1/meal-plans", tags=["Meal Plans"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"🌐 Starting server on {host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("APP_ENV") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
