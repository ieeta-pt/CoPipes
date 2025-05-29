import httpx
import os
import asyncio
from fastapi import HTTPException

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_ADMIN_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")
API_AUTH = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

async def wait_for_dag_to_register(dag_id: str, retries: int = 100, delay: float = 5.0):
    """Poll the Airflow API until the DAG is available (or until retries are exhausted)."""
    dag_url = f"{AIRFLOW_API_URL}/dags/{dag_id}"
    
    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            print(f"🔁 Checking if DAG '{dag_id}' is registered (attempt {attempt + 1})...")
            try:
                response = await client.get(dag_url, auth=API_AUTH)
                if response.status_code == 200:
                    print(f"✅ DAG '{dag_id}' is registered in Airflow.")
                    return True
            except httpx.RequestError:
                pass
            await asyncio.sleep(delay)
    
    raise HTTPException(status_code=404, detail=f"DAG '{dag_id}' not found after {retries} retries.")

async def trigger_dag_run(name: str):
    """Trigger a DAG run only after DAG is confirmed to exist."""
    dag_id = name.replace(" ", "_")
    await wait_for_dag_to_register(dag_id)

    trigger_url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(trigger_url, json={}, auth=API_AUTH)
            print(f"🚀 DAG trigger response: {response.json()}")
            response.raise_for_status()
            status = response.json().get("state", "unknown")
            if status == "queued":
                # Wait for up to 60 seconds, checking every 5 seconds
                max_retries = 12
                retry_delay = 5
                dag_run_id = response.json().get("dag_run_id")
                if dag_run_id:
                    for _ in range(max_retries):
                        await asyncio.sleep(retry_delay)
                        status_url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}"
                        status_response = await client.get(status_url, auth=API_AUTH)
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            current_state = status_data.get("state")
                            if current_state in ["success", "failed"]:
                                status = current_state
                                break
                            print(f"DAG run status: {current_state}, waiting...")
            return status
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")
        
async def get_airflow_dags():
    """Fetch the list of DAGs from the Airflow API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AIRFLOW_API_URL}/dags", auth=API_AUTH)
            response.raise_for_status()
            return response.json().get("dags", [])
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")
        