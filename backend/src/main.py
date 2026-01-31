"""
Todo AI Chatbot - FastAPI Application Entry Point.

Provides health check endpoint and database connectivity verification.
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager

# Fix for Windows: Use SelectorEventLoop with increased limit
# ProactorEventLoop has issues with some async libraries
if sys.platform == "win32":
    # Use selector event loop policy (more compatible)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from datetime import datetime, timezone
from enum import Enum
from typing import AsyncGenerator

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import check_connection, close_engine, create_tables, get_engine, migrate_tasks_table, migrate_users_table
from .api import chat_router, voice_router
from .api.tasks import router as tasks_router
from .api.auth import router as auth_router
from .chatkit import create_chatkit_endpoint


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Health Status Response Model (per data-model.md)
class HealthStatusEnum(str, Enum):
    """Overall system health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class ServerStatusEnum(str, Enum):
    """Server operational status."""
    RUNNING = "running"


class DatabaseStatusEnum(str, Enum):
    """Database connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class HealthStatus(BaseModel):
    """
    Health check response model.

    Fields per data-model.md and contracts/health.yaml.
    """
    status: HealthStatusEnum
    server: ServerStatusEnum
    database: DatabaseStatusEnum
    timestamp: str  # ISO 8601 format


# Track database connection status
_db_connected: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup (database connection) and shutdown (cleanup).
    """
    global _db_connected

    # Startup
    logger.info("Application starting...")

    try:
        # Initialize database engine
        get_engine()

        # Verify database connection
        _db_connected = check_connection()

        if _db_connected:
            logger.info("Database connected successfully")

            # Create database tables for all registered models
            create_tables()

            # Run migrations to add any missing columns
            migrate_tasks_table()
            migrate_users_table()
        else:
            logger.warning("Database connection failed - server will start but /health will report unhealthy")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        _db_connected = False

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Application shutting down...")
    close_engine()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot",
    description="AI-powered Todo Chatbot with MCP-compliant architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(tasks_router)
app.include_router(auth_router)  # Authentication endpoints
app.include_router(create_chatkit_endpoint())


@app.get("/", tags=["System"])
async def root():
    """Root endpoint for health check and HuggingFace Spaces."""
    return {"status": "ok", "message": "Todo AI Chatbot API is running"}


@app.get(
    "/health",
    response_model=HealthStatus,
    responses={
        200: {"description": "System is healthy"},
        503: {"description": "System is unhealthy (database connection failed)"},
    },
    tags=["System"],
    summary="Health Check",
    description="Returns the health status of the server and database connection",
)
async def health_check(response: Response) -> HealthStatus:
    """
    Health check endpoint.

    Returns 200 with status="healthy" when DB connected.
    Returns 503 with status="unhealthy" when DB disconnected.

    Per contracts/health.yaml specification.
    """
    # Check current database status
    db_status = DatabaseStatusEnum.CONNECTED if _db_connected else DatabaseStatusEnum.DISCONNECTED
    overall_status = HealthStatusEnum.HEALTHY if _db_connected else HealthStatusEnum.UNHEALTHY

    # Set appropriate HTTP status code
    if not _db_connected:
        response.status_code = 503

    return HealthStatus(
        status=overall_status,
        server=ServerStatusEnum.RUNNING,
        database=db_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
