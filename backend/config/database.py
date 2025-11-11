"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import os
from typing import Generator

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


def drop_db():
    """
    Drop all tables - USE WITH CAUTION.
    Only for testing or development reset.
    """
    Base.metadata.drop_all(bind=engine)
