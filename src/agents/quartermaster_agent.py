"""
Quartermaster Agent

Manages all file system operations and asset storage.
Provides a unified interface for file handling across the system.
"""

import shutil
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib

from .base_agent import BaseAgent


class QuartermasterAgent(BaseAgent):
    """
    The Quartermaster Agent is responsible for:
    - Managing project directory structure
    - Storing and retrieving video clips
    - Handling uploads and downloads
    - Organizing assets (images, audio, text)
    - Interfacing with cloud storage (S3, etc.)
    - Managing cache storage backend
    """

    def __init__(self, agent_id: str = "quartermaster_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.base_dir = Path(config.get("base_dir", "./projects"))
        self.cache_dir = Path(config.get("cache_dir", "./cache"))
        self.temp_dir = Path(config.get("temp_dir", "./temp"))

        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file management task.

        Supported operations:
        - create_project: Create project directory structure
        - store_clip: Store a generated clip
        - retrieve_clip: Get a clip by ID
        - store_in_cache: Store file in cache
        - retrieve_from_cache: Get file from cache
        - upload_asset: Upload user asset (image, audio)
        - delete_asset: Remove an asset
        - cleanup_temp: Clean temporary files

        Args:
            task: {
                "operation": "create_project|store_clip|...",
                "data": {...}
            }
        """
        try:
            self.validate_task(task, ["operation"])
            operation = task["operation"]

            operations = {
                "create_project": self._create_project,
                "store_clip": self._store_clip,
                "retrieve_clip": self._retrieve_clip,
                "store_in_cache": self._store_in_cache,
                "retrieve_from_cache": self._retrieve_from_cache,
                "upload_asset": self._upload_asset,
                "delete_asset": self._delete_asset,
                "cleanup_temp": self._cleanup_temp,
            }

            if operation not in operations:
                raise ValueError(f"Unknown operation: {operation}")

            return await operations[operation](task.get("data", {}))

        except Exception as e:
            return await self.handle_error(e, task)

    async def _create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create directory structure for a new project.

        Structure:
        projects/
          proj_xyz/
            clips/          # Generated video clips
            assets/         # User uploaded assets
              images/
              audio/
            exports/        # Final rendered videos
            storyboard.json
        """
        self.validate_task(data, ["projectId"])
        project_id = data["projectId"]

        project_dir = self.base_dir / project_id
        if project_dir.exists():
            return {
                "success": False,
                "error": f"Project already exists: {project_id}"
            }

        # Create directory structure
        (project_dir / "clips").mkdir(parents=True)
        (project_dir / "assets" / "images").mkdir(parents=True)
        (project_dir / "assets" / "audio").mkdir(parents=True)
        (project_dir / "exports").mkdir(parents=True)

        self.logger.info(f"Created project directory: {project_id}")

        return {
            "success": True,
            "projectId": project_id,
            "projectDir": str(project_dir),
            "structure": {
                "clips": str(project_dir / "clips"),
                "assets": str(project_dir / "assets"),
                "exports": str(project_dir / "exports")
            }
        }

    async def _store_clip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a generated clip in the project directory.

        Args:
            data: {
                "projectId": "proj_xyz",
                "clipId": "clip_abc",
                "sourceFile": "/tmp/generated.mp4"
            }
        """
        self.validate_task(data, ["projectId", "clipId", "sourceFile"])

        project_id = data["projectId"]
        clip_id = data["clipId"]
        source_file = Path(data["sourceFile"])

        if not source_file.exists():
            return {
                "success": False,
                "error": f"Source file not found: {source_file}"
            }

        # Destination
        clips_dir = self.base_dir / project_id / "clips"
        dest_file = clips_dir / f"{clip_id}.mp4"

        # Copy file
        shutil.copy2(source_file, dest_file)

        self.logger.info(f"Stored clip {clip_id} in project {project_id}")

        return {
            "success": True,
            "clipId": clip_id,
            "storedPath": str(dest_file),
            "fileSize": dest_file.stat().st_size
        }

    async def _retrieve_clip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a clip file path."""
        self.validate_task(data, ["projectId", "clipId"])

        project_id = data["projectId"]
        clip_id = data["clipId"]

        clip_file = self.base_dir / project_id / "clips" / f"{clip_id}.mp4"

        if not clip_file.exists():
            return {
                "success": False,
                "error": f"Clip not found: {clip_id}"
            }

        return {
            "success": True,
            "clipId": clip_id,
            "filePath": str(clip_file),
            "fileSize": clip_file.stat().st_size
        }

    async def _store_in_cache(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a file in the cache directory.

        Args:
            data: {
                "cacheKey": "abc123...",
                "sourceFile": "/tmp/generated.mp4"
            }
        """
        self.validate_task(data, ["cacheKey", "sourceFile"])

        cache_key = data["cacheKey"]
        source_file = Path(data["sourceFile"])

        if not source_file.exists():
            return {
                "success": False,
                "error": f"Source file not found: {source_file}"
            }

        # Store with cache key as filename
        cache_file = self.cache_dir / f"{cache_key}.mp4"
        shutil.copy2(source_file, cache_file)

        self.logger.info(f"Stored in cache: {cache_key[:16]}...")

        return {
            "success": True,
            "cacheKey": cache_key,
            "cachePath": str(cache_file),
            "fileSize": cache_file.stat().st_size
        }

    async def _retrieve_from_cache(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve a file from cache.

        Args:
            data: {
                "cacheKey": "abc123..."
            }
        """
        self.validate_task(data, ["cacheKey"])

        cache_key = data["cacheKey"]
        cache_file = self.cache_dir / f"{cache_key}.mp4"

        if not cache_file.exists():
            return {
                "success": False,
                "cacheHit": False,
                "error": f"Cache miss: {cache_key}"
            }

        return {
            "success": True,
            "cacheHit": True,
            "cacheKey": cache_key,
            "filePath": str(cache_file),
            "fileSize": cache_file.stat().st_size
        }

    async def _upload_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a user asset (image, audio, etc.).

        Args:
            data: {
                "projectId": "proj_xyz",
                "assetType": "image|audio",
                "fileName": "photo.jpg",
                "sourceFile": "/tmp/upload.jpg"
            }
        """
        self.validate_task(data, ["projectId", "assetType", "fileName", "sourceFile"])

        project_id = data["projectId"]
        asset_type = data["assetType"]
        file_name = data["fileName"]
        source_file = Path(data["sourceFile"])

        if not source_file.exists():
            return {
                "success": False,
                "error": f"Source file not found: {source_file}"
            }

        # Destination
        assets_dir = self.base_dir / project_id / "assets" / asset_type
        dest_file = assets_dir / file_name

        # Copy file
        shutil.copy2(source_file, dest_file)

        # Compute hash for deduplication
        file_hash = self._compute_file_hash(dest_file)

        self.logger.info(f"Uploaded asset {file_name} to project {project_id}")

        return {
            "success": True,
            "projectId": project_id,
            "assetType": asset_type,
            "fileName": file_name,
            "assetPath": str(dest_file),
            "fileHash": file_hash,
            "fileSize": dest_file.stat().st_size
        }

    async def _delete_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an asset file."""
        self.validate_task(data, ["projectId", "assetPath"])

        project_id = data["projectId"]
        asset_path = Path(data["assetPath"])

        # Security: Ensure path is within project directory
        project_dir = self.base_dir / project_id
        if not str(asset_path).startswith(str(project_dir)):
            return {
                "success": False,
                "error": "Invalid path: outside project directory"
            }

        if not asset_path.exists():
            return {
                "success": False,
                "error": f"Asset not found: {asset_path}"
            }

        asset_path.unlink()

        self.logger.info(f"Deleted asset: {asset_path}")

        return {
            "success": True,
            "assetPath": str(asset_path),
            "deleted": True
        }

    async def _cleanup_temp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up temporary files."""
        removed_count = 0
        removed_size = 0

        for temp_file in self.temp_dir.glob("*"):
            if temp_file.is_file():
                removed_size += temp_file.stat().st_size
                temp_file.unlink()
                removed_count += 1

        self.logger.info(f"Cleaned up {removed_count} temp files ({removed_size} bytes)")

        return {
            "success": True,
            "filesRemoved": removed_count,
            "bytesFreed": removed_size
        }

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_project_dir(self, project_id: str) -> Path:
        """Get the project directory path."""
        return self.base_dir / project_id

    def get_clips_dir(self, project_id: str) -> Path:
        """Get the clips directory for a project."""
        return self.base_dir / project_id / "clips"

    def get_assets_dir(self, project_id: str) -> Path:
        """Get the assets directory for a project."""
        return self.base_dir / project_id / "assets"

    def get_exports_dir(self, project_id: str) -> Path:
        """Get the exports directory for a project."""
        return self.base_dir / project_id / "exports"
