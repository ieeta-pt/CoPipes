from schemas.workflow import WorkflowPermissions, WorkflowRole, CompleteWorkflowPermissions, WorkflowCollaborator
from schemas.organization import OrganizationRole
from typing import Dict, List
from database import SupabaseClient

def get_user_workflow_role(workflow_data: dict, current_user: dict) -> WorkflowRole:
    """
    Determine user's role in a specific workflow.
    
    Args:
        workflow_data: The workflow record from database
        current_user: Current authenticated user data
        
    Returns:
        WorkflowRole enum value
    """
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    # Check if user is the owner
    if workflow_data["user_id"] == user_id:
        return WorkflowRole.OWNER
    
    # Check collaborators from the workflow_collaborators table
    supabase = SupabaseClient()
    try:
        workflow_collaborators = supabase.get_workflow_collaborators_from_table(workflow_data["id"])
        for collab in workflow_collaborators:
            if collab.get("email") == user_email:
                return WorkflowRole(collab.get("role", WorkflowRole.VIEWER))
    except Exception as e:
        print(f"Failed to get workflow collaborators: {e}")
        # Fall back to legacy collaborators if table doesn't exist or query fails
    
    # Check legacy collaborators (default to VIEWER role)
    legacy_collaborators = workflow_data.get("collaborators", []) or []
    if user_email in legacy_collaborators:
        return WorkflowRole.VIEWER
    
    # Check organization membership
    org_id = workflow_data.get("organization_id")
    if org_id:
        from services.organization_service import OrganizationService
        org_service = OrganizationService()
        org_role = org_service.get_user_role_in_organization(org_id, user_id)
        if org_role:
            # Organization members get viewer access by default
            return WorkflowRole.VIEWER
    
    # No access - return None (will be handled by caller)
    return None

def get_workflow_permissions(workflow_data: dict, current_user: dict) -> WorkflowPermissions:
    """
    Determine user permissions for a specific workflow based on their role.
    
    Args:
        workflow_data: The workflow record from database
        current_user: Current authenticated user data
        
    Returns:
        WorkflowPermissions object with permission flags
    """
    user_role = get_user_workflow_role(workflow_data, current_user)
    
    if user_role is None:
        # No access
        return WorkflowPermissions(
            role=WorkflowRole.VIEWER,
            is_owner=False,
            can_view=False,
            can_edit=False,
            can_execute=False,
            can_download=False,
            can_copy=False,
            can_delete=False,
            can_manage_permissions=False,
            can_view_sensitive_data=False
        )
    
    # Calculate permissions based on role
    return WorkflowPermissions(
        role=user_role,
        is_owner=user_role == WorkflowRole.OWNER,
        can_view=user_role.can_view(),
        can_edit=user_role.can_edit(),
        can_execute=user_role.can_execute(),
        can_download=user_role.can_download(),
        can_copy=user_role.can_copy(),
        can_delete=user_role.can_delete(),
        can_manage_permissions=user_role.can_manage_permissions(),
        can_view_sensitive_data=user_role.can_view_sensitive_data()
    )

