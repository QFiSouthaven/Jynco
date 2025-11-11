"""
Project model representing a user's video timeline.
"""
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """
    Project represents the top-level entity for a user's video timeline.
    It contains multiple segments that will be rendered into a final video.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="projects")
    segments = relationship(
        "Segment",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Segment.order_index"
    )
    render_jobs = relationship(
        "RenderJob",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="RenderJob.created_at.desc()"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, user_id={self.user_id})>"
