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
            
            # Add owner as owner member
            self.client.table("organization_members").insert({
                "id": str(uuid4()),
                "user_id": owner_id,
                "organization_id": org_id,
                "role": OrganizationRole.OWNER,
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
        """Get all members of an organization (only if user can manage members)."""
        try:
            # Check if user can manage members of this organization
            role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not role_check.data:
                raise Exception("Access denied: User is not a member of this organization")
                
            user_role = OrganizationRole(role_check.data[0]["role"])
            if not user_role.can_manage_members():
                raise Exception("Access denied: Insufficient privileges to view organization members")
            
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
            # Check if inviter can manage members
            role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", inviter_id)\
                .execute()
            
            if not role_check.data:
                raise Exception("Access denied: User is not a member of this organization")
                
            inviter_role = OrganizationRole(role_check.data[0]["role"])
            
            # Check if inviter can manage members
            if not inviter_role.can_manage_members():
                raise Exception("Access denied: Insufficient privileges to invite users")
            
            # Check if trying to invite someone with higher or equal role to inviter
            if invite_data.role.get_role_hierarchy_level() >= inviter_role.get_role_hierarchy_level():
                raise Exception("Access denied: Cannot invite users with equal or higher privileges")
            
            # Only owners and admins can invite other admins
            if invite_data.role == OrganizationRole.ADMIN and not inviter_role.can_manage_admins():
                raise Exception("Access denied: Only owners and admins can invite other admins")
            
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
            # Check remover's role
            remover_role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", remover_id)\
                .execute()
            
            if not remover_role_check.data:
                raise Exception("Access denied: User is not a member of this organization")
                
            remover_role = OrganizationRole(remover_role_check.data[0]["role"])
            
            if not remover_role.can_manage_members():
                raise Exception("Access denied: Insufficient privileges to remove users")
            
            # Get target user's role
            target_role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", user_to_remove_id)\
                .execute()
            
            if not target_role_check.data:
                raise Exception("User is not a member of this organization")
                
            target_role = OrganizationRole(target_role_check.data[0]["role"])
            
            # Cannot remove someone with equal or higher privileges
            if target_role.get_role_hierarchy_level() >= remover_role.get_role_hierarchy_level():
                raise Exception("Access denied: Cannot remove users with equal or higher privileges")
            
            # Cannot remove organization owner
            if target_role == OrganizationRole.OWNER:
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
            # Check updater's role
            updater_role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", updater_id)\
                .execute()
            
            if not updater_role_check.data:
                raise Exception("Access denied: User is not a member of this organization")
                
            updater_role = OrganizationRole(updater_role_check.data[0]["role"])
            
            if not updater_role.can_manage_members():
                raise Exception("Access denied: Insufficient privileges to update user roles")
            
            # Get target user's current role
            target_role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not target_role_check.data:
                raise Exception("User is not a member of this organization")
                
            current_role = OrganizationRole(target_role_check.data[0]["role"])
            
            # Cannot update role of organization owner
            if current_role == OrganizationRole.OWNER:
                raise Exception("Cannot change role of organization owner")
            
            # Cannot assign role equal or higher than updater's role
            if new_role.get_role_hierarchy_level() >= updater_role.get_role_hierarchy_level():
                raise Exception("Access denied: Cannot assign roles equal or higher than your own")
            
            # Cannot update someone with equal or higher privileges
            if current_role.get_role_hierarchy_level() >= updater_role.get_role_hierarchy_level():
                raise Exception("Access denied: Cannot update users with equal or higher privileges")
            
            # Only owners and admins can assign admin role
            if new_role == OrganizationRole.ADMIN and not updater_role.can_manage_admins():
                raise Exception("Access denied: Only owners and admins can assign admin role")
            
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
            # Check if user has permission to delete organization
            role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not role_check.data:
                raise Exception("Access denied: User is not a member of this organization")
                
            user_role = OrganizationRole(role_check.data[0]["role"])
            
            if not user_role.can_delete_organization():
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
    
    def transfer_ownership(self, org_id: str, new_owner_id: str, current_owner_id: str) -> dict:
        """Transfer organization ownership to another member."""
        try:
            # Check if current user is owner
            role_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", current_owner_id)\
                .execute()
            
            if not role_check.data:
                raise Exception("Access denied: User is not a member of this organization")
                
            current_role = OrganizationRole(role_check.data[0]["role"])
            
            if not current_role.can_transfer_ownership():
                raise Exception("Access denied: Only organization owner can transfer ownership")
            
            # Check if new owner is a member
            new_owner_check = self.client.table("organization_members")\
                .select("role")\
                .eq("organization_id", org_id)\
                .eq("user_id", new_owner_id)\
                .execute()
            
            if not new_owner_check.data:
                raise Exception("New owner must be a member of the organization")
            
            # Update organization owner
            self.client.table("organizations")\
                .update({"owner_id": new_owner_id})\
                .eq("id", org_id)\
                .execute()
            
            # Update roles: new owner becomes OWNER, old owner becomes ADMIN
            self.client.table("organization_members")\
                .update({"role": OrganizationRole.OWNER})\
                .eq("organization_id", org_id)\
                .eq("user_id", new_owner_id)\
                .execute()
            
            self.client.table("organization_members")\
                .update({"role": OrganizationRole.ADMIN})\
                .eq("organization_id", org_id)\
                .eq("user_id", current_owner_id)\
                .execute()
            
            return {"message": "Organization ownership successfully transferred"}
        except Exception as e:
            print(f"Failed to transfer ownership: {e}")
            raise