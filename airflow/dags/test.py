from airflow import DAG
from datetime import datetime

from components.transformation.cohorts.to_key_value import to_key_value
from components.extraction.csv import csv

with DAG (
    dag_id="test",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_kzo = csv(filename='', file_separation='comma')
    to_key_value_55z = to_key_value(data='Data to reorganize', fixed_columns='List of fixed columns names', measurement_columns='List of measurement columns')
    csv_xh4 = csv(filename='', file_separation='comma')


