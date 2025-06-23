import os
import tempfile
import json
from typing import Dict, Any, Optional, Union
from airflow.decorators import task

@task
def execute_notebook(
    input_notebook: Union[str, Dict[str, Any]],
    output_directory: str = "/shared_data/notebooks/output",
    parameters: Optional[Dict[str, Any]] = None,
    **context
) -> Dict[str, Any]:
    """
    Execute a Jupyter notebook using the PapermillOperator with configurable parameters.
    
    Args:
        input_notebook: Either path to notebook file or notebook content as dict
        output_directory: Directory to save executed notebook
        parameters: Dictionary of parameters to pass to notebook
        **context: Airflow context
    
    Returns:
        Dict containing execution results and output file path
    """
    execution_date = context['ds']
    
    # Handle input notebook - either path or notebook content
    if isinstance(input_notebook, str):
        # It's a file path
        input_notebook_path = input_notebook
        notebook_name = os.path.basename(input_notebook_path)
    else:
        # It's notebook content as dict, create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as temp_file:
            json.dump(input_notebook, temp_file)
            input_notebook_path = temp_file.name
            notebook_name = f"temp_notebook_{execution_date}.ipynb"
    
    # Try to create output directory, fallback to /tmp if permission denied
    try:
        os.makedirs(output_directory, mode=0o777, exist_ok=True)
    except PermissionError:
        output_directory = "/tmp/notebooks/output"
        os.makedirs(output_directory, mode=0o777, exist_ok=True)
    
    # Generate output notebook path
    name_without_ext = os.path.splitext(notebook_name)[0]
    output_notebook = os.path.join(output_directory, f"{name_without_ext}_{execution_date}.ipynb")
    
    # Default parameters if none provided
    if parameters is None:
        parameters = {}
    
    # Add execution date to parameters
    parameters['execution_date'] = execution_date
    
    # Use papermill directly instead of operator since we're in a task
    import papermill as pm
    
    pm.execute_notebook(
        input_path=input_notebook_path,
        output_path=output_notebook,
        parameters=parameters,
        kernel_name="python3"
    )
    
    # Clean up temporary file if it was created
    if not isinstance(input_notebook, str) and os.path.exists(input_notebook_path):
        os.unlink(input_notebook_path)
    
    # Return execution results
    return {
        "status": "success",
        "input_notebook": str(input_notebook_path) if isinstance(input_notebook, str) else "notebook_content",
        "output_notebook": output_notebook,
        "execution_date": execution_date,
        "parameters_used": parameters
    }