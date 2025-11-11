"""
ComfyUI Adapter for Video Generation.
Integrates with ComfyUI's REST API for video generation workflows.
"""
import httpx
import uuid
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .base import VideoModelInterface, GenerationStatus, GenerationResult


class ComfyUIAdapter(VideoModelInterface):
    """
    Adapter for ComfyUI video generation.

    ComfyUI is a node-based interface for AI image/video generation.
    This adapter communicates with ComfyUI's REST API to submit workflows
    and retrieve generated videos.
    """

    def __init__(self, api_key: str = "", config: Optional[Dict[str, Any]] = None):
        """
        Initialize ComfyUI adapter.

        Args:
            api_key: Not required for local ComfyUI instances, but kept for interface compatibility
            config: Configuration including ComfyUI URL and workflow settings
        """
        super().__init__(api_key, config)
        self.comfyui_url = config.get("comfyui_url", "http://comfyui:8188") if config else "http://comfyui:8188"
        self.default_workflow = config.get("default_workflow") if config else None
        self.client = httpx.AsyncClient(timeout=30.0)
        self._jobs: Dict[str, Dict[str, Any]] = {}

    @property
    def model_name(self) -> str:
        return "comfyui"

    async def initiate_generation(
        self,
        prompt: str,
        model_params: Dict[str, Any]
    ) -> str:
        """
        Initiate video generation via ComfyUI.

        Args:
            prompt: Text prompt for video generation
            model_params: Parameters including workflow definition, resolution, duration, etc.

        Returns:
            prompt_id: Unique identifier for the ComfyUI job
        """
        # Get workflow from params or use default
        workflow = model_params.get("workflow", self.default_workflow)

        if not workflow:
            raise ValueError("No workflow provided. Include 'workflow' in model_params or set default_workflow in config")

        # Inject prompt into workflow
        workflow_with_prompt = self._inject_prompt(workflow, prompt, model_params)

        # Generate client ID for this request
        client_id = str(uuid.uuid4())

        # Submit prompt to ComfyUI
        try:
            response = await self.client.post(
                f"{self.comfyui_url}/prompt",
                json={
                    "prompt": workflow_with_prompt,
                    "client_id": client_id
                }
            )
            response.raise_for_status()
            result = response.json()

            prompt_id = result.get("prompt_id")
            if not prompt_id:
                raise ValueError("No prompt_id returned from ComfyUI")

            # Store job info
            self._jobs[prompt_id] = {
                "status": GenerationStatus.PROCESSING,
                "prompt": prompt,
                "model_params": model_params,
                "client_id": client_id,
                "started_at": datetime.utcnow()
            }

            return prompt_id

        except httpx.HTTPError as e:
            raise Exception(f"Failed to initiate ComfyUI generation: {str(e)}")

    def _inject_prompt(
        self,
        workflow: Dict[str, Any],
        prompt: str,
        model_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Inject prompt and parameters into ComfyUI workflow.

        This method looks for text input nodes in the workflow and replaces
        their text with the provided prompt. Override this method for custom
        workflow structures.

        Args:
            workflow: ComfyUI workflow JSON
            prompt: Text prompt to inject
            model_params: Additional parameters to inject

        Returns:
            Modified workflow with injected values
        """
        workflow = workflow.copy()

        # Find and update text input nodes
        # Common node types: "CLIPTextEncode", "TextNode", etc.
        prompt_node_id = model_params.get("prompt_node_id", "6")  # Default node ID for prompts

        if prompt_node_id in workflow:
            if "inputs" in workflow[prompt_node_id]:
                workflow[prompt_node_id]["inputs"]["text"] = prompt

        # Inject other parameters (resolution, steps, etc.)
        if "width" in model_params and "sampler_node_id" in model_params:
            sampler_id = model_params["sampler_node_id"]
            if sampler_id in workflow and "inputs" in workflow[sampler_id]:
                workflow[sampler_id]["inputs"]["width"] = model_params["width"]

        if "height" in model_params and "sampler_node_id" in model_params:
            sampler_id = model_params["sampler_node_id"]
            if sampler_id in workflow and "inputs" in workflow[sampler_id]:
                workflow[sampler_id]["inputs"]["height"] = model_params["height"]

        return workflow

    async def get_status(self, external_job_id: str) -> GenerationStatus:
        """
        Check the status of a ComfyUI generation job.

        Args:
            external_job_id: ComfyUI prompt_id

        Returns:
            Current generation status
        """
        try:
            response = await self.client.get(f"{self.comfyui_url}/history/{external_job_id}")
            response.raise_for_status()
            history = response.json()

            if external_job_id not in history:
                # Job might still be in queue
                return GenerationStatus.PROCESSING

            job_info = history[external_job_id]

            # Check if job has completed
            if "outputs" in job_info:
                return GenerationStatus.COMPLETED

            # Check for errors
            if job_info.get("status", {}).get("status_str") == "error":
                return GenerationStatus.FAILED

            return GenerationStatus.PROCESSING

        except httpx.HTTPError as e:
            # If we can't reach ComfyUI, assume still processing
            return GenerationStatus.PROCESSING

    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Retrieve the result of a completed ComfyUI generation job.

        Args:
            external_job_id: ComfyUI prompt_id

        Returns:
            GenerationResult with video URL and metadata
        """
        try:
            response = await self.client.get(f"{self.comfyui_url}/history/{external_job_id}")
            response.raise_for_status()
            history = response.json()

            if external_job_id not in history:
                return GenerationResult(
                    status=GenerationStatus.PROCESSING,
                    external_job_id=external_job_id
                )

            job_info = history[external_job_id]

            # Check for errors
            if job_info.get("status", {}).get("status_str") == "error":
                error_messages = job_info.get("status", {}).get("messages", [])
                error_msg = "; ".join([str(msg) for msg in error_messages]) if error_messages else "Unknown error"
                return GenerationResult(
                    status=GenerationStatus.FAILED,
                    error_message=error_msg,
                    external_job_id=external_job_id
                )

            # Check if job has completed and get outputs
            if "outputs" not in job_info:
                return GenerationResult(
                    status=GenerationStatus.PROCESSING,
                    external_job_id=external_job_id
                )

            outputs = job_info["outputs"]

            # Find video/image outputs
            video_url = None
            for node_id, node_output in outputs.items():
                if "videos" in node_output or "gifs" in node_output:
                    # Get first video
                    media_list = node_output.get("videos", node_output.get("gifs", []))
                    if media_list:
                        filename = media_list[0]["filename"]
                        # Construct URL to retrieve the file
                        video_url = f"{self.comfyui_url}/view?filename={filename}&type=output"
                        break
                elif "images" in node_output:
                    # Fallback to images if no video
                    images = node_output["images"]
                    if images:
                        filename = images[0]["filename"]
                        video_url = f"{self.comfyui_url}/view?filename={filename}&type=output"
                        break

            if not video_url:
                return GenerationResult(
                    status=GenerationStatus.FAILED,
                    error_message="No video or image output found in ComfyUI result",
                    external_job_id=external_job_id
                )

            job_data = self._jobs.get(external_job_id, {})

            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                video_url=video_url,
                external_job_id=external_job_id,
                metadata={
                    "prompt": job_data.get("prompt", ""),
                    "model_params": job_data.get("model_params", {}),
                    "comfyui_outputs": outputs
                },
                completed_at=datetime.utcnow()
            )

        except httpx.HTTPError as e:
            return GenerationResult(
                status=GenerationStatus.FAILED,
                error_message=f"Failed to retrieve ComfyUI result: {str(e)}",
                external_job_id=external_job_id
            )

    async def cancel_generation(self, external_job_id: str) -> bool:
        """
        Cancel a ComfyUI generation job.

        Args:
            external_job_id: ComfyUI prompt_id

        Returns:
            True if cancellation succeeded
        """
        try:
            # ComfyUI's interrupt endpoint
            response = await self.client.post(f"{self.comfyui_url}/interrupt")
            response.raise_for_status()

            # Update local job status
            if external_job_id in self._jobs:
                self._jobs[external_job_id]["status"] = GenerationStatus.FAILED

            return True
        except httpx.HTTPError:
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
