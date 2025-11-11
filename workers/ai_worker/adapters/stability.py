"""
Stability AI Video Generation Adapter.
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .base import VideoModelInterface, GenerationStatus, GenerationResult


class StabilityAIAdapter(VideoModelInterface):
    """
    Adapter for Stability AI video generation model.

    API Documentation: https://platform.stability.ai/docs
    """

    BASE_URL = "https://api.stability.ai/v2beta"

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = config.get("timeout", 300) if config else 300

    @property
    def model_name(self) -> str:
        return "stability-ai"

    def validate_params(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Stability AI specific parameters.

        Expected parameters:
        - cfg_scale: 0-35 (how closely to follow prompt)
        - motion_bucket_id: 1-255 (amount of motion)
        - seed: integer (for reproducibility)
        """
        validated = model_params.copy()

        # Validate CFG scale
        cfg_scale = validated.get("cfg_scale", 7.0)
        if not 0 <= cfg_scale <= 35:
            raise ValueError(f"Invalid cfg_scale: {cfg_scale}. Must be between 0 and 35.")
        validated["cfg_scale"] = cfg_scale

        # Validate motion bucket
        motion_bucket = validated.get("motion_bucket_id", 127)
        if not 1 <= motion_bucket <= 255:
            raise ValueError(f"Invalid motion_bucket_id: {motion_bucket}. Must be between 1 and 255.")
        validated["motion_bucket_id"] = motion_bucket

        # Seed is optional
        if "seed" in validated:
            validated["seed"] = int(validated["seed"])

        return validated

    async def initiate_generation(
        self,
        prompt: str,
        model_params: Dict[str, Any]
    ) -> str:
        """
        Initiate video generation with Stability AI.
        """
        validated_params = self.validate_params(model_params)

        payload = {
            "text_prompts": [{"text": prompt, "weight": 1.0}],
            "cfg_scale": validated_params.get("cfg_scale", 7.0),
            "motion_bucket_id": validated_params.get("motion_bucket_id", 127),
            "samples": 1
        }

        if "seed" in validated_params:
            payload["seed"] = validated_params["seed"]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.BASE_URL}/video/generate",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            external_job_id = data.get("id")

            if not external_job_id:
                raise Exception("No job ID returned from Stability AI API")

            return external_job_id

    async def get_status(self, external_job_id: str) -> GenerationStatus:
        """
        Check the status of a Stability AI generation job.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/video/result/{external_job_id}",
                headers=self.headers
            )

            # Stability AI returns 202 while processing, 200 when complete
            if response.status_code == 202:
                return GenerationStatus.PROCESSING
            elif response.status_code == 200:
                return GenerationStatus.COMPLETED
            elif response.status_code >= 400:
                return GenerationStatus.FAILED
            else:
                return GenerationStatus.PENDING

    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Retrieve the result of a completed Stability AI generation job.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/video/result/{external_job_id}",
                headers=self.headers
            )

            if response.status_code == 202:
                return GenerationResult(
                    status=GenerationStatus.PROCESSING,
                    external_job_id=external_job_id
                )

            if response.status_code >= 400:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                return GenerationResult(
                    status=GenerationStatus.FAILED,
                    error_message=error_msg,
                    external_job_id=external_job_id
                )

            # Status code 200 - completed
            # Stability AI returns video as binary data or URL in response
            data = response.json()
            video_url = data.get("video_url") or data.get("artifacts", [{}])[0].get("url")

            if not video_url:
                raise Exception("No video URL in completed job")

            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                video_url=video_url,
                external_job_id=external_job_id,
                metadata={
                    "seed": data.get("seed"),
                    "cfg_scale": data.get("cfg_scale"),
                    "motion_bucket_id": data.get("motion_bucket_id")
                },
                completed_at=datetime.utcnow()
            )

    async def cancel_generation(self, external_job_id: str) -> bool:
        """
        Cancel a Stability AI generation job.
        Note: Stability AI may not support cancellation for all job types.
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(
                    f"{self.BASE_URL}/video/{external_job_id}",
                    headers=self.headers
                )
                return response.status_code in [200, 204]
        except Exception:
            return False
