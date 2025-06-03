from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrganizationRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    owner_id: str
    member_count: int = 0

class UserOrganization(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: OrganizationRole
    invited_at: datetime
    invited_by: str

class InviteUserRequest(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.MEMBER

class InviteResponse(BaseModel):
    message: str
    invite_id: Optional[str] = None

class OrganizationMember(BaseModel):
    user_id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: OrganizationRole
    joined_at: datetime
    invited_by: str

class OrganizationListResponse(BaseModel):
    organizations: List[OrganizationResponse]
    total: int