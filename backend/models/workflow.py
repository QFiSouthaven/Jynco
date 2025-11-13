"""
Workflow model for storing reusable ComfyUI workflows.
"""
from sqlalchemy import Column, String, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class Workflow(Base, TimestampMixin):
    """
    Workflow represents a reusable ComfyUI workflow template.
    It can be created by users or provided as defaults by the system.
    """

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    workflow_json = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="workflows")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name}, category={self.category}, is_default={self.is_default})>"
