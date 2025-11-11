"""
Local storage client for video storage operations (alternative to S3).
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID
import mimetypes


class LocalStorageClient:
    """
    Local file storage client for uploading and managing video assets.
    Mimics S3Client interface but uses local filesystem.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None
    ):
        """
        Initialize local storage client.

        Args:
            storage_path: Base path for local storage
        """
        self.storage_path = Path(storage_path or os.getenv("LOCAL_STORAGE_PATH", "/videos"))
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
            file_path: Local path to the source file
            storage_key: Storage key (relative path in storage)
            content_type: MIME type (auto-detected if not provided)

        Returns:
            Local file URL/path of the stored file
        """
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)

        # Create full destination path
        dest_path = self.storage_path / storage_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to destination
        shutil.copy2(file_path, dest_path)

        return self.get_url(storage_key)

    def upload_fileobj(
        self,
        fileobj,
        storage_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file object to local storage.

        Args:
            fileobj: File-like object
            storage_key: Storage key (relative path)
            content_type: MIME type

        Returns:
            Local file URL/path
        """
        dest_path = self.storage_path / storage_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(fileobj, f)

        return self.get_url(storage_key)

    def download_file(self, storage_key: str, download_path: str) -> None:
        """
        Copy a file from storage to a local path.

        Args:
            storage_key: Storage key (relative path in storage)
            download_path: Destination path to download the file
        """
        source_path = self.storage_path / storage_key
        shutil.copy2(source_path, download_path)

    def delete_file(self, storage_key: str) -> None:
        """
        Delete a file from storage.

        Args:
            storage_key: Storage key (relative path in storage)
        """
        file_path = self.storage_path / storage_key
        if file_path.exists():
            file_path.unlink()

    def get_url(self, storage_key: str) -> str:
        """
        Get the local file URL/path for a storage key.

        Args:
            storage_key: Storage key

        Returns:
            Local file path as string
        """
        return f"file://{self.storage_path / storage_key}"

    def generate_segment_key(self, project_id: UUID, segment_id: UUID) -> str:
        """
        Generate a storage key for a video segment.

        Args:
            project_id: Project UUID
            segment_id: Segment UUID

        Returns:
            Storage key path
        """
        return f"projects/{project_id}/segments/{segment_id}.mp4"

    def generate_composition_key(self, project_id: UUID, render_job_id: UUID) -> str:
        """
        Generate a storage key for a composed video.

        Args:
            project_id: Project UUID
            render_job_id: Render job UUID

        Returns:
            Storage key path
        """
        return f"projects/{project_id}/renders/{render_job_id}.mp4"

    def file_exists(self, storage_key: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            storage_key: Storage key

        Returns:
            True if file exists, False otherwise
        """
        return (self.storage_path / storage_key).exists()

    def get_file_size(self, storage_key: str) -> int:
        """
        Get the size of a file in storage.

        Args:
            storage_key: Storage key

        Returns:
            File size in bytes
        """
        file_path = self.storage_path / storage_key
        return file_path.stat().st_size if file_path.exists() else 0
