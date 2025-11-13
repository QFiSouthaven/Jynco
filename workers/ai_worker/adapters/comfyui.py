"""
ComfyUI Adapter for Video Generation.
Integrates with ComfyUI's REST API for video generation workflows.
"""
import httpx
import uuid
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import VideoModelInterface, GenerationStatus, GenerationResult
from .exceptions import (
    ComfyUIConnectionError,
    ComfyUITimeoutError,
    ComfyUIWorkflowError,
    ComfyUIMissingNodeError,
    ComfyUIInvalidParametersError,
    ComfyUIGenerationError,
    ComfyUIOutputError
)

logger = logging.getLogger(__name__)


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

        # Configure timeout - longer for generation, shorter for status checks
        self.request_timeout = config.get("request_timeout", 30.0) if config else 30.0
        self.generation_timeout = config.get("generation_timeout", 300.0) if config else 300.0

        self.client = httpx.AsyncClient(timeout=self.request_timeout)
        self._jobs: Dict[str, Dict[str, Any]] = {}

        logger.info(f"ComfyUIAdapter initialized with URL: {self.comfyui_url}")

    @property
    def model_name(self) -> str:
        return "comfyui"

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if ComfyUI is reachable and responsive.

        Returns:
            Dictionary with health status information
        """
        try:
            response = await self.client.get(f"{self.comfyui_url}/system_stats", timeout=5.0)
            response.raise_for_status()
            return {
                "status": "healthy",
                "url": self.comfyui_url,
                "details": response.json()
            }
        except httpx.TimeoutException:
            logger.warning(f"ComfyUI health check timed out: {self.comfyui_url}")
            return {
                "status": "timeout",
                "url": self.comfyui_url,
                "error": "Health check timed out"
            }
        except httpx.ConnectError as e:
            logger.warning(f"ComfyUI health check connection failed: {self.comfyui_url}")
            return {
                "status": "unreachable",
                "url": self.comfyui_url,
                "error": "Cannot connect to ComfyUI service"
            }
        except Exception as e:
            logger.error(f"ComfyUI health check error: {e}")
            return {
                "status": "error",
                "url": self.comfyui_url,
                "error": str(e)
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True
    )
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

        Raises:
            ComfyUIWorkflowError: If workflow is invalid or missing
            ComfyUIConnectionError: If cannot connect to ComfyUI
            ComfyUITimeoutError: If request times out
            ComfyUIInvalidParametersError: If parameters are invalid
        """
        logger.info(f"Initiating ComfyUI generation with prompt: {prompt[:50]}...")

        # Get workflow from params or use default
        workflow = model_params.get("workflow", self.default_workflow)

        if not workflow:
            logger.error("No workflow provided in model_params or config")
            raise ComfyUIWorkflowError(
                "No workflow provided. Include 'workflow' in model_params or set default_workflow in config"
            )

        # Validate workflow structure
        if not isinstance(workflow, dict):
            logger.error(f"Invalid workflow type: {type(workflow)}")
            raise ComfyUIWorkflowError("Workflow must be a valid JSON object")

        # Inject prompt into workflow
        try:
            workflow_with_prompt = self._inject_prompt(workflow, prompt, model_params)
        except Exception as e:
            logger.error(f"Failed to inject prompt into workflow: {e}")
            raise ComfyUIWorkflowError(f"Failed to process workflow: {str(e)}")

        # Generate client ID for this request
        client_id = str(uuid.uuid4())

        # Submit prompt to ComfyUI
        try:
            logger.debug(f"Submitting workflow to {self.comfyui_url}/prompt")
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
                logger.error("No prompt_id in ComfyUI response")
                raise ComfyUIGenerationError("No prompt_id returned from ComfyUI")

            # Store job info
            self._jobs[prompt_id] = {
                "status": GenerationStatus.PROCESSING,
                "prompt": prompt,
                "model_params": model_params,
                "client_id": client_id,
                "started_at": datetime.utcnow()
            }

            logger.info(f"ComfyUI generation initiated successfully: prompt_id={prompt_id}")
            return prompt_id

        except httpx.TimeoutException as e:
            logger.error(f"ComfyUI request timed out: {e}")
            raise ComfyUITimeoutError(url=self.comfyui_url, timeout=int(self.request_timeout))

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to ComfyUI at {self.comfyui_url}: {e}")
            raise ComfyUIConnectionError(url=self.comfyui_url)

        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", str(error_data))
            except:
                error_detail = e.response.text

            logger.error(f"ComfyUI HTTP error {e.response.status_code}: {error_detail}")

            # Check for specific error types
            if "node" in error_detail.lower() and "not found" in error_detail.lower():
                raise ComfyUIMissingNodeError(details=error_detail)
            elif "invalid" in error_detail.lower() or "parameter" in error_detail.lower():
                raise ComfyUIInvalidParametersError(details=error_detail)
            else:
                raise ComfyUIGenerationError(details=error_detail)

        except httpx.HTTPError as e:
            logger.error(f"ComfyUI HTTP error: {e}")
            raise ComfyUIConnectionError(
                message=f"HTTP error communicating with ComfyUI: {str(e)}",
                url=self.comfyui_url
            )

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

        Raises:
            ComfyUIConnectionError: If cannot connect to ComfyUI
        """
        try:
            response = await self.client.get(f"{self.comfyui_url}/history/{external_job_id}")
            response.raise_for_status()
            history = response.json()

            if external_job_id not in history:
                # Job might still be in queue
                logger.debug(f"Job {external_job_id} not in history yet, still processing")
                return GenerationStatus.PROCESSING

            job_info = history[external_job_id]

            # Check if job has completed
            if "outputs" in job_info:
                logger.info(f"Job {external_job_id} completed successfully")
                return GenerationStatus.COMPLETED

            # Check for errors
            if job_info.get("status", {}).get("status_str") == "error":
                logger.warning(f"Job {external_job_id} failed")
                return GenerationStatus.FAILED

            logger.debug(f"Job {external_job_id} still processing")
            return GenerationStatus.PROCESSING

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to ComfyUI for status check: {e}")
            raise ComfyUIConnectionError(url=self.comfyui_url)

        except httpx.TimeoutException as e:
            logger.warning(f"Status check timed out for job {external_job_id}")
            # On timeout, assume still processing rather than failing
            return GenerationStatus.PROCESSING

        except httpx.HTTPError as e:
            logger.error(f"HTTP error checking status: {e}")
            # For other HTTP errors, assume still processing
            return GenerationStatus.PROCESSING

    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Retrieve the result of a completed ComfyUI generation job.

        Args:
            external_job_id: ComfyUI prompt_id

        Returns:
            GenerationResult with video URL and metadata

        Raises:
            ComfyUIConnectionError: If cannot connect to ComfyUI
            ComfyUIOutputError: If no valid output was produced
        """
        try:
            response = await self.client.get(f"{self.comfyui_url}/history/{external_job_id}")
            response.raise_for_status()
            history = response.json()

            if external_job_id not in history:
                logger.debug(f"Job {external_job_id} not in history, still processing")
                return GenerationResult(
                    status=GenerationStatus.PROCESSING,
                    external_job_id=external_job_id
                )

            job_info = history[external_job_id]

            # Check for errors
            if job_info.get("status", {}).get("status_str") == "error":
                error_messages = job_info.get("status", {}).get("messages", [])
                error_detail = "; ".join([str(msg) for msg in error_messages]) if error_messages else "Unknown error"

                logger.error(f"ComfyUI job {external_job_id} failed: {error_detail}")

                # Try to determine error type from message
                error_lower = error_detail.lower()
                if "node" in error_lower and ("not found" in error_lower or "missing" in error_lower):
                    error_exception = ComfyUIMissingNodeError(details=error_detail)
                elif "timeout" in error_lower:
                    error_exception = ComfyUITimeoutError(message=error_detail)
                elif "parameter" in error_lower or "invalid" in error_lower:
                    error_exception = ComfyUIInvalidParametersError(details=error_detail)
                else:
                    error_exception = ComfyUIGenerationError(details=error_detail)

                return GenerationResult(
                    status=GenerationStatus.FAILED,
                    error_message=error_exception.message,
                    external_job_id=external_job_id,
                    metadata={"error_code": error_exception.error_code}
                )

            # Check if job has completed and get outputs
            if "outputs" not in job_info:
                logger.debug(f"Job {external_job_id} has no outputs yet, still processing")
                return GenerationResult(
                    status=GenerationStatus.PROCESSING,
                    external_job_id=external_job_id
                )

            outputs = job_info["outputs"]

            # Find video/image outputs
            video_url = None
            media_type = None
            for node_id, node_output in outputs.items():
                if "videos" in node_output or "gifs" in node_output:
                    # Get first video
                    media_list = node_output.get("videos", node_output.get("gifs", []))
                    if media_list:
                        filename = media_list[0]["filename"]
                        # Construct URL to retrieve the file
                        video_url = f"{self.comfyui_url}/view?filename={filename}&type=output"
                        media_type = "video"
                        logger.info(f"Found video output: {filename}")
                        break
                elif "images" in node_output:
                    # Fallback to images if no video
                    images = node_output["images"]
                    if images:
                        filename = images[0]["filename"]
                        video_url = f"{self.comfyui_url}/view?filename={filename}&type=output"
                        media_type = "image"
                        logger.info(f"Found image output: {filename}")
                        break

            if not video_url:
                logger.error(f"No video or image output found for job {external_job_id}")
                error_exception = ComfyUIOutputError()
                return GenerationResult(
                    status=GenerationStatus.FAILED,
                    error_message=error_exception.message,
                    external_job_id=external_job_id,
                    metadata={"error_code": error_exception.error_code}
                )

            job_data = self._jobs.get(external_job_id, {})

            logger.info(f"ComfyUI job {external_job_id} completed successfully")
            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                video_url=video_url,
                external_job_id=external_job_id,
                metadata={
                    "prompt": job_data.get("prompt", ""),
                    "model_params": job_data.get("model_params", {}),
                    "comfyui_outputs": outputs,
                    "media_type": media_type
                },
                completed_at=datetime.utcnow()
            )

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to ComfyUI to retrieve result: {e}")
            raise ComfyUIConnectionError(url=self.comfyui_url)

        except httpx.TimeoutException as e:
            logger.error(f"Timeout retrieving result for job {external_job_id}")
            raise ComfyUITimeoutError(timeout=int(self.request_timeout))

        except httpx.HTTPError as e:
            logger.error(f"HTTP error retrieving result: {e}")
            raise ComfyUIConnectionError(
                message=f"Failed to retrieve ComfyUI result: {str(e)}",
                url=self.comfyui_url
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
            logger.info(f"Cancelling ComfyUI job {external_job_id}")
            # ComfyUI's interrupt endpoint
            response = await self.client.post(f"{self.comfyui_url}/interrupt")
            response.raise_for_status()

            # Update local job status
            if external_job_id in self._jobs:
                self._jobs[external_job_id]["status"] = GenerationStatus.FAILED

            logger.info(f"Successfully cancelled job {external_job_id}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to cancel job {external_job_id}: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        logger.info("Closing ComfyUIAdapter HTTP client")
        await self.client.aclose()
