"""
Runway Gen-3 AI Video Generation Adapter.
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .base import VideoModelInterface, GenerationStatus, GenerationResult


class RunwayGen3Adapter(VideoModelInterface):
    """
    Adapter for Runway Gen-3 AI video generation model.

    API Documentation: https://docs.runwayml.com/
    """

    BASE_URL = "https://api.runwayml.com/v1"

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = config.get("timeout", 300) if config else 300

    @property
    def model_name(self) -> str:
        return "runway-gen3"

    def validate_params(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Runway Gen-3 specific parameters.

        Expected parameters:
        - duration: 5 or 10 seconds
        - aspect_ratio: "16:9", "9:16", "1:1"
        - resolution: "720p", "1080p"
        """
        validated = model_params.copy()

        # Validate duration
        duration = validated.get("duration", 5)
        if duration not in [5, 10]:
            raise ValueError(f"Invalid duration: {duration}. Must be 5 or 10 seconds.")
        validated["duration"] = duration

        # Validate aspect ratio
        aspect_ratio = validated.get("aspect_ratio", "16:9")
        if aspect_ratio not in ["16:9", "9:16", "1:1"]:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}")
        validated["aspect_ratio"] = aspect_ratio

        # Validate resolution
        resolution = validated.get("resolution", "1080p")
        if resolution not in ["720p", "1080p"]:
            raise ValueError(f"Invalid resolution: {resolution}")
        validated["resolution"] = resolution

        return validated

    async def initiate_generation(
        self,
        prompt: str,
        model_params: Dict[str, Any]
    ) -> str:
        """
        Initiate video generation with Runway Gen-3.
        """
        validated_params = self.validate_params(model_params)

        payload = {
            "model": "gen3",
            "prompt": prompt,
            "duration": validated_params["duration"],
            "aspect_ratio": validated_params["aspect_ratio"],
            "resolution": validated_params["resolution"]
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.BASE_URL}/generate",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            external_job_id = data.get("id")

            if not external_job_id:
                raise Exception("No job ID returned from Runway API")

            return external_job_id

    async def get_status(self, external_job_id: str) -> GenerationStatus:
        """
        Check the status of a Runway generation job.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/generate/{external_job_id}",
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            runway_status = data.get("status", "").lower()

            # Map Runway statuses to our GenerationStatus enum
            status_map = {
                "pending": GenerationStatus.PENDING,
                "processing": GenerationStatus.PROCESSING,
                "running": GenerationStatus.PROCESSING,
                "succeeded": GenerationStatus.COMPLETED,
                "completed": GenerationStatus.COMPLETED,
                "failed": GenerationStatus.FAILED,
                "error": GenerationStatus.FAILED
            }

            return status_map.get(runway_status, GenerationStatus.PENDING)

    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Retrieve the result of a completed Runway generation job.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/generate/{external_job_id}",
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            status = await self.get_status(external_job_id)

            if status == GenerationStatus.FAILED:
                error_msg = data.get("error", "Unknown error")
                return GenerationResult(
                    status=status,
                    error_message=error_msg,
                    external_job_id=external_job_id
                )

            if status != GenerationStatus.COMPLETED:
                return GenerationResult(
                    status=status,
                    external_job_id=external_job_id
                )

            video_url = data.get("output", {}).get("url")
            if not video_url:
                raise Exception("No video URL in completed job")

            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                video_url=video_url,
                external_job_id=external_job_id,
                metadata={
                    "duration": data.get("duration"),
                    "resolution": data.get("resolution"),
                    "aspect_ratio": data.get("aspect_ratio")
                },
                completed_at=datetime.utcnow()
            )

    async def cancel_generation(self, external_job_id: str) -> bool:
        """
        Cancel a Runway generation job.
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(
                    f"{self.BASE_URL}/generate/{external_job_id}",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception:
            return False
