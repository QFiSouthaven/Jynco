"""
API routes for Project management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from config import get_db, get_default_user_id
try:
    from backend.models import Project
except ModuleNotFoundError:
    from models import Project
from schemas import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new video project.
    """
    # TODO: Add authentication and get user_id from auth
    # For now, using the default development user
    user_id = get_default_user_id()

    project = Project(
        user_id=user_id,
        name=project_data.name,
        description=project_data.description
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all projects for the current user.
    """
    # TODO: Filter by authenticated user_id
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Update fields if provided
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    db.delete(project)
    db.commit()

    return None
