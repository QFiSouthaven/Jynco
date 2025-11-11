"""
Configuration Loader

Loads and manages configuration for the Jynco system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Load and manage application configuration."""

    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to config file. If None, auto-detect based on environment
            environment: Environment name (development, production). If None, use JYNCO_ENV or default to development
        """
        self.environment = environment or os.getenv("JYNCO_ENV", "development")

        if config_path:
            self.config_path = Path(config_path)
        else:
            # Auto-detect config file based on environment
            base_dir = Path(__file__).parent.parent.parent
            self.config_path = base_dir / "config" / f"{self.environment}.json"

        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        # Expand environment variables in config values
        self._expand_env_vars(self.config)

    def _expand_env_vars(self, config: Any) -> Any:
        """Recursively expand environment variables in config."""
        if isinstance(config, dict):
            return {k: self._expand_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            if config.startswith("${") and config.endswith("}"):
                var_name = config[2:-1]
                return os.getenv(var_name, config)
            return config
        else:
            return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Supports dot notation for nested keys (e.g., "agents.architect.max_retries")
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.get(f"agents.{agent_name}", {})

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return self.get("cache", {})

    def get_queue_config(self) -> Dict[str, Any]:
        """Get job queue configuration."""
        return self.get("job_queue", {})

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global config instance
_config: Optional[ConfigLoader] = None


def init_config(config_path: Optional[str] = None, environment: Optional[str] = None) -> ConfigLoader:
    """
    Initialize global configuration.

    Args:
        config_path: Path to config file
        environment: Environment name

    Returns:
        ConfigLoader instance
    """
    global _config
    _config = ConfigLoader(config_path, environment)
    return _config


def get_config() -> ConfigLoader:
    """
    Get global configuration instance.

    Returns:
        ConfigLoader instance

    Raises:
        RuntimeError: If config not initialized
    """
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call init_config() first.")
    return _config
