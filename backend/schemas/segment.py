"""
Pydantic schemas for Segment API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SegmentBase(BaseModel):
    """Base schema for Segment."""
    order_index: int = Field(..., ge=0)
    prompt: str = Field(..., min_length=1)
    model_params: Dict[str, Any] = Field(default_factory=dict)


class SegmentCreate(SegmentBase):
    """Schema for creating a new segment."""
    pass


class SegmentUpdate(BaseModel):
    """Schema for updating a segment."""
    order_index: Optional[int] = Field(None, ge=0)
    prompt: Optional[str] = Field(None, min_length=1)
    model_params: Optional[Dict[str, Any]] = None


class SegmentResponse(SegmentBase):
    """Schema for segment response."""
    id: UUID
    project_id: UUID
    status: str
    s3_asset_url: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    external_job_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
