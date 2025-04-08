import httpx
import os

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
API_AUTH = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

async def trigger_dag_run(dag_id: str):
    print(f"Triggering DAG run for {dag_id}...")
    async with httpx.AsyncClient() as client:
        print(f"Sending request to {AIRFLOW_API_URL}/{dag_id}/dagRuns")
        try:
            response = await client.post(f"{AIRFLOW_API_URL}/{dag_id}/dagRuns", auth=API_AUTH)
            print(f"Response status code: {response.status_code}")
            response.raise_for_status()  
            print(f"Response content: {response.content}")
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")