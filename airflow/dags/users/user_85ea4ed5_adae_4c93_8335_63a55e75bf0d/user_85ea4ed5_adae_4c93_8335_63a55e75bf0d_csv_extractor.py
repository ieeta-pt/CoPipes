from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv

with DAG (
    dag_id="user_85ea4ed5_adae_4c93_8335_63a55e75bf0d_CSV_extractor",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_y4p = csv(filename='', file_separation='Comma')


