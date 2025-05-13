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
            self.client.table("workflows").insert(workflow.dict()).execute()
            print("Inserted workflow into Supabase")
        except Exception as e:
            print(f"Failed to insert workflow into Supabase: {e}")
            raise
    
    def update_workflow(self, workflow_name, update_data: WorkflowDB):
        """Update a workflow in the database."""
        try:
            self.client.table("workflows").update(update_data.dict()).eq("name", workflow_name).execute()
            print(f"Updated workflow {workflow_name} in Supabase")
        except Exception as e:
            print(f"Failed to update workflow {workflow_name} in Supabase: {e}")
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

    def update_workflow(self, workflow_name, update_data: WorkflowDB):
        """Update a workflow in the database."""
        try:
            self.client.table("workflows").update(update_data.dict()).eq("name", workflow_name).execute()
            print(f"Updated workflow {workflow_name} in Supabase")
        except Exception as e:
            print(f"Failed to update workflow {workflow_name} in Supabase: {e}")
            raise

    def delete_workflow(self, workflow_name):
        """Delete a workflow from the database."""
        try:
            self.client.table("workflows").delete().eq("name", workflow_name).execute()
            print(f"Deleted workflow {workflow_name} from Supabase")
        except Exception as e:
            print(f"Failed to delete workflow {workflow_name} from Supabase: {e}")
            raise