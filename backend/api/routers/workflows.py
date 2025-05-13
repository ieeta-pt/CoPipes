from datetime import datetime
import traceback

from fastapi import APIRouter, HTTPException

from schemas.workflow import WorkflowAirflow, WorkflowDB
from utils.dag_factory import generate_dag, remove_dag
from database import SupabaseClient

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found, but I am here to help!"}},
    dependencies=[],
)
supabase = SupabaseClient()

@router.post("/")
async def add_workflow(workflow: WorkflowAirflow):
    try:
        _ = generate_dag(workflow.dict())
        
        workflow_db = WorkflowDB(
            created_at=datetime.now().isoformat(),
            name=workflow.dag_id,
            last_edit=datetime.now().isoformat(),
        )
        supabase.add_workflow(workflow_db)
        
        # background_tasks.add_task(trigger_dag_run, dag_id)
        return {"status": "success", "message": "Workflow received and DAG created", "dag_id": workflow.dag_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/")
async def get_workflows():
    try:
        workflows = supabase.get_workflows()
        return workflows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{workflow_name}")
async def delete_workflow(workflow_name: str):
    try:
        supabase.delete_workflow(workflow_name)
        dag_id = workflow_name.replace(" ", "_").lower()
        remove_dag(dag_id)
        return {"status": "success", "message": f"Workflow {workflow_name} deleted"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))