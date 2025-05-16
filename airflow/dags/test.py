from airflow import DAG
from datetime import datetime

from components.transformation.cohorts.migrate import migrate
from components.extraction.csv import csv
from components.transformation.cohorts.harmonize import harmonize
from components.transformation.cohorts.to_key_value import to_key_value

with DAG (
    dag_id="Test",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_gft = csv(filename='', file_separation=',')
    harmonize_igk = harmonize(data='Data to harmonize', mappings='Data mappings', adhoc_harmonization='True / False')
    to_key_value_fcd = to_key_value(data='Data to reorganize', fixed_columns='List of fixed columns names', measurement_columns='List of measurement columns')
    migrate_nss = migrate(person_data='Data for personal information table', observation_data='Data for personal information table', mappings='Data mappings', adhoc_migration='True / False')


