"""
FastAPI dependencies for authentication and common functionality.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

from .security import decode_token, get_user_by_id

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user (allows anonymous access).
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        
    Returns:
        User data dictionary if authenticated, None otherwise
    """
    if credentials is None:
        return None
        
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        user = await get_user_by_id(user_id)
        return user
        
    except (ValueError, Exception):
        return None