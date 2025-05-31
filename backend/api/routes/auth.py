from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from services.supabase_client import supabase
from schemas.user import UserRegister, UserLogin, UserUpdate, EmailRequest, TokenResponse
from utils.auth import create_access_token, get_current_user, JWT_ACCESS_TOKEN_EXPIRE_HOURS
from config import FRONTEND_URL

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

@router.post("/signup", response_model=dict)
async def signup(user_data: UserRegister):
    """Register a new user"""
    try:
        # Sign up user with Supabase (auto-confirm email)
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                },
                "email_confirm": False  # Skip email confirmation
            }
        })
        
        if response.user:
            return {
                "message": "User registered successfully. You can now log in.",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/signin", response_model=TokenResponse)
async def signin(user_data: UserLogin):
    """Sign in user with email and password"""
    try:
        # Authenticate with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if response.user and response.session:
            # Create JWT token
            access_token_expires = timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS)
            access_token = create_access_token(
                data={"sub": response.user.id, "email": response.user.email},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name")
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
            
    except Exception as e:
        if "Invalid login credentials" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/signout")
async def signout():
    """Sign out user"""
    try:
        supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-password")
async def reset_password(email_data: EmailRequest):
    """Send password reset email"""
    try:
        response = supabase.auth.reset_password_email(
            email_data.email,
            {
                "redirect_to": f"{FRONTEND_URL}/auth/reset-password"
            }
        )
        return {"message": "Password reset email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/update-profile")
async def update_profile(user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user profile"""
    try:
        # Update user metadata
        update_data = {}
        if user_data.full_name:
            update_data["data"] = {"full_name": user_data.full_name}
        
        if user_data.email and user_data.email != current_user["email"]:
            update_data["email"] = user_data.email
            
        if user_data.password:
            update_data["password"] = user_data.password
            
        if update_data:
            response = supabase.auth.update_user(update_data)
            return {
                "message": "Profile updated successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name")
                }
            }
        else:
            return {"message": "No changes to update"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )