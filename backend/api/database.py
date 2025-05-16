import os
from supabase import create_client, Client
from schemas.workflow import WorkflowDB
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
from utils.auth import get_password_hash

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
# SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET')

# if not all([SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET, SUPABASE_BUCKET]):
#     raise EnvironmentError("One or more Supabase environment variables are missing.")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise EnvironmentError("One or more Supabase environment variables are missing.")   

class SupabaseClient:
    """Supabase client for interacting with the database."""
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def get_client(self) -> Client:
        return self.client
    
    # Authentication methods
    def create_user(self, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user in the database."""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")
                
            # Hash the password
            hashed_password = get_password_hash(password)
            
            # Create user data
            user_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            
            user_data = {
                "id": user_id,
                "email": email,
                "password": hashed_password,
                "full_name": full_name,
                "created_at": created_at
            }
            
            # Insert user into database
            self.client.table("users").insert(user_data).execute()
            
            # Return user data without password
            del user_data["password"]
            return user_data
        except Exception as e:
            print(f"Failed to create user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID."""
        try:
            response = self.client.table("users").select("id, email, full_name, created_at").eq("id", user_id).execute()
            if not response.data:
                return None
            return response.data[0]
        except Exception as e:
            print(f"Failed to get user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email."""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            if not response.data:
                return None
            return response.data[0]
        except Exception as e:
            print(f"Failed to get user by email: {e}")
            raise
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user's information."""
        try:
            # Don't allow updating these fields directly
            if "id" in update_data:
                del update_data["id"]
            if "created_at" in update_data:
                del update_data["created_at"]
                
            # Hash password if it's being updated
            if "password" in update_data:
                update_data["password"] = get_password_hash(update_data["password"])
                
            # Update user
            self.client.table("users").update(update_data).eq("id", user_id).execute()
            
            # Return updated user
            return self.get_user(user_id)
        except Exception as e:
            print(f"Failed to update user: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            self.client.table("users").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            print(f"Failed to delete user: {e}")
            raise
            
    def save_refresh_token(self, user_id: str, refresh_token: str) -> None:
        """Save a refresh token for a user."""
        try:
            token_data = {
                "user_id": user_id,
                "token": refresh_token,
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("refresh_tokens").insert(token_data).execute()
        except Exception as e:
            print(f"Failed to save refresh token: {e}")
            raise
            
    def verify_refresh_token(self, refresh_token: str) -> Optional[str]:
        """Verify a refresh token and return the user ID if valid."""
        try:
            response = self.client.table("refresh_tokens").select("user_id").eq("token", refresh_token).execute()
            if not response.data:
                return None
            return response.data[0]["user_id"]
        except Exception as e:
            print(f"Failed to verify refresh token: {e}")
            raise
            
    def invalidate_refresh_token(self, refresh_token: str) -> None:
        """Invalidate a refresh token."""
        try:
            self.client.table("refresh_tokens").delete().eq("token", refresh_token).execute()
        except Exception as e:
            print(f"Failed to invalidate refresh token: {e}")
            raise
            
    def invalidate_all_user_tokens(self, user_id: str) -> None:
        """Invalidate all refresh tokens for a user."""
        try:
            self.client.table("refresh_tokens").delete().eq("user_id", user_id).execute()
        except Exception as e:
            print(f"Failed to invalidate all user tokens: {e}")
            raise
    
    # Workflow methods
    def add_workflow(self, workflow: WorkflowDB, tasks: list = None):
        """Add a workflow to the database."""
        try:
            # Check if the workflow already exists
            existing_workflow = self.client.table("workflows").select("*").eq("name", workflow.name).execute()
            if existing_workflow.data:
                print(f"Workflow {workflow.name} already exists. Updating instead.")
                self.update_workflow(workflow, tasks)
                return
            self.client.table("workflows").insert(workflow.dict()).execute()
            if tasks: 
                self.add_tasks(workflow.name, tasks)
            print("Inserted workflow into Supabase")
        except Exception as e:
            print(f"Failed to insert workflow into Supabase: {e}")
            raise

    def add_tasks(self, workflow_name, tasks: list):
        """Add tasks to a workflow in the database."""
        try:
            tasks_dict = {i: task.dict() for i, task in enumerate(tasks)}
            self.client.table("tasks").insert({"workflow_name": workflow_name, "tasks": tasks_dict}).execute()
            print(f"Inserted tasks for workflow {workflow_name} into Supabase")
        except Exception as e:
            print(f"Failed to insert tasks for workflow {workflow_name} into Supabase: {e}")
            raise
    
    def update_workflow(self, update_data: WorkflowDB, tasks: list = None):
        """Update a workflow in the database."""
        try:
            name = update_data.name.replace("_", " ")
            self.client.table("workflows").update(update_data.dict()).eq("name", name).execute()
            if tasks:
                self.update_tasks(update_data.name, tasks)
            print(f"Updated workflow {update_data.name} in Supabase")
        except Exception as e:
            print(f"Failed to update workflow {update_data.name} in Supabase: {e}")
            raise
    
    def update_tasks(self, workflow_name, tasks: list):
        """Update tasks for a workflow in the database."""
        try:
            tasks_dict = {i: task.dict() for i, task in enumerate(tasks)}
            self.client.table("tasks").update({"tasks": tasks_dict}).eq("workflow_name", workflow_name).execute()
            print(f"Updated tasks for workflow {workflow_name} in Supabase")
        except Exception as e:
            print(f"Failed to update tasks for workflow {workflow_name} in Supabase: {e}")
            raise

    def get_workflows(self, user_id: str = None):
        """Get all workflows from the database, optionally filtered by user ID."""
        try:
            query = self.client.table("workflows").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            workflows = query.execute()
            print(f"Fetched workflows: {workflows.data}")
            return workflows.data
        except Exception as e:
            print(f"Failed to fetch workflows from Supabase: {e}")
            raise

    def get_workflow_tasks(self, workflow_name, user_id: str = None):
        """Get a specific workflow from the database, optionally checking user_id."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            # First check if the workflow exists and belongs to the user
            if user_id:
                workflow = self.client.table("workflows").select("*").eq("name", workflow_name).eq("user_id", user_id).execute()
                if not workflow.data:
                    print(f"Workflow {workflow_name} not found or doesn't belong to user {user_id} in Supabase")
                    return None
                    
            workflow_tasks = self.client.table("tasks").select("*").eq("workflow_name", workflow_name).execute()
            if not workflow_tasks.data:
                print(f"Workflow {workflow_name} tasks not found in Supabase")
                return None
            print(f"Fetched workflow {workflow_name}: {workflow_tasks.data}")
            tasks = workflow_tasks.data[0]['tasks']
            tasks = [task for task in tasks.values()]
            return tasks
        except Exception as e:
            print(f"Failed to fetch workflow {workflow_name} from Supabase: {e}")
            raise

    def delete_workflow(self, workflow_name, user_id: str = None):
        """Delete a workflow from the database, optionally checking user_id."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            
            # Only delete if it belongs to the user (if user_id is provided)
            query = self.client.table("workflows").delete()
            if user_id:
                query = query.eq("user_id", user_id)
            query.eq("name", workflow_name).execute()
            
            # Also delete the tasks
            self.client.table("tasks").delete().eq("workflow_name", workflow_name).execute()
            
            print(f"Deleted workflow {workflow_name} from Supabase")
        except Exception as e:
            print(f"Failed to delete workflow {workflow_name} from Supabase: {e}")
            raise