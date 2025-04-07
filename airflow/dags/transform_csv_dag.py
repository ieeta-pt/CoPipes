from airflow import DAG
from datetime import datetime

from components.cohorts.transform_to_kv import transform_to_kv
from components.postgres.create_conn import create_connection
from components.postgres.create_table import create_table
from components.extract.csv import extract_csv
from components.postgres.write_to_db import write_to_postgres

with DAG (
    dag_id="transform_csv_dag",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False,
    description="This DAG transforms a CSV file and writes it to a PostgreSQL database."
) as dag:

    extract_csv_task = extract_csv(
        filename = "/opt/airflow/data/input_data/20190510 EMIF Patient Data.csv"
    )

    transformer_task = transform_to_kv(
        data = extract_csv_task,
        fixed_columns = ["Patient ID", "Date of"],
        measurement_columns = ["Insomnia Severity Index (ISI)", "Epworth Sleepiness Scale (ESS)", "RBDSQ total"]
    )

    create_connection_task = create_connection()

    create_table_task = create_table(
        columns = [
            "Patient ID", 
            "Date of ",
            "Variable",
            "Measure"
        ],
        table_name = "Berlin"
    )

    write_to_db_task = write_to_postgres(
        data = transformer_task
    )

    extract_csv_task >> transformer_task >> create_connection_task >> create_table_task >> write_to_db_task