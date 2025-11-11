"""
Redis client for real-time state management.
"""
import redis
import json
import os
from typing import Optional, Dict, Any
from uuid import UUID


class RedisClient:
    """
    Redis client for tracking real-time render job and segment status.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis client.

        Args:
            redis_url: Redis connection URL (default from environment)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.redis_url, decode_responses=True)

    def set_render_job_progress(
        self,
        render_job_id: UUID,
        segments_total: int,
        segments_completed: int,
        status: str
    ):
        """
        Update render job progress in Redis.

        Args:
            render_job_id: UUID of the render job
            segments_total: Total number of segments
            segments_completed: Number of completed segments
            status: Current status
        """
        key = f"render_job:{render_job_id}"
        self.client.hset(
            key,
            mapping={
                "segments_total": segments_total,
                "segments_completed": segments_completed,
                "status": status,
                "progress_percentage": (segments_completed / segments_total * 100) if segments_total > 0 else 0
            }
        )
        # Set expiration to 24 hours
        self.client.expire(key, 86400)

    def get_render_job_progress(self, render_job_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get render job progress from Redis.

        Args:
            render_job_id: UUID of the render job

        Returns:
            Dictionary with progress data or None if not found
        """
        key = f"render_job:{render_job_id}"
        data = self.client.hgetall(key)
        if not data:
            return None

        return {
            "segments_total": int(data.get("segments_total", 0)),
            "segments_completed": int(data.get("segments_completed", 0)),
            "status": data.get("status", "unknown"),
            "progress_percentage": float(data.get("progress_percentage", 0))
        }

    def increment_render_job_progress(self, render_job_id: UUID):
        """
        Increment the completed segments counter for a render job.

        Args:
            render_job_id: UUID of the render job
        """
        key = f"render_job:{render_job_id}"
        self.client.hincrby(key, "segments_completed", 1)

        # Recalculate progress percentage
        data = self.client.hgetall(key)
        segments_total = int(data.get("segments_total", 0))
        segments_completed = int(data.get("segments_completed", 0))

        if segments_total > 0:
            progress = (segments_completed / segments_total) * 100
            self.client.hset(key, "progress_percentage", progress)

    def set_segment_status(
        self,
        segment_id: UUID,
        status: str,
        render_job_id: Optional[UUID] = None
    ):
        """
        Update segment status in Redis.

        Args:
            segment_id: UUID of the segment
            status: Current status
            render_job_id: Optional render job ID for tracking
        """
        key = f"segment:{segment_id}"
        data = {"status": status}
        if render_job_id:
            data["render_job_id"] = str(render_job_id)

        self.client.hset(key, mapping=data)
        # Set expiration to 24 hours
        self.client.expire(key, 86400)

    def get_segment_status(self, segment_id: UUID) -> Optional[str]:
        """
        Get segment status from Redis.

        Args:
            segment_id: UUID of the segment

        Returns:
            Status string or None if not found
        """
        key = f"segment:{segment_id}"
        return self.client.hget(key, "status")

    def delete_render_job_progress(self, render_job_id: UUID):
        """
        Delete render job progress from Redis.

        Args:
            render_job_id: UUID of the render job
        """
        key = f"render_job:{render_job_id}"
        self.client.delete(key)

    def publish_segment_completed(self, segment_id: UUID, render_job_id: UUID):
        """
        Publish a segment completion event to a Redis pub/sub channel.

        Args:
            segment_id: UUID of the completed segment
            render_job_id: UUID of the render job
        """
        message = json.dumps({
            "segment_id": str(segment_id),
            "render_job_id": str(render_job_id),
            "event": "segment_completed"
        })
        self.client.publish("segment_events", message)
