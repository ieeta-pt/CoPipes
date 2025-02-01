from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from components import hello_world

default_args = {
    "owner": "raquel",
}

with DAG(
    "my_dag_v01",
    default_args=default_args,
    start_date=datetime(2025, 1, 30),
    schedule_interval="@daily"
) as dag:
  task1 = PythonOperator(
    task_id="hello_world",
    python_callable=hello_world.hello_world
  )
  
task1