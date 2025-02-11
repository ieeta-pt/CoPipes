from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from components.read_csv import read_csv
from components.process_data.process_data import process_data
from components.process_data.write_to_db import write_to_db
from components.process_data.create_table import create_table
from components.create_conn import create_postgres_connection

with DAG(
    dag_id="process_student_grades",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False,
) as dag:
    create_connection_task = create_postgres_connection()

    create_table_task = create_table()

    read_csv_task = PythonOperator(
        task_id="read_csv",
        python_callable=read_csv,
        op_args=["/opt/airflow/data/input_data/input.csv"]
    )

    process_data_task = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
    )

    write_to_db_task = PythonOperator(
        task_id="write_to_db",
        python_callable=write_to_db,
    )

    create_connection_task >> create_table_task 
    read_csv_task >> process_data_task >> write_to_db_task
