"""
Storage Factory - Context-Aware Storage Selection

Selects the appropriate storage backend (S3 or local) based on execution mode
and provides user isolation for multi-tenant deployments.
"""
import logging
from pathlib import Path
from typing import Protocol, Optional, Union
from uuid import UUID

from config import get_settings
from .s3_client import S3Client
from .local_storage_client import LocalStorageClient

logger = logging.getLogger(__name__)


class StorageBackend(Protocol):
    """Protocol defining the storage backend interface."""

    def upload_file(self, file_path: str, storage_key: str, content_type: Optional[str] = None) -> str:
        """Upload a file to storage."""
        ...

    def upload_fileobj(self, file_obj, storage_key: str, content_type: str = "video/mp4") -> str:
        """Upload a file object to storage."""
        ...

    def download_file(self, storage_key: str, local_path: str):
        """Download a file from storage."""
        ...

    def delete_file(self, storage_key: str):
        """Delete a file from storage."""
        ...

    def get_url(self, storage_key: str) -> str:
        """Get the URL for a stored file."""
        ...


class SecureS3Backend:
    """
    S3 backend with user isolation for production multi-tenant deployments.

    Enforces user-scoped prefixes to prevent unauthorized access.
    """

    def __init__(self, s3_client: S3Client):
        self.client = s3_client

    def _get_user_prefix(self, user_id: Union[str, UUID]) -> str:
        """Get the S3 prefix for a user's files."""
        return f"users/{str(user_id)}/"

    def _validate_key_access(self, storage_key: str, user_id: Union[str, UUID]) -> None:
        """
        Validate that the storage key belongs to the user.

        Args:
            storage_key: S3 key to validate
            user_id: User ID to check against

        Raises:
            PermissionError: If key doesn't belong to user
        """
        user_prefix = self._get_user_prefix(user_id)

        if not storage_key.startswith(user_prefix):
            logger.error(
                f"Access denied: User {user_id} attempted to access {storage_key} "
                f"outside their prefix {user_prefix}"
            )
            raise PermissionError(f"Access denied: file does not belong to user")

    def upload_file(
        self,
        file_path: str,
        storage_key: str,
        user_id: Union[str, UUID],
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file with user isolation."""
        user_prefix = self._get_user_prefix(user_id)
        full_key = f"{user_prefix}{storage_key}"

        logger.info(f"Uploading file for user {user_id}: {full_key}")

        return self.client.upload_file(file_path, full_key, content_type)

    def upload_fileobj(
        self,
        file_obj,
        storage_key: str,
        user_id: Union[str, UUID],
        content_type: str = "video/mp4"
    ) -> str:
        """Upload a file object with user isolation."""
        user_prefix = self._get_user_prefix(user_id)
        full_key = f"{user_prefix}{storage_key}"

        return self.client.upload_fileobj(file_obj, full_key, content_type)

    def download_file(
        self,
        storage_key: str,
        local_path: str,
        user_id: Union[str, UUID]
    ):
        """Download a file with access validation."""
        # Validate user has access to this key
        self._validate_key_access(storage_key, user_id)

        return self.client.download_file(storage_key, local_path)

    def delete_file(
        self,
        storage_key: str,
        user_id: Union[str, UUID]
    ):
        """Delete a file with access validation."""
        # Validate user has access to this key
        self._validate_key_access(storage_key, user_id)

        return self.client.delete_file(storage_key)

    def get_url(self, storage_key: str, user_id: Union[str, UUID]) -> str:
        """Get URL with access validation."""
        # Validate user has access to this key
        self._validate_key_access(storage_key, user_id)

        return self.client.get_url(storage_key)

    def get_presigned_url(
        self,
        storage_key: str,
        user_id: Union[str, UUID],
        expiration: int = 3600
    ) -> str:
        """Generate presigned URL with access validation."""
        # Validate user has access to this key
        self._validate_key_access(storage_key, user_id)

        return self.client.get_presigned_url(storage_key, expiration)


class SecureLocalBackend:
    """
    Local storage backend with user isolation.

    Prevents path traversal and enforces user-scoped directories.
    """

    def __init__(self, local_client: LocalStorageClient):
        self.client = local_client
        self.base_path = Path(local_client.storage_path).resolve()

    def _get_user_directory(self, user_id: Union[str, UUID]) -> Path:
        """Get the storage directory for a user."""
        return self.base_path / "users" / str(user_id)

    def _validate_path_safety(self, path: Path) -> None:
        """
        Validate path doesn't escape the storage directory.

        Args:
            path: Path to validate

        Raises:
            ValueError: If path traversal detected
        """
        resolved = path.resolve()

        if not resolved.is_relative_to(self.base_path):
            logger.error(f"Path traversal detected: {path} -> {resolved}")
            raise ValueError("Path traversal detected")

    def upload_file(
        self,
        file_path: str,
        storage_key: str,
        user_id: Union[str, UUID],
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file with user isolation."""
        user_dir = self._get_user_directory(user_id)
        full_path = user_dir / storage_key

        # Validate path safety
        self._validate_path_safety(full_path)

        # Ensure user directory exists
        user_dir.mkdir(parents=True, exist_ok=True)

        # Convert to relative key for client
        relative_key = str(full_path.relative_to(self.base_path))

        return self.client.upload_file(file_path, relative_key, content_type)

    def upload_fileobj(
        self,
        file_obj,
        storage_key: str,
        user_id: Union[str, UUID],
        content_type: str = "video/mp4"
    ) -> str:
        """Upload a file object with user isolation."""
        user_dir = self._get_user_directory(user_id)
        full_path = user_dir / storage_key

        # Validate path safety
        self._validate_path_safety(full_path)

        # Ensure user directory exists
        user_dir.mkdir(parents=True, exist_ok=True)

        # Convert to relative key for client
        relative_key = str(full_path.relative_to(self.base_path))

        return self.client.upload_fileobj(file_obj, relative_key, content_type)

    def download_file(
        self,
        storage_key: str,
        local_path: str,
        user_id: Union[str, UUID]
    ):
        """Download a file with access validation."""
        user_dir = self._get_user_directory(user_id)
        full_path = user_dir / storage_key

        # Validate path safety
        self._validate_path_safety(full_path)

        # Validate file belongs to user
        if not full_path.is_relative_to(user_dir):
            raise PermissionError("Access denied: file does not belong to user")

        relative_key = str(full_path.relative_to(self.base_path))

        return self.client.download_file(relative_key, local_path)

    def delete_file(
        self,
        storage_key: str,
        user_id: Union[str, UUID]
    ):
        """Delete a file with access validation."""
        user_dir = self._get_user_directory(user_id)
        full_path = user_dir / storage_key

        # Validate path safety
        self._validate_path_safety(full_path)

        # Validate file belongs to user
        if not full_path.is_relative_to(user_dir):
            raise PermissionError("Access denied: file does not belong to user")

        relative_key = str(full_path.relative_to(self.base_path))

        return self.client.delete_file(relative_key)

    def get_url(self, storage_key: str, user_id: Union[str, UUID]) -> str:
        """Get URL with access validation."""
        user_dir = self._get_user_directory(user_id)
        full_path = user_dir / storage_key

        # Validate path safety
        self._validate_path_safety(full_path)

        relative_key = str(full_path.relative_to(self.base_path))

        return self.client.get_url(relative_key)


class StorageFactory:
    """
    Factory for creating storage backends based on execution mode.

    Selects S3 or local storage and applies user isolation policies.
    """

    @staticmethod
    def create_storage() -> Union[SecureS3Backend, SecureLocalBackend]:
        """
        Create the appropriate storage backend based on execution mode.

        Returns:
            Configured storage backend with user isolation

        Raises:
            ValueError: If required configuration is missing for production mode
        """
        settings = get_settings()
        mode = settings.jynco_execution_mode

        if mode == "production":
            # Production: S3 is MANDATORY
            if not settings.s3_bucket or not settings.aws_access_key_id:
                raise ValueError(
                    "Production mode requires S3 configuration. "
                    "Set S3_BUCKET, AWS_ACCESS_KEY_ID, and AWS_SECRET_ACCESS_KEY."
                )

            logger.info("✅ Using S3 storage backend (production mode)")

            s3_client = S3Client(
                bucket_name=settings.s3_bucket,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region=settings.aws_region
            )

            return SecureS3Backend(s3_client)

        elif mode == "self-hosted-production":
            # Self-hosted: Prefer S3, allow local with warning
            if settings.use_s3_storage or (settings.s3_bucket and settings.aws_access_key_id):
                logger.info("✅ Using S3 storage backend (self-hosted production mode)")

                s3_client = S3Client(
                    bucket_name=settings.s3_bucket,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region=settings.aws_region
                )

                return SecureS3Backend(s3_client)

            else:
                logger.warning(
                    "⚠️  SELF-HOSTED PRODUCTION WARNING:\n"
                    "   Using local storage instead of S3.\n"
                    "   For production deployments, S3 is strongly recommended.\n"
                    "   Files will be stored in: {}\n".format(settings.local_storage_path)
                )

                local_client = LocalStorageClient(storage_path=settings.local_storage_path)

                return SecureLocalBackend(local_client)

        else:  # developer mode
            # Developer: Default to local for ease of setup
            logger.info(f"Using local storage backend (developer mode): {settings.local_storage_path}")

            local_client = LocalStorageClient(storage_path=settings.local_storage_path)

            return SecureLocalBackend(local_client)


# Singleton instance
_storage_backend: Optional[Union[SecureS3Backend, SecureLocalBackend]] = None


def get_storage_backend() -> Union[SecureS3Backend, SecureLocalBackend]:
    """Get the singleton storage backend instance."""
    global _storage_backend

    if _storage_backend is None:
        _storage_backend = StorageFactory.create_storage()

    return _storage_backend
