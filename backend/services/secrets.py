"""
Secrets Management Service - Three-Tier Security Model

Provides secure access to sensitive credentials (API keys, database passwords, etc.)
with different backends based on execution mode.
"""
import logging
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SecretsBackend(ABC):
    """Base class for secrets storage backends."""

    @abstractmethod
    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve a secret.

        Args:
            path: Secret path (e.g., "videofoundry/database/password")
            key: Optional key within the secret (for structured secrets)

        Returns:
            Secret value (string or dict)
        """
        pass

    @abstractmethod
    def set_secret(self, path: str, value: Any) -> None:
        """
        Store a secret (if backend supports writes).

        Args:
            path: Secret path
            value: Secret value (string or dict)
        """
        pass


class VaultBackend(SecretsBackend):
    """HashiCorp Vault secrets backend."""

    def __init__(self, vault_addr: str, vault_token: str, vault_namespace: Optional[str] = None):
        try:
            import hvac
        except ImportError:
            raise ImportError(
                "hvac library not installed. "
                "Install with: pip install hvac"
            )

        self.client = hvac.Client(url=vault_addr, token=vault_token, namespace=vault_namespace)

        # Verify connection
        if not self.client.is_authenticated():
            raise ValueError("Vault authentication failed")

        logger.info(f"✅ Connected to HashiCorp Vault at {vault_addr}")

    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """Retrieve secret from Vault KV v2."""
        try:
            # Vault KV v2 API
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            data = response['data']['data']

            if key:
                return data.get(key)
            return data

        except Exception as e:
            logger.error(f"Failed to retrieve secret from Vault: {path} - {e}")
            raise

    def set_secret(self, path: str, value: Any) -> None:
        """Store secret in Vault KV v2."""
        try:
            if isinstance(value, str):
                value = {"value": value}

            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=value
            )

            logger.info(f"Secret stored in Vault: {path}")

        except Exception as e:
            logger.error(f"Failed to store secret in Vault: {path} - {e}")
            raise


class AWSSecretsManagerBackend(SecretsBackend):
    """AWS Secrets Manager backend."""

    def __init__(self, region: str = "us-east-1"):
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 library not installed. "
                "Install with: pip install boto3"
            )

        self.client = boto3.client('secretsmanager', region_name=region)
        logger.info(f"✅ Connected to AWS Secrets Manager (region: {region})")

    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=path)

            secret_string = response['SecretString']

            # Try to parse as JSON
            try:
                data = json.loads(secret_string)
                if key:
                    return data.get(key)
                return data
            except json.JSONDecodeError:
                # Plain string secret
                return secret_string

        except Exception as e:
            logger.error(f"Failed to retrieve secret from AWS: {path} - {e}")
            raise

    def set_secret(self, path: str, value: Any) -> None:
        """Store secret in AWS Secrets Manager."""
        try:
            if isinstance(value, dict):
                secret_string = json.dumps(value)
            else:
                secret_string = str(value)

            try:
                # Try to create new secret
                self.client.create_secret(
                    Name=path,
                    SecretString=secret_string
                )
                logger.info(f"Secret created in AWS: {path}")

            except self.client.exceptions.ResourceExistsException:
                # Secret exists, update it
                self.client.put_secret_value(
                    SecretId=path,
                    SecretString=secret_string
                )
                logger.info(f"Secret updated in AWS: {path}")

        except Exception as e:
            logger.error(f"Failed to store secret in AWS: {path} - {e}")
            raise


class EnvFileBackend(SecretsBackend):
    """Environment variables / .env file backend (INSECURE - development only)."""

    def __init__(self, env_file: Optional[str] = None):
        self.env_file = Path(env_file) if env_file else Path(".env")

        if self.env_file.exists():
            logger.warning(
                f"⚠️  Using .env file for secrets: {self.env_file.absolute()}\n"
                f"   This is INSECURE and should only be used in developer mode."
            )
        else:
            logger.warning(
                f"⚠️  .env file not found: {self.env_file.absolute()}\n"
                f"   Falling back to system environment variables."
            )

    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret from environment variables.

        Path is converted to uppercase env var name.
        E.g., "videofoundry/database/password" -> "VIDEOFOUNDRY_DATABASE_PASSWORD"
        """
        env_var = path.upper().replace('/', '_').replace('-', '_')

        value = os.getenv(env_var)

        if value is None:
            # Try alternative formats
            alt_var = path.split('/')[-1].upper()  # Just the last part
            value = os.getenv(alt_var)

        if value is None:
            logger.warning(f"Secret not found in environment: {path} (tried {env_var})")
            return None

        # Try to parse as JSON if it looks like JSON
        if value.startswith('{') or value.startswith('['):
            try:
                data = json.loads(value)
                if key:
                    return data.get(key)
                return data
            except json.JSONDecodeError:
                pass

        return value

    def set_secret(self, path: str, value: Any) -> None:
        """Setting secrets not supported for env backend (read-only)."""
        logger.warning("EnvFileBackend does not support setting secrets")
        raise NotImplementedError("Cannot set secrets in environment backend")


