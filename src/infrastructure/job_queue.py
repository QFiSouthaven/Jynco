"""
Priority Job Queue System

Implements the job queuing system for render tasks.
Supports priority levels and multiple workers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
from collections import deque
from datetime import datetime
import json
from pathlib import Path
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobPriority(str, Enum):
    """Job priority levels."""
    HIGH = "high"      # Preview renders
    NORMAL = "normal"  # Final renders
    LOW = "low"        # Batch processing


class Job:
    """Represents a job in the queue."""

    def __init__(self, job_id: str, job_type: str, data: Dict[str, Any],
                 priority: JobPriority = JobPriority.NORMAL):
        self.job_id = job_id
        self.job_type = job_type
        self.data = data
        self.priority = priority
        self.status = JobStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize job to dictionary."""
        return {
            "jobId": self.job_id,
            "jobType": self.job_type,
            "data": self.data,
            "priority": self.priority.value,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "result": self.result
        }


class QueueBackend(ABC):
    """Abstract base class for queue backends."""

    @abstractmethod
    async def enqueue(self, job: Job) -> bool:
        """Add job to queue."""
        pass

    @abstractmethod
    async def dequeue(self, timeout: Optional[int] = None) -> Optional[Job]:
        """Remove and return next job from queue."""
        pass

    @abstractmethod
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        pass

    @abstractmethod
    async def update_job(self, job: Job) -> bool:
        """Update job status."""
        pass

    @abstractmethod
    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """List jobs, optionally filtered by status."""
        pass


