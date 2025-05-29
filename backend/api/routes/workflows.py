from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from datetime import datetime
import traceback
import json

from utils.dag_factory import generate_dag, remove_dag
from utils.airflow_api import trigger_dag_run

from database import SupabaseClient
from schemas.workflow import WorkflowAirflow, WorkflowDB

router = APIRouter(
    prefix="/api/workflows",
    tags=["workflows"]
)

supabase = SupabaseClient()

@router.post("/new")
async def receive_workflow(workflow: WorkflowAirflow):
    try:
        generate_dag(workflow.model_dump())
        
        workflow_db = WorkflowDB(
            name=workflow.dag_id.replace("_", " "),
            last_edit=datetime.now().isoformat(),
        )
        supabase.add_workflow(workflow_db, workflow.tasks)
        
        return {"status": "success", "message": "Workflow received and DAG created", "dag_id": workflow.dag_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all")
async def get_workflows():
    try:
        workflows = supabase.get_workflows()
        return workflows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{workflow_name}")
async def get_workflow(workflow_name: str):
    try:
        workflow_tasks = supabase.get_workflow_tasks(workflow_name)
        if not workflow_tasks:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"dag_id": workflow_name, "tasks": workflow_tasks}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{workflow_name}")
async def update_workflow(workflow_name: str, workflow: WorkflowAirflow):
    try:
        supabase.update_workflow(workflow.model_dump(), workflow.tasks)
        
        generate_dag(workflow.model_dump())
        
        return {"status": "success", "message": f"Workflow {workflow.dag_id} updated"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{workflow_name}")
async def delete_workflow(workflow_name: str):
    try:
        supabase.delete_workflow(workflow_name)
        remove_dag(workflow_name)
        return {"status": "success", "message": f"Workflow {workflow_name} deleted"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/execute/{workflow_name}")
async def trigger_workflow(workflow: WorkflowAirflow, background_tasks: BackgroundTasks):
    try:
        generate_dag(workflow.model_dump())
        # run_status = background_tasks.add_task(trigger_dag_run, workflow.dag_id)
        # Trigger the DAG and wait for the result
        run_status = await trigger_dag_run(workflow.dag_id)
        # Update the last run status with the actual result
        supabase.update_workflow_last_run(workflow.dag_id, run_status)

        return {"status": "success", "message": f"Workflow {workflow.dag_id} triggered"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_workflow(file: UploadFile = File(...)):
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
        
        # Generate DAG file
        generate_dag(workflow.model_dump())
        
        # Save to database
        workflow_db = WorkflowDB(
            name=workflow.dag_id.replace("_", " "),
            last_edit=datetime.now().isoformat(),
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