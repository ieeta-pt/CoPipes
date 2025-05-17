import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# from database import SupabaseClient

# Constants for token generation and validation
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Initialize Supabase client
# supabase = SupabaseClient()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that the password matches the hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash from plain password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Create the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create a new refresh token with longer expiration."""
    expires = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    from database import SupabaseClient  # Import here to avoid circular import
    supabase = SupabaseClient()
    """Validate and extract user information from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type", "access")
        
        if user_id is None:
            raise credentials_exception
        if token_type != "access":
            raise credentials_exception
            
        # Get user from database
        user = supabase.get_user(user_id)
        if user is None:
            raise credentials_exception
            
        return user
        
    except jwt.JWTError:
        raise credentials_exception


async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with email and password."""
    from database import SupabaseClient  # Import here to avoid circular import
    supabase = SupabaseClient()
    user = supabase.get_user_by_email(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.get("password")):
        return None
        
    return user 