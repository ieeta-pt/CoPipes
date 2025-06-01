from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv

with DAG (
    dag_id="user_45207ac4_21d7_4beb_a24b_92829ff6d367_test",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_48c = csv(filename='', file_separation='Comma')


