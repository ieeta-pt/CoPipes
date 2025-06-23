from datetime import datetime, timedelta
from airflow import DAG
from components.extraction.csv import csv
from components.analysis.execute_notebook import execute_notebook

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'csv_notebook_analysis',
    default_args=default_args,
    description='Load CSV data and execute notebook analysis',
    schedule_interval=None,
    catchup=False,
    tags=['csv', 'notebook', 'analysis'],
)

# Define the workflow
csv_data = csv(filename="weekly_sales_june_w3.csv", file_separation=",")
notebook_task = execute_notebook(
    input_notebook="/home/raquelparadinha/Desktop/MEI/2ano/thesis-dev/test.ipynb",
    output_directory="/shared_data/notebooks/output",
    parameters=csv_data
)

# Set dependencies
csv_data >> notebook_task