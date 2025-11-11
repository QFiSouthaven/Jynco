"""
Motion Agent

Wraps image-to-video AI models and implements intelligent caching.
Generates video clips from static images using motion prompts.
"""

import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent


class MotionAgent(BaseAgent):
    """
    The Motion Agent is responsible for:
    - Generating video clips from images using AI models
    - Implementing cache-first strategy to minimize GPU costs
    - Computing deterministic cache keys from inputs
    - Coordinating with external AI services (Runway, Stability AI, etc.)
    """

    def __init__(self, agent_id: str = "motion_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.cache = None  # Will be injected by infrastructure
        self.ai_model = config.get("ai_model", "runway_gen3")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute motion generation task.

        Args:
            task: {
                "clipId": "clip_xyz",
                "sourceImage": "/path/to/image.jpg",
                "motionPrompt": "camera pans left slowly",
                "duration": 3.0,
                "useCache": true
            }

        Returns:
            {
                "success": true,
                "clipId": "clip_xyz",
                "outputFile": "/path/to/output.mp4",
                "cacheKey": "abc123...",
                "cacheHit": true/false,
                "generationTime": 12.5
            }
        """
        try:
            self.validate_task(task, ["clipId", "sourceImage", "motionPrompt"])

            source_image = task["sourceImage"]
            motion_prompt = task["motionPrompt"]
            use_cache = task.get("useCache", True)

            # Step 1: Compute deterministic cache key
            cache_key = self._compute_cache_key(source_image, motion_prompt)

            # Step 2: Check cache if enabled
            if use_cache and self.cache:
                cached_result = await self._check_cache(cache_key)
                if cached_result:
                    self.logger.info(f"Cache hit for clip {task['clipId']}")
                    return {
                        "success": True,
                        "clipId": task["clipId"],
                        "outputFile": cached_result["file_path"],
                        "cacheKey": cache_key,
                        "cacheHit": True,
                        "generationTime": 0.0
                    }

            # Step 3: Cache miss - generate video
            self.logger.info(f"Cache miss for clip {task['clipId']}, generating...")
            generation_result = await self._generate_video(
                source_image,
                motion_prompt,
                task.get("duration", 3.0)
            )

            # Step 4: Store in cache
            if use_cache and self.cache:
                await self._store_in_cache(cache_key, generation_result["file_path"])

            return {
                "success": True,
                "clipId": task["clipId"],
                "outputFile": generation_result["file_path"],
                "cacheKey": cache_key,
                "cacheHit": False,
                "generationTime": generation_result["generation_time"]
            }

        except Exception as e:
            return await self.handle_error(e, task)

    def _compute_cache_key(self, source_image: str, motion_prompt: str) -> str:
        """
        Compute deterministic SHA-256 hash for caching.

        The cache key is computed from:
        - Source image content (file hash)
        - Motion prompt text (exact string)

        Args:
            source_image: Path to source image
            motion_prompt: Motion description text

        Returns:
            64-character hex string (SHA-256)
        """
        hasher = hashlib.sha256()

        # Hash image content
        with open(source_image, 'rb') as f:
            hasher.update(f.read())

        # Hash motion prompt
        hasher.update(motion_prompt.encode('utf-8'))

        # Include model version to invalidate cache on model updates
        hasher.update(self.ai_model.encode('utf-8'))

        return hasher.hexdigest()

    async def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Check if cached result exists.

        Args:
            cache_key: Cache key to lookup

        Returns:
            Dict with file_path if found, None otherwise
        """
        if not self.cache:
            return None

        # Query cache backend (Redis/S3)
        result = await self.cache.get(cache_key)
        if result and Path(result["file_path"]).exists():
            return result

        return None

    async def _store_in_cache(self, cache_key: str, file_path: str) -> None:
        """
        Store generated video in cache.

        Args:
            cache_key: Cache key
            file_path: Path to generated video file
        """
        if not self.cache:
            return

        await self.cache.set(cache_key, {
            "file_path": file_path,
            "model": self.ai_model
        })

        self.logger.info(f"Stored result in cache: {cache_key[:16]}...")

    async def _generate_video(self, source_image: str, motion_prompt: str,
                             duration: float) -> Dict[str, Any]:
        """
        Generate video using AI model.

        This is a placeholder that will be replaced with actual AI model integration.

        Args:
            source_image: Path to source image
            motion_prompt: Motion description
            duration: Video duration in seconds

        Returns:
            {
                "file_path": "/path/to/generated.mp4",
                "generation_time": 12.5
            }
        """
        # TODO: Integrate with actual AI model (Runway, Stability AI, etc.)
        # For now, this is a placeholder

        self.logger.info(f"Generating video with {self.ai_model}")
        self.logger.info(f"  Source: {source_image}")
        self.logger.info(f"  Prompt: {motion_prompt}")
        self.logger.info(f"  Duration: {duration}s")

        # Placeholder: In production, this would:
        # 1. Upload image to AI service
        # 2. Submit generation job with prompt
        # 3. Poll for completion
        # 4. Download result
        # 5. Store in project assets

        raise NotImplementedError(
            "AI model integration not yet implemented. "
            "This requires API keys and model selection configuration."
        )

    def set_cache(self, cache_backend):
        """Inject cache backend dependency."""
        self.cache = cache_backend
