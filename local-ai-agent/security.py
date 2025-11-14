# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file into the environment
load_dotenv()

# Retrieve the secret token from the environment, making it available to our app
AGENT_SECRET_TOKEN = os.getenv("AGENT_SECRET_TOKEN")
if not AGENT_SECRET_TOKEN:
    # Fail loudly and immediately on startup if the secret is missing.
    raise ValueError("CRITICAL ERROR: AGENT_SECRET_TOKEN not found. Set it in your .env file.")

# Initialize the HTTPBearer security scheme, which tells FastAPI how to look for the token
security_scheme = HTTPBearer()

async def verify_token(creds: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Validates the Bearer token provided in the request's Authorization header.
    This function serves as a dependable guard for our protected endpoints.
    """
    if not creds or creds.scheme != "Bearer" or creds.credentials != AGENT_SECRET_TOKEN:
        # If the token is missing, malformed, or incorrect, deny access immediately.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # If the token is valid, the function completes, allowing the request to proceed to the endpoint.
    return True
