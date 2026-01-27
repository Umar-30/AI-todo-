"""
Database connection management for Todo AI Chatbot.

Provides SQLModel engine creation, connection verification, and table management
for Neon PostgreSQL.
"""
import logging
from typing import Generator
from sqlmodel import create_engine, text, SQLModel, Session
from sqlalchemy import Engine

from .config import get_settings

logger = logging.getLogger(__name__)

# Global engine instance
_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Get or create the SQLModel database engine.

    Uses postgresql+psycopg driver for Neon serverless PostgreSQL.
    SSL is enabled automatically via sslmode=require in connection string.

    Returns:
        SQLAlchemy Engine configured for Neon PostgreSQL.
    """
    global _engine
    if _engine is None:
        settings = get_settings()

        # Convert postgres:// to postgresql+psycopg:// for SQLAlchemy 2.0
        database_url = settings.database_url
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

        _engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before use
        )
        logger.info("Database engine created successfully")

    return _engine


def check_connection() -> bool:
    """
    Check if the database connection is working.

    Executes a simple query to verify connectivity.

    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection verified")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def close_engine() -> None:
    """Close the database engine and release connections."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Database engine closed")


def create_tables() -> None:
    """
    Create all database tables from registered SQLModel models.

    This function uses SQLModel.metadata.create_all() to create tables
    for all models that have been imported and registered.

    Note: Models must be imported before calling this function for their
    tables to be created.
    """
    # Import models to register them with SQLModel.metadata
    # This ensures the models are known before create_all is called
    from . import models  # noqa: F401

    engine = get_engine()
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection in FastAPI.

    Yields:
        SQLModel Session for database operations.
    """
    with Session(get_engine()) as session:
        yield session


def migrate_tasks_table() -> None:
    """
    Add missing columns to tasks table if they don't exist.
    This handles schema migration for priority and category columns.
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Check if priority column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'priority'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE tasks ADD COLUMN priority VARCHAR(10)"))
                logger.info("Added 'priority' column to tasks table")

            # Check if category column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'category'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE tasks ADD COLUMN category VARCHAR(50)"))
                logger.info("Added 'category' column to tasks table")

            # Check if due_date column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'due_date'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP"))
                logger.info("Added 'due_date' column to tasks table")

            conn.commit()
            logger.info("Tasks table migration completed")
    except Exception as e:
        logger.error(f"Failed to migrate tasks table: {e}")
        raise


def migrate_users_table() -> None:
    """
    Add missing columns to users table if they don't exist.
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Check if password_hash column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'password_hash'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                logger.info("Added 'password_hash' column to users table")

            # Check if provider column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'provider'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE users ADD COLUMN provider VARCHAR(50) DEFAULT 'credentials'"))
                logger.info("Added 'provider' column to users table")

            # Check if provider_id column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'provider_id'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE users ADD COLUMN provider_id VARCHAR(255)"))
                logger.info("Added 'provider_id' column to users table")

            conn.commit()
            logger.info("Users table migration completed")
    except Exception as e:
        logger.error(f"Failed to migrate users table: {e}")
        raise