def get_user_workflows(current_user: dict):
    """
    Get all workflows that a user can access (owned + collaborated).
    
    Args:
        current_user: Current authenticated user data
        
    Returns:
        List of workflows with permission information and owner details
    """
    supabase = SupabaseClient()
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    # Get workflows where user is owner
    owned_workflows = supabase.get_workflows(user_id)
    
    # Get all workflows where user is a collaborator
    all_workflows = supabase.get_workflows()  # Get all workflows
    collaborated_workflows = []
    
    for workflow in all_workflows:
        collaborators = workflow.get("collaborators", []) or []
        if user_email in collaborators and workflow["user_id"] != user_id:
            collaborated_workflows.append(workflow)
    
    # Get owner information for all unique user_ids and organization IDs
    unique_owner_ids = set()
    unique_org_ids = set()
    for workflow in owned_workflows + collaborated_workflows:
        unique_owner_ids.add(workflow["user_id"])
        if workflow.get("organization_id"):
            unique_org_ids.add(workflow["organization_id"])
    
    # Fetch owner details from profiles table
    owner_details = {}
    for owner_id in unique_owner_ids:
        try:
            profile_result = supabase.client.table("profiles").select("email, full_name").eq("id", owner_id).execute()
            if profile_result.data:
                owner_details[owner_id] = profile_result.data[0]
            else:
                # Fallback: if no profile, use current user data if it's the current user
                if owner_id == user_id:
                    owner_details[owner_id] = {
                        "email": current_user["email"],
                        "full_name": current_user.get("full_name")
                    }
        except Exception as e:
            print(f"Error fetching owner details for {owner_id}: {e}")
            # Fallback for current user
            if owner_id == user_id:
                owner_details[owner_id] = {
                    "email": current_user["email"],
                    "full_name": current_user.get("full_name")
                }
    
    # Fetch organization details
    org_details = {}
    for org_id in unique_org_ids:
        try:
            org_result = supabase.client.table("organizations").select("id, name").eq("id", org_id).execute()
            if org_result.data:
                org_details[org_id] = org_result.data[0]
        except Exception as e:
            print(f"Error fetching organization details for {org_id}: {e}")
    
    # Combine and add permission info and owner details
    all_user_workflows = []
    
    for workflow in owned_workflows:
        permissions = get_workflow_permissions(workflow, current_user)
        workflow["permissions"] = permissions.model_dump()
        workflow["role"] = "owner"
        
        # Add owner information
        owner_info = owner_details.get(workflow["user_id"], {})
        workflow["owner_email"] = owner_info.get("email", current_user["email"])
        workflow["owner_name"] = owner_info.get("full_name")
        
        # Add organization information
        org_id = workflow.get("organization_id")
        if org_id and org_id in org_details:
            workflow["organization_name"] = org_details[org_id]["name"]
        else:
            workflow["organization_name"] = None
        
        all_user_workflows.append(workflow)
    
    for workflow in collaborated_workflows:
        permissions = get_workflow_permissions(workflow, current_user)
        workflow["permissions"] = permissions.model_dump()
        workflow["role"] = "collaborator"
        
        # Add owner information
        owner_info = owner_details.get(workflow["user_id"], {})
        workflow["owner_email"] = owner_info.get("email", "Unknown")
        workflow["owner_name"] = owner_info.get("full_name")
        
        # Add organization information
        org_id = workflow.get("organization_id")
        if org_id and org_id in org_details:
            workflow["organization_name"] = org_details[org_id]["name"]
        else:
            workflow["organization_name"] = None
        
        all_user_workflows.append(workflow)
    
    return all_user_workflows

def check_workflow_access(workflow_name: str, current_user: dict, required_permission: str = "can_edit"):
    """
    Check if user has access to a specific workflow operation.
    
    Args:
        workflow_name: Name of the workflow
        current_user: Current authenticated user data
        required_permission: Permission to check (can_edit, can_execute, can_download, can_delete, can_manage_collaborators)
        
    Returns:
        Tuple of (workflow_data, permissions) if access granted, raises exception if not
    """
    from fastapi import HTTPException
    
    user_email = current_user["email"]
    
    # Use get_user_workflows to get all workflows the user has access to
    # This includes both owned and collaborated workflows with proper permissions
    accessible_workflows = get_user_workflows(current_user)
    
    # Find the workflow by name within the user's accessible workflows
    workflow_name_clean = workflow_name.replace("_", " ")
    workflow_data = None
    
    for workflow in accessible_workflows:
        if workflow["name"] == workflow_name_clean:
            workflow_data = workflow
            break
    
    if not workflow_data:
        print(f"Workflow '{workflow_name_clean}' not found in user's accessible workflows")
        print(f"User {user_email} has access to: {[w['name'] for w in accessible_workflows]}")
        raise HTTPException(status_code=404, detail="Workflow not found or access denied")
    
    permissions = get_workflow_permissions(workflow_data, current_user)
    
    # Check the required permission
    if not getattr(permissions, required_permission):
        print(f"User {user_email} denied permission '{required_permission}' for workflow '{workflow_name_clean}'")
        raise HTTPException(status_code=403, detail=f"Permission denied: {required_permission}")
    
    return workflow_data, permissions

