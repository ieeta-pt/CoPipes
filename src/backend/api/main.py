import os
from dotenv import load_dotenv

load_dotenv() 

import sys
sys.path.append(os.path.abspath("/home/raquelparadinha/Desktop/MEI/2ano/thesis-dev/airflow_setup"))

from fastapi import FastAPI, HTTPException
import httpx
from airflow_setup.dags.dag_manager import create_dag

from typing import Dict, Any
from datetime import datetime

app = FastAPI()




AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_dags")
async def get_airflow_dags():
    auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)  

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(AIRFLOW_API_URL, auth=auth)
            response.raise_for_status()  
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")
        
default_args = {
    "owner": "airflow",
    "start_date": datetime(2018, 1, 1),
    "email": ["someEmail@gmail.com"],
    "email_on_failure": False,
}

@app.post("/create_dag")
async def create_dag(definition: Dict[str, Any]):
    try:
        result = create_dag(None, default_args, definition)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))