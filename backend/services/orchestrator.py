"""
Orchestrator service for managing render jobs and dispatching tasks.
"""
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from models import Project, Segment, RenderJob
from models.segment import SegmentStatus
from models.render_job import RenderJobStatus
from services.rabbitmq_client import RabbitMQClient
from services.redis_client import RedisClient

logger = logging.getLogger(__name__)


class RenderOrchestrator:
    """
    Orchestrates the rendering of video projects.
    Implements intelligent task dispatching to only regenerate modified segments.
    """

    def __init__(
        self,
        rabbitmq_client: RabbitMQClient,
        redis_client: RedisClient
    ):
        """
        Initialize the orchestrator.

        Args:
            rabbitmq_client: RabbitMQ client for task publishing
            redis_client: Redis client for state management
        """
        self.rabbitmq = rabbitmq_client
        self.redis = redis_client

    def create_render_job(
        self,
        db: Session,
        project_id: UUID
    ) -> RenderJob:
        """
        Create a new render job for a project.
        Implements intelligent segment comparison to only regenerate modified segments.

        Args:
            db: Database session
            project_id: UUID of the project to render

        Returns:
            Created RenderJob

        Raises:
            ValueError: If project not found or has no segments
        """
        # Fetch project with segments
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if not project.segments:
            raise ValueError(f"Project {project_id} has no segments")

        # Get the last render job to compare segments
        last_render_job = (
            db.query(RenderJob)
            .filter(RenderJob.project_id == project_id)
            .filter(RenderJob.status == RenderJobStatus.COMPLETED)
            .order_by(RenderJob.created_at.desc())
            .first()
        )

        # Determine which segments need regeneration
        segments_to_generate = self._identify_segments_to_regenerate(
            current_segments=project.segments,
            last_render_job=last_render_job
        )

        # Create new render job
        render_job = RenderJob(
            project_id=project_id,
            status=RenderJobStatus.PENDING,
            segments_total=len(segments_to_generate),
            segments_completed=0,
            segment_ids=[str(seg.id) for seg in project.segments]
        )

        db.add(render_job)
        db.commit()
        db.refresh(render_job)

        # Initialize progress tracking in Redis
        self.redis.set_render_job_progress(
            render_job_id=render_job.id,
            segments_total=render_job.segments_total,
            segments_completed=0,
            status=RenderJobStatus.PROCESSING.value
        )

        # Update render job status
        render_job.status = RenderJobStatus.PROCESSING
        db.commit()

        # Dispatch segment generation tasks
        for segment in segments_to_generate:
            self._dispatch_segment_task(db, segment, render_job.id)

        logger.info(
            f"Created render job {render_job.id} for project {project_id}. "
            f"Dispatching {len(segments_to_generate)} segment tasks."
        )

        return render_job

    def _identify_segments_to_regenerate(
        self,
        current_segments: List[Segment],
        last_render_job: RenderJob | None
    ) -> List[Segment]:
        """
        Identify which segments need to be regenerated.
        Only regenerates segments that are new or have been modified.

        Args:
            current_segments: Current segments in the project
            last_render_job: Last completed render job (or None)

        Returns:
            List of segments that need regeneration
        """
        if last_render_job is None:
            # First render - generate all segments
            return [seg for seg in current_segments if seg.status != SegmentStatus.COMPLETED]

        # Get IDs of previously rendered segments
        last_segment_ids = set(last_render_job.segment_ids)

        segments_to_generate = []
        for segment in current_segments:
            # Regenerate if:
            # 1. Segment is new (not in last render)
            # 2. Segment has not been completed yet
            # 3. Segment has no S3 asset URL
            if (
                str(segment.id) not in last_segment_ids
                or segment.status != SegmentStatus.COMPLETED
                or not segment.s3_asset_url
            ):
                segments_to_generate.append(segment)

        return segments_to_generate

    def _dispatch_segment_task(
        self,
        db: Session,
        segment: Segment,
        render_job_id: UUID
    ):
        """
        Dispatch a segment generation task to the worker queue.

        Args:
            db: Database session
            segment: Segment to generate
            render_job_id: UUID of the render job
        """
        # Update segment status
        segment.status = SegmentStatus.GENERATING
        db.commit()

        # Update Redis
        self.redis.set_segment_status(
            segment_id=segment.id,
            status=SegmentStatus.GENERATING.value,
            render_job_id=render_job_id
        )

        # Publish task to RabbitMQ
        self.rabbitmq.publish_segment_task(
            segment_id=segment.id,
            render_job_id=render_job_id,
            prompt=segment.prompt,
            model_params=segment.model_params
        )

        logger.info(f"Dispatched segment task: segment_id={segment.id}")

    def handle_segment_completion(
        self,
        db: Session,
        segment_id: UUID,
        render_job_id: UUID,
        s3_asset_url: str
    ):
        """
        Handle completion of a segment generation task.

        Args:
            db: Database session
            segment_id: UUID of the completed segment
            render_job_id: UUID of the render job
            s3_asset_url: S3 URL of the generated video
        """
        # Update segment
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if segment:
            segment.status = SegmentStatus.COMPLETED
            segment.s3_asset_url = s3_asset_url
            db.commit()

        # Update render job progress
        render_job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
        if render_job:
            render_job.segments_completed += 1
            db.commit()

            # Update Redis
            self.redis.increment_render_job_progress(render_job_id)

            # Check if all segments are complete
            if render_job.segments_completed >= render_job.segments_total:
                self._trigger_composition(db, render_job)

        # Publish completion event
        self.rabbitmq.publish_segment_completed_event(
            segment_id=segment_id,
            render_job_id=render_job_id
        )

        logger.info(f"Segment {segment_id} completed for render job {render_job_id}")

    def _trigger_composition(self, db: Session, render_job: RenderJob):
        """
        Trigger video composition when all segments are complete.

        Args:
            db: Database session
            render_job: RenderJob to compose
        """
        render_job.status = RenderJobStatus.COMPOSITING
        db.commit()

        # Update Redis
        self.redis.set_render_job_progress(
            render_job_id=render_job.id,
            segments_total=render_job.segments_total,
            segments_completed=render_job.segments_completed,
            status=RenderJobStatus.COMPOSITING.value
        )

        # Publish composition task
        segment_ids = [UUID(sid) for sid in render_job.segment_ids]
        self.rabbitmq.publish_composition_task(
            render_job_id=render_job.id,
            project_id=render_job.project_id,
            segment_ids=segment_ids
        )

        logger.info(f"Triggered composition for render job {render_job.id}")

    def handle_composition_completion(
        self,
        db: Session,
        render_job_id: UUID,
        s3_final_url: str
    ):
        """
        Handle completion of video composition.

        Args:
            db: Database session
            render_job_id: UUID of the render job
            s3_final_url: S3 URL of the final video
        """
        render_job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
        if render_job:
            render_job.status = RenderJobStatus.COMPLETED
            render_job.s3_final_url = s3_final_url
            db.commit()

            # Update Redis
            self.redis.set_render_job_progress(
                render_job_id=render_job.id,
                segments_total=render_job.segments_total,
                segments_completed=render_job.segments_completed,
                status=RenderJobStatus.COMPLETED.value
            )

            logger.info(f"Render job {render_job_id} completed. Final video: {s3_final_url}")
