from pydantic import BaseModel, EmailStr
from typing import Optional, List
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

class UserOrganizationInfo(BaseModel):
    organization_id: str
    organization_name: str
    role: OrganizationRole
    