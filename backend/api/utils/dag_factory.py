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
    print("Generating DAG from config...")
    ## Worflow parameters ##
    dag_id = config["dag_id"]
    schedule_interval = f'"{config["schedule_interval"]}"' if config["schedule_interval"] else None # Mudar para valor default
    start_date = ", ".join(map(str, datetime.fromisoformat(config["start_date"]).timetuple()[:3])) if config["start_date"] else (2025, 2, 3) # Mudar para valor default

    print(f"dag_id: {dag_id} \nstart_date: {start_date} \nschedule_interval: {schedule_interval}")

    tasks_definitions = []
    dependencies = []
    dynamic_imports = set()

    for task in config["tasks"]:
        print(f"Processing task: {task['id']}")
        task_id = task["id"]
        module_path = task["type"].replace(" ", "_").lower()
        if task["subtype"]:
            module_path += "." + task["subtype"].replace(" ", "_").lower()
        function_name = task["content"].replace(" ", "_").lower()
        module_path += "." + function_name
        print(f"Module path: {module_path}")
        params = task["config"]
        print(f"Parameters: {params}")

        dynamic_imports.add(f"from components.{module_path} import {function_name}")
        print(f"Dynamic imports: {dynamic_imports}")

        resolved_params = []
        for param in params:
            print(f"Resolving parameter: {param}")
            resolved_params.append(f"{param['name']}={repr(param['value'])}")
        print(f"Resolved parameters: {resolved_params}")

        # for key, value in params.items():
        #     if isinstance(value, str) and value.startswith("$ref:"):
        #         referenced_task = value.split(":")[1]  
        #         resolved_params.append(f"{key}={referenced_task}")
        #     else:
        #         resolved_params.append(f"{key}={repr(value)}")

        params_str = ", ".join(resolved_params)
        print(f"Parameters string: {params_str}")

        tasks_definitions.append(TASK_TEMPLATE.format(task_id=task_id, task_function=function_name, params=params_str))

        if task["dependencies"]:
            for dep in task["dependencies"]:
                dependencies.append(DEPENDENCY_TEMPLATE.format(upstream=dep, downstream=task_id))
        else: 
            dependencies = None

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
    dag_file = output_path / f"{dag_id}.py"

    with open(dag_file, "w") as f:
        f.write(dag_code)

    return dag_file
