import os
from pathlib import Path
import re

DAG_OUTPUT_DIR = "/opt/airflow/dags"
os.makedirs(DAG_OUTPUT_DIR, exist_ok=True)

DAG_TEMPLATE = """from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

{dynamic_imports}

with DAG (
    dag_id="{dag_id}",
    schedule={schedule},
    start_date={start_date},
    catchup=False,
    is_paused_upon_creation=False
) as dag:

{tasks_definitions}

{dependencies}
"""

TASK_TEMPLATE = """    {task_id} = {task_function}({params})"""

DEPENDENCY_TEMPLATE = """    {upstream} >> {downstream}"""


def generate_dag(config, user_id: str = None):
    """Generates an Airflow DAG file from a JSON config with user isolation."""
    print("Generating DAG from config...")
    ## Workflow parameters ##
    base_dag_id = config["dag_id"].replace(" ", "_")
    
    # Add user prefix for isolation if user_id is provided
    if user_id:
        # Sanitize user_id to replace hyphens with underscores for consistency
        sanitized_user_id = user_id.replace("-", "_")
        dag_id = f"user_{sanitized_user_id}_{base_dag_id}"
    else:
        dag_id = base_dag_id
        
    schedule = f'"{config["schedule"]}"' if config["schedule"] else None
    print(f"\nSTART DATE: {config['start_date']}\n")
    
    # Handle start_date - can be either a string (ISO format) or an object with year/month/day
    start_date = None
    if config.get("start_date"):
        if isinstance(config["start_date"], str):
            # Parse ISO date string (e.g., "2025-01-15")
            try:
                from datetime import datetime as dt
                parsed_date = dt.fromisoformat(config["start_date"])
                start_date = f'datetime({parsed_date.year}, {parsed_date.month}, {parsed_date.day})'
            except ValueError:
                print(f"Invalid date format: {config['start_date']}")
                start_date = None
        elif isinstance(config["start_date"], dict):
            # Handle object format {year: 2025, month: 1, day: 15}
            start_date = f'datetime({config["start_date"]["year"]}, {config["start_date"]["month"]}, {config["start_date"]["day"]})'

    print(f"dag_id: {dag_id} \nstart_date: {start_date} \nschedule: {schedule}")

    tasks_definitions = []
    dependencies = []
    dynamic_imports = set()

    for task in config["tasks"]:
        task_id = task["id"].replace(" ", "_").lower()
        module_path = task["type"].replace(" ", "_").lower()
        if task["subtype"]:
            module_path += "." + task["subtype"].replace(" ", "_").lower()
        function_name = task["content"].replace(" ", "_").lower()
        module_path += "." + function_name
        params = task["config"]

        dynamic_imports.add(f"from components.{module_path} import {function_name}")

        resolved_params = []
        for param in params:
            name = param["name"].replace(" ", "_").lower()
            value = param["value"]
            
            # Handle task references
            if isinstance(value, str) and value.startswith("$ref:"):
                referenced_task = value.split(":")[1].lower().replace(" ", "_")
                resolved_params.append(f"{name}={referenced_task}")
            else:
                resolved_params.append(f"{name}={repr(value)}")

        params_str = ", ".join(resolved_params)

        tasks_definitions.append(TASK_TEMPLATE.format(task_id=task_id, task_function=function_name, params=params_str))

        if task["dependencies"]:
            for dep in task["dependencies"]:
                dependencies.append(DEPENDENCY_TEMPLATE.format(upstream=dep, downstream=task_id))
        else:
            dependencies = None

        print(f"Task: {task_id} \nModule: {module_path} \nFunction: {function_name} \nParams: {params_str} \nDependencies: {dependencies}")

    dag_code = DAG_TEMPLATE.format(
        dag_id=dag_id,
        schedule=schedule,
        start_date=start_date,
        dynamic_imports="\n".join(dynamic_imports),
        tasks_definitions="\n".join(tasks_definitions),
        dependencies="\n".join(dependencies) if dependencies else "",
    )

    # Create user-specific directory if user_id is provided
    if user_id:
        # Sanitize user_id to replace hyphens with underscores for consistency
        sanitized_user_id = user_id.replace("-", "_")
        output_path = Path(DAG_OUTPUT_DIR) / "users" / f"user_{sanitized_user_id}"
    else:
        output_path = Path(DAG_OUTPUT_DIR)
    
    os.makedirs(output_path, exist_ok=True)
    
    file_path = re.sub(r"[^\w]", "_", dag_id).lower()
    dag_file = output_path / f"{file_path}.py"

    with open(dag_file, "w") as f:
        f.write(dag_code)
        
    print(f"DAG file created at {dag_file}")

    return dag_id  # Return the actual dag_id used



def remove_dag(dag_id, user_id: str = None):
    """Removes an Airflow DAG file with proper permission handling."""
    # Generate the full DAG ID with user prefix (same logic as generate_dag)
    base_dag_id = dag_id.replace(" ", "_")
    
    if user_id:
        # Sanitize user_id to replace hyphens with underscores for consistency
        sanitized_user_id = user_id.replace("-", "_")
        full_dag_id = f"user_{sanitized_user_id}_{base_dag_id}"
    else:
        full_dag_id = base_dag_id
    
    # Clean the dag_id for file name
    clean_dag_id = re.sub(r"[^\w]", "_", full_dag_id).lower()
    
    # Try user-specific path first if user_id provided
    if user_id:
        # Sanitize user_id to replace hyphens with underscores for consistency
        sanitized_user_id = user_id.replace("-", "_")
        user_dag_file = Path(DAG_OUTPUT_DIR) / "users" / f"user_{sanitized_user_id}" / f"{clean_dag_id}.py"
        user_dir = user_dag_file.parent
        
        if user_dag_file.exists():
            try:
                user_dag_file.unlink()
                # Try to remove user directory if it's empty
                try:
                    if user_dir.exists() and not any(user_dir.iterdir()):
                        os.rmdir(user_dir)
                        print(f"Empty user directory removed: {user_dir}")
                except OSError as e:
                    print(f"Could not remove empty directories: {e}")
                
                return
            except OSError as e:
                print(f"Error removing DAG file {dag_id}: {e}")
    
    # Try root dags directory (for backwards compatibility)
    dag_file = Path(DAG_OUTPUT_DIR) / f"{clean_dag_id}.py"
    if dag_file.exists():
        try:
            dag_file.unlink()
            print(f"DAG file {dag_id} removed from root directory.")
        except OSError as e:
            print(f"Error removing DAG file {dag_id} from root: {e}")
            # If we can't delete the file, try to make it empty so Airflow won't load it
            try:
                with open(dag_file, 'w') as f:
                    f.write("# DAG file marked for deletion\n")
                print(f"DAG file {dag_id} cleared (could not delete due to permissions)")
            except Exception as clear_error:
                print(f"Could not clear DAG file either: {clear_error}")
    else:
        print(f"DAG file {dag_id} does not exist in any location.")
