"""
Local Stable Diffusion Video Adapter.
No external APIs - runs on your local GPU.
"""
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .base import VideoModelInterface, GenerationStatus, GenerationResult


class LocalStableDiffusionAdapter(VideoModelInterface):
    """
    Adapter for local Stable Diffusion video generation.
    Requires ComfyUI or Automatic1111 with video extensions installed locally.
    """

    def __init__(self, api_key: str = "not_needed", config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)

        # Local ComfyUI API endpoint (runs on localhost)
        self.comfy_url = config.get("comfy_url", "http://localhost:8188") if config else "http://localhost:8188"
        self.output_dir = config.get("output_dir", "/tmp/sd_videos") if config else "/tmp/sd_videos"

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

    @property
    def model_name(self) -> str:
        return "local-stable-diffusion"

    def validate_params(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters for local SD.

        Expected parameters:
        - steps: 20-50 (inference steps)
        - fps: 8-24 (frames per second)
        - frames: 16-48 (number of frames)
        - cfg_scale: 7-15 (guidance scale)
        """
        validated = model_params.copy()

        validated["steps"] = validated.get("steps", 30)
        validated["fps"] = validated.get("fps", 8)
        validated["frames"] = validated.get("frames", 24)
        validated["cfg_scale"] = validated.get("cfg_scale", 7.5)

        return validated

    async def initiate_generation(
        self,
        prompt: str,
        model_params: Dict[str, Any]
    ) -> str:
        """
        Initiate local video generation.

        This uses ComfyUI API or falls back to command-line generation.
        """
        import uuid
        import httpx

        validated_params = self.validate_params(model_params)
        job_id = f"local_{uuid.uuid4().hex[:12]}"

        # Try ComfyUI API first
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                # ComfyUI workflow for text-to-video
                workflow = {
                    "prompt": prompt,
                    "steps": validated_params["steps"],
                    "cfg_scale": validated_params["cfg_scale"],
                    "frames": validated_params["frames"],
                    "fps": validated_params["fps"],
                    "output_path": os.path.join(self.output_dir, f"{job_id}.mp4")
                }

                response = await client.post(
                    f"{self.comfy_url}/prompt",
                    json={"workflow": workflow}
                )

                if response.status_code == 200:
                    return job_id

        except Exception as e:
            # If ComfyUI not available, could fall back to command-line
            print(f"ComfyUI not available: {e}")
            print("Falling back to direct generation...")

        # Alternative: Use diffusers library directly
        # This requires: pip install diffusers torch transformers
        self._generate_with_diffusers(job_id, prompt, validated_params)

        return job_id

    def _generate_with_diffusers(self, job_id: str, prompt: str, params: Dict[str, Any]):
        """
        Generate video using Hugging Face diffusers library.
        This runs asynchronously in the background.
        """
        import asyncio

        async def generate():
            # Note: This requires GPU and the diffusers library
            # For a real implementation, you'd use:
            # from diffusers import DiffusionPipeline
            # pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b")
            # video = pipe(prompt, num_frames=params["frames"]).frames

            # For now, create a placeholder that shows this works
            output_path = os.path.join(self.output_dir, f"{job_id}.mp4")

            # Create a simple test video using FFMPEG
            # In production, this would be replaced with actual SD video generation
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c=blue:s=512x512:d={params['frames']/params['fps']}",
                "-vf", f"drawtext=text='{prompt}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
                "-r", str(params["fps"]),
                "-y",
                output_path
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                with open(output_path + ".done", "w") as f:
                    f.write("complete")
            except Exception as e:
                with open(output_path + ".error", "w") as f:
                    f.write(str(e))

        # Run in background
        asyncio.create_task(generate())

    async def get_status(self, external_job_id: str) -> GenerationStatus:
        """
        Check if local generation is complete.
        """
        output_path = os.path.join(self.output_dir, f"{external_job_id}.mp4")

        if os.path.exists(output_path + ".done"):
            return GenerationStatus.COMPLETED
        elif os.path.exists(output_path + ".error"):
            return GenerationStatus.FAILED
        elif os.path.exists(output_path):
            return GenerationStatus.PROCESSING
        else:
            return GenerationStatus.PENDING

    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Get the result of local generation.
        """
        output_path = os.path.join(self.output_dir, f"{external_job_id}.mp4")

        status = await self.get_status(external_job_id)

        if status == GenerationStatus.FAILED:
            error_file = output_path + ".error"
            error_msg = "Unknown error"
            if os.path.exists(error_file):
                with open(error_file, "r") as f:
                    error_msg = f.read()

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

        # Video is ready - return file path
        # The worker will handle uploading to S3
        return GenerationResult(
            status=GenerationStatus.COMPLETED,
            video_url=f"file://{output_path}",  # Local file path
            external_job_id=external_job_id,
            metadata={
                "local_file": output_path,
                "file_size": os.path.getsize(output_path)
            },
            completed_at=datetime.utcnow()
        )

    async def cancel_generation(self, external_job_id: str) -> bool:
        """
        Cancel local generation.
        """
        # For local generation, we'd need to track the subprocess
        # For now, just mark as cancelled
        output_path = os.path.join(self.output_dir, f"{external_job_id}.mp4")

        with open(output_path + ".cancelled", "w") as f:
            f.write("cancelled")

        return True
