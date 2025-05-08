from airflow import DAG
from datetime import datetime

from components.loading.postgres.create_table import create_table

with DAG (
    dag_id="sql",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    create_table_xh = create_table(columns='List of columns', table_name='My table')
    create_table_5m = create_table(columns='List of columns', table_name='My table')


