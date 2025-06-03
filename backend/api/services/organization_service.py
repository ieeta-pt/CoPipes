from datetime import datetime
from typing import List, Optional
from services.supabase_client import supabase_admin
from schemas.organization import (
    OrganizationCreate, OrganizationResponse, OrganizationRole,
    InviteUserRequest, OrganizationMember
)
from uuid import uuid4

class OrganizationService:
    """Service for managing organizations and their members."""
    
    def __init__(self):
        self.client = supabase_admin

    def create_organization(self, org_data: OrganizationCreate, owner_id: str) -> OrganizationResponse:
        """Create a new organization with the user as owner."""
        try:
            org_id = str(uuid4())
            
            # Create organization
            org_result = self.client.table("organizations").insert({
                "id": org_id,
                "name": org_data.name,
                "description": org_data.description,
                "owner_id": owner_id,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            # Add owner as admin member
            self.client.table("organization_members").insert({
                "id": str(uuid4()),
                "user_id": owner_id,
                "organization_id": org_id,
                "role": OrganizationRole.ADMIN,
                "invited_at": datetime.now().isoformat(),
                "invited_by": owner_id
            }).execute()
            
            return OrganizationResponse(
                id=org_id,
                name=org_data.name,
                description=org_data.description,
                created_at=datetime.now(),
                owner_id=owner_id,
                member_count=1
            )
        except Exception as e:
            print(f"Failed to create organization: {e}")
            raise

    def get_user_organizations(self, user_id: str) -> List[OrganizationResponse]:
        """Get all organizations a user belongs to."""
        try:
            # Get organizations where user is a member
            result = self.client.table("organization_members")\
                .select("organization_id, organizations!inner(id, name, description, owner_id, created_at)")\
                .eq("user_id", user_id)\
                .execute()
            
            organizations = []
            for item in result.data:
                org = item["organizations"]
                # Get member count
                member_count_result = self.client.table("organization_members")\
                    .select("id", count="exact")\
                    .eq("organization_id", org["id"])\
                    .execute()
                
                organizations.append(OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    description=org["description"],
                    created_at=datetime.fromisoformat(org["created_at"].replace('Z', '+00:00')),
                    owner_id=org["owner_id"],
                    member_count=member_count_result.count or 0
                ))
            
            return organizations
        except Exception as e:
            print(f"Failed to get user organizations: {e}")
            raise

    def get_organization_members(self, org_id: str, user_id: str) -> List[OrganizationMember]:
        """Get all members of an organization (only if user is admin)."""
        try:
            # Check if user is admin of this organization
            admin_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not admin_check.data or admin_check.data[0]["role"] != OrganizationRole.ADMIN:
                raise Exception("Access denied: Only admins can view organization members")
            
            # Get all members with user info
            result = self.client.table("organization_members")\
                .select("user_id, role, invited_at, invited_by")\
                .eq("organization_id", org_id)\
                .execute()
            
            members = []
            for member in result.data:
                # Get user profile info from Supabase auth
                try:
                    user_profile = self.client.table("profiles")\
                        .select("email, full_name")\
                        .eq("id", member["user_id"])\
                        .execute()
                    
                    if user_profile.data:
                        profile = user_profile.data[0]
                        members.append(OrganizationMember(
                            user_id=member["user_id"],
                            email=profile["email"],
                            full_name=profile.get("full_name"),
                            role=OrganizationRole(member["role"]),
                            joined_at=datetime.fromisoformat(member["invited_at"].replace('Z', '+00:00')),
                            invited_by=member["invited_by"]
                        ))
                except Exception as profile_error:
                    print(f"Failed to get profile for user {member['user_id']}: {profile_error}")
                    continue
            
            return members
        except Exception as e:
            print(f"Failed to get organization members: {e}")
            raise

    def invite_user_to_organization(self, org_id: str, invite_data: InviteUserRequest, inviter_id: str) -> dict:
        """Invite a user to join an organization."""
        try:
            # Check if inviter is admin
            admin_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", inviter_id)\
                .execute()
            
            if not admin_check.data or admin_check.data[0]["role"] != OrganizationRole.ADMIN:
                raise Exception("Access denied: Only admins can invite users")
            
            # Check if user exists in auth system
            user_check = self.client.table("profiles")\
                .select("id")\
                .eq("email", str(invite_data.email))\
                .execute()
            
            if not user_check.data:
                raise Exception(f"User with email {invite_data.email} not found")
            
            invited_user_id = user_check.data[0]["id"]
            
            # Check if user is already a member
            existing_member = self.client.table("organization_members")\
                .select("id")\
                .eq("organization_id", org_id)\
                .eq("user_id", invited_user_id)\
                .execute()
            
            if existing_member.data:
                raise Exception("User is already a member of this organization")
            
            # Add user to organization
            self.client.table("organization_members").insert({
                "id": str(uuid4()),
                "user_id": invited_user_id,
                "organization_id": org_id,
                "role": invite_data.role,
                "invited_at": datetime.now().isoformat(),
                "invited_by": inviter_id
            }).execute()
            
            return {"message": f"User {invite_data.email} successfully added to organization"}
        except Exception as e:
            print(f"Failed to invite user to organization: {e}")
            raise

    def remove_user_from_organization(self, org_id: str, user_to_remove_id: str, remover_id: str) -> dict:
        """Remove a user from an organization."""
        try:
            # Check if remover is admin
            admin_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", remover_id)\
                .execute()
            
            if not admin_check.data or admin_check.data[0]["role"] != OrganizationRole.ADMIN:
                raise Exception("Access denied: Only admins can remove users")
            
            # Get organization info to check if removing owner
            org_info = self.client.table("organizations")\
                .select("owner_id")\
                .eq("id", org_id)\
                .execute()
            
            if org_info.data and org_info.data[0]["owner_id"] == user_to_remove_id:
                raise Exception("Cannot remove organization owner")
            
            # Remove user from organization
            self.client.table("organization_members")\
                .delete()\
                .eq("organization_id", org_id)\
                .eq("user_id", user_to_remove_id)\
                .execute()
            
            return {"message": "User successfully removed from organization"}
        except Exception as e:
            print(f"Failed to remove user from organization: {e}")
            raise

    def update_user_role(self, org_id: str, user_id: str, new_role: OrganizationRole, updater_id: str) -> dict:
        """Update a user's role in an organization."""
        try:
            # Check if updater is admin
            admin_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", updater_id)\
                .execute()
            
            if not admin_check.data or admin_check.data[0]["role"] != OrganizationRole.ADMIN:
                raise Exception("Access denied: Only admins can update user roles")
            
            # Get organization info to check if updating owner
            org_info = self.client.table("organizations")\
                .select("owner_id")\
                .eq("id", org_id)\
                .execute()
            
            if org_info.data and org_info.data[0]["owner_id"] == user_id:
                raise Exception("Cannot change role of organization owner")
            
            # Update user role
            self.client.table("organization_members")\
                .update({"role": new_role})\
                .eq("organization_id", org_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return {"message": f"User role updated to {new_role}"}
        except Exception as e:
            print(f"Failed to update user role: {e}")
            raise

    def get_user_role_in_organization(self, org_id: str, user_id: str) -> Optional[OrganizationRole]:
        """Get a user's role in a specific organization."""
        try:
            result = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if result.data:
                return OrganizationRole(result.data[0]["role"])
            return None
        except Exception as e:
            print(f"Failed to get user role: {e}")
            return None

    def delete_organization(self, org_id: str, user_id: str) -> dict:
        """Delete an organization (only owner can do this)."""
        try:
            # Check if user is owner
            org_check = self.client.table("organizations")\
                .select("owner_id")\
                .eq("id", org_id)\
                .execute()
            
            if not org_check.data or org_check.data[0]["owner_id"] != user_id:
                raise Exception("Access denied: Only organization owner can delete the organization")
            
            # Delete all members first
            self.client.table("organization_members")\
                .delete()\
                .eq("organization_id", org_id)\
                .execute()
            
            # Delete organization
            self.client.table("organizations")\
                .delete()\
                .eq("id", org_id)\
                .execute()
            
            return {"message": "Organization successfully deleted"}
        except Exception as e:
            print(f"Failed to delete organization: {e}")
            raise