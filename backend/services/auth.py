"""
Authentication and Authorization Service

Supports both JWT-based authentication and OIDC/SAML integration.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import get_settings
from config.database import get_db
from models.user import User, UserRole

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer(auto_error=False)  # Don't auto-error to allow optional auth

# OAuth2 scheme for OIDC
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",  # Will be set dynamically based on OIDC provider
    tokenUrl="",
    auto_error=False
)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when user lacks required permissions."""
    pass


class AuthService:
    """Authentication and authorization service."""

    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.secret_key
        self.algorithm = self.settings.jwt_algorithm
        self.access_token_expire_minutes = self.settings.access_token_expire_minutes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Token payload (must include 'sub' for user ID)
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "videofoundry"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise AuthenticationError("Invalid authentication credentials")

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.

        Args:
            db: Database session
            username: Username or email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Try to find user by username or email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            return None

        if not user.hashed_password:
            # User is OIDC-only, cannot authenticate with password
            logger.warning(f"User {username} attempted password auth but is OIDC-only")
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            logger.warning(f"Inactive user {username} attempted to log in")
            return None

        return user

    def get_or_create_oidc_user(
        self,
        db: Session,
        external_id: str,
        email: str,
        username: Optional[str] = None,
        provider: str = "oidc",
        claims: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Get or create a user from OIDC claims.

        Args:
            db: Database session
            external_id: Subject claim from OIDC provider
            email: User email
            username: Optional username
            provider: Identity provider name
            claims: Additional OIDC claims

        Returns:
            User object
        """
        # Try to find existing user by external_id
        user = db.query(User).filter(User.external_id == external_id).first()

        if user:
            # Update email if changed
            if user.email != email:
                user.email = email
                db.commit()
                db.refresh(user)
            return user

        # Create new user
        username = username or email.split('@')[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1

        # Determine role from claims (if provider supports it)
        role = UserRole.USER
        if claims and 'roles' in claims:
            if 'admin' in claims['roles'] or 'videofoundry-admin' in claims['roles']:
                role = UserRole.ADMIN

        user = User(
            email=email,
            username=username,
            external_id=external_id,
            external_provider=provider,
            role=role,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new OIDC user: {username} ({email}) from provider {provider}")

        return user


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get the singleton auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


# Dependency injection functions for FastAPI

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current authenticated user (optional).

    Returns None if no authentication provided (for optional auth endpoints).
    """
    settings = get_settings()

    # If IAM is disabled (developer mode), return None
    if not settings.enable_iam:
        logger.debug("IAM disabled, skipping authentication")
        return None

    if not credentials:
        return None

    auth_service = get_auth_service()

    try:
        payload = auth_service.decode_token(credentials.credentials)
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            return None

        if not user.is_active:
            return None

        # Set user context for Row-Level Security
        db.execute(f"SET LOCAL app.current_user_id = '{user.id}'")
        db.execute(f"SET LOCAL app.current_user_role = '{user.role.value}'")

        return user

    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user (required).

    Raises HTTPException if authentication fails.
    """
    settings = get_settings()

    # If IAM is disabled (developer mode), create a mock user
    if not settings.enable_iam:
        logger.warning("IAM disabled - using mock user (INSECURE - developer mode only)")
        # Return a mock admin user for development
        mock_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not mock_user:
            # Create a default admin user if none exists
            mock_user = User(
                email="dev@localhost",
                username="developer",
                role=UserRole.ADMIN,
                is_active=True,
                hashed_password=None
            )
            db.add(mock_user)
            db.commit()
            db.refresh(mock_user)

        # Set user context
        db.execute(f"SET LOCAL app.current_user_id = '{mock_user.id}'")
        db.execute(f"SET LOCAL app.current_user_role = '{mock_user.role.value}'")

        return mock_user

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = get_auth_service()

    try:
        payload = auth_service.decode_token(credentials.credentials)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Set user context for Row-Level Security
        db.execute(f"SET LOCAL app.current_user_id = '{user.id}'")
        db.execute(f"SET LOCAL app.current_user_role = '{user.role.value}'")

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current user and verify they have admin role.

    Raises HTTPException if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user


def require_permission(permission: str):
    """
    Decorator factory for requiring specific permissions.

    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: User = Depends(require_permission("admin.access"))):
            ...
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return current_user

    return permission_checker
