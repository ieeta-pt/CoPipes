from datetime import datetime
from services.supabase_client import supabase_admin
from schemas.workflow import WorkflowDB

class SupabaseClient:
    """Supabase client for interacting with the database."""
    def __init__(self):
        self.client = supabase_admin

    def add_workflow(self, workflow: WorkflowDB, tasks: list = None):
        """Add a workflow to the database."""
        try:
            # Check if the workflow already exists for this user
            existing_workflow = self.client.table("workflows").select("*").eq("name", workflow.name).eq("user_id", workflow.user_id).execute()
            if existing_workflow.data:
                print(f"Workflow {workflow.name} already exists for user. Updating instead.")
                workflow_id = existing_workflow.data[0]['id']
                update_data = {"last_edit": workflow.last_edit}
                self.update_workflow(workflow_id, update_data, tasks)
                return
            
            # Insert workflow and get the returned id
            result = self.client.table("workflows").insert(workflow.model_dump()).execute()
            workflow_id = result.data[0]['id']
            
            if tasks: 
                self.add_tasks(workflow_id, tasks)
            print("Inserted workflow into Supabase")
        except Exception as e:
            print(f"Failed to insert workflow into Supabase: {e}")
            raise

    def add_tasks(self, workflow_id: int, tasks: list):
        """Add tasks to a workflow in the database."""
        try:
            tasks_dict = {i: task.dict() for i, task in enumerate(tasks)}
            self.client.table("tasks").insert({"workflow_id": workflow_id, "tasks": tasks_dict}).execute()
            print(f"Inserted tasks for workflow_id {workflow_id} into Supabase")
        except Exception as e:
            print(f"Failed to insert tasks for workflow_id {workflow_id} into Supabase: {e}")
            raise
    
    def update_workflow(self, workflow_id: int, update_data: dict, tasks: list = None):
        """Update a workflow in the database."""
        try:
            self.client.table("workflows").update(update_data).eq("id", workflow_id).execute()
            if tasks:
                self.update_tasks(workflow_id, tasks)
            print(f"Updated workflow_id {workflow_id} in Supabase")
        except Exception as e:
            print(f"Failed to update workflow_id {workflow_id} in Supabase: {e}")
            raise
    
    def update_tasks(self, workflow_id: int, tasks: list):
        """Update tasks for a workflow in the database."""
        try:
            tasks_dict = {i: task.dict() for i, task in enumerate(tasks)}
            self.client.table("tasks").update({"tasks": tasks_dict}).eq("workflow_id", workflow_id).execute()
            print(f"Updated tasks for workflow_id {workflow_id} in Supabase")
        except Exception as e:
            print(f"Failed to update tasks for workflow_id {workflow_id} in Supabase: {e}")
            raise

    def get_workflows(self, user_id: str = None):
        """Get all workflows from the database, optionally filtered by user."""
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

    def get_workflow_tasks(self, workflow_name, user_id: str = None, user_email: str = None):
        """Get a specific workflow from the database with collaboration support."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            
            # First try to get workflow as owner
            workflow_result = None
            if user_id:
                workflow_query = self.client.table("workflows").select("*").eq("name", workflow_name).eq("user_id", user_id)
                workflow_result = workflow_query.execute()
            
            # If not found as owner and user_email provided, check collaboration
            if (not workflow_result or not workflow_result.data) and user_email:
                all_workflows_query = self.client.table("workflows").select("*").eq("name", workflow_name)
                all_workflows_result = all_workflows_query.execute()
                
                for workflow in all_workflows_result.data:
                    collaborators = workflow.get("collaborators", []) or []
                    if user_email in collaborators:
                        workflow_result = type('obj', (object,), {'data': [workflow]})()
                        break
            
            if not workflow_result or not workflow_result.data:
                print(f"Workflow {workflow_name} not found or access denied for user {user_id}")
                return None
            
            workflow_id = workflow_result.data[0]['id']
            
            # Get tasks for this workflow
            workflow_tasks = self.client.table("tasks").select("*").eq("workflow_id", workflow_id).execute()
            if not workflow_tasks.data:
                print(f"No tasks found for workflow {workflow_name}")
                return []
            
            print(f"Fetched workflow {workflow_name}: {workflow_tasks.data}")
            tasks = workflow_tasks.data[0]['tasks']
            tasks = [task for task in tasks.values()]
            return tasks
        except Exception as e:
            print(f"Failed to fetch workflow {workflow_name} from Supabase: {e}")
            raise

    def delete_workflow(self, workflow_name, user_id: str = None):
        """Delete a workflow from the database."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            query = self.client.table("workflows").delete().eq("name", workflow_name)
            if user_id:
                query = query.eq("user_id", user_id)
            query.execute()
            print(f"Deleted workflow {workflow_name} from Supabase")
        except Exception as e:
            print(f"Failed to delete workflow {workflow_name} from Supabase: {e}")
            raise

    def update_workflow_last_run(self, workflow_name: str, status: str, user_id: str = None):
        """Update the last run status and timestamp for a workflow."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            update_data = {
                "last_run": datetime.now().isoformat(),
                "status": status
            }
            query = self.client.table("workflows").update(update_data).eq("name", workflow_name)
            if user_id:
                query = query.eq("user_id", user_id)
            query.execute()
            print(f"Updated last run for workflow {workflow_name} in Supabase")
        except Exception as e:
            print(f"Failed to update last run for workflow {workflow_name} in Supabase: {e}")
            raise

    def add_collaborator(self, workflow_id: int, collaborator_email: str):
        """Add a collaborator to a workflow."""
        try:
            # Get current workflow data
            workflow_result = self.client.table("workflows").select("collaborators").eq("id", workflow_id).execute()
            if not workflow_result.data:
                raise Exception(f"Workflow with id {workflow_id} not found")
            
            current_collaborators = workflow_result.data[0].get("collaborators", []) or []
            
            # Ensure it's a list (PostgreSQL text[] should always return a list)
            if not isinstance(current_collaborators, list):
                current_collaborators = []
            
            # Add new collaborator if not already present
            if collaborator_email not in current_collaborators:
                current_collaborators.append(collaborator_email)
                self.client.table("workflows").update({"collaborators": current_collaborators}).eq("id", workflow_id).execute()
                print(f"Added collaborator {collaborator_email} to workflow {workflow_id}")
            else:
                print(f"Collaborator {collaborator_email} already exists for workflow {workflow_id}")
        except Exception as e:
            print(f"Failed to add collaborator to workflow {workflow_id}: {e}")
            raise

    def remove_collaborator(self, workflow_id: int, collaborator_email: str):
        """Remove a collaborator from a workflow."""
        try:
            # Get current workflow data
            workflow_result = self.client.table("workflows").select("collaborators").eq("id", workflow_id).execute()
            if not workflow_result.data:
                raise Exception(f"Workflow with id {workflow_id} not found")
            
            current_collaborators = workflow_result.data[0].get("collaborators", []) or []
            
            # Ensure it's a list (PostgreSQL text[] should always return a list)
            if not isinstance(current_collaborators, list):
                current_collaborators = []
            
            # Remove collaborator if present
            if collaborator_email in current_collaborators:
                current_collaborators.remove(collaborator_email)
                self.client.table("workflows").update({"collaborators": current_collaborators}).eq("id", workflow_id).execute()
                print(f"Removed collaborator {collaborator_email} from workflow {workflow_id}")
            else:
                print(f"Collaborator {collaborator_email} not found for workflow {workflow_id}")
        except Exception as e:
            print(f"Failed to remove collaborator from workflow {workflow_id}: {e}")
            raise

    def get_workflow_by_name(self, workflow_name: str, user_id: str = None):
        """Get workflow data by name."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            query = self.client.table("workflows").select("*").eq("name", workflow_name)
            if user_id:
                query = query.eq("user_id", user_id)
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Failed to fetch workflow {workflow_name}: {e}")
            raise

    def check_user_exists_by_email(self, email: str) -> bool:
        """Check if a user exists in Supabase auth by email."""
        print(f"INFO: Checking user existence for email: {email}")
        
        try:
            response = self.client.table("profiles").select("email").eq("email", email).execute()

            if response.data:
                print(f"INFO: User found with email: {email}")
                return True
            else:
                print("DEBUG: No users found or response doesn't have users attribute")
            
            print(f"INFO: User not found with email: {email}")
            return False
            
        except Exception as e:
            print(f"ERROR: Failed to check user existence: {e}")
            print(f"ERROR: Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            # If there's an error, we'll be conservative and return True
            # This prevents blocking legitimate collaborators due to API issues
            return True

    def add_workflow_collaborator_to_table(self, workflow_id: int, user_email: str, role: str, invited_by_id: str):
        """Add a collaborator to the workflow_collaborators table."""
        try:
            # Get user_id from email
            user_result = self.client.table("profiles").select("id").eq("email", user_email).execute()
            if not user_result.data:
                raise Exception(f"User with email {user_email} not found")
            
            user_id = user_result.data[0]["id"]
            
            # Insert into workflow_collaborators table
            collaborator_data = {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "role": role,
                "invited_by": invited_by_id
            }
            
            self.client.table("workflow_collaborators").insert(collaborator_data).execute()
            print(f"Added collaborator {user_email} with role {role} to workflow {workflow_id}")
            
        except Exception as e:
            print(f"Failed to add collaborator to workflow_collaborators table: {e}")
            raise

    def update_workflow_collaborator_role_in_table(self, workflow_id: int, user_email: str, new_role: str):
        """Update a collaborator's role in the workflow_collaborators table."""
        try:
            # Get user_id from email
            user_result = self.client.table("profiles").select("id").eq("email", user_email).execute()
            if not user_result.data:
                raise Exception(f"User with email {user_email} not found")
            
            user_id = user_result.data[0]["id"]
            
            # Update role in workflow_collaborators table
            self.client.table("workflow_collaborators").update({"role": new_role}).eq("workflow_id", workflow_id).eq("user_id", user_id).execute()
            print(f"Updated collaborator {user_email} role to {new_role} for workflow {workflow_id}")
            
        except Exception as e:
            print(f"Failed to update collaborator role in workflow_collaborators table: {e}")
            raise

    def remove_workflow_collaborator_from_table(self, workflow_id: int, user_email: str):
        """Remove a collaborator from the workflow_collaborators table."""
        try:
            # Get user_id from email
            user_result = self.client.table("profiles").select("id").eq("email", user_email).execute()
            if not user_result.data:
                raise Exception(f"User with email {user_email} not found")
            
            user_id = user_result.data[0]["id"]
            
            # Remove from workflow_collaborators table
            self.client.table("workflow_collaborators").delete().eq("workflow_id", workflow_id).eq("user_id", user_id).execute()
            print(f"Removed collaborator {user_email} from workflow {workflow_id}")
            
        except Exception as e:
            print(f"Failed to remove collaborator from workflow_collaborators table: {e}")
            raise

    def get_workflow_collaborators_from_table(self, workflow_id: int):
        """Get all collaborators for a workflow from the workflow_collaborators table."""
        try:
            result = self.client.table("workflow_collaborators").select("""
                *,
                user:profiles(email, full_name),
                invited_by_user:profiles!invited_by(email, full_name)
            """).eq("workflow_id", workflow_id).execute()
            
            collaborators = []
            for collab in result.data:
                collaborators.append({
                    "email": collab["user"]["email"],
                    "full_name": collab["user"]["full_name"],
                    "role": collab["role"],
                    "invited_at": collab["invited_at"],
                    "invited_by": collab["invited_by_user"]["email"]
                })
            
            return collaborators
            
        except Exception as e:
            print(f"Failed to get collaborators from workflow_collaborators table: {e}")
            raise