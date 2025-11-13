"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import os
from typing import Generator
import uuid as uuid_lib

# Handle imports for both backend container (/app) and worker containers (/app/backend)
try:
    from backend.models.base import Base
except ModuleNotFoundError:
    from models.base import Base

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/videofoundry")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Allow up to 20 connections beyond pool_size
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"  # Log SQL statements in dev
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions in non-FastAPI contexts (workers).
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Should be run during application startup or via migration tool.
    """
    Base.metadata.create_all(bind=engine)
    # Create default user for development if it doesn't exist
    create_default_user()
    # Create default workflows
    create_default_workflows()


def drop_db():
    """
    Drop all tables - USE WITH CAUTION.
    Only for testing or development reset.
    """
    Base.metadata.drop_all(bind=engine)


# Fixed UUID for default user (consistent across restarts)
DEFAULT_USER_ID = uuid_lib.UUID("00000000-0000-0000-0000-000000000001")


def create_default_user():
    """
    Create a default user for development if it doesn't exist.
    This allows project creation without authentication.
    """
    # Import dependencies here to avoid circular imports and missing deps in workers
    try:
        from backend.models.user import User
    except ModuleNotFoundError:
        from models.user import User

    import bcrypt

    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        # Ensure password is bytes and under 72 bytes
        pwd_bytes = password.encode('utf-8')[:72]
        return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')

    db = SessionLocal()
    try:
        # Check if default user already exists
        existing_user = db.query(User).filter(User.id == DEFAULT_USER_ID).first()
        if existing_user:
            return existing_user

        # Create default user
        hashed_password = hash_password("development")
        default_user = User(
            id=DEFAULT_USER_ID,
            email="dev@videofoundry.local",
            username="developer",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        print(f"Created default user: {default_user.username} (ID: {default_user.id})")
        return default_user
    except Exception as e:
        db.rollback()
        print(f"Error creating default user: {e}")
        raise
    finally:
        db.close()


def get_default_user_id():
    """
    Get the default user ID for development.
    This should be used in place of authentication until auth is implemented.
    """
    return DEFAULT_USER_ID


def create_default_workflows():
    """
    Create default ComfyUI workflows if they don't exist.
    This populates the workflow library with the two basic workflows.
    """
    import json
    from pathlib import Path

    # Import dependencies here to avoid circular imports
    try:
        from backend.models.workflow import Workflow
    except ModuleNotFoundError:
        from models.workflow import Workflow

    db = SessionLocal()
    try:
        # Check if default workflows already exist
        existing_defaults = db.query(Workflow).filter(Workflow.is_default == True).count()
        if existing_defaults > 0:
            print(f"Default workflows already exist ({existing_defaults} found)")
            return

        # Path to workflow files
        workflows_dir = Path(__file__).parent.parent.parent / "workflows"

        # Define default workflows to create
        default_workflows = [
            {
                "name": "Text to Video (Basic)",
                "description": "Basic text-to-video workflow using AnimateDiff with SDXL. Generates 16 frames at 512x512 resolution.",
                "category": "text-to-video",
                "file": "text-to-video-basic.json"
            },
            {
                "name": "Image to Video (Basic)",
                "description": "Basic image-to-video workflow using Stable Video Diffusion (SVD). Generates smooth video from a single image at 1024x576 resolution.",
                "category": "image-to-video",
                "file": "image-to-video-basic.json"
            }
        ]

        # Create each workflow
        for workflow_def in default_workflows:
            workflow_file = workflows_dir / workflow_def["file"]

            if not workflow_file.exists():
                print(f"Warning: Workflow file not found: {workflow_file}")
                continue

            # Read the workflow JSON
            with open(workflow_file, 'r') as f:
                workflow_json = json.load(f)

            # Create the workflow record
            workflow = Workflow(
                user_id=DEFAULT_USER_ID,
                name=workflow_def["name"],
                description=workflow_def["description"],
                category=workflow_def["category"],
                workflow_json=workflow_json,
                is_default=True
            )
            db.add(workflow)
            print(f"Created default workflow: {workflow_def['name']}")

        db.commit()
        print(f"Successfully created {len(default_workflows)} default workflows")

    except Exception as e:
        db.rollback()
        print(f"Error creating default workflows: {e}")
        # Don't raise - this is not critical for app startup
    finally:
        db.close()
