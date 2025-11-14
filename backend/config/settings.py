"""
Application settings using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field, model_validator
from functools import lru_cache
from typing import Optional, Any, Literal
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Video Foundry"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # Security: Execution Mode (Three-Tier Model)
    jynco_execution_mode: Literal["production", "self-hosted-production", "developer"] = "developer"

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

    # Secrets Management (Vault)
    vault_addr: Optional[str] = None
    vault_token: Optional[str] = None
    vault_namespace: Optional[str] = "videofoundry"

    # Authentication/IAM
    oidc_provider_url: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    enable_iam: bool = True  # Can be disabled in developer mode

    # Workflow Security
    workflow_allowlist_path: str = "/config/workflow_allowlist.yaml"
    enable_workflow_vetting: bool = True

    # Network Security
    enable_network_isolation: bool = False  # Set to True in production
    egress_proxy_url: Optional[str] = None
    egress_allowlist: Optional[str] = None  # Comma-separated domains

    # Storage
    use_s3_storage: Optional[bool] = None  # Auto-determined by execution mode if not set
    local_storage_path: str = "/videos"

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

    @model_validator(mode='after')
    def validate_security_configuration(self):
        """Validate security configuration based on execution mode."""
        mode = self.jynco_execution_mode

        logger.info(f"🔒 Initializing Video Foundry in {mode.upper()} mode")

        if mode == "production":
            self._validate_production_mode()
        elif mode == "self-hosted-production":
            self._validate_self_hosted_mode()
        else:  # developer
            self._validate_developer_mode()

        return self

    def _validate_production_mode(self):
        """Validate production mode requirements - FAIL if missing critical components."""
        errors = []

        # Vault is MANDATORY
        if not self.vault_addr or not self.vault_token:
            errors.append("VAULT_ADDR and VAULT_TOKEN are required in production mode")

        # S3 is MANDATORY
        if not self.s3_bucket or not self.aws_access_key_id:
            errors.append("S3_BUCKET and AWS credentials are required in production mode")

        # IAM is MANDATORY
        if not self.oidc_provider_url:
            errors.append("OIDC_PROVIDER_URL is required in production mode")

        if errors:
            error_msg = "❌ PRODUCTION MODE CONFIGURATION ERRORS:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Force production-safe settings
        self.enable_iam = True
        self.enable_workflow_vetting = True
        self.enable_network_isolation = True
        self.use_s3_storage = True
        self.debug = False

        logger.info("✅ Production mode validation passed")
        logger.info("   - Vault: Configured")
        logger.info("   - S3 Storage: Enabled")
        logger.info("   - IAM/RBAC: Enabled")
        logger.info("   - Network Isolation: Enabled")
        logger.info("   - Workflow Vetting: Strict allow-list")

    def _validate_self_hosted_mode(self):
        """Validate self-hosted mode - WARN if best practices not followed."""
        warnings = []

        # Vault is RECOMMENDED
        if not self.vault_addr:
            warnings.append(
                "Vault not configured. Using .env for secrets is NOT recommended for production."
            )

        # S3 is RECOMMENDED but not required
        if not self.s3_bucket:
            warnings.append(
                "S3 not configured. Using local storage. For production, cloud storage is recommended."
            )
            self.use_s3_storage = False
        else:
            self.use_s3_storage = True

        # IAM is RECOMMENDED
        if not self.oidc_provider_url:
            warnings.append(
                "IAM not configured. Basic authentication will be used. OIDC/SAML recommended for production."
            )

        if warnings:
            logger.warning("⚠️  SELF-HOSTED PRODUCTION MODE WARNINGS:")
            for warning in warnings:
                logger.warning(f"   - {warning}")

        # Set reasonable defaults
        self.enable_workflow_vetting = True  # Mandatory
        self.enable_network_isolation = self.egress_proxy_url is not None

        logger.info("✅ Self-hosted production mode initialized")
        logger.info(f"   - Vault: {'Configured' if self.vault_addr else 'NOT configured (using .env)'}")
        logger.info(f"   - Storage: {'S3' if self.use_s3_storage else 'Local volume'}")
        logger.info(f"   - IAM: {'Enabled' if self.oidc_provider_url else 'Basic auth'}")
        logger.info("   - Workflow Vetting: Admin-configurable allow-list")

    def _validate_developer_mode(self):
        """Validate developer mode - WARN about security risks."""
        logger.warning("⚠️  DEVELOPER MODE ACTIVE - NOT SECURE FOR PRODUCTION USE")
        logger.warning("   Security features are relaxed for development convenience")
        logger.warning("   - Secrets: .env files permitted")
        logger.warning("   - Storage: Local volume (default)")
        logger.warning("   - Workflow Vetting: Permissive (log-and-warn)")
        logger.warning("   - IAM: Optional")
        logger.warning("")
        logger.warning("   ⚠️  DO NOT use developer mode on public networks")
        logger.warning("   ⚠️  DO NOT process sensitive data in developer mode")
        logger.warning("")

        # Set permissive defaults
        self.use_s3_storage = False if not self.s3_bucket else True
        self.enable_iam = bool(self.oidc_provider_url)
        self.enable_network_isolation = False

        logger.info("✅ Developer mode initialized")
        logger.info("   - Sandboxing: Enabled (host protection)")
        logger.info("   - Workflow Vetting: Log-and-warn mode")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
