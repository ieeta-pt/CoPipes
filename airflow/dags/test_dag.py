from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv

with DAG (
    dag_id="test_dag",
    schedule_interval=None,
    start_date=datetime((2025, 2, 3)),
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    CSV_1 = csv(filename='20190510 EMIF Patient Data.csv', file_sep=',')


