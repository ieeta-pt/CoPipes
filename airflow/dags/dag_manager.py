"""Dag Factory"""
from airflow import DAG
import importlib
from datetime import datetime
import json

def load_dag_definition(json_file_path: str) -> dict:
    """
    Reads a DAG definition from a JSON file and converts any values that
    require type transformations (like the start_date string to a datetime object).

    Args:
        json_file_path (str): Path to the JSON file containing the DAG definition.

    Returns:
        dict: The DAG definition as a dictionary.
    """
    with open(json_file_path, 'r') as f:
        dag_definition = json.load(f)

    # Convert 'start_date' in default_args from a string to a datetime object
    if "default_args" in dag_definition:
        default_args = dag_definition["default_args"]
        if "start_date" in default_args:
            # Expecting a string like "2018, 1, 1"
            start_date_str = default_args["start_date"]
            try:
                # Split by comma, strip whitespace and convert each part to int
                start_date_tuple = tuple(int(part.strip()) for part in start_date_str.split(","))
                default_args["start_date"] = datetime(*start_date_tuple)
            except Exception as e:
                raise ValueError(f"Error parsing start_date '{start_date_str}': {e}")

        # Convert email_on_failure from a string to a boolean if necessary
        if "email_on_failure" in default_args:
            email_on_failure = default_args["email_on_failure"]
            if isinstance(email_on_failure, str):
                # This will convert "true"/"True" to True, anything else to False
                default_args["email_on_failure"] = email_on_failure.lower() == "true"

    return dag_definition

def import_operator(operator: str):
    """Dynamically imports a class.
    
    Args:
        operator (str): The complete class name (e.g., 'airflow.operators.dummy_operator.DummyOperator')
    
    Returns:
        type: The imported class.
    
    Raises:
        ImportError: If the module or class cannot be found.
    """
    if '.' not in operator:
        raise ValueError("Invalid input: The string must contain at least one dot (.)")
    
    module_path, class_name = operator.rsplit('.', 1)  
    
    try:
        module = importlib.import_module(module_path) 
        class_ = getattr(module, class_name) 
        return class_
    except ModuleNotFoundError:
        raise ImportError(f"Module '{module_path}' not found.")
    except AttributeError:
        raise ImportError(f"Class '{class_name}' not found in module '{module_path}'.")

def create_dag(schedule, default_args, dag_definition):
    """Create dags dynamically."""
    with DAG(
        dag_definition["name"], 
        schedule=schedule, 
        default_args=default_args
    ) as dag:

        tasks = {}
        for node in dag_definition["nodes"]:
            task_operator = import_operator(node["_type"])  
            task_id = node["name"].replace(" ", "")

            tasks[task_id] = task_operator(
                task_id=task_id,
                dag=dag,
                **node["parameters"]  
            )

        for node_name, downstream_conn in dag_definition["connections"].items():
            for ds_task in downstream_conn:
                tasks[node_name] >> tasks[ds_task]

    globals()[dag_definition["name"]] = dag
    return dag


# Example usage:
if __name__ == "__main__":
    # Load the DAG definition from the JSON file
    dag_definition = load_dag_definition("dags_definition/demo_1.json")
    
    # Create the DAG dynamically.
    # You can adjust the schedule as needed (e.g., '@daily', '0 12 * * *', etc.)
    dag = create_dag(
        schedule='@daily', 
        default_args=dag_definition["default_args"], 
        dag_definition=dag_definition
    )
    
    # The created DAG is now available in globals under its name (e.g., "demo_3")
    print(f"DAG '{dag_definition['name']}' created successfully.")