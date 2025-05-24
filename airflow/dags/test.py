from airflow import DAG
from datetime import datetime

from components.extraction.csv import csv
from components.loading.postgres.create_connection import create_connection
from components.transformation.cohorts.migrate import migrate
from components.transformation.cohorts.harmonize import harmonize
from components.transformation.cohorts.to_key_value import to_key_value
from components.loading.postgres.write_to_db import write_to_db
from components.loading.postgres.create_table import create_table

with DAG (
    dag_id="test",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_s47 = csv(filename='', file_separation=',')
    to_key_value_95y = to_key_value(data='Data to reorganize', fixed_columns='List of fixed columns names', measurement_columns='List of measurement columns')
    create_connection_m7x = create_connection(database_name='My database')
    harmonize_k4s = harmonize(data='Data to harmonize', mappings='Data mappings', adhoc_harmonization='True / False')
    create_table_rmq = create_table(columns='List of columns', table_name='My table')
    migrate_bsd = migrate(person_data='Data for personal information table', observation_data='Data for personal information table', mappings='Data mappings', adhoc_migration='True / False')
    write_to_db_ssy = write_to_db(data='Table contents', table_name='My table')


