import json
import argparse
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import importlib

DAG_DEFINITIONS_PATH = Path("./dags_definition")  
TASK_PACKAGE = "dags.components"  

def generate_dag(dag_id: str):
    """
    Reads the JSON definition for a specific DAG and generates it dynamically.
    """
    dag_json_path = DAG_DEFINITIONS_PATH / f"{dag_id}.json"

    if not dag_json_path.exists():
        print(f"❌ DAG definition file '{dag_json_path}' not found.")
        return

    with open(dag_json_path, "r") as f:
        dag_config = json.load(f)

    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime.strptime(dag_config.get("start_date", "2025-02-01"), "%Y-%m-%d"),
        "retries": dag_config.get("retries", 1),
        "retry_delay": timedelta(minutes=dag_config.get("retry_delay", 5)),
    }

    # Define DAG
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description=dag_config.get("description", ""),
        schedule_interval=dag_config.get("schedule_interval", None),
        catchup=False,
    )

    tasks = {}

    # Create tasks dynamically
    for task in dag_config.get("tasks", []):
        task_id = task["task_id"]
        module_name, function_name = task["function"].rsplit(".", 1)  # Extract module and function name
        
        try:
            module = importlib.import_module(f"{TASK_PACKAGE}.{module_name}")
            task_function = getattr(module, function_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(f"Error loading function {task['function']}: {e}")

        # Define PythonOperator task
        tasks[task_id] = PythonOperator(
            task_id=task_id,
            python_callable=task_function,
            dag=dag
        )

    # Define dependencies
    for task in dag_config.get("tasks", []):
        if "dependencies" in task:
            for dep in task["dependencies"]:
                tasks[dep] >> tasks[task["task_id"]]

    # Register DAG dynamically
    globals()[dag_id] = dag
    print(f"✔ DAG '{dag_id}' successfully loaded!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a specific Airflow DAG")
    parser.add_argument("--dag_id", required=True, help="DAG ID to generate")
    args = parser.parse_args()

    generate_dag(args.dag_id)
    print(f"✔ DAG '{args.dag_id}' has been processed.")
