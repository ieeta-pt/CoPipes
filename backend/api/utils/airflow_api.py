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

async def trigger_dag_run(name: str, user_id: str = None, schedule_type: str = "now"):
    """Trigger a DAG run or just schedule it based on schedule_type."""
    base_dag_id = name.replace(" ", "_")
    
    # Use user-prefixed DAG ID if user_id is provided
    if user_id:
        # Sanitize user_id to replace hyphens with underscores for consistency
        sanitized_user_id = user_id.replace("-", "_")
        dag_id = f"user_{sanitized_user_id}_{base_dag_id}"
    else:
        dag_id = base_dag_id
        
    await wait_for_dag_to_register(dag_id)

    # For "later" and "multiple" scheduling, just confirm the DAG is scheduled (not triggered)
    if schedule_type in ["later", "multiple"]:
        print(f"📅 DAG '{dag_id}' scheduled successfully (will run according to its schedule)")
        return {
            "status": "scheduled",
            "dag_run_id": None,
            "execution_date": None,
            "start_date": None,
            "end_date": None,
            "message": f"DAG scheduled successfully. It will run according to its defined schedule."
        }
    
    # For "now" scheduling, trigger immediately
    trigger_url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(trigger_url, json={}, auth=API_AUTH)
            result = response.json()
            print(f"🚀 DAG trigger response: {result}")
            response.raise_for_status()
            
            status = result.get("state", "unknown")
            dag_run_id = result.get("dag_run_id")
            
            if status == "queued" and dag_run_id:
                # Wait for up to 60 seconds, checking every 5 seconds
                max_retries = 12
                retry_delay = 5
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
            
            return {
                "status": status,
                "dag_run_id": dag_run_id,
                "execution_date": result.get("execution_date"),
                "start_date": result.get("start_date"),
                "end_date": result.get("end_date")
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")

async def get_dag_runs(dag_id: str, limit: int = 10):
    """Get recent DAG runs for a specific DAG."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns",
                params={"limit": limit, "order_by": "-execution_date"},
                auth=API_AUTH
            )
            response.raise_for_status()
            return response.json().get("dag_runs", [])
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")

async def get_dag_run_details(dag_id: str, dag_run_id: str):
    """Get details of a specific DAG run."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}",
                auth=API_AUTH
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")

async def get_task_instances(dag_id: str, dag_run_id: str):
    """Get task instances for a specific DAG run."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
                auth=API_AUTH
            )
            response.raise_for_status()
            return response.json().get("task_instances", [])
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")

async def get_task_xcom_entries(dag_id: str, dag_run_id: str, task_id: str):
    """Get XCOM entries for a specific task instance with their values."""
    async with httpx.AsyncClient() as client:
        try:
            # First, get the list of XCOM entries (metadata only)
            response = await client.get(
                f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries",
                auth=API_AUTH
            )
            response.raise_for_status()
            xcom_entries = response.json().get("xcom_entries", [])
            
            # For each XCOM entry, fetch the actual value
            xcom_entries_with_values = []
            for entry in xcom_entries:
                try:
                    # Get the specific XCOM value by key
                    value_response = await client.get(
                        f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries/{entry['key']}",
                        auth=API_AUTH
                    )
                    if value_response.status_code == 200:
                        value_data = value_response.json()
                        # Add the value to the entry
                        entry_with_value = {**entry, "value": value_data.get("value")}
                        xcom_entries_with_values.append(entry_with_value)
                    else:
                        # If we can't get the value, include the entry without it
                        entry_with_value = {**entry, "value": None}
                        xcom_entries_with_values.append(entry_with_value)
                except httpx.HTTPStatusError:
                    # If individual XCOM value fetch fails, include entry without value
                    entry_with_value = {**entry, "value": None}
                    xcom_entries_with_values.append(entry_with_value)
                except httpx.RequestError:
                    # If individual XCOM value fetch fails, include entry without value
                    entry_with_value = {**entry, "value": None}
                    xcom_entries_with_values.append(entry_with_value)
            
            return xcom_entries_with_values
            
        except httpx.HTTPStatusError as e:
            # XCOM might not exist for all tasks, so we don't raise an error
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=f"Airflow API error: {e}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to Airflow API")
        