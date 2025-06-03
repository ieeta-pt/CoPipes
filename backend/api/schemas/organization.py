from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrganizationRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"
    
    def can_manage_members(self) -> bool:
        """Check if role can invite/remove members."""
        return self in [self.OWNER, self.ADMIN, self.MANAGER]
    
    def can_manage_admins(self) -> bool:
        """Check if role can manage admin-level users."""
        return self in [self.OWNER, self.ADMIN]
    
    def can_delete_organization(self) -> bool:
        """Check if role can delete the organization."""
        return self == self.OWNER
    
    def can_transfer_ownership(self) -> bool:
        """Check if role can transfer organization ownership."""
        return self == self.OWNER
    
    def can_create_workflows(self) -> bool:
        """Check if role can create workflows in the organization."""
        return self in [self.OWNER, self.ADMIN, self.MANAGER, self.MEMBER]
    
    def can_view_workflows(self) -> bool:
        """Check if role can view organization workflows."""
        return True  # All roles can view workflows
    
    def can_manage_organization_settings(self) -> bool:
        """Check if role can modify organization settings."""
        return self in [self.OWNER, self.ADMIN]
    
    def get_role_hierarchy_level(self) -> int:
        """Get numeric level for role hierarchy comparison."""
        hierarchy = {
            self.OWNER: 5,
            self.ADMIN: 4,
            self.MANAGER: 3,
            self.MEMBER: 2,
            self.VIEWER: 1
        }
        return hierarchy.get(self, 0)

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