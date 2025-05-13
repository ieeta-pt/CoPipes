from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv

with DAG (
    dag_id="my_workflow",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_fe = csv(filename='', file_separation=',')


