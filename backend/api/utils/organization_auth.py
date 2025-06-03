from fastapi import HTTPException, status, Depends
from typing import Optional
from utils.auth import get_current_user
from services.organization_service import OrganizationService
from schemas.organization import OrganizationRole

organization_service = OrganizationService()

async def require_organization_admin(
    org_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dependency that ensures the current user is an admin of the specified organization."""
    user_role = organization_service.get_user_role_in_organization(org_id, current_user["id"])
    
    if user_role != OrganizationRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Organization admin privileges required"
        )
    
    return current_user

async def require_organization_member(
    org_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dependency that ensures the current user is a member of the specified organization."""
    user_role = organization_service.get_user_role_in_organization(org_id, current_user["id"])
    
    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Organization membership required"
        )
    
    # Add organization context to user
    current_user["organization_id"] = org_id
    current_user["organization_role"] = user_role
    return current_user

def check_organization_access(
    org_id: str,
    user_id: str,
    required_role: Optional[OrganizationRole] = None
) -> bool:
    """Check if a user has access to an organization with optional role requirement."""
    user_role = organization_service.get_user_role_in_organization(org_id, user_id)
    
    if user_role is None:
        return False
    
    if required_role and user_role != required_role:
        return False
    
    return True

def get_user_organization_context(user_id: str) -> dict:
    """Get user's organization context including all organizations and roles."""
    try:
        organizations = organization_service.get_user_organizations(user_id)
        return {
            "organizations": [
                {
                    "id": org.id,
                    "name": org.name,
                    "role": organization_service.get_user_role_in_organization(org.id, user_id)
                }
                for org in organizations
            ]
        }
    except Exception as e:
        print(f"Failed to get user organization context: {e}")
        return {"organizations": []}