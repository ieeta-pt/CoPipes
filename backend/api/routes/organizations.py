from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from services.organization_service import OrganizationService
from schemas.organization import (
    OrganizationCreate, OrganizationResponse, OrganizationRole,
    InviteUserRequest, OrganizationMember
)
from utils.auth import get_current_user
from utils.organization_auth import require_organization_owner, require_member_management_permission

router = APIRouter(
    prefix="/api/organizations",
    tags=["organizations"],
)

organization_service = OrganizationService()

@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new organization."""
    try:
        return organization_service.create_organization(org_data, current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[OrganizationResponse])
async def get_user_organizations(current_user: dict = Depends(get_current_user)):
    """Get all organizations the current user belongs to."""
    try:
        return organization_service.get_user_organizations(current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{org_id}/members", response_model=List[OrganizationMember])
async def get_organization_members(
    org_id: str,
    current_user: dict = Depends(require_member_management_permission)
):
    """Get all members of an organization (requires member management privileges)."""
    try:
        return organization_service.get_organization_members(org_id, current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{org_id}/invite")
async def invite_user_to_organization(
    org_id: str,
    invite_data: InviteUserRequest,
    current_user: dict = Depends(require_member_management_permission)
):
    """Invite a user to join the organization (requires member management privileges)."""
    try:
        return organization_service.invite_user_to_organization(
            org_id, invite_data, current_user["id"]
        )
    except Exception as e:
        if "Access denied" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        elif "not found" in str(e) or "already a member" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{org_id}/members/{user_id}")
async def remove_user_from_organization(
    org_id: str,
    user_id: str,
    current_user: dict = Depends(require_member_management_permission)
):
    """Remove a user from the organization (requires member management privileges)."""
    try:
        return organization_service.remove_user_from_organization(
            org_id, user_id, current_user["id"]
        )
    except Exception as e:
        if "Access denied" in str(e) or "Cannot remove" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{org_id}/members/{user_id}/role")
async def update_user_role(
    org_id: str,
    user_id: str,
    role_data: dict,
    current_user: dict = Depends(require_member_management_permission)
):
    """Update a user's role in the organization (requires member management privileges)."""
    try:
        new_role = OrganizationRole(role_data.get("role"))
        return organization_service.update_user_role(
            org_id, user_id, new_role, current_user["id"]
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified"
        )
    except Exception as e:
        if "Access denied" in str(e) or "Cannot change role" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{org_id}/role")
async def get_user_role_in_organization(
    org_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the current user's role in a specific organization."""
    try:
        role = organization_service.get_user_role_in_organization(org_id, current_user["id"])
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this organization"
            )
        return {"role": role}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{org_id}")
async def delete_organization(
    org_id: str,
    current_user: dict = Depends(require_organization_owner)
):
    """Delete an organization (owner only)."""
    try:
        return organization_service.delete_organization(org_id, current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{org_id}/transfer-ownership")
async def transfer_organization_ownership(
    org_id: str,
    transfer_data: dict,
    current_user: dict = Depends(require_organization_owner)
):
    """Transfer organization ownership to another member (owner only)."""
    try:
        new_owner_id = transfer_data.get("new_owner_id")
        if not new_owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="new_owner_id is required"
            )
        
        return organization_service.transfer_ownership(
            org_id, new_owner_id, current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        if "Access denied" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )