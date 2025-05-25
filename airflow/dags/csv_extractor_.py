from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv

with DAG (
    dag_id="CSV_extractor_",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_o62 = csv(filename='infos.csv', file_separation='comma')


