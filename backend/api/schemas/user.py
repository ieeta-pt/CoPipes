from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
import re
from schemas.organization import OrganizationRole

class EmailRequest(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class BaseUser(BaseModel):
    id: str | None = None
    email: EmailStr
    
class UserRegister(BaseUser):
    full_name: str
    password: str
    organization_id: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class UserLogin(BaseUser):
    password: str

class UserProfile(BaseUser):
    full_name: str
    avatar_url: str | None = None
    current_organization_id: Optional[str] = None
    organizations: List[dict] = []

class UserUpdate(BaseUser):
    full_name: str | None = None
    avatar_url: str | None = None
    password: str | None = None
    email: EmailStr | None = None
    current_organization_id: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is None:
            return v
        
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class UserOrganizationInfo(BaseModel):
    organization_id: str
    organization_name: str
    role: OrganizationRole
    