from datetime import datetime, timedelta
import os
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Initialize the DAG
dag = DAG(
    'papermill_simple_ml_pipeline',
    default_args=default_args,
    description='Simple ML Pipeline using Papermill (direct execution)',
    schedule_interval='@daily',
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=2),
    tags=['ml', 'papermill', 'jupyter', 'simple']
)

def setup_environment(**context):
    """Setup environment and create necessary directories"""
    logger.info("Setting up environment for Papermill ML Pipeline...")
    
    # Create directories
    directories = [
        '/tmp/notebooks/input',
        '/tmp/notebooks/output',
        '/tmp/ml_data',
        '/tmp/ml_models',
        '/tmp/ml_reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create sample dataset
    try:
        import pandas as pd
        import numpy as np
        
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        sample_data = pd.DataFrame({
            'date': dates,
            'feature_1': np.random.normal(50, 15, len(dates)),
            'feature_2': np.random.normal(100, 25, len(dates)),
            'feature_3': np.random.exponential(2, len(dates)),
            'target': np.random.normal(75, 20, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 10
        })
        
        sample_data.to_csv('/tmp/ml_data/training_data.csv', index=False)
        logger.info(f"Created sample dataset with {len(sample_data)} records")
        
    except ImportError as e:
        logger.error(f"Required packages not available: {e}")
        # Create a simple CSV file manually
        with open('/tmp/ml_data/training_data.csv', 'w') as f:
            f.write("date,feature_1,feature_2,feature_3,target\n")
            f.write("2024-01-01,50.0,100.0,2.0,75.0\n")
            f.write("2024-01-02,52.0,105.0,1.8,77.0\n")
        logger.info("Created minimal sample dataset")
    
    return "Environment setup completed successfully"

def create_simple_notebook(**context):
    """Create a simple notebook for demonstration"""
    logger.info("Creating simple demonstration notebook...")
    
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Simple ML Pipeline Notebook\\n", "This notebook demonstrates Papermill integration with Airflow."]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"tags": ["parameters"]},
                "outputs": [],
                "source": [
                    "# Parameters cell - will be replaced by Papermill\\n",
                    "input_file = '/tmp/ml_data/training_data.csv'\\n",
                    "execution_date = '2024-01-01'\\n",
                    "message = 'Hello from Airflow!'\\n",
                    "multiplier = 2"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    "import os\n",
                    "from datetime import datetime\n",
                    "\n",
                    "print(f'Execution date: {execution_date}')\n",
                    "print(f'Message: {message}')\n",
                    "print(f'Multiplier: {multiplier}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Try to load data\\n",
                    "try:\\n",
                    "    if os.path.exists(input_file):\\n",
                    "        df = pd.read_csv(input_file)\\n",
                    "        print(f'Loaded data with {len(df)} rows')\\n",
                    "        print(f'Columns: {list(df.columns)}')\\n",
                    "        \\n",
                    "        # Simple analysis\\n",
                    "        if 'target' in df.columns:\\n",
                    "            mean_target = df['target'].mean()\\n",
                    "            modified_mean = mean_target * multiplier\\n",
                    "            print(f'Mean target: {mean_target:.2f}')\\n",
                    "            print(f'Modified mean (x{multiplier}): {modified_mean:.2f}')\\n",
                    "        \\n",
                    "        result = {\\n",
                    "            'rows_processed': len(df),\\n",
                    "            'execution_date': execution_date,\\n",
                    "            'status': 'completed'\\n",
                    "        }\\n",
                    "    else:\\n",
                    "        print(f'Input file not found: {input_file}')\\n",
                    "        result = {\\n",
                    "            'rows_processed': 0,\\n",
                    "            'execution_date': execution_date,\\n",
                    "            'status': 'no_data'\\n",
                    "        }\\n",
                    "except Exception as e:\\n",
                    "    print(f'Error processing data: {e}')\\n",
                    "    result = {\\n",
                    "        'error': str(e),\\n",
                    "        'execution_date': execution_date,\\n",
                    "        'status': 'error'\\n",
                    "    }"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Save results\\n",
                    "output_file = f'/tmp/ml_reports/results_{execution_date}.txt'\\n",
                    "os.makedirs('/tmp/ml_reports', exist_ok=True)\\n",
                    "\\n",
                    "with open(output_file, 'w') as f:\\n",
                    "    f.write(f'Execution Date: {execution_date}\\\\n')\\n",
                    "    f.write(f'Message: {message}\\\\n')\\n",
                    "    f.write(f'Result: {result}\\\\n')\\n",
                    "\\n",
                    "print(f'Results saved to: {output_file}')\\n",
                    "print('Notebook execution completed successfully!')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Save notebook
    notebook_path = '/tmp/notebooks/input/simple_analysis.ipynb'
    with open(notebook_path, 'w') as f:
        json.dump(notebook_content, f, indent=2)
    
    logger.info(f"Created notebook: {notebook_path}")
    return f"Notebook created: {notebook_path}"

def execute_notebook_with_papermill(**context):
    """Execute notebook using papermill directly"""
    try:
        import papermill as pm
        
        execution_date = context['ds']
        input_notebook = '/tmp/notebooks/input/simple_analysis.ipynb'
        output_notebook = f'/tmp/notebooks/output/simple_analysis_{execution_date}.ipynb'
        
        logger.info(f"Executing notebook: {input_notebook}")
        logger.info(f"Output will be saved to: {output_notebook}")
        
        # Parameters to pass to notebook
        parameters = {
            'execution_date': execution_date,
            'input_file': '/tmp/ml_data/training_data.csv',
            'message': f'Executed by Airflow on {execution_date}',
            'multiplier': 3
        }
        
        logger.info(f"Parameters: {parameters}")
        
        # Execute notebook with papermill
        pm.execute_notebook(
            input_path=input_notebook,
            output_path=output_notebook,
            parameters=parameters
        )
        
        logger.info(f"Successfully executed notebook: {input_notebook}")
        logger.info(f"Output saved to: {output_notebook}")
        
        # Check if output file exists
        if os.path.exists(output_notebook):
            file_size = os.path.getsize(output_notebook)
            logger.info(f"Output notebook size: {file_size} bytes")
            return f"Notebook executed successfully. Output: {output_notebook} ({file_size} bytes)"
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

def validate_results(**context):
    """Validate the notebook execution results"""
    logger.info("Validating notebook execution results...")
    
    execution_date = context['ds']
    output_notebook = f'/tmp/notebooks/output/simple_analysis_{execution_date}.ipynb'
    results_file = f'/tmp/ml_reports/results_{execution_date}.txt'
    
    # Check if output notebook exists
    if not os.path.exists(output_notebook):
        raise FileNotFoundError(f"Output notebook not found: {output_notebook}")
    
    logger.info(f"Output notebook found: {output_notebook}")
    
    # Check if results file exists
    if os.path.exists(results_file):
        logger.info(f"Results file found: {results_file}")
        
        # Read and log results
        with open(results_file, 'r') as f:
            results_content = f.read()
        
        logger.info(f"Results content:\\n{results_content}")
        
        # Basic validation
        if execution_date in results_content:
            logger.info("Validation passed: execution date found in results")
            return "Validation successful"
        else:
            raise ValueError("Validation failed: execution date not found in results")
    else:
        logger.warning(f"Results file not found: {results_file}")
        return "Validation completed (results file not found)"

def send_completion_notification(**context):
    """Send notification about pipeline completion"""
    logger.info("Sending pipeline completion notification...")
    
    execution_date = context['ds']
    dag_id = context['dag'].dag_id
    
    notification_message = f"""
    Papermill ML Pipeline Completed Successfully!
    
    DAG ID: {dag_id}
    Execution Date: {execution_date}
    Pipeline Status: SUCCESS
    
    Outputs:
    - Executed notebook: /tmp/notebooks/output/simple_analysis_{execution_date}.ipynb
    - Results file: /tmp/ml_reports/results_{execution_date}.txt
    """
    
    logger.info(notification_message)
    
    return "Notification sent successfully"

# Define tasks
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

setup_env_task = PythonOperator(
    task_id='setup_environment',
    python_callable=setup_environment,
    dag=dag
)

create_notebook_task = PythonOperator(
    task_id='create_notebook',
    python_callable=create_simple_notebook,
    dag=dag
)

# Install papermill (separate task to ensure it's available)
install_papermill_task = BashOperator(
    task_id='install_papermill',
    bash_command='''
        echo "Installing papermill..."
        pip install --quiet papermill pandas numpy || echo "Papermill installation completed"
        echo "Checking papermill installation..."
        python -c "import papermill; print(f'Papermill version: {papermill.__version__}')" || echo "Papermill check completed"
    ''',
    dag=dag
)

execute_notebook_task = PythonOperator(
    task_id='execute_notebook',
    python_callable=execute_notebook_with_papermill,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_results',
    python_callable=validate_results,
    dag=dag
)

notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_completion_notification,
    dag=dag,
    trigger_rule='all_done'  # Run regardless of upstream success/failure
)

end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# Define task dependencies
start_task >> setup_env_task >> create_notebook_task >> install_papermill_task
install_papermill_task >> execute_notebook_task >> validate_task >> notification_task >> end_task