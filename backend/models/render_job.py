"""
RenderJob model representing a specific request to render a project.
"""
from sqlalchemy import Column, String, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from .base import Base, TimestampMixin


class RenderJobStatus(str, enum.Enum):
    """Status enumeration for render jobs."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPOSITING = "compositing"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderJob(Base, TimestampMixin):
    """
    RenderJob represents a specific request to render a project.
    It captures a snapshot of the project's segments at the time of request
    and tracks the overall progress of generating the final composite video.
    """

    __tablename__ = "render_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Status tracking
    status = Column(SQLEnum(RenderJobStatus), default=RenderJobStatus.PENDING, nullable=False, index=True)

    # Progress tracking
    segments_total = Column(Integer, nullable=False, default=0)
    segments_completed = Column(Integer, nullable=False, default=0)

    # Snapshot of segment IDs at time of render request (for idempotency and tracking)
    segment_ids = Column(JSONB, nullable=False, default=[])

    # Final output
    s3_final_url = Column(String(512), nullable=True)
    error_message = Column(String(1000), nullable=True)

    # Metadata
    render_metadata = Column(JSONB, nullable=True, default={})  # Store duration, resolution, etc.

    # Relationships
    project = relationship("Project", back_populates="render_jobs")

    def __repr__(self):
        return f"<RenderJob(id={self.id}, project_id={self.project_id}, status={self.status}, progress={self.segments_completed}/{self.segments_total})>"

    @property
    def progress_percentage(self) -> float:
        """Calculate render job progress as percentage."""
        if self.segments_total == 0:
            return 0.0
        return (self.segments_completed / self.segments_total) * 100

    class Config:
        use_enum_values = True
