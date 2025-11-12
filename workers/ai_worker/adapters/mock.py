"""
Mock AI Video Generation Adapter for testing.
Generates real video files using ffmpeg for testing the full pipeline.
"""
import asyncio
import uuid
import subprocess
import tempfile
from pathlib import Path
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
        Generate a real test video using ffmpeg.
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
            try:
                # Generate a real video file using ffmpeg
                video_path = await self._generate_test_video(job["prompt"], job["model_params"])
                job["status"] = GenerationStatus.COMPLETED
                job["video_url"] = f"file://{video_path}"
                job["completed_at"] = datetime.utcnow()
            except Exception as e:
                job["status"] = GenerationStatus.FAILED
                job["error"] = f"Failed to generate test video: {str(e)}"

    async def _generate_test_video(self, prompt: str, model_params: Dict[str, Any]) -> str:
        """
        Generate a test video file using ffmpeg.
        Creates a simple video with colored background and text overlay.

        Args:
            prompt: Text prompt (will be displayed in the video)
            model_params: Parameters including duration, aspect_ratio

        Returns:
            Path to the generated video file
        """
        duration = model_params.get("duration", 5)
        aspect_ratio = model_params.get("aspect_ratio", "16:9")

        # Calculate resolution based on aspect ratio
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        elif aspect_ratio == "9:16":
            width, height = 720, 1280
        elif aspect_ratio == "1:1":
            width, height = 1024, 1024
        else:
            width, height = 1280, 720

        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path = temp_file.name
        temp_file.close()

        # Truncate prompt for display (max 100 chars)
        display_text = prompt[:100] if len(prompt) > 100 else prompt
        # Escape text for ffmpeg
        display_text = display_text.replace("'", "'\\''").replace(":", "\\:")

        # Generate video with ffmpeg
        # Create a colored background with scrolling text
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=blue:s={width}x{height}:d={duration}",
            "-vf", f"drawtext=text='{display_text}':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ]

        # Run ffmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"ffmpeg failed: {stderr.decode() if stderr else 'Unknown error'}")

        return output_path

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
