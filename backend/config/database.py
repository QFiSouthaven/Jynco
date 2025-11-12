"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import os
from typing import Generator
from passlib.context import CryptContext
import uuid as uuid_lib

# Handle imports for both backend container (/app) and worker containers (/app/backend)
try:
    from backend.models.base import Base
    from backend.models.user import User
except ModuleNotFoundError:
    from models.base import Base
    from models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    db = SessionLocal()
    try:
        # Check if default user already exists
        existing_user = db.query(User).filter(User.id == DEFAULT_USER_ID).first()
        if existing_user:
            return existing_user

        # Create default user
        hashed_password = pwd_context.hash("development")
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
