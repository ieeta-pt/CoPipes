from airflow import DAG
from datetime import datetime

from components.loading.postgres.write_to_db import write_to_db
from components.loading.postgres.create_table import create_table
from components.extraction.csv import csv
from components.loading.postgres.create_connection import create_connection
from components.transformation.cohorts.to_key_value import to_key_value
from components.transformation.cohorts.migrate import migrate
from components.transformation.cohorts.harmonize import harmonize

with DAG (
    dag_id="total",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_6nl = csv(filename='', file_separation=',')
    to_key_value_d44 = to_key_value(data='Data to reorganize', fixed_columns='List of fixed columns names', measurement_columns='List of measurement columns')
    harmonize_htv = harmonize(data='Data to harmonize', mappings='Data mappings', adhoc_harmonization='True / False')
    migrate_2ew = migrate(person_data='Data for personal information table', observation_data='Data for personal information table', mappings='Data mappings', adhoc_migration='True / False')
    create_connection_nhn = create_connection(database_name='My database')
    create_table_4hy = create_table(columns='List of columns', table_name='My table')
    write_to_db_ha9 = write_to_db(data='Table contents', table_name='My table')


