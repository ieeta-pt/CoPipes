import os

from fastapi import FastAPI, HTTPException, UploadFile, File
import httpx

from schemas.dags import CreateDAG
from utils.dag_factory import generate_dag

from schemas.workflow import WorkflowRequest

app = FastAPI()

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

API_AUTH = auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

UPLOAD_DIR = "/shared_data"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/workflows")
async def receive_workflow(workflow: WorkflowRequest):
    print("✅ Received workflow:")
    for comp in workflow.components:
        print(f"  • {comp.content} [{comp.type}]")
    return {"status": "success", "received": len(workflow.components)}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"status": "saved", "filename": file.filename}

@app.get("/get_dags")
async def get_airflow_dags():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(AIRFLOW_API_URL, auth=API_AUTH)
            response.raise_for_status()  
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")
        
@app.get("/run_dag/{dag_id}")
async def trigger_dag_run(dag_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://airflow-webserver:8080/api/v1/dags/{dag_id}/dagRuns", auth=API_AUTH)
            response.raise_for_status()  
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")
        
@app.post("/create_dag")
async def create_dag(dag_definition: CreateDAG):
    """API endpoint to generate DAG dynamically."""
    try:
        dag_file = generate_dag(dag_definition.dict())
        return {"message": "DAG created successfully", "dag_path": str(dag_file)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))