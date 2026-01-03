"""
Centralized configuration management for Volari.

Handles loading configuration from environment variables, .env files,
and the settings file.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Any

logger = logging.getLogger(__name__)


class Config:
    """Application configuration container.

    Loads configuration from environment variables with fallbacks
    to sensible defaults.
    """

    # Singleton instance
    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._load_dotenv()
        self._load_config()

    def _load_dotenv(self) -> None:
        """Load .env file if it exists."""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ.setdefault(key.strip(), value.strip())
                logger.debug("Loaded .env file from %s", env_path)
            except Exception as e:
                logger.warning("Failed to load .env file: %s", e)

    def _load_config(self) -> None:
        """Load configuration from environment."""
        # VirusTotal
        self.virustotal_api_key: str = os.getenv("VIRUSTOTAL_API_KEY", "")

        # Logging
        log_level = os.getenv("VOLARI_LOG_LEVEL", "INFO").upper()
        self.log_level: int = getattr(logging, log_level, logging.INFO)

        # Output
        self.output_dir: str = os.getenv("VOLARI_OUTPUT_DIR", "")

        # Theme
        self.theme: str = os.getenv("VOLARI_THEME", "dark")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return getattr(self, key, default)


# Global config instance
config = Config()
