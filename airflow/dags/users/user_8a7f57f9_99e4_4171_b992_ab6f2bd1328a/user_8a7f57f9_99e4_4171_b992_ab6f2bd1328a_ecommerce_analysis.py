from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv
from components.analysis.execute_notebook import execute_notebook

with DAG (
    dag_id="user_8a7f57f9_99e4_4171_b992_ab6f2bd1328a_Ecommerce_analysis",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_3sg = csv(filename='weekly_sales_june_w3.csv', file_separation=',')
    execute_notebook_qxp = execute_notebook(input_notebook='test.ipynb', output_directory='/shared_data/notebooks/output', parameters=csv_3sg)

    csv_3sg >> execute_notebook_qxp
