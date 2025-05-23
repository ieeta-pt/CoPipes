import os
from supabase import create_client, Client
from schemas.workflow import WorkflowDB

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
    
    def add_workflow(self, workflow: WorkflowDB, tasks: list = None):
        """Add a workflow to the database."""
        try:
            # Check if the workflow already exists
            existing_workflow = self.client.table("workflows").select("*").eq("name", workflow.name).execute()
            if existing_workflow.data:
                print(f"Workflow {workflow.name} already exists. Updating instead.")
                self.update_workflow(workflow.name, workflow, tasks)
                return
            self.client.table("workflows").insert(workflow.model_dump()).execute()
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

    def get_workflows(self):
        """Get all workflows from the database."""
        try:
            workflows = self.client.table("workflows").select("*").execute()
            print(f"Fetched workflows: {workflows.data}")
            return workflows.data
        except Exception as e:
            print(f"Failed to fetch workflows from Supabase: {e}")
            raise

    def get_workflow_tasks(self, workflow_name):
        """Get a specific workflow from the database."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            workflow_tasks = self.client.table("tasks").select("*").eq("workflow_name", workflow_name).execute()
            if not workflow_tasks.data:
                print(f"Workflow {workflow_name} not found in Supabase")
                return None
            print(f"Fetched workflow {workflow_name}: {workflow_tasks.data}")
            tasks = workflow_tasks.data[0]['tasks']
            tasks = [task for task in tasks.values()]
            return tasks
        except Exception as e:
            print(f"Failed to fetch workflow {workflow_name} from Supabase: {e}")
            raise

    def delete_workflow(self, workflow_name):
        """Delete a workflow from the database."""
        try:
            workflow_name = workflow_name.replace("_", " ")
            self.client.table("workflows").delete().eq("name", workflow_name).execute()
            print(f"Deleted workflow {workflow_name} from Supabase")
        except Exception as e:
            print(f"Failed to delete workflow {workflow_name} from Supabase: {e}")
            raise