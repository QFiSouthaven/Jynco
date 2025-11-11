"""
Storage factory for creating S3 or Local Storage clients.
"""
import os
from typing import Union
from .s3_client import S3Client
from .local_storage_client import LocalStorageClient


def create_storage_client() -> Union[S3Client, LocalStorageClient]:
    """
    Create a storage client based on environment configuration.

    Returns:
        S3Client if USE_LOCAL_STORAGE is false, LocalStorageClient otherwise
    """
    use_local_storage = os.getenv("USE_LOCAL_STORAGE", "false").lower() in ("true", "1", "yes")

    if use_local_storage:
        return LocalStorageClient()
    else:
        return S3Client()
