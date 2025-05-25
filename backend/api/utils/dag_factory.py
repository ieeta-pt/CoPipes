import os
from datetime import datetime
from pathlib import Path
import re


DAG_OUTPUT_DIR = "/opt/airflow/dags"
os.makedirs(DAG_OUTPUT_DIR, exist_ok=True)

DAG_TEMPLATE = """from airflow import DAG
from datetime import datetime

{dynamic_imports}

with DAG (
    dag_id="{dag_id}",
    schedule_interval={schedule_interval},
    catchup=False,
    is_paused_upon_creation=False
) as dag:

{tasks_definitions}

{dependencies}
"""

TASK_TEMPLATE = """    {task_id} = {task_function}({params})"""

DEPENDENCY_TEMPLATE = """    {upstream} >> {downstream}"""


def generate_dag(config):
    """Generates an Airflow DAG file from a JSON config."""
    print("Generating DAG from config...")
    ## Worflow parameters ##
    dag_id = config["dag_id"].replace(" ", "_")
    schedule_interval = f'"{config["schedule_interval"]}"' if config["schedule_interval"] else None 
    start_date = ", ".join(map(str, datetime.fromisoformat(config["start_date"]).timetuple()[:3])) if config["start_date"] else None

    print(f"dag_id: {dag_id} \nstart_date: {start_date} \nschedule_interval: {schedule_interval}")

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
            resolved_params.append(f"{name}={repr(param['value'])}")

        # for key, value in params.items():
        #     if isinstance(value, str) and value.startswith("$ref:"):
        #         referenced_task = value.split(":")[1]  
        #         resolved_params.append(f"{key}={referenced_task}")
        #     else:
        #         resolved_params.append(f"{key}={repr(value)}")

        params_str = ", ".join(resolved_params)

        tasks_definitions.append(TASK_TEMPLATE.format(task_id=task_id, task_function=function_name, params=params_str))

        if task["dependencies"] and len(task["dependencies"]) > 0:
            for dep in task["dependencies"]:
                if dep != None:
                    dep = dep.replace(" ", "_").lower()
                    dependencies.append(DEPENDENCY_TEMPLATE.format(upstream=dep, downstream=task_id))

        print(f"Task: {task_id} \nModule: {module_path} \nFunction: {function_name} \nParams: {params_str} \nDependencies: {dependencies}")

    dag_code = DAG_TEMPLATE.format(
        dag_id=dag_id,
        schedule_interval=schedule_interval,
        start_date=start_date,
        dynamic_imports="\n".join(dynamic_imports),
        tasks_definitions="\n".join(tasks_definitions),
        dependencies="\n".join(dependencies) if dependencies else "",
    )

    output_path = Path(DAG_OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = re.sub(r"[^\w]", "_", dag_id).lower()
    dag_file = output_path / f"{file_path}.py"

    with open(dag_file, "w") as f:
        f.write(dag_code)
        print(f"DAG file created at {dag_file}")
    
    return



def remove_dag(dag_id):
    """Removes an Airflow DAG file."""
    dag_id = re.sub(r"[^\w]", "_", dag_id).lower()
    dag_file = Path(DAG_OUTPUT_DIR) / f"{dag_id}.py"
    if dag_file.exists():
        dag_file.unlink()
        print(f"DAG file {dag_id} removed.")
    else:
        print(f"DAG file {dag_id} does not exist.")
