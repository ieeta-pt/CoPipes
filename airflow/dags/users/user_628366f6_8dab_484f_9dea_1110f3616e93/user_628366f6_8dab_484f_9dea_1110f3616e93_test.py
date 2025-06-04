from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv

with DAG (
    dag_id="user_628366f6_8dab_484f_9dea_1110f3616e93_test",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_3lz = csv(filename='', file_separation='Comma')


