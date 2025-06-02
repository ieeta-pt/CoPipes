import os
import logging
from typing import Dict, Any, Optional
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def execute_notebook(
    input_notebook_path: str,
    output_directory: str = "/shared_data/notebooks/output",
    parameters: Optional[Dict[str, Any]] = None,
    **context
) -> Dict[str, Any]:
    """
    Execute a Jupyter notebook using papermill with configurable parameters.
    
    Args:
        input_notebook_path: Path to input notebook file
        output_directory: Directory to save executed notebook
        parameters: Dictionary of parameters to pass to notebook
        **context: Airflow context
    
    Returns:
        Dict containing execution results and output file path
    """
    try:
        import papermill as pm
        
        execution_date = context['ds']
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Generate output notebook path
        notebook_name = os.path.basename(input_notebook_path)
        name_without_ext = os.path.splitext(notebook_name)[0]
        output_notebook = os.path.join(output_directory, f"{name_without_ext}_{execution_date}.ipynb")
        
        logger.info(f"Executing notebook: {input_notebook_path}")
        logger.info(f"Output will be saved to: {output_notebook}")
        
        # Default parameters if none provided
        if parameters is None:
            parameters = {}
        
        # Always include execution date in parameters
        parameters['execution_date'] = execution_date
        
        logger.info(f"Parameters: {parameters}")
        
        # Execute notebook with papermill
        pm.execute_notebook(
            input_path=input_notebook_path,
            output_path=output_notebook,
            parameters=parameters
        )
        
        logger.info(f"Successfully executed notebook: {input_notebook_path}")
        logger.info(f"Output saved to: {output_notebook}")
        
        # Check if output file exists and get metadata
        if os.path.exists(output_notebook):
            file_size = os.path.getsize(output_notebook)
            logger.info(f"Output notebook size: {file_size} bytes")
            
            return {
                "status": "success",
                "input_notebook": input_notebook_path,
                "output_notebook": output_notebook,
                "file_size_bytes": file_size,
                "execution_date": execution_date,
                "parameters_used": parameters
            }
        else:
            raise FileNotFoundError(f"Expected output notebook not found: {output_notebook}")
        
    except ImportError:
        error_msg = "Papermill is not installed. Please install with: pip install papermill"
        logger.error(error_msg)
        raise ImportError(error_msg)
    except Exception as e:
        error_msg = f"Error executing notebook: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)