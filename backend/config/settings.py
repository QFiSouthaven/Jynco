"""
Application settings using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from functools import lru_cache
from typing import Optional, Any


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Video Foundry"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/videofoundry"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    segment_queue_name: str = "segment_generation"
    composition_queue_name: str = "video_composition"
    completion_exchange: str = "segment_completed"

    # AWS S3
    s3_bucket: str = "video-foundry-dev"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"

    # AI Model APIs
    runway_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None

    # CORS - stored as Any to prevent automatic JSON parsing
    cors_origins: Any = Field(default=["http://localhost:3000", "http://localhost:5173"])

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if v is None or v == "":
            return ["http://localhost:3000", "http://localhost:5173"]
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return ["http://localhost:3000", "http://localhost:5173"]
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        if isinstance(v, list):
            return v
        # Fallback to default
        return ["http://localhost:3000", "http://localhost:5173"]

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        # Don't parse environment variables as JSON
        env_parse_none_str=None
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
