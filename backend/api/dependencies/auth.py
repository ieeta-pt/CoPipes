from fastapi import Depends, HTTPException, status
from utils.auth import get_current_user

async def require_auth(current_user: dict = Depends(get_current_user)):
    """Dependency to use on protected routes that require authentication."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user 