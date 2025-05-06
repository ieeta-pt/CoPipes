import os

from fastapi import FastAPI, HTTPException, UploadFile, File
import httpx
from fastapi import BackgroundTasks

from utils.dag_factory import generate_dag
from utils.airflow_api import trigger_dag_run, get_airflow_dags

from schemas.workflow import WorkflowRequest

app = FastAPI()

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

API_AUTH = auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

UPLOAD_DIR = "/shared_data/"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/workflows")
async def receive_workflow(workflow: WorkflowRequest):
    print("✅ Received workflow:")
    try:
        generate_dag(workflow.dict())
        dag_id = workflow.dag_id
        # background_tasks.add_task(trigger_dag_run, dag_id)
        return {"status": "success", "message": "Workflow received and DAG created", "dag_id": dag_id}
    except Exception as e:
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

        