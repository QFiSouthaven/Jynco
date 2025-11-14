"""
Security module for the Local AI Agent.
Implements Bearer token authentication to protect all tool endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the secret token from environment
AGENT_SECRET_TOKEN = os.getenv("AGENT_SECRET_TOKEN")
if not AGENT_SECRET_TOKEN:
    raise ValueError(
        "CRITICAL ERROR: AGENT_SECRET_TOKEN not found in environment. "
        "Please set it in your .env file. Generate one with: "
        "python -c \"import secrets; print(secrets.token_hex(32))\""
    )

# Initialize HTTPBearer security scheme
security_scheme = HTTPBearer()


async def verify_token(
    creds: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> bool:
    """
    Validates the Bearer token provided in the Authorization header.

    This function acts as a dependency guard for protected endpoints.
    Only requests with a valid Bearer token matching AGENT_SECRET_TOKEN
    are allowed through.

    Args:
        creds: HTTP authorization credentials extracted by FastAPI

    Returns:
        bool: True if token is valid

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or missing
    """
    if (
        not creds
        or creds.scheme != "Bearer"
        or creds.credentials != AGENT_SECRET_TOKEN
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
