"""Dag Factory"""
from airflow import DAG
import importlib

def create_dag(schedule, default_args, definition):
    """Create dags dynamically."""
    with DAG(
        definition["name"], schedule=schedule, default_args=default_args
    ) as dag:

        tasks = {}
        for node in definition["nodes"]:
            operator = load_operator(node["_type"])
            params = node["parameters"]

            node_name = node["name"].replace(" ", "")
            params["task_id"] = node_name
            params["dag"] = dag
            tasks[node_name] = operator(**params)

        for node_name, downstream_conn in definition["connections"].items():
            for ds_task in downstream_conn:
                tasks[node_name] >> tasks[ds_task]

    globals()[definition["name"]] = dag
    return dag


def load_operator(fqdn: str):
    """Dynamically imports a class from a fully qualified class name.
    
    Args:
        fqdn (str): The fully qualified class name (e.g., 'airflow.operators.dummy_operator.DummyOperator')
    
    Returns:
        type: The imported class.
    
    Raises:
        ImportError: If the module or class cannot be found.
    """
    if '.' not in fqdn:
        raise ValueError("Invalid input: The string must contain at least one dot (.)")
    
    module_path, class_name = fqdn.rsplit('.', 1)  # Split into module and class
    
    try:
        module = importlib.import_module(module_path)  # Import the module
        class_ = getattr(module, class_name)  # Get the class from the module
        return class_
    except ModuleNotFoundError:
        raise ImportError(f"Module '{module_path}' not found.")
    except AttributeError:
        raise ImportError(f"Class '{class_name}' not found in module '{module_path}'.")


# default_args = {
#     "owner": "airflow",
#     "start_date": datetime(2018, 1, 1),
#     "email": ["someEmail@gmail.com"],
#     "email_on_failure": False,
# }

# definition = {
#                 "name": "demo_5",
#                 "nodes": [
#                     {
#                         "name": "Start",
#                         "_type": "airflow.operators.bash.BashOperator",
#                         "parameters": {
#                             "bash_command": "echo I am task 1"
#                         },
#                     },
#                     {
#                         "name": "HTTPRequest",
#                         "_type": "airflow.operators.bash.BashOperator",
#                         "parameters": {
#                             "bash_command": "echo I am task 2"
#                         },
#                     },
#                     {
#                         "name": "End",
#                         "_type": "airflow.operators.bash.BashOperator",
#                         "parameters": {
#                             "bash_command": "echo I am task 3"
#                         },
#                     },
#                     {
#                         "name": "ExecuteCommand",
#                         "_type": "airflow.operators.bash.BashOperator",
#                         "parameters": {
#                             "bash_command": "echo I am task 4"
#                         },
#                     }
#                 ],
#                 "connections": {
#                     "Start": ["ExecuteCommand", "HTTPRequest"],
#                     "HTTPRequest": ["End"],
#                     "ExecuteCommand": ["End"]
#                 }
#             }

# create_dag(None, default_args, definition)