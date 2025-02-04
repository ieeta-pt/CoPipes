import os
import subprocess

from fastapi import FastAPI, HTTPException
import httpx

from pathlib import Path
import json

app = FastAPI()

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

API_AUTH = auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

DAG_FACTORY_PATH = Path("/airflow/dags/dag_factory.py")
DAG_OUTPUT_DIR = Path("/airflow/dags/dags_definition")

@app.get("/")
def read_root():
    return {"Hello": "World"}

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
        
@app.post("/create_dag/")
async def create_dag(dag_definition: dict):
    try:
        dag_id = dag_definition.get("dag_id")
        if not dag_id:
            raise HTTPException(status_code=400, detail="DAG ID is required")

        dag_file_path = DAG_OUTPUT_DIR / f"{dag_id}.json"

        # Save DAG definition as JSON
        with open(dag_file_path, "w") as json_file:
            json.dump(dag_definition, json_file, indent=4)

        # Trigger DAG factory script
        process = subprocess.run(
            ["python3", DAG_FACTORY_PATH, "--dag_ide", dag_id],
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error generating DAG: {process.stderr}")

        return {"message": f"DAG '{dag_id}' created and loaded into Airflow successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))