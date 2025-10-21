"""
FastAPI application entry point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llmbattler_shared.config import settings
from llmbattler_shared.logging_config import setup_logging

from llmbattler_backend.api import battles, models, sessions

# Configure logging
logger = setup_logging("llmbattler_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting llmbattler-backend...")

    # TODO: Initialize database connections
    # - MongoDB (Motor)
    # - PostgreSQL (SQLAlchemy async)
    # - Create MongoDB indexes

    logger.info("Backend startup complete")

    yield

    logger.info("Shutting down llmbattler-backend...")

    # TODO: Close database connections

    logger.info("Backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="llmbattler API",
    description="AI Language Model Battle Arena - Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "llmbattler-backend"}


# Include API routers
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(battles.router, prefix="/api", tags=["battles"])

# TODO: Include other routers
# from llmbattler_backend.api import leaderboard
# app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])
