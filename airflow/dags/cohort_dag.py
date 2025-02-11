from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from components.create_conn import create_postgres_connection
from components.read_csv import read_csv
from components.cohorts.create_base_table import create_mapping
from components.cohorts.store_mapping import store_mapping

with DAG(
    dag_id="cohort_dag",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False
) as dag:
    create_connection_task = create_postgres_connection()

    read_csv_task = PythonOperator(
        task_id="read_csv",
        python_callable=read_csv,
        op_args=["/opt/airflow/data/input_data/BERLIN_20190515 EMIF Data sample(20190510 EMIF Patient Data).csv"]
    )

    create_base_table_task = PythonOperator(
        task_id="create_base_table",
        python_callable=create_mapping,
        op_kwargs={
            "columns_dst": [
            'person_id',
            'gender_concept_id',
            'year_of_birth',
            'month_of_birth',
            'day_of_birth',
    		'birth_datetime',
            'death_datetime',
            'race_concept_id',
            'ethnicity_concept_id',
            'location_id',
    		'provider_id',
            'care_site_id',
            'person_source_value',
            'gender_source_value',
            'gender_source_concept_id',
    		'race_source_value',
            'race_source_concept_id',
            'ethnicity_source_value',
            'ethnicity_source_concept_id'
            ],
            "table": "person",
            "column_mapper": {
                'person_id': 'Patient ID',
                'gender_concept_id': 'Sex'
                }
        }
    )

    store_mapping_task = PythonOperator(
        task_id="store_mapping",
        python_callable=store_mapping,
        op_kwargs={
            "table": "person",
        }
    )

    create_connection_task >> read_csv_task >> create_base_table_task >> store_mapping_task
