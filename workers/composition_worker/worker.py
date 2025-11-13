"""
Composition Worker Service for stitching video segments.
Listens for segment completion events and composes final videos using FFMPEG.
"""
import asyncio
import logging
import os
import sys
import subprocess
import tempfile
from uuid import UUID
from pathlib import Path
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_db_context
from backend.models import RenderJob, Segment
from backend.models.render_job import RenderJobStatus
from backend.services import RabbitMQClient, RedisClient, S3Client, LocalStorageClient
import pika.exceptions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompositionWorker:
    """
    Composition Worker that stitches video segments into final videos.
    """

    def __init__(self):
        """Initialize the composition worker."""
        self.rabbitmq = RabbitMQClient()
        self.redis = RedisClient()

        # Use local storage if AWS credentials are not configured
        aws_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        use_local_storage = not aws_key or aws_key.strip() == ""

        if use_local_storage:
            self.storage = LocalStorageClient()
            logger.info("Using LocalStorageClient (AWS credentials not configured)")
        else:
            self.storage = S3Client()
            logger.info("Using S3Client")

        self.queue_name = os.getenv("COMPOSITION_QUEUE_NAME", "video_composition")

        logger.info("Composition Worker initialized")

    def process_composition_task(self, message: dict):
        """
        Process a video composition task.

        Args:
            message: Task message containing render_job_id, project_id, segment_ids
        """
        render_job_id = UUID(message["render_job_id"])
        project_id = UUID(message["project_id"])
        segment_ids = [UUID(sid) for sid in message["segment_ids"]]

        logger.info(f"Processing composition for render job {render_job_id}")

        try:
            # Update status
            with get_db_context() as db:
                render_job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
                if render_job:
                    render_job.status = RenderJobStatus.COMPOSITING
                    db.commit()

            self.redis.set_render_job_progress(
                render_job_id=render_job_id,
                segments_total=len(segment_ids),
                segments_completed=len(segment_ids),
                status=RenderJobStatus.COMPOSITING.value
            )

            # Download all segment videos from S3
            segment_files = self._download_segments(segment_ids)

            if not segment_files:
                raise Exception("No segment files to compose")

            # Compose video using FFMPEG
            logger.info(f"Composing {len(segment_files)} segments")
            final_video_path = self._compose_video(segment_files)

            # Upload final video to storage (S3 or local)
            storage_key = self.storage.generate_composition_key(project_id, render_job_id)
            storage_url = self.storage.upload_file(final_video_path, storage_key, content_type="video/mp4")

            # Update database
            with get_db_context() as db:
                render_job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
                if render_job:
                    render_job.status = RenderJobStatus.COMPLETED
                    render_job.s3_final_url = storage_url
                    db.commit()

            # Update Redis
            self.redis.set_render_job_progress(
                render_job_id=render_job_id,
                segments_total=len(segment_ids),
                segments_completed=len(segment_ids),
                status=RenderJobStatus.COMPLETED.value
            )

            logger.info(f"Render job {render_job_id} completed. Final video: {s3_url}")

            # Cleanup
            self._cleanup_files(segment_files + [final_video_path])

        except Exception as e:
            logger.error(f"Error composing render job {render_job_id}: {e}", exc_info=True)

            # Update status to failed
            with get_db_context() as db:
                render_job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
                if render_job:
                    render_job.status = RenderJobStatus.FAILED
                    render_job.error_message = str(e)
                    db.commit()

            self.redis.set_render_job_progress(
                render_job_id=render_job_id,
                segments_total=len(segment_ids),
                segments_completed=len(segment_ids),
                status=RenderJobStatus.FAILED.value
            )

    def _download_segments(self, segment_ids: list[UUID]) -> list[str]:
        """
        Download segment videos from S3.

        Args:
            segment_ids: List of segment UUIDs in order

        Returns:
            List of local file paths
        """
        segment_files = []

        with get_db_context() as db:
            for segment_id in segment_ids:
                segment = db.query(Segment).filter(Segment.id == segment_id).first()

                if not segment or not segment.s3_asset_url:
                    logger.warning(f"Segment {segment_id} not found or missing asset URL")
                    continue

                asset_url = segment.s3_asset_url

                # Handle local file URLs
                if asset_url.startswith("file://"):
                    # Local storage - extract path and use directly or copy to temp
                    local_path = asset_url.replace("file://", "")
                    if Path(local_path).exists():
                        segment_files.append(local_path)
                        logger.info(f"Using local segment file: {local_path}")
                    else:
                        logger.error(f"Local file not found: {local_path}")
                    continue

                # Handle S3 URLs
                # URL format: https://bucket.s3.region.amazonaws.com/key
                if hasattr(self.storage, 'bucket_name'):
                    storage_key = asset_url.split(f"{self.storage.bucket_name}.s3.")[-1].split("/", 1)[-1] if "/" in asset_url else None
                else:
                    logger.error(f"Cannot parse storage key from URL: {asset_url}")
                    continue

                if not storage_key:
                    logger.error(f"Could not extract storage key from URL: {asset_url}")
                    continue

                # Download to temp file
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tmp_file.close()

                try:
                    self.storage.download_file(storage_key, tmp_file.name)
                    segment_files.append(tmp_file.name)
                    logger.info(f"Downloaded segment {segment_id} to {tmp_file.name}")
                except Exception as e:
                    logger.error(f"Failed to download segment {segment_id}: {e}")

        return segment_files

    def _compose_video(self, segment_files: list[str]) -> str:
        """
        Compose video segments using FFMPEG.

        Args:
            segment_files: List of video file paths in order

        Returns:
            Path to the final composed video
        """
        # Create a concat file for FFMPEG
        concat_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt")

        for file_path in segment_files:
            concat_file.write(f"file '{file_path}'\n")

        concat_file.close()

        # Output file
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_file.close()

        try:
            # Run FFMPEG to concatenate videos
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file.name,
                "-c", "copy",
                "-y",  # Overwrite output file
                output_file.name
            ]

            logger.info(f"Running FFMPEG: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"FFMPEG completed successfully. Output: {output_file.name}")

            return output_file.name

        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG error: {e.stderr}")
            raise Exception(f"FFMPEG failed: {e.stderr}")

        finally:
            # Clean up concat file
            Path(concat_file.name).unlink(missing_ok=True)

    def _cleanup_files(self, file_paths: list[str]):
        """
        Clean up temporary files.

        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                Path(file_path).unlink(missing_ok=True)
                logger.debug(f"Deleted temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {e}")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((pika.exceptions.AMQPConnectionError, ConnectionError)),
        reraise=True
    )
    def _connect_and_consume(self):
        """Connect to RabbitMQ and start consuming with retry logic."""
        def callback(message: dict):
            """Callback for RabbitMQ messages with error handling."""
            try:
                self.process_composition_task(message)
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                # Message will be requeued if not acknowledged
                raise

        logger.info(f"Connecting to RabbitMQ and starting consumer on queue: {self.queue_name}")
        self.rabbitmq.consume_messages(self.queue_name, callback)

    def run(self):
        """Start the worker and begin consuming messages with resilience."""
        logger.info(f"Composition Worker starting. Listening on queue: {self.queue_name}")

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                self._connect_and_consume()
            except KeyboardInterrupt:
                logger.info("Worker stopped by user")
                break
            except (pika.exceptions.AMQPConnectionError, ConnectionError) as e:
                retry_count += 1
                wait_time = min(2 ** retry_count, 60)
                logger.error(
                    f"Connection error (attempt {retry_count}/{max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                if retry_count < max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Exiting.")
                    raise
            except Exception as e:
                logger.error(f"Unexpected worker error: {e}", exc_info=True)
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
                else:
                    raise
            finally:
                try:
                    self.rabbitmq.close()
                except:
                    pass


if __name__ == "__main__":
    worker = CompositionWorker()
    worker.run()
