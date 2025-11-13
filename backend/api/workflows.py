"""
API routes for Workflow management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from config import get_db, get_default_user_id
try:
    from backend.models import Workflow
except ModuleNotFoundError:
    from models import Workflow
from schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new workflow.
    """
    # TODO: Add authentication and get user_id from auth
    # For now, using the default development user
    user_id = get_default_user_id()

    workflow = Workflow(
        user_id=user_id,
        name=workflow_data.name,
        description=workflow_data.description,
        category=workflow_data.category,
        workflow_json=workflow_data.workflow_json,
        is_default=False  # User-created workflows are never defaults
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(
    category: Optional[str] = Query(None, description="Filter by category"),
    include_defaults: bool = Query(True, description="Include default workflows"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all workflows for the current user, optionally including defaults.
    Can be filtered by category.
    """
    # TODO: Filter by authenticated user_id
    user_id = get_default_user_id()

    query = db.query(Workflow)

    # Build filter conditions
    if include_defaults:
        # Show user's workflows + default workflows
        query = query.filter(
            (Workflow.user_id == user_id) | (Workflow.is_default == True)
        )
    else:
        # Show only user's workflows
        query = query.filter(Workflow.user_id == user_id)

    # Apply category filter if provided
    if category:
        query = query.filter(Workflow.category == category)

    # Order by defaults first, then by name
    query = query.order_by(Workflow.is_default.desc(), Workflow.name)

    workflows = query.offset(skip).limit(limit).all()
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific workflow by ID.
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )

    return workflow


@router.get("/by-name/{name}", response_model=WorkflowResponse)
def get_workflow_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific workflow by name.
    Useful for loading default workflows.
    """
    # Try to find default workflow first, then user's workflow
    user_id = get_default_user_id()

    workflow = db.query(Workflow).filter(
        Workflow.name == name,
        (Workflow.is_default == True) | (Workflow.user_id == user_id)
    ).first()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{name}' not found"
        )

    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a workflow. Users cannot update default workflows.
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )

    if workflow.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify default workflows"
        )

    # Update fields if provided
    if workflow_data.name is not None:
        workflow.name = workflow_data.name
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.category is not None:
        workflow.category = workflow_data.category
    if workflow_data.workflow_json is not None:
        workflow.workflow_json = workflow_data.workflow_json

    db.commit()
    db.refresh(workflow)

    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a workflow. Users cannot delete default workflows.
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )

    if workflow.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete default workflows"
        )

    db.delete(workflow)
    db.commit()

    return None


@router.get("/categories/list", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """
    List all unique workflow categories.
    """
    user_id = get_default_user_id()

    categories = db.query(Workflow.category).filter(
        (Workflow.user_id == user_id) | (Workflow.is_default == True)
    ).distinct().all()

    return [cat[0] for cat in categories]
