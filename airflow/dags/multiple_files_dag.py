from datetime import datetime
from airflow import DAG

from components.extraction.csv import csv
from components.transformation.cohorts.to_key_value import to_key_value
from components.transformation.cohorts.harmonize import harmonize
from components.utils.cohorts.standard_ad_hoc import create_new_measures
from components.transformation.cohorts.migrate import migrate
from components.loading.postgres.create_connection import create_connection
from components.loading.postgres.create_table import create_table
from components.loading.postgres.write_to_db import write_to_db

##### UTILS FUNCTIONS #####

def get_files():
    csv_files = ["/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Diagnosis.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Sleep.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Blood and CSF.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Neuropsychology.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Patient Data.csv"]
    return csv_files

with DAG (
    'cohort_harmonization_dag',
    schedule=None,
    start_date=datetime(2025, 2, 3),
    catchup=False
) as dag:

    files = get_files()

    extract_csv_task = csv.expand(filename=files)

    transform_task = to_key_value.expand(data=extract_csv_task)

    extract_content_mappings_task = csv(
        filename = "/opt/airflow/data/input_data/UsagiExportContentMapping_v6.csv"
    )

    harmonizer_task = harmonize.partial(
            mappings=extract_content_mappings_task, 
            adhoc_harmonization=True
        ).expand(
            data = transform_task,
    )

    adhoc_task = create_new_measures(
        data=harmonizer_task, 
        adhoc_harmonization=True
    )

    extract_column_mappings_task = csv(
        filename = "/opt/airflow/data/input_data/UsagiExportColumnMapping_v2.csv"
    )

    migrator_task = migrate(
        person_data=extract_csv_task, 
        observation_data=adhoc_task, 
        mappings=extract_column_mappings_task, 
        adhoc_migration=True
    )

    create_conn_task = create_connection()

    create_table_person_task = create_table(
        columns = [
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
        table_name = "person"
    )

    write_to_table_person_task = write_to_db(
        data=migrator_task,
        table_name="person"
    )

    create_table_obs_task = create_table(
        columns = [
            'observation_id',
            'person_id',
            'observation_concept_id',
            'observation_date',
            'observation_datetime',
            'observation_type_concept_id',
            'value_as_number',
            'value_as_string',
            'value_as_concept_id',
            'unit_concept_id',
            'provider_id',
            'visit_occurrence_id',
            'visit_detail_id',
            'observation_source_value',
            'observation_source_concept_id',
            'unit_source_value',
            'qualifier_source_value'
        ],
        table_name = "observation"
    )

    extract_csv_task >> transform_task >> extract_content_mappings_task >> harmonizer_task >> extract_column_mappings_task >> migrator_task
    create_conn_task >> create_table_person_task >> write_to_table_person_task
    create_conn_task >> create_table_obs_task
