from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv

with DAG (
    dag_id="generated_dag",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_lz = csv(filename='', file_separation=',')


