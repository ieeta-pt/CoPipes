import os
from datetime import datetime
from pathlib import Path

DAG_OUTPUT_DIR = "/opt/airflow/dags"
os.makedirs(DAG_OUTPUT_DIR, exist_ok=True)

DAG_TEMPLATE = """from airflow import DAG
from datetime import datetime

{dynamic_imports}

with DAG (
    dag_id="{dag_id}",
    schedule_interval={schedule_interval},
    start_date=datetime({start_date}),
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
    
    dag_id = config["dag_id"]
    schedule_interval = "None" if config["schedule_interval"] is None else f'"{config["schedule_interval"]}"'
    start_date = ", ".join(map(str, datetime.fromisoformat(config["start_date"]).timetuple()[:3]))

    tasks_definitions = []
    dependencies = []
    dynamic_imports = set()
    task_references = {}

    for task in config["tasks"]:
        task_id = task["task_id"]
        module_path = task["module"]
        function_name = task["function"]
        params = task["params"]

        dynamic_imports.add(f"from {module_path} import {function_name}")

        resolved_params = []
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$ref:"):
                referenced_task = value.split(":")[1]  
                resolved_params.append(f"{key}={referenced_task}")
            else:
                resolved_params.append(f"{key}={repr(value)}")

        params_str = ", ".join(resolved_params)
        task_references[task_id] = task_id

        tasks_definitions.append(TASK_TEMPLATE.format(task_id=task_id, task_function=function_name, params=params_str))

        for dep in task["dependencies"]:
            dependencies.append(DEPENDENCY_TEMPLATE.format(upstream=dep, downstream=task_id))

    dag_code = DAG_TEMPLATE.format(
        dag_id=dag_id,
        schedule_interval=schedule_interval,
        start_date=start_date,
        dynamic_imports="\n".join(dynamic_imports),
        tasks_definitions="\n".join(tasks_definitions),
        dependencies="\n".join(dependencies),
    )

    output_path = Path(DAG_OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    dag_file = output_path / f"{dag_id}.py"

    with open(dag_file, "w") as f:
        f.write(dag_code)

    return dag_file
