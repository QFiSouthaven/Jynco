"""
API routes for Render Job management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio
import json

from config import get_db
from models import RenderJob
from schemas import RenderJobCreate, RenderJobResponse
from services import RabbitMQClient, RedisClient, RenderOrchestrator

router = APIRouter(prefix="/api", tags=["render"])

# Initialize services
rabbitmq_client = RabbitMQClient()
redis_client = RedisClient()
orchestrator = RenderOrchestrator(rabbitmq_client, redis_client)


@router.post("/projects/{project_id}/render", response_model=RenderJobResponse, status_code=status.HTTP_201_CREATED)
def start_render(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Start a new render job for a project.
    """
    try:
        render_job = orchestrator.create_render_job(db, project_id)
        return render_job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start render: {str(e)}"
        )


@router.get("/render-jobs/{render_job_id}", response_model=RenderJobResponse)
def get_render_job(
    render_job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get render job status and details.
    """
    render_job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()

    if not render_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {render_job_id} not found"
        )

    return render_job


@router.get("/projects/{project_id}/render-jobs", response_model=List[RenderJobResponse])
def list_render_jobs(
    project_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all render jobs for a project.
    """
    render_jobs = (
        db.query(RenderJob)
        .filter(RenderJob.project_id == project_id)
        .order_by(RenderJob.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return render_jobs


@router.websocket("/render-jobs/{render_job_id}/progress")
async def render_job_progress_websocket(
    websocket: WebSocket,
    render_job_id: UUID
):
    """
    WebSocket endpoint for real-time render job progress updates.
    """
    await websocket.accept()

    try:
        while True:
            # Get progress from Redis
            progress = redis_client.get_render_job_progress(render_job_id)

            if progress:
                await websocket.send_json({
                    "render_job_id": str(render_job_id),
                    "status": progress["status"],
                    "segments_total": progress["segments_total"],
                    "segments_completed": progress["segments_completed"],
                    "progress_percentage": progress["progress_percentage"]
                })

                # If completed or failed, close the connection
                if progress["status"] in ["completed", "failed"]:
                    break

            # Wait before next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
