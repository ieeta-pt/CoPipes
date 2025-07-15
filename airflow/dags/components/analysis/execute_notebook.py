import os
import tempfile
import json
from typing import Dict, Any, Optional, Union
from airflow.decorators import task
import papermill as pm
from jupyter_client.kernelspec import find_kernel_specs

@task
def execute_notebook(
    input_notebook: Union[str, Dict[str, Any]],
    output_directory: str = "/shared_data/notebooks/output",
    parameters: Optional[Dict[str, Any]] = None,
    kernel_name: str = "python3",
    execution_timeout: int = 3600,
    **context
) -> Dict[str, Any]:
    """
    Execute a Jupyter notebook using papermill with configurable parameters.
    
    Args:
        input_notebook: Either path to notebook file or notebook content as dict
        output_directory: Directory to save executed notebook
        parameters: Dictionary of parameters to pass to notebook
        kernel_name: Name of the kernel to use for execution
        execution_timeout: Maximum execution time in seconds
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
    
    # Validate kernel availability
    available_kernels = find_kernel_specs()
    if kernel_name not in available_kernels:
        return {
            "status": "failed",
            "error": f"Kernel '{kernel_name}' not found. Available kernels: {list(available_kernels.keys())}",
            "input_notebook": str(input_notebook_path) if isinstance(input_notebook, str) else "notebook_content",
            "output_notebook": output_notebook,
            "execution_date": execution_date,
            "parameters_used": parameters
        }
    
    # Execute notebook with comprehensive error handling
    try:
        pm.execute_notebook(
            input_path=input_notebook_path,
            output_path=output_notebook,
            parameters=parameters,
            kernel_name=kernel_name,
            execution_timeout=execution_timeout
        )
        execution_status = "success"
        error_message = None
    except pm.PapermillExecutionError as e:
        execution_status = "failed"
        error_message = f"Notebook execution failed: {str(e)}"
    except FileNotFoundError as e:
        execution_status = "failed"
        error_message = f"Input notebook not found: {str(e)}"
    except PermissionError as e:
        execution_status = "failed"
        error_message = f"Permission denied: {str(e)}"
    except Exception as e:
        execution_status = "failed"
        error_message = f"Unexpected error during notebook execution: {str(e)}"
    
    # Clean up temporary file if it was created
    if not isinstance(input_notebook, str) and os.path.exists(input_notebook_path):
        os.unlink(input_notebook_path)
    
    # Return execution results
    result = {
        "status": execution_status,
        "input_notebook": str(input_notebook_path) if isinstance(input_notebook, str) else "notebook_content",
        "output_notebook": output_notebook,
        "execution_date": execution_date,
        "parameters_used": parameters
    }
    
    if error_message:
        result["error"] = error_message
    
    return result