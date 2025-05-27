from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv

with DAG (
    dag_id="CSV_extractor",
    schedule_interval=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_g0u = csv(filename='File to read', file_separation='Comma')


