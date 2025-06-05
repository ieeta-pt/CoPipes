import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from datetime import datetime
import traceback
import json

from utils.dag_factory import generate_dag, remove_dag
from utils.airflow_api import trigger_dag_run, get_dag_runs, get_dag_run_details, get_task_instances, get_task_xcom_entries
from utils.auth import get_current_user
from utils.workflow_permissions import (
    get_user_workflows, check_workflow_access, get_workflow_collaborators,
    add_workflow_collaborator, update_workflow_collaborator_role, remove_workflow_collaborator
)

from database import SupabaseClient
from schemas.workflow import (
    WorkflowAirflow, WorkflowDB,
    AddCollaboratorRequest, UpdateCollaboratorRequest
)

UPLOAD_DIR = "/shared_data/"

router = APIRouter(
    prefix="/api/workflows",
    tags=["workflows"]
)

supabase = SupabaseClient()

@router.post("/new")
async def receive_workflow(workflow: WorkflowAirflow, current_user: dict = Depends(get_current_user), organization_id: str = None):
    try:
        # Generate DAG with user context
        actual_dag_id = generate_dag(workflow.model_dump(), current_user["id"])
        
        workflow_db = WorkflowDB(
            name=workflow.dag_id.replace("_", " "),
            last_edit=datetime.now().isoformat(),
            user_id=current_user["id"],
            organization_id=organization_id,
            collaborators=[]
        )
        supabase.add_workflow(workflow_db, workflow.tasks)
        
        return {"status": "success", "message": "Workflow received and DAG created", "dag_id": actual_dag_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all")
async def get_workflows(current_user: dict = Depends(get_current_user)):
    try:
        print(f"GET all workflows requested by user: {current_user['id']} ({current_user['email']})")
        workflows = get_user_workflows(current_user)
        print(f"Returning {len(workflows)} workflows for user {current_user['email']}")
        return workflows
    except HTTPException as he:
        print(f"HTTPException getting workflows for user: {he.status_code} - {he.detail}")
        raise he
    except Exception as e:
        print(f"Error getting workflows: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{workflow_name}")
async def get_workflow(workflow_name: str, current_user: dict = Depends(get_current_user)):
    try:
        print(f"GET workflow '{workflow_name}' requested by user: {current_user['id']} ({current_user['email']})")
        workflow_data, permissions = check_workflow_access(workflow_name, current_user, "can_edit")
        workflow_tasks = supabase.get_workflow_tasks(workflow_name, current_user["id"], current_user["email"])
        if workflow_tasks is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        print(f"Successfully retrieved workflow '{workflow_name}' for user {current_user['email']}")
        return {
            "dag_id": workflow_name, 
            "tasks": workflow_tasks,
            "permissions": permissions.model_dump(),
            "collaborators": workflow_data.get("collaborators", [])
        }
    except HTTPException as he:
        print(f"HTTPException getting workflow '{workflow_name}' for user {current_user['email']}: {he.status_code} - {he.detail}")
        raise he
    except Exception as e:
        print(f"Error getting workflow '{workflow_name}' for user {current_user['email']}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{workflow_name}")
async def update_workflow(workflow_name: str, workflow: WorkflowAirflow, current_user: dict = Depends(get_current_user)):
    try:
        workflow_data, permissions = check_workflow_access(workflow_name, current_user, "can_edit")
        
        workflow_id = workflow_data["id"]
        update_data = {"last_edit": datetime.now().isoformat()}
        supabase.update_workflow(workflow_id, update_data, workflow.tasks)
        
        # Generate DAG with owner context (DAGs are always generated with owner's ID)
        actual_dag_id = generate_dag(workflow.model_dump(), workflow_data["user_id"])
        
        return {"status": "success", "message": f"Workflow {actual_dag_id} updated"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{workflow_name}")
async def delete_workflow(workflow_name: str, current_user: dict = Depends(get_current_user)):
    try:
        workflow_data, permissions = check_workflow_access(workflow_name, current_user, "can_delete")
        
        # First delete from database (use owner's ID for workflow deletion)
        supabase.delete_workflow(workflow_name, workflow_data["user_id"])
        print(f"Workflow {workflow_name} deleted from database")
        
        # Then try to remove the DAG file (use owner's ID for DAG deletion)
        try:
            remove_dag(workflow_name, workflow_data["user_id"])
            return {"status": "success", "message": f"Workflow {workflow_name} deleted successfully"}
        except Exception as dag_error:
            print(f"Warning: DAG file removal had issues: {dag_error}")
            # Even if DAG file deletion has issues, the workflow is removed from DB
            return {
                "status": "success", 
                "message": f"Workflow {workflow_name} deleted from database. DAG file may need manual cleanup.",
                "warning": "DAG file cleanup may be incomplete due to permission issues"
            }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/execute/{workflow_name}")
async def trigger_workflow(workflow: WorkflowAirflow, _background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    try:
        workflow_data_db, permissions = check_workflow_access(workflow.dag_id.replace("_", " "), current_user, "can_execute")
            
        # Generate DAG with owner context (DAGs are always generated with owner's ID)
        workflow_data = workflow.model_dump()
        _actual_dag_id = generate_dag(workflow_data, workflow_data_db["user_id"])
        
        # Determine schedule type based on the payload
        schedule_type = "now"  # default
        if workflow_data.get("schedule") == "@once" and workflow_data.get("start_date"):
            schedule_type = "later"
        elif workflow_data.get("schedule") and workflow_data.get("schedule") != "@once":
            schedule_type = "multiple"
        
        print(f"Schedule type determined: {schedule_type}")
        
        # Trigger the DAG or just schedule it based on type (use owner's ID)
        run_result = await trigger_dag_run(workflow.dag_id, workflow_data_db["user_id"], schedule_type)
        # Update the last run status with the actual result (use owner's ID)
        supabase.update_workflow_last_run(workflow.dag_id, run_result["status"], workflow_data_db["user_id"])

        # Customize message based on schedule type
        if schedule_type == "now":
            message = f"Workflow {workflow.dag_id} executed immediately"
        elif schedule_type == "later":
            message = f"Workflow {workflow.dag_id} scheduled for later execution"
        else:  # multiple
            message = f"Workflow {workflow.dag_id} scheduled with recurring schedule"
        
        return {
            "status": "success", 
            "message": message,
            "execution_result": run_result
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_workflow(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a workflow JSON file and create a new workflow."""
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are allowed")
        
        # Read and parse the JSON content
        content = await file.read()
        try:
            workflow_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Validate required fields
        if 'dag_id' not in workflow_data or 'tasks' not in workflow_data:
            raise HTTPException(status_code=400, detail="Missing required fields: dag_id or tasks")
        
        # Create WorkflowAirflow object from uploaded data
        workflow = WorkflowAirflow(**workflow_data)
        
        # Generate DAG file with user context
        _actual_dag_id = generate_dag(workflow.model_dump(), current_user["id"])
        
        # Save to database
        workflow_db = WorkflowDB(
            name=workflow.dag_id.replace("_", " "),
            last_edit=datetime.now().isoformat(),
            user_id=current_user["id"],
            collaborators=[]
        )
        supabase.add_workflow(workflow_db, workflow.tasks)
        
        return {
            "status": "success", 
            "message": "Workflow uploaded successfully", 
            "dag_id": workflow.dag_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload workflow: {str(e)}")
    
@router.post("/file_input")
async def file_input(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a file to the server."""
    """This endpoint is for uploading files that can be used as inputs to workflows."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"status": "saved", "filename": file.filename}

@router.get("/{workflow_name}/runs")
async def get_workflow_runs(workflow_name: str, current_user: dict = Depends(get_current_user)):
    """Get recent runs for a workflow."""
    try:
        # Convert workflow name to user-specific DAG ID
        workflow_name_clean = workflow_name.replace("_", " ")
        workflow = supabase.get_workflow_by_name(workflow_name_clean, current_user["id"])
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Generate the actual DAG ID that would be used in Airflow
        sanitized_user_id = current_user["id"].replace("-", "_")
        dag_id = f"user_{sanitized_user_id}_{workflow_name}"
        
        runs = await get_dag_runs(dag_id, limit=5)
        return {"runs": runs}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_name}/runs/{dag_run_id}")
async def get_workflow_run_details(
    workflow_name: str, 
    dag_run_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Get detailed results for a specific workflow run."""
    try:
        # Convert workflow name to user-specific DAG ID
        workflow_name_clean = workflow_name.replace("_", " ")
        workflow = supabase.get_workflow_by_name(workflow_name_clean, current_user["id"])
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Generate the actual DAG ID that would be used in Airflow
        sanitized_user_id = current_user["id"].replace("-", "_")
        dag_id = f"user_{sanitized_user_id}_{workflow_name}"
        
        # Get DAG run details
        dag_run = await get_dag_run_details(dag_id, dag_run_id)
        
        # Get task instances
        task_instances = await get_task_instances(dag_id, dag_run_id)
        
        # Get XCOM for each task (limited to avoid overwhelming response)
        tasks_with_logs = []
        for task in task_instances[:10]:  # Limit to first 10 tasks
            try:
                # Get XCOM entries
                xcom_entries = await get_task_xcom_entries(dag_id, dag_run_id, task["task_id"])
                
                tasks_with_logs.append({
                    **task,
                    "xcom_entries": xcom_entries
                })
            except Exception as e:
                traceback.print_exc()
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to get XCOM entries for task {task['task_id']}: {str(e)}"
                )
        
        return {
            "dag_run": dag_run,
            "task_instances": tasks_with_logs
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




#  Collaborator Management Routes
@router.post("/{workflow_name}/collaborators")
async def add_collaborator(
    workflow_name: str, 
    request: AddCollaboratorRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Add a collaborator with specific role to a workflow."""
    try:
        workflow_data, _ = check_workflow_access(workflow_name, current_user, "can_manage_permissions")
        
        # Validate email format
        if "@" not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Check if collaborator email is the same as owner
        if request.email.lower() == current_user["email"].lower():
            raise HTTPException(status_code=400, detail="Cannot add yourself as a collaborator")
        
        # Check if user exists in the system
        user_exists = supabase.check_user_exists_by_email(request.email)
        if not user_exists:
            raise HTTPException(
                status_code=400, 
                detail=f"User with email '{request.email}' is not registered. Please ask them to create an account first."
            )
        
        # Add collaborator to the workflow_collaborators table
        supabase.add_workflow_collaborator_to_table(
            workflow_data["id"], 
            request.email, 
            request.role.value, 
            current_user["id"]
        )
        
        return {
            "status": "success", 
            "message": f"Added {request.email} as {request.role.value} to {workflow_name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        # Handle duplicate collaborator error specifically
        if hasattr(e, 'code') and e.code == '23505':
            raise HTTPException(
                status_code=409, 
                detail=f"User '{request.email}' is already a collaborator on this workflow"
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{workflow_name}/collaborators/{collaborator_email}/role")
async def update_collaborator_role(
    workflow_name: str, 
    collaborator_email: str, 
    request: UpdateCollaboratorRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Update a collaborator's role in a workflow."""
    try:
        workflow_data, _ = check_workflow_access(workflow_name, current_user, "can_manage_permissions")
        
        # Update collaborator role in the workflow_collaborators table
        supabase.update_workflow_collaborator_role_in_table(
            workflow_data["id"], 
            collaborator_email, 
            request.role.value
        )
        
        return {
            "status": "success", 
            "message": f"Updated {collaborator_email} role to {request.role.value} in {workflow_name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{workflow_name}/collaborators/{collaborator_email}")
async def remove_collaborator(
    workflow_name: str, 
    collaborator_email: str, 
    current_user: dict = Depends(get_current_user)
):
    """Remove a collaborator from a workflow ( version)."""
    try:
        workflow_data, _ = check_workflow_access(workflow_name, current_user, "can_manage_permissions")
        
        # Remove collaborator from the workflow_collaborators table
        supabase.remove_workflow_collaborator_from_table(
            workflow_data["id"], 
            collaborator_email
        )
        
        return {
            "status": "success", 
            "message": f"Removed {collaborator_email} from {workflow_name} collaborators"
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_name}/collaborators")
async def get_collaborators(workflow_name: str, current_user: dict = Depends(get_current_user)):
    """Get list of collaborators with their roles for a workflow."""
    try:
        workflow_data, permissions = check_workflow_access(workflow_name, current_user, "can_view")
        
        # Get collaborators using  permissions
        collaborators = get_workflow_collaborators(workflow_data, current_user)
        
        return {
            "workflow_name": workflow_name,
            "collaborators": collaborators,
            "permissions": permissions.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{workflow_name}/copy")
async def copy_workflow(workflow_name: str, current_user: dict = Depends(get_current_user)):
    """Create a copy/fork of a workflow."""
    try:
        workflow_data, _ = check_workflow_access(workflow_name, current_user, "can_copy")
        
        # Get original workflow tasks
        workflow_tasks = supabase.get_workflow_tasks(workflow_name, workflow_data["user_id"], current_user["email"])
        if workflow_tasks is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create new workflow name
        original_name = workflow_data["name"]
        new_name = f"{original_name} (Copy)"
        counter = 1
        while supabase.get_workflow_by_name(new_name, current_user["id"]):
            counter += 1
            new_name = f"{original_name} (Copy {counter})"
        
        # Create new workflow
        new_dag_id = new_name.replace(" ", "_")
        new_workflow = WorkflowAirflow(
            dag_id=new_dag_id,
            schedule="@once",
            start_date=None,
            tasks=workflow_tasks
        )
        
        # Generate DAG for the copy
        actual_dag_id = generate_dag(new_workflow.model_dump(), current_user["id"])
        
        # Save copy to database
        workflow_db = WorkflowDB(
            name=new_name,
            last_edit=datetime.now().isoformat(),
            user_id=current_user["id"],
            organization_id=workflow_data.get("organization_id"),
            collaborators=[],
            workflow_collaborators=[]
        )
        supabase.add_workflow(workflow_db, new_workflow.tasks)
        
        return {
            "status": "success", 
            "message": f"Created copy of {workflow_name} as {new_name}",
            "new_workflow_name": new_name,
            "dag_id": actual_dag_id
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Organization-specific workflow routes
@router.get("/organization/{org_id}")
async def get_organization_workflows_endpoint(
    org_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Get all workflows belonging to an organization."""
    try:
        # Use the imported function with correct name to avoid conflict
        from utils.workflow_permissions import get_organization_workflows as get_org_workflows
        
        workflows = get_org_workflows(org_id, current_user)
        return {"workflows": workflows, "organization_id": org_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/organization/{org_id}/new")
async def create_organization_workflow(
    org_id: str,
    workflow: WorkflowAirflow,
    current_user: dict = Depends(get_current_user)
):
    """Create a new workflow within an organization."""
    try:
        # Check if user is a member of the organization
        from services.organization_service import OrganizationService
        org_service = OrganizationService()
        user_role = org_service.get_user_role_in_organization(org_id, current_user["id"])
        
        if user_role is None:
            raise HTTPException(status_code=403, detail="Access denied: Not a member of this organization")
        
        # Generate DAG with user context
        actual_dag_id = generate_dag(workflow.model_dump(), current_user["id"])
        
        workflow_db = WorkflowDB(
            name=workflow.dag_id.replace("_", " "),
            last_edit=datetime.now().isoformat(),
            user_id=current_user["id"],
            organization_id=org_id,
            collaborators=[]
        )
        supabase.add_workflow(workflow_db, workflow.tasks)
        
        return {
            "status": "success", 
            "message": "Organization workflow created successfully", 
            "dag_id": actual_dag_id,
            "organization_id": org_id
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))