from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv
from components.operator.bash.bashoperator import bashoperator
from components.operator.python.pythonoperator import pythonoperator

with DAG (
    dag_id="test_workflow",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    python_1 = pythonoperator(task_id='print_hello', python_callable="print('Hello World!')")
    bash_1 = bashoperator(task_id='list_files', bash_command='ls -la')
    csv_jym = csv(filename='', file_separation=',')


