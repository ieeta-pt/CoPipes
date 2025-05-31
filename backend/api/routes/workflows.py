from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from datetime import datetime
import traceback
import json

from utils.dag_factory import generate_dag, remove_dag, fix_dag_permissions
from utils.airflow_api import trigger_dag_run, get_dag_runs, get_dag_run_details, get_task_instances, get_task_logs, get_task_xcom_entries
from utils.auth import get_current_user

from database import SupabaseClient
from schemas.workflow import WorkflowAirflow, WorkflowDB

router = APIRouter(
    prefix="/api/workflows",
    tags=["workflows"]
)

supabase = SupabaseClient()

@router.post("/new")
async def receive_workflow(workflow: WorkflowAirflow, current_user: dict = Depends(get_current_user)):
    try:
        # Generate DAG with user context
        actual_dag_id = generate_dag(workflow.model_dump(), current_user["id"])
        
        workflow_db = WorkflowDB(
            name=workflow.dag_id.replace("_", " "),
            last_edit=datetime.now().isoformat(),
            user_id=current_user["id"]
        )
        supabase.add_workflow(workflow_db, workflow.tasks)
        
        return {"status": "success", "message": "Workflow received and DAG created", "dag_id": actual_dag_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all")
async def get_workflows(current_user: dict = Depends(get_current_user)):
    try:
        workflows = supabase.get_workflows(current_user["id"])
        return workflows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{workflow_name}")
async def get_workflow(workflow_name: str, current_user: dict = Depends(get_current_user)):
    try:
        workflow_tasks = supabase.get_workflow_tasks(workflow_name, current_user["id"])
        if not workflow_tasks:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"dag_id": workflow_name, "tasks": workflow_tasks}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{workflow_name}")
async def update_workflow(workflow_name: str, workflow: WorkflowAirflow, current_user: dict = Depends(get_current_user)):
    try:
        # Get workflow id first
        workflow_name_clean = workflow_name.replace("_", " ")
        workflows = supabase.get_workflows(current_user["id"])
        workflow_record = next((w for w in workflows if w["name"] == workflow_name_clean), None)
        
        if not workflow_record:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_id = workflow_record["id"]
        update_data = {"last_edit": datetime.now().isoformat()}
        supabase.update_workflow(workflow_id, update_data, workflow.tasks)
        
        # Generate DAG with user context
        actual_dag_id = generate_dag(workflow.model_dump(), current_user["id"])
        
        return {"status": "success", "message": f"Workflow {actual_dag_id} updated"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{workflow_name}")
async def delete_workflow(workflow_name: str, current_user: dict = Depends(get_current_user)):
    try:
        # First delete from database
        supabase.delete_workflow(workflow_name, current_user["id"])
        print(f"Workflow {workflow_name} deleted from database")
        
        # Then try to remove the DAG file
        try:
            remove_dag(workflow_name, current_user["id"])
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

@router.post("/admin/fix-permissions")
async def fix_permissions(_current_user: dict = Depends(get_current_user)):
    """Admin endpoint to fix DAG file permissions."""
    try:
        success = fix_dag_permissions()
        if success:
            return {"status": "success", "message": "DAG permissions fixed successfully"}
        else:
            return {"status": "warning", "message": "Permission fix completed with some warnings"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fix permissions: {str(e)}")
    
@router.post("/execute/{workflow_name}")
async def trigger_workflow(workflow: WorkflowAirflow, _background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    try:
        # Verify user owns this workflow
        workflow_tasks = supabase.get_workflow_tasks(workflow.dag_id.replace("_", " "), current_user["id"])
        if not workflow_tasks:
            raise HTTPException(status_code=404, detail="Workflow not found or access denied")
            
        # Generate DAG with user context
        workflow_data = workflow.model_dump()
        _actual_dag_id = generate_dag(workflow_data, current_user["id"])
        
        # Determine schedule type based on the payload
        schedule_type = "now"  # default
        if workflow_data.get("schedule") == "@once" and workflow_data.get("start_date"):
            schedule_type = "later"
        elif workflow_data.get("schedule") and workflow_data.get("schedule") != "@once":
            schedule_type = "multiple"
        
        print(f"Schedule type determined: {schedule_type}")
        
        # Trigger the DAG or just schedule it based on type
        run_result = await trigger_dag_run(workflow.dag_id, current_user["id"], schedule_type)
        # Update the last run status with the actual result
        supabase.update_workflow_last_run(workflow.dag_id, run_result["status"], current_user["id"])

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
            user_id=current_user["id"]
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

@router.get("/{workflow_name}/runs")
async def get_workflow_runs(workflow_name: str, current_user: dict = Depends(get_current_user)):
    """Get recent runs for a workflow."""
    try:
        # Convert workflow name to user-specific DAG ID
        workflow_name_clean = workflow_name.replace("_", " ")
        workflows = supabase.get_workflows(current_user["id"])
        workflow_record = next((w for w in workflows if w["name"] == workflow_name_clean), None)
        
        if not workflow_record:
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
        workflows = supabase.get_workflows(current_user["id"])
        workflow_record = next((w for w in workflows if w["name"] == workflow_name_clean), None)
        
        if not workflow_record:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Generate the actual DAG ID that would be used in Airflow
        sanitized_user_id = current_user["id"].replace("-", "_")
        dag_id = f"user_{sanitized_user_id}_{workflow_name}"
        
        # Get DAG run details
        dag_run = await get_dag_run_details(dag_id, dag_run_id)
        
        # Get task instances
        task_instances = await get_task_instances(dag_id, dag_run_id)
        
        # Get logs and XCOM for each task (limited to avoid overwhelming response)
        tasks_with_logs = []
        for task in task_instances[:10]:  # Limit to first 10 tasks
            try:
                # Get logs
                logs = await get_task_logs(dag_id, dag_run_id, task["task_id"], task.get("try_number", 1))
                
                # Get XCOM entries
                xcom_entries = await get_task_xcom_entries(dag_id, dag_run_id, task["task_id"])
                
                tasks_with_logs.append({
                    **task,
                    "logs": logs,
                    "xcom_entries": xcom_entries
                })
            except Exception as log_error:
                # If we can't get logs for a task, include it without logs but try to get XCOM
                try:
                    xcom_entries = await get_task_xcom_entries(dag_id, dag_run_id, task["task_id"])
                except:
                    xcom_entries = []
                    
                tasks_with_logs.append({
                    **task,
                    "logs": {"content": f"Failed to retrieve logs: {str(log_error)}"},
                    "xcom_entries": xcom_entries
                })
        
        return {
            "dag_run": dag_run,
            "task_instances": tasks_with_logs
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))