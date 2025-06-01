from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv

with DAG (
    dag_id="user_cbd6da17_3e9d_4d32_8127_f3ef4d000bed_1",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_18g = csv(filename='', file_separation='Comma')


