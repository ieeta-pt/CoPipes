from airflow import DAG
from datetime import datetime

from components.transformation.cohorts.migrate import migrate
from components.transformation.cohorts.harmonize import harmonize
from components.loading.postgres.create_table import create_table
from components.loading.postgres.create_connection import create_connection
from components.transformation.cohorts.to_key_value import to_key_value
from components.extraction.csv import csv
from components.loading.postgres.write_to_db import write_to_db

with DAG (
    dag_id="complete",
    schedule_interval=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_w6b = csv(filename='File to read', file_separation='Comma')
    to_key_value_ooa = to_key_value(data='Data to reorganize (CSV extraction result)', fixed_columns='List of fixed columns names (separated by commas)', measurement_columns='List of measurement columns (separated by commas)')
    harmonize_tff = harmonize(data='Data to harmonize (To key value result)', mappings='Data mappings (CSV extraction result or file)', adhoc_harmonization='False')
    migrate_9kj = migrate(person_data='Data for personal information table (CSV extraction result)', observation_data='Data for personal information table (Harmonize result)', mappings='Data mappings (CSV extraction result or file)', adhoc_migration='False')
    create_connection_aga = create_connection()
    create_table_g84 = create_table(columns='List of columns (separated by commas)', table_name='My table')
    write_to_db_2ph = write_to_db(data='Table contents (Migrate result)', table_name='My table')


