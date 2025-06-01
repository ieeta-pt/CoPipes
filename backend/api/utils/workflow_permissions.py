from schemas.workflow import WorkflowPermissions
from database import SupabaseClient

def get_workflow_permissions(workflow_data: dict, current_user: dict) -> WorkflowPermissions:
    """
    Determine user permissions for a specific workflow.
    
    Args:
        workflow_data: The workflow record from database
        current_user: Current authenticated user data
        
    Returns:
        WorkflowPermissions object with permission flags
    """
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    # Check if user is the owner
    is_owner = workflow_data["user_id"] == user_id
    
    # Check if user is a collaborator
    collaborators = workflow_data.get("collaborators", []) or []
    is_collaborator = user_email in collaborators
    
    # Owner permissions
    if is_owner:
        return WorkflowPermissions(
            is_owner=True,
            can_edit=True,
            can_execute=True,
            can_download=True,
            can_delete=True,
            can_manage_collaborators=True
        )
    
    # Collaborator permissions
    if is_collaborator:
        return WorkflowPermissions(
            is_owner=False,
            can_edit=True,
            can_execute=True,
            can_download=True,
            can_delete=False,
            can_manage_collaborators=False
        )
    
    # No access
    return WorkflowPermissions(
        is_owner=False,
        can_edit=False,
        can_execute=False,
        can_download=False,
        can_delete=False,
        can_manage_collaborators=False
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
    
    # Get owner information for all unique user_ids
    unique_owner_ids = set()
    for workflow in owned_workflows + collaborated_workflows:
        unique_owner_ids.add(workflow["user_id"])
    
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
        
        all_user_workflows.append(workflow)
    
    for workflow in collaborated_workflows:
        permissions = get_workflow_permissions(workflow, current_user)
        workflow["permissions"] = permissions.model_dump()
        workflow["role"] = "collaborator"
        
        # Add owner information
        owner_info = owner_details.get(workflow["user_id"], {})
        workflow["owner_email"] = owner_info.get("email", "Unknown")
        workflow["owner_name"] = owner_info.get("full_name")
        
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