class InMemoryQueue(QueueBackend):
    """
    In-memory queue backend.

    Suitable for development and single-process deployments.
    Uses separate queues for each priority level.
    """

    def __init__(self):
        self.high_priority_queue: deque = deque()
        self.normal_priority_queue: deque = deque()
        self.low_priority_queue: deque = deque()
        self.jobs: Dict[str, Job] = {}
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)

    async def enqueue(self, job: Job) -> bool:
        """Add job to appropriate priority queue."""
        async with self._lock:
            # Store job
            self.jobs[job.job_id] = job

            # Add to appropriate queue
            if job.priority == JobPriority.HIGH:
                self.high_priority_queue.append(job.job_id)
            elif job.priority == JobPriority.NORMAL:
                self.normal_priority_queue.append(job.job_id)
            else:
                self.low_priority_queue.append(job.job_id)

            # Notify waiting workers
            self._not_empty.notify()

            return True

    async def dequeue(self, timeout: Optional[int] = None) -> Optional[Job]:
        """
        Remove and return next job.

        Priority order: HIGH > NORMAL > LOW
        """
        async with self._not_empty:
            # Wait for job to be available
            while not self._has_jobs():
                try:
                    await asyncio.wait_for(
                        self._not_empty.wait(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    return None

            # Get job from highest priority queue
            job_id = None
            if self.high_priority_queue:
                job_id = self.high_priority_queue.popleft()
            elif self.normal_priority_queue:
                job_id = self.normal_priority_queue.popleft()
            elif self.low_priority_queue:
                job_id = self.low_priority_queue.popleft()

            if job_id:
                job = self.jobs.get(job_id)
                if job:
                    job.status = JobStatus.RUNNING
                    job.started_at = datetime.utcnow()
                    return job

            return None

    def _has_jobs(self) -> bool:
        """Check if any jobs are available."""
        return bool(
            self.high_priority_queue or
            self.normal_priority_queue or
            self.low_priority_queue
        )

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        async with self._lock:
            return self.jobs.get(job_id)

    async def update_job(self, job: Job) -> bool:
        """Update job in storage."""
        async with self._lock:
            if job.job_id in self.jobs:
                self.jobs[job.job_id] = job
                return True
            return False

    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """List all jobs, optionally filtered by status."""
        async with self._lock:
            jobs = list(self.jobs.values())
            if status:
                jobs = [j for j in jobs if j.status == status]
            return jobs

    async def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        async with self._lock:
            return {
                "total_jobs": len(self.jobs),
                "high_priority": len(self.high_priority_queue),
                "normal_priority": len(self.normal_priority_queue),
                "low_priority": len(self.low_priority_queue),
                "pending": sum(1 for j in self.jobs.values() if j.status == JobStatus.PENDING),
                "running": sum(1 for j in self.jobs.values() if j.status == JobStatus.RUNNING),
                "completed": sum(1 for j in self.jobs.values() if j.status == JobStatus.COMPLETED),
                "failed": sum(1 for j in self.jobs.values() if j.status == JobStatus.FAILED)
            }


class RabbitMQQueue(QueueBackend):
    """
    RabbitMQ queue backend.

    Suitable for production multi-server deployments.
    Provides durability and distributed processing.
    """

    def __init__(self, rabbitmq_url: str = "amqp://localhost"):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        # TODO: Initialize RabbitMQ connection
        # import aio_pika
        # self.connection = await aio_pika.connect_robust(rabbitmq_url)

    async def enqueue(self, job: Job) -> bool:
        """Publish job to RabbitMQ."""
        # TODO: Implement RabbitMQ publish
        raise NotImplementedError("RabbitMQ backend not yet implemented")

    async def dequeue(self, timeout: Optional[int] = None) -> Optional[Job]:
        """Consume job from RabbitMQ."""
        # TODO: Implement RabbitMQ consume
        raise NotImplementedError("RabbitMQ backend not yet implemented")

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        # TODO: Implement job lookup (requires persistence)
        raise NotImplementedError("RabbitMQ backend not yet implemented")

    async def update_job(self, job: Job) -> bool:
        """Update job status."""
        # TODO: Implement job update (requires persistence)
        raise NotImplementedError("RabbitMQ backend not yet implemented")

    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """List jobs."""
        # TODO: Implement job listing (requires persistence)
        raise NotImplementedError("RabbitMQ backend not yet implemented")


class JobQueue:
    """
    High-level job queue manager.

    Provides a unified interface for job queue operations.
    """

    def __init__(self, backend: QueueBackend):
        self.backend = backend

    async def submit(self, job_data: Dict[str, Any], priority: str = "normal") -> str:
        """
        Submit a new job to the queue.

        Args:
            job_data: Job data including jobId, projectId, etc.
            priority: "high", "normal", or "low"

        Returns:
            Job ID
        """
        job_id = job_data.get("jobId")
        if not job_id:
            raise ValueError("Job data must include 'jobId'")

        job_priority = JobPriority(priority)
        job = Job(
            job_id=job_id,
            job_type=job_data.get("jobType", "render"),
            data=job_data,
            priority=job_priority
        )

        await self.backend.enqueue(job)
        return job_id

    async def pull(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Pull next job from queue.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Job data dictionary or None if no jobs available
        """
        job = await self.backend.dequeue(timeout=timeout)
        if job:
            return job.data
        return None

    async def complete(self, job_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark a job as completed.

        Args:
            job_id: Job ID
            result: Optional result data

        Returns:
            True if updated successfully
        """
        job = await self.backend.get_job(job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result = result
            return await self.backend.update_job(job)
        return False

    async def fail(self, job_id: str, error: str) -> bool:
        """
        Mark a job as failed.

        Args:
            job_id: Job ID
            error: Error message

        Returns:
            True if updated successfully
        """
        job = await self.backend.get_job(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error = error
            return await self.backend.update_job(job)
        return False

    async def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job status dictionary or None if not found
        """
        job = await self.backend.get_job(job_id)
        if job:
            return job.to_dict()
        return None

    async def list_pending(self) -> List[Dict[str, Any]]:
        """List all pending jobs."""
        jobs = await self.backend.list_jobs(status=JobStatus.PENDING)
        return [job.to_dict() for job in jobs]

    async def list_running(self) -> List[Dict[str, Any]]:
        """List all running jobs."""
        jobs = await self.backend.list_jobs(status=JobStatus.RUNNING)
        return [job.to_dict() for job in jobs]

    async def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        if hasattr(self.backend, 'get_stats'):
            return await self.backend.get_stats()
        return {"error": "Stats not supported by this backend"}


# Factory function
def create_job_queue(queue_type: str = "memory", **kwargs) -> JobQueue:
    """
    Create a job queue with the specified backend.

    Args:
        queue_type: "memory" or "rabbitmq"
        **kwargs: Backend-specific configuration

    Returns:
        JobQueue instance
    """
    if queue_type == "memory":
        backend = InMemoryQueue()
    elif queue_type == "rabbitmq":
        backend = RabbitMQQueue(
            rabbitmq_url=kwargs.get("rabbitmq_url", "amqp://localhost")
        )
    else:
        raise ValueError(f"Unknown queue type: {queue_type}")

    return JobQueue(backend)
