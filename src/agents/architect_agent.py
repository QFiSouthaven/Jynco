"""
Architect Agent

The central coordinator that orchestrates the entire video generation pipeline.
Manages job dispatch, monitors progress, and implements retry logic.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .base_agent import BaseAgent
from ..schemas.storyboard_types import ClipStatus


class ArchitectAgent(BaseAgent):
    """
    The Architect Agent is responsible for:
    - Strategic planning of generation pipeline
    - Dispatching jobs to worker agents
    - Monitoring job status and implementing retry logic
    - Submitting render jobs to the priority queue
    - Ensuring graceful degradation on failures
    """

    def __init__(self, agent_id: str = "architect_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay_base = config.get("retry_delay_base", 2.0)  # Exponential backoff base

        # Agent dependencies (injected)
        self.storyboard_agent = None
        self.motion_agent = None
        self.render_agent = None
        self.job_queue = None

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute high-level orchestration task.

        Supported operations:
        - generate_project: Generate all clips in a project
        - generate_clip: Generate a single clip
        - render_preview: Create a quick preview render
        - render_final: Create final export

        Args:
            task: {
                "operation": "generate_project|generate_clip|render_preview|render_final",
                "projectId": "proj_123",
                "clipId": "clip_abc",  # For single clip operations
                "priority": "preview|final"  # For render operations
            }
        """
        try:
            self.validate_task(task, ["operation"])
            operation = task["operation"]

            operations = {
                "generate_project": self._generate_project,
                "generate_clip": self._generate_clip,
                "render_preview": self._render_preview,
                "render_final": self._render_final,
            }

            if operation not in operations:
                raise ValueError(f"Unknown operation: {operation}")

            return await operations[operation](task)

        except Exception as e:
            return await self.handle_error(e, task)

    async def _generate_project(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all clips in a project.

        This is the main pipeline orchestration method.
        """
        self.validate_task(task, ["projectId"])
        project_id = task["projectId"]

        self.logger.info(f"Starting project generation: {project_id}")

        # Step 1: Read storyboard
        storyboard_result = await self.storyboard_agent.execute({
            "operation": "read",
            "data": {}
        })

        if not storyboard_result.get("success"):
            return storyboard_result

        storyboard = storyboard_result["storyboard"]
        timeline = storyboard.get("timeline", [])

        # Step 2: Get pending clips
        pending_clips = [clip for clip in timeline if clip.get("status") == "pending"]

        self.logger.info(f"Found {len(pending_clips)} pending clips")

        # Step 3: Generate each clip with retry logic
        results = []
        for clip in pending_clips:
            result = await self._generate_clip_with_retry({
                "clipId": clip["clipId"],
                "projectId": project_id
            })
            results.append(result)

        # Step 4: Summarize results
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful

        return {
            "success": failed == 0,
            "projectId": project_id,
            "totalClips": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    async def _generate_clip(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single clip without retry logic."""
        self.validate_task(task, ["clipId"])
        clip_id = task["clipId"]

        self.logger.info(f"Generating clip: {clip_id}")

        # Step 1: Get clip details from storyboard
        clip_result = await self.storyboard_agent.execute({
            "operation": "get_clip",
            "data": {"clipId": clip_id}
        })

        if not clip_result.get("success"):
            return clip_result

        clip = clip_result["clip"]

        # Step 2: Update status to generating
        job_id = f"job_motion_{uuid.uuid4().hex[:12]}"
        await self.storyboard_agent.execute({
            "operation": "update_clip",
            "data": {
                "clipId": clip_id,
                "status": "generating",
                "jobId": job_id
            }
        })

        # Step 3: Dispatch to Motion Agent
        try:
            motion_result = await self.motion_agent.execute({
                "clipId": clip_id,
                "sourceImage": clip.get("sourceImage"),
                "motionPrompt": clip.get("motionPrompt"),
                "duration": clip.get("duration", 3.0)
            })

            if motion_result.get("success"):
                # Step 4: Update storyboard with success
                await self.storyboard_agent.execute({
                    "operation": "update_clip",
                    "data": {
                        "clipId": clip_id,
                        "status": "completed",
                        "sourceFile": motion_result["outputFile"],
                        "cacheKey": motion_result.get("cacheKey")
                    }
                })

                self.logger.info(f"Successfully generated clip: {clip_id}")
                return motion_result
            else:
                raise Exception(motion_result.get("error", "Unknown error"))

        except Exception as e:
            # Step 5: Update storyboard with failure
            await self.storyboard_agent.execute({
                "operation": "update_clip",
                "data": {
                    "clipId": clip_id,
                    "status": "failed",
                    "errorMessage": str(e)
                }
            })

            self.logger.error(f"Failed to generate clip {clip_id}: {str(e)}")
            return {
                "success": False,
                "clipId": clip_id,
                "error": str(e)
            }

    async def _generate_clip_with_retry(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a clip with exponential backoff retry logic.

        Implements resilience pattern:
        1. Attempt generation
        2. If failure, retry with exponential backoff
        3. After max retries, mark as failed but preserve project
        """
        clip_id = task["clipId"]
        attempt = 0

        while attempt < self.max_retries:
            result = await self._generate_clip(task)

            if result.get("success"):
                return result

            # Exponential backoff
            attempt += 1
            if attempt < self.max_retries:
                delay = self.retry_delay_base ** attempt
                self.logger.warning(
                    f"Retry {attempt}/{self.max_retries} for clip {clip_id} "
                    f"after {delay}s delay"
                )
                await asyncio.sleep(delay)

        # All retries exhausted
        self.logger.error(f"All retries exhausted for clip {clip_id}")
        return {
            "success": False,
            "clipId": clip_id,
            "error": "Max retries exceeded",
            "attempts": self.max_retries
        }

    async def _render_preview(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a preview render job (high priority).

        Preview renders are:
        - Lower resolution
        - Fast processing
        - High priority in queue
        - Interactive feedback for user
        """
        self.validate_task(task, ["projectId"])
        project_id = task["projectId"]

        job_id = f"job_render_{uuid.uuid4().hex[:12]}"

        render_job = {
            "jobId": job_id,
            "projectId": project_id,
            "priority": "preview",
            "renderSettings": {
                "resolution": "720p",
                "quality": "medium",
                "fast_encoding": True
            }
        }

        if self.job_queue:
            await self.job_queue.submit(render_job, priority="high")
            self.logger.info(f"Submitted preview render job: {job_id}")
        else:
            self.logger.warning("Job queue not configured, cannot submit render job")

        return {
            "success": True,
            "jobId": job_id,
            "projectId": project_id,
            "priority": "preview"
        }

    async def _render_final(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a final export render job (normal priority).

        Final renders are:
        - Full resolution
        - High quality encoding
        - Normal priority in queue
        - Background processing
        """
        self.validate_task(task, ["projectId"])
        project_id = task["projectId"]

        job_id = f"job_render_{uuid.uuid4().hex[:12]}"

        render_job = {
            "jobId": job_id,
            "projectId": project_id,
            "priority": "final",
            "renderSettings": {
                "resolution": "1080p",
                "quality": "high",
                "fast_encoding": False
            }
        }

        if self.job_queue:
            await self.job_queue.submit(render_job, priority="normal")
            self.logger.info(f"Submitted final render job: {job_id}")
        else:
            self.logger.warning("Job queue not configured, cannot submit render job")

        return {
            "success": True,
            "jobId": job_id,
            "projectId": project_id,
            "priority": "final"
        }

    # Dependency injection methods
    def set_storyboard_agent(self, agent):
        """Inject storyboard agent dependency."""
        self.storyboard_agent = agent

    def set_motion_agent(self, agent):
        """Inject motion agent dependency."""
        self.motion_agent = agent

    def set_render_agent(self, agent):
        """Inject render agent dependency."""
        self.render_agent = agent

    def set_job_queue(self, queue):
        """Inject job queue dependency."""
        self.job_queue = queue
