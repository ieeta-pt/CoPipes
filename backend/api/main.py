import os

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
import httpx

from utils.dag_factory import generate_dag, remove_dag
from utils.airflow_api import trigger_dag_run, get_airflow_dags

from schemas.workflow import WorkflowAirflow, WorkflowDB
from datetime import datetime
import random

from database import SupabaseClient 
import traceback

app = FastAPI()
supabase = SupabaseClient()

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

API_AUTH = auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

UPLOAD_DIR = "/shared_data/"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/workflows")
async def receive_workflow(workflow: WorkflowAirflow):
    try:
        generate_dag(workflow.dict())
        
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
    
@app.get("/api/workflows")
async def get_workflows():
    try:
        workflows = supabase.get_workflows()
        return workflows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/workflows/{workflow_name}")
async def get_workflow(workflow_name: str):
    try:
        workflow_tasks = supabase.get_workflow_tasks(workflow_name)
        if not workflow_tasks:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"dag_id": workflow_name, "tasks": workflow_tasks}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/api/workflows/{workflow_name}")
async def update_workflow(workflow_name: str, workflow: WorkflowAirflow):
    try:
        workflow_db = WorkflowDB(
            name=workflow.dag_id,
            last_edit=datetime.now().isoformat(),
        )
        supabase.update_workflow(workflow_db, workflow.tasks)
        
        generate_dag(workflow.dict())
        
        return {"status": "success", "message": f"Workflow {workflow.dag_id} updated"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/api/workflows/{workflow_name}")
async def delete_workflow(workflow_name: str):
    try:
        supabase.delete_workflow(workflow_name)
        remove_dag(workflow_name)
        return {"status": "success", "message": f"Workflow {workflow_name} deleted"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"status": "saved", "filename": file.filename}

@app.get("/api/get_dags")
async def get_dags():
    try:
        dags = await get_airflow_dags()
        print(f"✅ Fetched DAGs: {dags}")
        return {"status": "success", "dags": dags}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

        