def get_organization_workflows(organization_id: str, current_user: dict):
    """
    Get all workflows that belong to an organization.
    
    Args:
        organization_id: Organization ID
        current_user: Current authenticated user data
        
    Returns:
        List of organization workflows with permission information
    """
    from services.organization_service import OrganizationService
    
    supabase = SupabaseClient()
    org_service = OrganizationService()
    
    # Check if user is a member of the organization
    user_role = org_service.get_user_role_in_organization(organization_id, current_user["id"])
    if user_role is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied: Not a member of this organization")
    
    # Get all workflows for the organization
    org_workflows_result = supabase.client.table("workflows")\
        .select("*")\
        .eq("organization_id", organization_id)\
        .execute()
    
    org_workflows = org_workflows_result.data
    
    # Get owner information for all workflows
    unique_owner_ids = set(workflow["user_id"] for workflow in org_workflows)
    owner_details = {}
    
    for owner_id in unique_owner_ids:
        try:
            profile_result = supabase.client.table("profiles").select("email, full_name").eq("id", owner_id).execute()
            if profile_result.data:
                owner_details[owner_id] = profile_result.data[0]
        except Exception as e:
            print(f"Error fetching owner details for {owner_id}: {e}")
    
    # Get organization name
    org_info = org_service.get_user_organizations(current_user["id"])
    org_name = None
    for org in org_info:
        if org.id == organization_id:
            org_name = org.name
            break
    
    # Add permissions and owner info to each workflow
    workflows_with_permissions = []
    for workflow in org_workflows:
        permissions = get_workflow_permissions(workflow, current_user)
        workflow["permissions"] = permissions.model_dump()
        workflow["organization_role"] = user_role
        workflow["organization_name"] = org_name
        
        # Add owner information
        owner_info = owner_details.get(workflow["user_id"], {})
        workflow["owner_email"] = owner_info.get("email", "Unknown")
        workflow["owner_name"] = owner_info.get("full_name")
        
        # Determine user's relationship to this workflow
        if workflow["user_id"] == current_user["id"]:
            workflow["role"] = "owner"
        elif current_user["email"] in (workflow.get("collaborators", []) or []):
            workflow["role"] = "collaborator"
        else:
            workflow["role"] = "organization_member"
        
        workflows_with_permissions.append(workflow)
    
    return workflows_with_permissions

def add_workflow_collaborator(workflow_data: dict, collaborator_email: str, role: WorkflowRole, inviter: dict) -> dict:
    """
    Add a collaborator to a workflow with specified role.
    
    Args:
        workflow_data: The workflow record from database
        collaborator_email: Email of user to add
        role: WorkflowRole to assign
        inviter: User adding the collaborator
        
    Returns:
        Updated workflow collaborators list
    """
    from datetime import datetime
    
    # Check if inviter has permission to manage collaborators
    inviter_permissions = get_workflow_permissions(workflow_data, inviter)
    if not inviter_permissions.can_manage_permissions:
        raise Exception("Access denied: Cannot manage workflow collaborators")
    
    # Get current collaborators
    workflow_collaborators = workflow_data.get("workflow_collaborators", []) or []
    
    # Check if collaborator already exists
    for collab in workflow_collaborators:
        if (isinstance(collab, dict) and collab.get("email") == collaborator_email) or \
           (hasattr(collab, "email") and collab.email == collaborator_email):
            raise Exception(f"User {collaborator_email} is already a collaborator")
    
    # Add new collaborator
    new_collaborator = {
        "email": collaborator_email,
        "role": role.value,
        "invited_at": datetime.now().isoformat(),
        "invited_by": inviter["email"]
    }
    
    workflow_collaborators.append(new_collaborator)
    return workflow_collaborators

