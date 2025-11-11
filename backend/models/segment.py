"""
Segment model representing individual video clips in a timeline.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from .base import Base, TimestampMixin


class SegmentStatus(str, enum.Enum):
    """Status enumeration for segments."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Segment(Base, TimestampMixin):
    """
    Segment represents a single, atomic video clip in a timeline.
    Each segment has a prompt, model parameters, and tracks its generation status.
    """

    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Sequence and content
    order_index = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)

    # Model configuration stored as JSONB for flexibility
    # Example: {"model": "runway-gen3", "duration": 5, "aspect_ratio": "16:9", "resolution": "1080p"}
    model_params = Column(JSONB, nullable=False, default={})

    # Generation status and results
    status = Column(SQLEnum(SegmentStatus), default=SegmentStatus.PENDING, nullable=False, index=True)
    s3_asset_url = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)

    # External AI model tracking
    external_job_id = Column(String(255), nullable=True)  # Track job ID from external AI service

    # Relationships
    project = relationship("Project", back_populates="segments")

    def __repr__(self):
        return f"<Segment(id={self.id}, project_id={self.project_id}, order_index={self.order_index}, status={self.status})>"

    class Config:
        use_enum_values = True
