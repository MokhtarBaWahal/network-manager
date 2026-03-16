"""
Main FastAPI Application
Unified Network Management Platform - Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import Base, engine
from app.core.config import settings
from app.api import devices, dashboard

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    print("▶️  Starting Unified Network Manager...")
    yield
    print("⏹️  Shutting down Unified Network Manager...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Network Management Platform",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "endpoints": {
            "devices": "/api/devices",
            "dashboard": "/api/dashboard",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "network-manager-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