def update_workflow_collaborator_role(workflow_data: dict, collaborator_email: str, new_role: WorkflowRole, updater: dict) -> dict:
    """
    Update a collaborator's role in a workflow.
    
    Args:
        workflow_data: The workflow record from database
        collaborator_email: Email of collaborator to update
        new_role: New WorkflowRole to assign
        updater: User making the update
        
    Returns:
        Updated workflow collaborators list
    """
    # Check if updater has permission to manage collaborators
    updater_permissions = get_workflow_permissions(workflow_data, updater)
    if not updater_permissions.can_manage_permissions:
        raise Exception("Access denied: Cannot manage workflow collaborators")
    
    # Get current collaborators
    workflow_collaborators = workflow_data.get("workflow_collaborators", []) or []
    
    # Find and update collaborator
    collaborator_found = False
    for i, collab in enumerate(workflow_collaborators):
        if (isinstance(collab, dict) and collab.get("email") == collaborator_email) or \
           (hasattr(collab, "email") and collab.email == collaborator_email):
            if isinstance(collab, dict):
                workflow_collaborators[i]["role"] = new_role.value
            else:
                workflow_collaborators[i].role = new_role
            collaborator_found = True
            break
    
    if not collaborator_found:
        raise Exception(f"Collaborator {collaborator_email} not found")
    
    return workflow_collaborators

def remove_workflow_collaborator(workflow_data: dict, collaborator_email: str, remover: dict) -> dict:
    """
    Remove a collaborator from a workflow.
    
    Args:
        workflow_data: The workflow record from database
        collaborator_email: Email of collaborator to remove
        remover: User removing the collaborator
        
    Returns:
        Updated workflow collaborators list
    """
    # Check if remover has permission to manage collaborators
    remover_permissions = get_workflow_permissions(workflow_data, remover)
    if not remover_permissions.can_manage_permissions:
        raise Exception("Access denied: Cannot manage workflow collaborators")
    
    # Cannot remove the workflow owner
    if workflow_data["user_id"] == collaborator_email:
        raise Exception("Cannot remove workflow owner")
    
    # Get current collaborators
    workflow_collaborators = workflow_data.get("workflow_collaborators", []) or []
    
    # Remove collaborator
    original_length = len(workflow_collaborators)
    workflow_collaborators = [
        collab for collab in workflow_collaborators
        if not ((isinstance(collab, dict) and collab.get("email") == collaborator_email) or
                (hasattr(collab, "email") and collab.email == collaborator_email))
    ]
    
    if len(workflow_collaborators) == original_length:
        raise Exception(f"Collaborator {collaborator_email} not found")
    
    return workflow_collaborators

def get_workflow_collaborators(workflow_data: dict, requestor: dict) -> List[Dict]:
    """
    Get list of workflow collaborators with their roles.
    
    Args:
        workflow_data: The workflow record from database
        requestor: User requesting the collaborator list
        
    Returns:
        List of collaborator information
    """
    # Check if requestor has access to view collaborators
    requestor_permissions = get_workflow_permissions(workflow_data, requestor)
    if not requestor_permissions.can_view:
        raise Exception("Access denied: Cannot view workflow collaborators")
    
    collaborators = []
    
    # Add owner
    owner_info = {
        "email": workflow_data.get("owner_email", "Unknown"),
        "role": WorkflowRole.OWNER.value,
        "is_owner": True,
        "invited_at": workflow_data.get("created_at"),
        "invited_by": "System"
    }
    collaborators.append(owner_info)
    
    # Add collaborators from the workflow_collaborators table
    supabase = SupabaseClient()
    try:
        workflow_collaborators = supabase.get_workflow_collaborators_from_table(workflow_data["id"])
        for collab in workflow_collaborators:
            collaborators.append({
                "email": collab.get("email"),
                "role": collab.get("role", WorkflowRole.VIEWER.value),
                "is_owner": False,
                "invited_at": collab.get("invited_at"),
                "invited_by": collab.get("invited_by")
            })
    except Exception as e:
        print(f"Failed to get workflow collaborators from table: {e}")
        # Continue to legacy collaborators if table query fails
    
    # Add legacy collaborators (as viewers)
    legacy_collaborators = workflow_data.get("collaborators", []) or []
    for email in legacy_collaborators:
        # Skip if already in  collaborators
        if not any(c["email"] == email for c in collaborators):
            collaborators.append({
                "email": email,
                "role": WorkflowRole.VIEWER.value,
                "is_owner": False,
                "invited_at": None,
                "invited_by": "Legacy"
            })
    
    return collaborators