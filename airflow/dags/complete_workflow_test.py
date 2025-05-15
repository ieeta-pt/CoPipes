from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv
from components.loading.postgres.create_connection import create_connection

with DAG (
    dag_id="Complete workflow test",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    create_connection_vej = create_connection(database_name='My database')
    csv_vvu = csv(filename='', file_separation=',')


