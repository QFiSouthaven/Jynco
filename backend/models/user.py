"""
User model for authentication and ownership.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from enum import Enum
from datetime import datetime

from .base import Base, TimestampMixin


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"       # Full system access, user management, security configuration
    USER = "user"         # CRUD on own projects, read shared projects, execute workflows
    VIEWER = "viewer"     # Read-only access to shared projects


class User(Base, TimestampMixin):
    """User model for authentication and project ownership."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OIDC-only users

    # Role-Based Access Control
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)

    # Identity Provider Integration (OIDC/SAML)
    external_id = Column(String(255), unique=True, nullable=True, index=True)  # Sub claim from OIDC
    external_provider = Column(String(50), nullable=True)  # 'keycloak', 'auth0', etc.

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)  # Deprecated, use role=ADMIN

    # Audit fields
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv4 or IPv6

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN or self.is_superuser

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: Permission string (e.g., 'project.create', 'user.manage')

        Returns:
            True if user has permission
        """
        # Admins have all permissions
        if self.is_admin:
            return True

        # Define permission matrix
        permissions_by_role = {
            UserRole.ADMIN: ['*'],  # All permissions
            UserRole.USER: [
                'project.create',
                'project.read.own',
                'project.update.own',
                'project.delete.own',
                'project.read.shared',
                'workflow.execute',
                'workflow.create',
                'workflow.read',
            ],
            UserRole.VIEWER: [
                'project.read.shared',
                'workflow.read',
            ]
        }

        role_permissions = permissions_by_role.get(self.role, [])

        # Wildcard permission
        if '*' in role_permissions:
            return True

        # Exact match
        if permission in role_permissions:
            return True

        # Prefix match (e.g., 'project.*' matches 'project.create')
        for perm in role_permissions:
            if perm.endswith('.*') and permission.startswith(perm[:-1]):
                return True

        return False

    def update_last_login(self, ip_address: str = None):
        """Update last login timestamp and IP."""
        self.last_login = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
