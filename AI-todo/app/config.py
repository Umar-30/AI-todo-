"""
Configuration management for Todo AI Chatbot.

Loads environment variables and provides typed configuration access.
Uses python-dotenv to load .env file for local development.
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


def _load_dotenv() -> None:
    """Load .env file if present (for local development)."""
    # Look for .env in the backend directory
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment from .env file")
    else:
        logger.debug("No .env file found, using system environment variables")


def _validate_database_url(url: str) -> None:
    """
    Validate DATABASE_URL format.

    Args:
        url: The database URL to validate.

    Raises:
        ConfigurationError: If URL format is invalid.
    """
    valid_prefixes = ("postgresql://", "postgres://")
    if not url.startswith(valid_prefixes):
        raise ConfigurationError(
            f"DATABASE_URL must start with 'postgresql://' or 'postgres://'.\n"
            f"Current value starts with: {url[:20]}...\n"
            f"Expected format: postgresql://user:password@host/dbname?sslmode=require"
        )


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    database_url: str
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Load settings from environment variables.

        Loads .env file if present, validates configuration,
        and provides helpful error messages for troubleshooting.

        Raises:
            ConfigurationError: If required variables are missing or invalid.
        """
        # Load .env file for local development
        _load_dotenv()

        database_url = os.getenv("DATABASE_URL")
        # Support both OPENROUTE_API_KEY and OPENROUTER_API_KEY
        openrouter_api_key = os.getenv("OPENROUTE_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        openrouter_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")

        # Validate DATABASE_URL
        if not database_url:
            raise ConfigurationError(
                "DATABASE_URL environment variable is required.\n\n"
                "Troubleshooting:\n"
                "1. Copy backend/.env.example to backend/.env\n"
                "2. Fill in your Neon PostgreSQL connection string\n"
                "3. Restart the application\n\n"
                "Expected format: postgresql://user:password@host/dbname?sslmode=require\n"
                "Get your connection string from: https://console.neon.tech"
            )

        _validate_database_url(database_url)

        # Validate OpenRouter API Key
        if not openrouter_api_key:
            raise ConfigurationError(
                "OPENROUTE_API_KEY environment variable is required.\n\n"
                "Troubleshooting:\n"
                "1. Copy backend/.env.example to backend/.env\n"
                "2. Add your OpenRouter API key\n"
                "3. Restart the application\n\n"
                "Get your API key from: https://openrouter.ai/keys"
            )

        # Clean up API key (remove quotes if present)
        openrouter_api_key = openrouter_api_key.strip('"').strip("'")

        # Log configuration loaded (without sensitive values)
        logger.info("Configuration loaded successfully")
        logger.debug(f"DATABASE_URL: {database_url[:20]}...***")
        logger.debug(f"OPENROUTER_API_KEY: {openrouter_api_key[:10]}...***")
        logger.debug(f"OPENROUTER_MODEL: {openrouter_model}")

        return cls(
            database_url=database_url,
            openrouter_api_key=openrouter_api_key,
            openrouter_base_url=openrouter_base_url,
            openrouter_model=openrouter_model,
        )


# Global settings instance (initialized on first access)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the application settings, loading from environment if needed."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
