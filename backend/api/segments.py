"""
API routes for Segment management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from config import get_db
from models import Segment, Project
from models.segment import SegmentStatus
from schemas import SegmentCreate, SegmentUpdate, SegmentResponse

router = APIRouter(prefix="/api", tags=["segments"])


@router.post("/projects/{project_id}/segments", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
def create_segment(
    project_id: UUID,
    segment_data: SegmentCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new segment to a project.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    segment = Segment(
        project_id=project_id,
        order_index=segment_data.order_index,
        prompt=segment_data.prompt,
        model_params=segment_data.model_params,
        status=SegmentStatus.PENDING
    )

    db.add(segment)
    db.commit()
    db.refresh(segment)

    return segment


@router.get("/projects/{project_id}/segments", response_model=List[SegmentResponse])
def list_segments(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    List all segments for a project.
    """
    segments = (
        db.query(Segment)
        .filter(Segment.project_id == project_id)
        .order_by(Segment.order_index)
        .all()
    )
    return segments


@router.get("/segments/{segment_id}", response_model=SegmentResponse)
def get_segment(
    segment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific segment by ID.
    """
    segment = db.query(Segment).filter(Segment.id == segment_id).first()

    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segment {segment_id} not found"
        )

    return segment


@router.put("/segments/{segment_id}", response_model=SegmentResponse)
def update_segment(
    segment_id: UUID,
    segment_data: SegmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a segment.
    """
    segment = db.query(Segment).filter(Segment.id == segment_id).first()

    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segment {segment_id} not found"
        )

    # Update fields if provided
    if segment_data.order_index is not None:
        segment.order_index = segment_data.order_index
    if segment_data.prompt is not None:
        segment.prompt = segment_data.prompt
        # Reset status when prompt changes
        segment.status = SegmentStatus.PENDING
        segment.s3_asset_url = None
    if segment_data.model_params is not None:
        segment.model_params = segment_data.model_params
        # Reset status when params change
        segment.status = SegmentStatus.PENDING
        segment.s3_asset_url = None

    db.commit()
    db.refresh(segment)

    return segment


@router.delete("/segments/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_segment(
    segment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a segment.
    """
    segment = db.query(Segment).filter(Segment.id == segment_id).first()

    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segment {segment_id} not found"
        )

    db.delete(segment)
    db.commit()

    return None
