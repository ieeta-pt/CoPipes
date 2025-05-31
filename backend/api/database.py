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

    def get_workflow_tasks(self, workflow_name, user_id: str = None):
        """Get a specific workflow from the database."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            
            # First get the workflow to check ownership and get id
            workflow_query = self.client.table("workflows").select("id").eq("name", workflow_name)
            if user_id:
                workflow_query = workflow_query.eq("user_id", user_id)
            
            workflow_result = workflow_query.execute()
            if not workflow_result.data:
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