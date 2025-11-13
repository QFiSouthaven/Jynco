"""
Pydantic schemas for RenderJob API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class RenderJobCreate(BaseModel):
    """Schema for creating a render job."""
    # No fields needed - render job is created from project state
    pass


class RenderJobProgress(BaseModel):
    """Schema for real-time render job progress."""
    render_job_id: UUID
    status: str
    segments_total: int
    segments_completed: int
    progress_percentage: float
    current_segment_id: Optional[UUID] = None
    current_segment_status: Optional[str] = None


class RenderJobResponse(BaseModel):
    """Schema for render job response."""
    id: UUID
    project_id: UUID
    status: str
    segments_total: int
    segments_completed: int
    segment_ids: List[str]
    s3_final_url: Optional[str] = None
    error_message: Optional[str] = None
    render_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.segments_total == 0:
            return 0.0
        return (self.segments_completed / self.segments_total) * 100

    class Config:
        from_attributes = True
