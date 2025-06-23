from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv
from components.analysis.jupyter.execute_notebook import execute_notebook
from components.analysis.statistical.descriptive_statistics import descriptive_statistics

with DAG (
    dag_id="user_8a7f57f9_99e4_4171_b992_ab6f2bd1328a_My_finances",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_6xx = csv(filename='', file_separation='Comma')
    execute_notebook_c6g = execute_notebook(input_notebook_path='', output_directory='/shared_data/notebooks/output', parameters='')
    descriptive_statistics_wzc = descriptive_statistics(data='', target_columns='', include='all', percentiles='0.25,0.5,0.75', generate_plots='True')


