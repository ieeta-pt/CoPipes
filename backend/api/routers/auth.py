from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from schemas.auth import UserCreate, UserLogin, TokenResponse, RefreshToken, PasswordResetRequest, PasswordReset, UserResponse
from utils.auth import authenticate_user, create_access_token, create_refresh_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from database import SupabaseClient

router = APIRouter(prefix="/api/auth", tags=["auth"])
supabase = SupabaseClient()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        user = supabase.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate and generate JWT token."""
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(user["id"])
    
    # Save refresh token to database
    supabase.save_refresh_token(user["id"], refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": refresh_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "created_at": user["created_at"]
        }
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token_data: RefreshToken):
    """Refresh an access token using a refresh token."""
    refresh_token = refresh_token_data.refresh_token
    
    # Verify refresh token
    user_id = supabase.verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Get user from database
    user = supabase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    new_refresh_token = create_refresh_token(user["id"])
    
    # Save new refresh token and invalidate old one
    supabase.invalidate_refresh_token(refresh_token)
    supabase.save_refresh_token(user["id"], new_refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": new_refresh_token,
        "user": user
    }


@router.post("/logout")
async def logout(refresh_token_data: RefreshToken):
    """Logout by invalidating the refresh token."""
    try:
        supabase.invalidate_refresh_token(refresh_token_data.refresh_token)
        return {"detail": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}"
        )


@router.post("/password-reset-request")
async def request_password_reset(reset_data: PasswordResetRequest):
    """Request a password reset."""
    # In a real implementation, this would send an email with a reset link
    # For simplicity, we're returning a success message regardless of whether the email exists
    return {"detail": "If your email is registered, you will receive a password reset link"}


@router.post("/password-reset")
async def reset_password(reset_data: PasswordReset):
    """Reset a password using a token."""
    # In a real implementation, this would verify the token and reset the password
    # For simplicity, this is not fully implemented
    return {"detail": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return current_user 