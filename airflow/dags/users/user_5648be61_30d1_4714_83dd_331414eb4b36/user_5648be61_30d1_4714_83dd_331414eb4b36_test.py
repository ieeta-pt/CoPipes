from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv

with DAG (
    dag_id="user_5648be61_30d1_4714_83dd_331414eb4b36_test",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_30u = csv(filename='', file_separation='Comma')


