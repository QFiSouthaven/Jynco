"""
Local storage client for video storage operations (S3 alternative).
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID
import mimetypes


class LocalStorageClient:
    """
    Local file system storage client for video assets.
    Alternative to S3 for development/testing.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize local storage client.

        Args:
            storage_path: Local directory path for storing files
            base_url: Base URL for accessing stored files (e.g., http://localhost:8000/storage)
        """
        self.storage_path = Path(storage_path or os.getenv("LOCAL_STORAGE_PATH", "/tmp/video-foundry/videos"))
        self.base_url = base_url or os.getenv("LOCAL_STORAGE_BASE_URL", "http://localhost:8000/storage")

        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def upload_file(
        self,
        file_path: str,
        storage_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Copy a file to local storage.

        Args:
            file_path: Local path to the file
            storage_key: Storage path (relative to storage_path)
            content_type: MIME type (not used, kept for compatibility)

        Returns:
            URL of the stored file

        Raises:
            IOError: If copy fails
        """
        # Create destination path
        dest_path = self.storage_path / storage_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(file_path, dest_path)

        return self.get_url(storage_key)

    def upload_fileobj(
        self,
        file_obj,
        storage_key: str,
        content_type: str = "video/mp4"
    ) -> str:
        """
        Write a file object to local storage.

        Args:
            file_obj: File-like object
            storage_key: Storage path
            content_type: MIME type (not used, kept for compatibility)

        Returns:
            URL of the stored file
        """
        dest_path = self.storage_path / storage_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(file_obj, f)

        return self.get_url(storage_key)

    def download_file(self, storage_key: str, local_path: str):
        """
        Copy a file from local storage.

        Args:
            storage_key: Storage path
            local_path: Local path to save the file

        Raises:
            IOError: If copy fails
        """
        src_path = self.storage_path / storage_key
        shutil.copy2(src_path, local_path)

    def delete_file(self, storage_key: str):
        """
        Delete a file from local storage.

        Args:
            storage_key: Storage path

        Raises:
            IOError: If deletion fails
        """
        file_path = self.storage_path / storage_key
        if file_path.exists():
            file_path.unlink()

    def get_url(self, storage_key: str) -> str:
        """
        Get the URL for a stored file.

        Args:
            storage_key: Storage path

        Returns:
            URL for the file
        """
        return f"{self.base_url}/{storage_key}"

    def get_presigned_url(
        self,
        storage_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Get URL for a stored file (no expiration for local storage).

        Args:
            storage_key: Storage path
            expiration: Not used (kept for compatibility)

        Returns:
            URL for the file
        """
        return self.get_url(storage_key)

    def generate_segment_key(self, project_id: UUID, segment_id: UUID) -> str:
        """
        Generate storage key for a segment video.

        Args:
            project_id: Project UUID
            segment_id: Segment UUID

        Returns:
            Storage key path
        """
        return f"segments/{project_id}/{segment_id}.mp4"

    def generate_final_video_key(self, project_id: UUID, render_job_id: UUID) -> str:
        """
        Generate storage key for a final rendered video.

        Args:
            project_id: Project UUID
            render_job_id: Render job UUID

        Returns:
            Storage key path
        """
        return f"renders/{project_id}/{render_job_id}.mp4"

    def get_file_path(self, storage_key: str) -> Path:
        """
        Get the absolute file system path for a storage key.

        Args:
            storage_key: Storage path

        Returns:
            Absolute file system path
        """
        return self.storage_path / storage_key

    def file_exists(self, storage_key: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            storage_key: Storage path

        Returns:
            True if file exists, False otherwise
        """
        return (self.storage_path / storage_key).exists()
