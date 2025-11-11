"""
Render Agent

Stateless worker that pulls jobs from the queue and renders final videos.
Wraps FFmpeg for video encoding and composition.
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import subprocess

from .base_agent import BaseAgent


class RenderAgent(BaseAgent):
    """
    The Render Agent is responsible for:
    - Pulling render jobs from the priority queue
    - Composing timeline clips into final video
    - Applying effects, transitions, and overlays
    - Encoding with FFmpeg according to output settings
    - Operating as a stateless worker (can be scaled horizontally)
    """

    def __init__(self, agent_id: str = "render_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.ffmpeg_path = config.get("ffmpeg_path", "ffmpeg")
        self.output_dir = Path(config.get("output_dir", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute render job.

        Args:
            task: {
                "jobId": "job_render_xyz",
                "projectId": "proj_123",
                "storyboard": {...},  # Full storyboard data
                "renderSettings": {
                    "resolution": "1080p",
                    "quality": "high",
                    "fast_encoding": false
                }
            }

        Returns:
            {
                "success": true,
                "jobId": "job_render_xyz",
                "outputFile": "/path/to/final_video.mp4",
                "renderTime": 45.2,
                "fileSize": 12345678
            }
        """
        try:
            self.validate_task(task, ["jobId", "projectId", "storyboard"])

            job_id = task["jobId"]
            project_id = task["projectId"]
            storyboard = task["storyboard"]
            render_settings = task.get("renderSettings", {})

            self.logger.info(f"Starting render job: {job_id}")

            # Step 1: Validate all clips are ready
            validation_result = self._validate_clips(storyboard)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid clips: {validation_result['errors']}")

            # Step 2: Generate FFmpeg command
            ffmpeg_cmd = self._build_ffmpeg_command(storyboard, render_settings, project_id)

            # Step 3: Execute render
            output_file = self.output_dir / f"{project_id}_final.mp4"
            render_result = await self._execute_render(ffmpeg_cmd, output_file)

            if render_result["success"]:
                self.logger.info(f"Render completed: {job_id}")
                return {
                    "success": True,
                    "jobId": job_id,
                    "projectId": project_id,
                    "outputFile": str(output_file),
                    "renderTime": render_result["duration"],
                    "fileSize": output_file.stat().st_size
                }
            else:
                raise Exception(f"Render failed: {render_result['error']}")

        except Exception as e:
            return await self.handle_error(e, task)

    def _validate_clips(self, storyboard: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that all clips are ready for rendering.

        Checks:
        - All clips have status 'completed'
        - All source files exist
        - No failed clips in timeline
        """
        timeline = storyboard.get("timeline", [])
        errors = []

        for clip in timeline:
            clip_id = clip.get("clipId")
            status = clip.get("status")
            source_file = clip.get("sourceFile")

            if status != "completed":
                errors.append(f"Clip {clip_id} not completed (status: {status})")

            if not source_file or not Path(source_file).exists():
                errors.append(f"Clip {clip_id} source file not found: {source_file}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "clipCount": len(timeline)
        }

    def _build_ffmpeg_command(self, storyboard: Dict[str, Any],
                             render_settings: Dict[str, Any],
                             project_id: str) -> list:
        """
        Build FFmpeg command for rendering.

        This is a simplified version. Production would handle:
        - Complex filter graphs for transitions
        - Audio mixing
        - Text overlays
        - Color grading
        """
        timeline = storyboard.get("timeline", [])
        output_settings = storyboard.get("outputSettings", {})

        # Extract settings
        resolution = render_settings.get("resolution", "1080p")
        quality = render_settings.get("quality", "high")
        fast_encoding = render_settings.get("fast_encoding", False)

        # Build input list
        inputs = []
        for clip in timeline:
            source_file = clip.get("sourceFile")
            if source_file:
                inputs.extend(["-i", source_file])

        # Build filter complex for concatenation
        filter_complex = f"concat=n={len(timeline)}:v=1:a=0[outv]"

        # Encoding settings
        codec = output_settings.get("codec", "h264")
        preset = "ultrafast" if fast_encoding else "slow"

        output_file = str(self.output_dir / f"{project_id}_final.mp4")

        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output file
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", self._get_codec_name(codec),
            "-preset", preset,
            "-crf", self._get_crf(quality),
            output_file
        ]

        return cmd

    def _get_codec_name(self, codec: str) -> str:
        """Map codec name to FFmpeg codec."""
        codec_map = {
            "h264": "libx264",
            "h265": "libx265",
            "vp9": "libvpx-vp9",
            "av1": "libaom-av1"
        }
        return codec_map.get(codec, "libx264")

    def _get_crf(self, quality: str) -> str:
        """Get CRF value based on quality setting."""
        crf_map = {
            "low": "28",
            "medium": "23",
            "high": "18",
            "ultra": "15"
        }
        return crf_map.get(quality, "23")

    async def _execute_render(self, ffmpeg_cmd: list, output_file: Path) -> Dict[str, Any]:
        """
        Execute FFmpeg render command asynchronously.

        Args:
            ffmpeg_cmd: FFmpeg command as list
            output_file: Output file path

        Returns:
            {
                "success": true/false,
                "duration": 12.5,
                "error": "..." (if failed)
            }
        """
        import time
        start_time = time.time()

        try:
            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            duration = time.time() - start_time

            if process.returncode == 0:
                self.logger.info(f"Render completed in {duration:.2f}s")
                return {
                    "success": True,
                    "duration": duration
                }
            else:
                error_msg = stderr.decode('utf-8')
                self.logger.error(f"FFmpeg error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": duration
                }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "duration": duration
            }

    async def start_worker(self, job_queue, storyboard_agent):
        """
        Start worker loop that pulls jobs from queue.

        This method runs continuously, pulling and processing render jobs.
        Designed to be run as a background worker.

        Args:
            job_queue: Job queue to pull from
            storyboard_agent: Storyboard agent for reading project state
        """
        self.logger.info(f"Starting render worker: {self.agent_id}")

        while True:
            try:
                # Pull job from queue (blocking with timeout)
                job = await job_queue.pull(timeout=30)

                if job:
                    self.logger.info(f"Pulled job: {job.get('jobId')}")

                    # Read current storyboard
                    storyboard_result = await storyboard_agent.execute({
                        "operation": "read",
                        "data": {}
                    })

                    if storyboard_result.get("success"):
                        job["storyboard"] = storyboard_result["storyboard"]

                        # Execute render
                        result = await self.execute(job)

                        if result.get("success"):
                            # Mark job as complete in queue
                            await job_queue.complete(job["jobId"])
                        else:
                            # Mark job as failed
                            await job_queue.fail(job["jobId"], result.get("error"))

                await asyncio.sleep(1)  # Brief pause between polls

            except Exception as e:
                self.logger.error(f"Worker error: {str(e)}", exc_info=True)
                await asyncio.sleep(5)  # Longer pause on error
