from datetime import datetime
from airflow import DAG

from components.extract.csv import extract_csv
from components.cohorts.transform_to_kv import transform_to_kv
from components.cohorts.harmonizer import harmonize
from components.cohorts.migrator import migrate
from components.postgres.create_conn import create_connection
from components.postgres.create_table import create_table

##### UTILS FUNCTIONS #####

def get_files():
    csv_files = ["/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Diagnosis.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Sleep.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Blood and CSF.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Neuropsychology.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Patient Data.csv"]
    return csv_files

with DAG (
    'multiple_files_dag',
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False
) as dag:

    files = get_files()

    extract_csv_task = extract_csv.expand(filename=files)

    transform_task = transform_to_kv.expand(data=extract_csv_task)

    extract_content_mappings_task = extract_csv(
        filename = "/opt/airflow/data/input_data/UsagiContentMapping_v5.csv"
    )

    harmonizer_task = harmonize.partial(
            mappings=extract_content_mappings_task, adhoc_harmonization=True
        ).expand(
            data = transform_task,
    )

    extract_column_mappings_task = extract_csv(
        filename = "/opt/airflow/data/input_data/UsagiExportColumnMapping_v2.csv"
    )

    migrator_task = migrate(data=extract_csv_task, mappings=extract_column_mappings_task, adhoc_migration=True)

    # create_conn_task = create_connection()

    # create_table_task = create_table(
    #     columns = [
    #         'person_id',
    #         'gender_concept_id',
    #         'year_of_birth',
    #         'month_of_birth',
    #         'day_of_birth',
    # 		'birth_datetime',
    #         'death_datetime',
    #         'race_concept_id',
    #         'ethnicity_concept_id',
    #         'location_id',
    # 		'provider_id',
    #         'care_site_id',
    #         'person_source_value',
    #         'gender_source_value',
    #         'gender_source_concept_id',
    # 		'race_source_value',
    #         'race_source_concept_id',
    #         'ethnicity_source_value',
    #         'ethnicity_source_concept_id'
    #     ],
    #     table_name = "person"
    # )

    extract_csv_task >> transform_task >> extract_content_mappings_task >> harmonizer_task >> extract_column_mappings_task >> migrator_task
    # create_conn_task >> create_table_task
