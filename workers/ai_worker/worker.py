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
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_db_context
from backend.models import Segment
from backend.models.segment import SegmentStatus
from backend.services import RabbitMQClient, RedisClient, S3Client
from adapters import VideoModelFactory
from adapters.exceptions import AdapterError, get_user_friendly_message
import pika.exceptions

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
        self.s3 = S3Client()
        self.queue_name = os.getenv("SEGMENT_QUEUE_NAME", "segment_generation")

        logger.info("AI Worker initialized")

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

            # Initiate video generation with better error handling
            logger.info(f"Initiating generation with {model_name} for segment {segment_id}")
            try:
                external_job_id = await adapter.initiate_generation(prompt, model_params)
            except AdapterError as e:
                # Adapter-specific error with error code
                logger.error(f"Adapter error initiating generation: {e.message}")
                self._handle_segment_failure(
                    segment_id=segment_id,
                    render_job_id=render_job_id,
                    error_message=e.message,
                    error_code=e.error_code,
                    is_retryable=e.is_retryable
                )
                return

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
                # Download video and upload to S3
                s3_url = await self._upload_to_s3(
                    video_url=result.video_url,
                    segment_id=segment_id,
                    render_job_id=render_job_id
                )

                # Update database
                with get_db_context() as db:
                    segment = db.query(Segment).filter(Segment.id == segment_id).first()
                    if segment:
                        segment.status = SegmentStatus.COMPLETED
                        segment.s3_asset_url = s3_url
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

                logger.info(f"Segment {segment_id} completed successfully. S3 URL: {s3_url}")

            else:
                # Handle failure
                error_msg = result.error_message or "Unknown error during generation"
                error_code = result.metadata.get("error_code") if result.metadata else None

                logger.error(f"Segment {segment_id} failed: {error_msg} (code: {error_code})")

                # Determine if error is retryable based on error code
                is_retryable = False
                if error_code:
                    error_info = get_user_friendly_message(error_code)
                    # Errors like connection issues and timeouts are retryable
                    is_retryable = error_code in ["COMFYUI_CONNECTION_ERROR", "COMFYUI_TIMEOUT", "COMFYUI_GENERATION_ERROR"]

                self._handle_segment_failure(
                    segment_id=segment_id,
                    render_job_id=render_job_id,
                    error_message=error_msg,
                    error_code=error_code,
                    is_retryable=is_retryable
                )

        except AdapterError as e:
            # Adapter-specific error with error code
            logger.error(f"Adapter error during processing: {e.message}", exc_info=True)
            self._handle_segment_failure(
                segment_id=segment_id,
                render_job_id=render_job_id,
                error_message=e.message,
                error_code=e.error_code,
                is_retryable=e.is_retryable
            )

        except TimeoutError as e:
            logger.error(f"Timeout processing segment {segment_id}: {e}")
            self._handle_segment_failure(
                segment_id=segment_id,
                render_job_id=render_job_id,
                error_message="Video generation timed out. The service may be overloaded.",
                error_code="COMFYUI_TIMEOUT",
                is_retryable=True
            )

        except Exception as e:
            logger.error(f"Unexpected error processing segment {segment_id}: {e}", exc_info=True)
            self._handle_segment_failure(
                segment_id=segment_id,
                render_job_id=render_job_id,
                error_message="An unexpected error occurred during video generation.",
                error_code="INTERNAL_ERROR",
                is_retryable=False
            )

    def _handle_segment_failure(
        self,
        segment_id: UUID,
        render_job_id: UUID,
        error_message: str,
        error_code: str = None,
        is_retryable: bool = False
    ):
        """
        Handle segment failure with proper error messaging.

        Args:
            segment_id: Segment UUID
            render_job_id: Render job UUID
            error_message: Error message
            error_code: Machine-readable error code
            is_retryable: Whether the error is retryable
        """
        logger.error(
            f"Segment {segment_id} failed: {error_message} "
            f"(code: {error_code}, retryable: {is_retryable})"
        )

        # Update database
        with get_db_context() as db:
            segment = db.query(Segment).filter(Segment.id == segment_id).first()
            if segment:
                segment.status = SegmentStatus.FAILED
                segment.error_message = error_message
                segment.error_code = error_code
                db.commit()

        # Update Redis
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

    async def _upload_to_s3(self, video_url: str, segment_id: UUID, render_job_id: UUID) -> str:
        """
        Download video from AI service and upload to S3.

        Args:
            video_url: URL of the generated video
            segment_id: Segment UUID
            render_job_id: Render job UUID

        Returns:
            S3 URL of the uploaded video
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
            # Generate S3 key
            # Get project_id from database
            with get_db_context() as db:
                segment = db.query(Segment).filter(Segment.id == segment_id).first()
                project_id = segment.project_id if segment else segment_id

            s3_key = self.s3.generate_segment_key(project_id, segment_id)

            # Upload to S3
            s3_url = self.s3.upload_file(tmp_path, s3_key, content_type="video/mp4")

            return s3_url

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

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
                asyncio.run(self.process_segment_task(message))
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                # Message will be requeued if not acknowledged
                raise

        logger.info(f"Connecting to RabbitMQ and starting consumer on queue: {self.queue_name}")
        self.rabbitmq.consume_messages(self.queue_name, callback)

    def run(self):
        """Start the worker and begin consuming messages with resilience."""
        logger.info(f"AI Worker starting. Listening on queue: {self.queue_name}")

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
    worker = AIWorker()
    worker.run()
