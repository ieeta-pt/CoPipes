from airflow import DAG
from datetime import datetime

from components.extract.csv import extract_csv

with DAG(
    dag_id="test_dag",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False,
) as dag:
    read_csv = extract_csv(
        filename="20190510 EMIF Patient Data.csv",
    )