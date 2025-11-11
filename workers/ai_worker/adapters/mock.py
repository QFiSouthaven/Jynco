"""
Mock AI Video Generation Adapter for testing.
"""
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from .base import VideoModelInterface, GenerationStatus, GenerationResult


class MockAIAdapter(VideoModelInterface):
    """
    Mock adapter for testing without calling real AI APIs.
    Simulates video generation with configurable delays and responses.
    """

    def __init__(self, api_key: str = "mock_key", config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)
        self.generation_delay = config.get("generation_delay", 2.0) if config else 2.0
        self.fail_rate = config.get("fail_rate", 0.0) if config else 0.0
        self._jobs: Dict[str, Dict[str, Any]] = {}

    @property
    def model_name(self) -> str:
        return "mock-ai"

    async def initiate_generation(
        self,
        prompt: str,
        model_params: Dict[str, Any]
    ) -> str:
        """
        Initiate mock video generation.
        """
        external_job_id = f"mock_job_{uuid.uuid4().hex[:12]}"

        self._jobs[external_job_id] = {
            "status": GenerationStatus.PROCESSING,
            "prompt": prompt,
            "model_params": model_params,
            "started_at": datetime.utcnow(),
            "should_fail": False  # Can be set based on fail_rate
        }

        # Simulate async processing
        asyncio.create_task(self._simulate_generation(external_job_id))

        return external_job_id

    async def _simulate_generation(self, external_job_id: str):
        """
        Simulate video generation with a delay.
        """
        await asyncio.sleep(self.generation_delay)

        job = self._jobs.get(external_job_id)
        if not job:
            return

        # Simulate failure based on fail_rate
        import random
        if random.random() < self.fail_rate:
            job["status"] = GenerationStatus.FAILED
            job["error"] = "Simulated generation failure"
        else:
            job["status"] = GenerationStatus.COMPLETED
            job["video_url"] = f"https://mock-cdn.example.com/videos/{external_job_id}.mp4"
            job["completed_at"] = datetime.utcnow()

    async def get_status(self, external_job_id: str) -> GenerationStatus:
        """
        Check the status of a mock generation job.
        """
        job = self._jobs.get(external_job_id)
        if not job:
            return GenerationStatus.FAILED

        return job["status"]

    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Retrieve the result of a mock generation job.
        """
        job = self._jobs.get(external_job_id)
        if not job:
            return GenerationResult(
                status=GenerationStatus.FAILED,
                error_message="Job not found",
                external_job_id=external_job_id
            )

        status = job["status"]

        if status == GenerationStatus.FAILED:
            return GenerationResult(
                status=status,
                error_message=job.get("error", "Unknown error"),
                external_job_id=external_job_id
            )

        if status != GenerationStatus.COMPLETED:
            return GenerationResult(
                status=status,
                external_job_id=external_job_id
            )

        return GenerationResult(
            status=GenerationStatus.COMPLETED,
            video_url=job["video_url"],
            external_job_id=external_job_id,
            metadata={
                "prompt": job["prompt"],
                "model_params": job["model_params"],
                "duration": job["model_params"].get("duration", 5)
            },
            completed_at=job.get("completed_at")
        )

    async def cancel_generation(self, external_job_id: str) -> bool:
        """
        Cancel a mock generation job.
        """
        if external_job_id in self._jobs:
            self._jobs[external_job_id]["status"] = GenerationStatus.FAILED
            self._jobs[external_job_id]["error"] = "Cancelled by user"
            return True
        return False