class SecretsManager:
    """
    Main secrets management service.

    Selects appropriate backend based on execution mode and configuration.
    """

    def __init__(
        self,
        execution_mode: str,
        vault_addr: Optional[str] = None,
        vault_token: Optional[str] = None,
        vault_namespace: Optional[str] = None,
        aws_region: Optional[str] = None,
        env_file: Optional[str] = None
    ):
        self.execution_mode = execution_mode
        self.backend = self._initialize_backend(
            vault_addr, vault_token, vault_namespace, aws_region, env_file
        )

    def _initialize_backend(
        self,
        vault_addr: Optional[str],
        vault_token: Optional[str],
        vault_namespace: Optional[str],
        aws_region: Optional[str],
        env_file: Optional[str]
    ) -> SecretsBackend:
        """Initialize the appropriate secrets backend."""

        if self.execution_mode == "production":
            # Production: Vault is MANDATORY
            if not vault_addr or not vault_token:
                # Try AWS Secrets Manager as fallback
                if aws_region or os.getenv('AWS_REGION'):
                    logger.warning(
                        "Vault not configured in production mode, using AWS Secrets Manager"
                    )
                    return AWSSecretsManagerBackend(region=aws_region or os.getenv('AWS_REGION'))
                else:
                    raise ValueError(
                        "Production mode requires either Vault or AWS Secrets Manager. "
                        "Set VAULT_ADDR and VAULT_TOKEN or configure AWS credentials."
                    )

            return VaultBackend(vault_addr, vault_token, vault_namespace)

        elif self.execution_mode == "self-hosted-production":
            # Self-hosted: Prefer Vault, allow .env with warning
            if vault_addr and vault_token:
                return VaultBackend(vault_addr, vault_token, vault_namespace)

            elif aws_region or os.getenv('AWS_REGION'):
                logger.info("Using AWS Secrets Manager for self-hosted production")
                return AWSSecretsManagerBackend(region=aws_region or os.getenv('AWS_REGION'))

            else:
                logger.warning(
                    "⚠️  SELF-HOSTED PRODUCTION MODE WARNING:\n"
                    "   Vault or AWS Secrets Manager not configured.\n"
                    "   Falling back to .env file for secrets.\n"
                    "   This is NOT recommended for production deployments.\n"
                    "   Please configure a vault for better security.\n"
                )
                return EnvFileBackend(env_file)

        else:  # developer mode
            # Developer: Use .env by default
            logger.info("Developer mode: Using .env file for secrets")
            return EnvFileBackend(env_file)

    def get(self, path: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a secret.

        Args:
            path: Secret path
            key: Optional key within secret
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        try:
            value = self.backend.get_secret(path, key)
            if value is None:
                return default
            return value
        except Exception as e:
            logger.warning(f"Failed to retrieve secret {path}: {e}")
            return default

    def get_required(self, path: str, key: Optional[str] = None) -> Any:
        """
        Get a required secret (raises exception if not found).

        Args:
            path: Secret path
            key: Optional key within secret

        Returns:
            Secret value

        Raises:
            ValueError: If secret not found
        """
        value = self.backend.get_secret(path, key)
        if value is None:
            raise ValueError(f"Required secret not found: {path}")
        return value

    def set(self, path: str, value: Any) -> None:
        """
        Set a secret.

        Args:
            path: Secret path
            value: Secret value
        """
        self.backend.set_secret(path, value)


# Singleton instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get the singleton secrets manager instance."""
    global _secrets_manager

    if _secrets_manager is None:
        from config import get_settings
        settings = get_settings()

        _secrets_manager = SecretsManager(
            execution_mode=settings.jynco_execution_mode,
            vault_addr=settings.vault_addr,
            vault_token=settings.vault_token,
            vault_namespace=settings.vault_namespace,
            aws_region=settings.aws_region,
            env_file=".env"
        )

    return _secrets_manager


# Convenience functions for common secrets

def get_database_password() -> str:
    """Get database password from secrets."""
    sm = get_secrets_manager()
    return sm.get("videofoundry/database/password", default=os.getenv("DATABASE_PASSWORD"))


def get_api_key(service: str) -> Optional[str]:
    """
    Get API key for an external service.

    Args:
        service: Service name (e.g., 'runway', 'stability')

    Returns:
        API key or None
    """
    sm = get_secrets_manager()
    return sm.get(f"videofoundry/api-keys/{service}", default=os.getenv(f"{service.upper()}_API_KEY"))


def get_jwt_secret() -> str:
    """Get JWT secret key."""
    sm = get_secrets_manager()
    return sm.get_required("videofoundry/jwt/secret")


def get_aws_credentials() -> Dict[str, str]:
    """Get AWS credentials from secrets."""
    sm = get_secrets_manager()

    return {
        "access_key_id": sm.get("videofoundry/aws/access_key_id", default=os.getenv("AWS_ACCESS_KEY_ID")),
        "secret_access_key": sm.get("videofoundry/aws/secret_access_key", default=os.getenv("AWS_SECRET_ACCESS_KEY")),
        "region": sm.get("videofoundry/aws/region", default=os.getenv("AWS_REGION", "us-east-1"))
    }
