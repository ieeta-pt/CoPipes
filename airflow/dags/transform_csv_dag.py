from airflow import DAG
from datetime import datetime

from components.cohorts.csv_transformer import transform_csv
from components.postgres.create_conn import create_connection
from components.postgres.create_table import create_table
from components.postgres.write_to_db import write_to_postgres

with DAG(
    dag_id="transform_csv_dag",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False,
    description="This DAG transforms a CSV file and writes it to a PostgreSQL database."
) as dag:

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

    transformer_task = transform_csv(
        csv_filename = "/opt/airflow/data/input_data/BERLIN_20190515.csv",
        fixed_columns = ["Patient ID", "Date of"],
        measurement_columns = ["Insomnia Severity Index (ISI)", "Epworth Sleepiness Scale (ESS)", "RBDSQ total"]
    )

    write_to_db_task = write_to_postgres(
        df = transformer_task,
        table_name = "Berlin"
    )

    create_connection_task >> create_table_task >> transformer_task >> write_to_db_task