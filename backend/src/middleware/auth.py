from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from ..utils.jwt_utils import verify_token, extract_user_id_from_token
import os

# Initialize the HTTP Bearer scheme
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """
    Dependency to get the current authenticated user from the JWT token.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        Dict: User information extracted from the token

    Raises:
        HTTPException: If the token is invalid or missing
    """
    token = credentials.credentials

    # Verify the token
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user information
    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "email": email
    }


def require_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to enforce that a user is authenticated.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        True if user is authenticated

    Raises:
        HTTPException: If the token is invalid or missing
    """
    try:
        user = get_current_user(credentials)
        return user
    except HTTPException:
        raise


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Convenience dependency to get just the current user ID.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        str: The current user's ID

    Raises:
        HTTPException: If the token is invalid or missing
    """
    user = get_current_user(credentials)
    return user["user_id"]