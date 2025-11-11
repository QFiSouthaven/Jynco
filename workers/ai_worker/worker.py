"""
AI Worker Service for video segment generation.
Consumes segment tasks from RabbitMQ and generates videos using AI models.
"""
import asyncio
import logging
import os
import sys
from uuid import UUID
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_db_context
from backend.models import Segment
from backend.models.segment import SegmentStatus
from backend.services import RabbitMQClient, RedisClient
from backend.services.storage_factory import create_storage_client
from adapters import VideoModelFactory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIWorker:
    """
    AI Worker that processes segment generation tasks.
    """

    def __init__(self):
        """Initialize the AI worker."""
        self.rabbitmq = RabbitMQClient()
        self.redis = RedisClient()
        self.storage = create_storage_client()
        self.queue_name = os.getenv("SEGMENT_QUEUE_NAME", "segment_generation")

        use_local = os.getenv("USE_LOCAL_STORAGE", "false").lower() in ("true", "1", "yes")
        storage_type = "Local Storage" if use_local else "S3"
        logger.info(f"AI Worker initialized with {storage_type}")

    async def process_segment_task(self, message: dict):
        """
        Process a single segment generation task.

        Args:
            message: Task message containing segment_id, render_job_id, prompt, model_params
        """
        segment_id = UUID(message["segment_id"])
        render_job_id = UUID(message["render_job_id"])
        prompt = message["prompt"]
        model_params = message["model_params"]

        logger.info(f"Processing segment {segment_id} for render job {render_job_id}")

        try:
            # Update status in Redis
            self.redis.set_segment_status(
                segment_id=segment_id,
                status=SegmentStatus.GENERATING.value,
                render_job_id=render_job_id
            )

            # Get model name from params (default to mock for testing)
            model_name = model_params.get("model", "mock-ai")

            # Create video model adapter
            adapter = VideoModelFactory.create(model_name)

            # Initiate video generation
            logger.info(f"Initiating generation with {model_name} for segment {segment_id}")
            external_job_id = await adapter.initiate_generation(prompt, model_params)

            # Update database with external job ID
            with get_db_context() as db:
                segment = db.query(Segment).filter(Segment.id == segment_id).first()
                if segment:
                    segment.external_job_id = external_job_id
                    db.commit()

            # Poll for completion
            logger.info(f"Polling for completion: external_job_id={external_job_id}")
            result = await self._poll_for_completion(adapter, external_job_id)

            if result.status.value == "completed" and result.video_url:
                # Download video and upload to storage
                storage_url = await self._upload_to_storage(
                    video_url=result.video_url,
                    segment_id=segment_id,
                    render_job_id=render_job_id
                )

                # Update database
                with get_db_context() as db:
                    segment = db.query(Segment).filter(Segment.id == segment_id).first()
                    if segment:
                        segment.status = SegmentStatus.COMPLETED
                        segment.s3_asset_url = storage_url  # Note: field name kept for compatibility
                        db.commit()

                # Update Redis
                self.redis.set_segment_status(
                    segment_id=segment_id,
                    status=SegmentStatus.COMPLETED.value,
                    render_job_id=render_job_id
                )

                # Increment render job progress
                self.redis.increment_render_job_progress(render_job_id)

                # Publish completion event
                self.rabbitmq.publish_segment_completed_event(
                    segment_id=segment_id,
                    render_job_id=render_job_id
                )

                logger.info(f"Segment {segment_id} completed successfully. Storage URL: {storage_url}")

            else:
                # Handle failure
                error_msg = result.error_message or "Unknown error during generation"
                logger.error(f"Segment {segment_id} failed: {error_msg}")

                with get_db_context() as db:
                    segment = db.query(Segment).filter(Segment.id == segment_id).first()
                    if segment:
                        segment.status = SegmentStatus.FAILED
                        segment.error_message = error_msg
                        db.commit()

                self.redis.set_segment_status(
                    segment_id=segment_id,
                    status=SegmentStatus.FAILED.value,
                    render_job_id=render_job_id
                )

        except Exception as e:
            logger.error(f"Error processing segment {segment_id}: {e}", exc_info=True)

            # Update status to failed
            with get_db_context() as db:
                segment = db.query(Segment).filter(Segment.id == segment_id).first()
                if segment:
                    segment.status = SegmentStatus.FAILED
                    segment.error_message = str(e)
                    db.commit()

            self.redis.set_segment_status(
                segment_id=segment_id,
                status=SegmentStatus.FAILED.value,
                render_job_id=render_job_id
            )

    async def _poll_for_completion(self, adapter, external_job_id: str, max_attempts: int = 180):
        """
        Poll the AI model for job completion.

        Args:
            adapter: Video model adapter
            external_job_id: External job ID
            max_attempts: Maximum polling attempts (default 180 = 3 minutes at 1s intervals)

        Returns:
            GenerationResult
        """
        for attempt in range(max_attempts):
            result = await adapter.get_result(external_job_id)

            if result.status.value in ["completed", "failed"]:
                return result

            await asyncio.sleep(1)

        # Timeout
        raise TimeoutError(f"Generation timed out after {max_attempts} seconds")

    async def _upload_to_storage(self, video_url: str, segment_id: UUID, render_job_id: UUID) -> str:
        """
        Download video from AI service and upload to storage (S3 or local).

        Args:
            video_url: URL of the generated video
            segment_id: Segment UUID
            render_job_id: Render job UUID

        Returns:
            Storage URL of the uploaded video
        """
        import httpx
        import tempfile

        # For mock adapter, the video_url might be fake
        # In production, download the video
        if video_url.startswith("https://mock-cdn"):
            # Mock case: create a dummy file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(b"MOCK_VIDEO_DATA")
                tmp_path = tmp.name
        else:
            # Download from AI service
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url)
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name

        try:
            # Generate storage key
            # Get project_id from database
            with get_db_context() as db:
                segment = db.query(Segment).filter(Segment.id == segment_id).first()
                project_id = segment.project_id if segment else segment_id

            storage_key = self.storage.generate_segment_key(project_id, segment_id)

            # Upload to storage
            storage_url = self.storage.upload_file(tmp_path, storage_key, content_type="video/mp4")

            return storage_url

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    def run(self):
        """Start the worker and begin consuming messages."""
        logger.info(f"AI Worker starting. Listening on queue: {self.queue_name}")

        def callback(message: dict):
            """Callback for RabbitMQ messages."""
            asyncio.run(self.process_segment_task(message))

        try:
            self.rabbitmq.consume_messages(self.queue_name, callback)
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
        finally:
            self.rabbitmq.close()


if __name__ == "__main__":
    worker = AIWorker()
    worker.run()
