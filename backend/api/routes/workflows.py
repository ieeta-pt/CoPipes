from fastapi import APIRouter, HTTPException
from datetime import datetime
import traceback

from utils.dag_factory import generate_dag, remove_dag

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
            name=workflow.dag_id,
            last_edit=datetime.now().isoformat(),
        )
        supabase.add_workflow(workflow_db, workflow.tasks)
        
        # background_tasks.add_task(trigger_dag_run, dag_id)
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
        workflow_db = WorkflowDB(
            name=workflow.dag_id,
            last_edit=datetime.now().isoformat(),
        )
        supabase.update_workflow(workflow_db, workflow.tasks)
        
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