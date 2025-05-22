import os

from fastapi import FastAPI, HTTPException, UploadFile, File

from routes import workflows
from utils.airflow_api import get_airflow_dags

from database import SupabaseClient 

app = FastAPI()
app.include_router(workflows.router)
supabase = SupabaseClient()

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

API_AUTH = auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

UPLOAD_DIR = "/shared_data/"

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

        