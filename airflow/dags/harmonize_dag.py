from airflow import DAG
from datetime import datetime

from components.cohorts.transform_to_kv import transform_to_kv
from components.postgres.create_conn import create_connection
from components.postgres.create_table import create_table
from components.extract.csv import extract_csv
from components.postgres.write_to_db import write_to_postgres
from components.cohorts.harmonizer import harmonize

with DAG(
    dag_id="harmonize_dag",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False,
    description="This DAG transforms a CSV file and writes it to a PostgreSQL database."
) as dag:

    extract_csv_task = extract_csv(
        filename = "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Diagnosis.csv"
    )

    transformer_task = transform_to_kv(
        data = extract_csv_task,
        fixed_columns = ["Patient ID", "Number of Visit", "Date of Diagnosis"],
        measurement_columns = ["Onset of Symptoms", "Diagnosis", "Etiology", "ICD-10 / DSM-V", "Height", "Weight", "Blood Pressure", "Heart Rate", "Date of Diagnosis"]
    )

    extract_mappings_task = extract_csv(
        filename = "/opt/airflow/data/input_data/UsagiContentMapping_v5.csv"
    )

    harmonizer_task = harmonize(
        data = transformer_task,
        mappings = extract_mappings_task
    )

    create_connection_task = create_connection()

    create_table_task = create_table(
        columns = [
            "Patient ID", 
            "Number of Visit",
            "Date of Diagnosis",
            "Variable",
            "Measure",
            "VariableConcept",
            "MeasureConcept",
            "MeasureNumber",
            "MeasureString"
        ],
        table_name = harmonizer_task["filename"]
    )

    write_to_db_task = write_to_postgres(
        data = harmonizer_task
    )

    extract_csv_task >> transformer_task >> extract_mappings_task >> harmonizer_task >> create_connection_task >> create_table_task >> write_to_db_task
