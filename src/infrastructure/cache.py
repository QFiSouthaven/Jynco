"""
Intelligent Caching System

Implements the cache-first strategy for generated video clips.
Supports multiple backends (Redis, S3, local filesystem).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store value in cache with optional TTL (seconds)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass


class LocalFilesystemCache(CacheBackend):
    """
    Local filesystem cache backend.

    Stores cache metadata in JSON files and video files in a directory.
    Suitable for development and single-server deployments.
    """

    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.metadata_dir = self.cache_dir / "metadata"
        self.files_dir = self.cache_dir / "files"

        # Create directories
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached entry."""
        metadata_file = self.metadata_dir / f"{key}.json"

        if not metadata_file.exists():
            return None

        # Read metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Check expiration
        if metadata.get("expires_at"):
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            if datetime.utcnow() > expires_at:
                # Expired, remove
                await self.delete(key)
                return None

        # Check if file exists
        file_path = metadata.get("file_path")
        if file_path and not Path(file_path).exists():
            # File missing, invalidate cache
            await self.delete(key)
            return None

        return metadata

    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store entry in cache."""
        metadata = {
            "key": key,
            "file_path": value.get("file_path"),
            "model": value.get("model"),
            "cached_at": datetime.utcnow().isoformat(),
            "expires_at": None
        }

        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            metadata["expires_at"] = expires_at.isoformat()

        metadata_file = self.metadata_dir / f"{key}.json"

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return True

    async def delete(self, key: str) -> bool:
        """Remove entry from cache."""
        metadata_file = self.metadata_dir / f"{key}.json"

        if metadata_file.exists():
            # Read metadata to get file path
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Remove metadata
            metadata_file.unlink()

            # Remove associated file if it exists
            file_path = metadata.get("file_path")
            if file_path:
                file_path = Path(file_path)
                if file_path.exists():
                    file_path.unlink()

            return True

        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists and is valid."""
        result = await self.get(key)
        return result is not None

    async def clear(self) -> bool:
        """Clear all cache entries."""
        import shutil

        # Remove and recreate directories
        shutil.rmtree(self.metadata_dir)
        shutil.rmtree(self.files_dir)

        self.metadata_dir.mkdir(parents=True)
        self.files_dir.mkdir(parents=True)

        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        metadata_files = list(self.metadata_dir.glob("*.json"))
        cache_files = list(self.files_dir.glob("*"))

        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())

        return {
            "entries": len(metadata_files),
            "files": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }


class RedisCache(CacheBackend):
    """
    Redis cache backend.

    Stores metadata in Redis and file paths reference S3 or filesystem.
    Suitable for production multi-server deployments.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        # TODO: Initialize Redis client
        # import redis.asyncio as redis
        # self.redis_client = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached entry from Redis."""
        # TODO: Implement Redis get
        raise NotImplementedError("Redis backend not yet implemented")

    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store entry in Redis."""
        # TODO: Implement Redis set
        raise NotImplementedError("Redis backend not yet implemented")

    async def delete(self, key: str) -> bool:
        """Remove entry from Redis."""
        # TODO: Implement Redis delete
        raise NotImplementedError("Redis backend not yet implemented")

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        # TODO: Implement Redis exists
        raise NotImplementedError("Redis backend not yet implemented")

    async def clear(self) -> bool:
        """Clear all cache entries."""
        # TODO: Implement Redis clear
        raise NotImplementedError("Redis backend not yet implemented")


class CacheManager:
    """
    High-level cache manager.

    Provides a unified interface for caching operations across the application.
    """

    def __init__(self, backend: CacheBackend):
        self.backend = backend

    async def get_cached_video(self, cache_key: str) -> Optional[str]:
        """
        Get cached video file path.

        Args:
            cache_key: Cache key (SHA-256 hash)

        Returns:
            File path if cached, None otherwise
        """
        result = await self.backend.get(cache_key)
        if result:
            return result.get("file_path")
        return None

    async def cache_video(self, cache_key: str, file_path: str,
                         model: str, ttl: Optional[int] = None) -> bool:
        """
        Cache a generated video.

        Args:
            cache_key: Cache key
            file_path: Path to video file
            model: Model used for generation
            ttl: Optional time-to-live in seconds

        Returns:
            True if cached successfully
        """
        return await self.backend.set(cache_key, {
            "file_path": file_path,
            "model": model
        }, ttl=ttl)

    async def invalidate(self, cache_key: str) -> bool:
        """Invalidate a cache entry."""
        return await self.backend.delete(cache_key)

    async def clear_all(self) -> bool:
        """Clear entire cache."""
        return await self.backend.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if hasattr(self.backend, 'get_stats'):
            return await self.backend.get_stats()
        return {"error": "Stats not supported by this backend"}


# Factory function
def create_cache(cache_type: str = "local", **kwargs) -> CacheManager:
    """
    Create a cache manager with the specified backend.

    Args:
        cache_type: "local" or "redis"
        **kwargs: Backend-specific configuration

    Returns:
        CacheManager instance
    """
    if cache_type == "local":
        backend = LocalFilesystemCache(
            cache_dir=kwargs.get("cache_dir", "./cache")
        )
    elif cache_type == "redis":
        backend = RedisCache(
            redis_url=kwargs.get("redis_url", "redis://localhost:6379")
        )
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")

    return CacheManager(backend)
