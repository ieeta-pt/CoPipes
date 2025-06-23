from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.transformation.cohorts.migrate import migrate
from components.loading.postgres.write_to_db import write_to_db
from components.transformation.cohorts.harmonize import harmonize
from components.loading.postgres.create_connection import create_connection
from components.loading.postgres.create_table import create_table
from components.extraction.csv import csv
from components.transformation.cohorts.to_key_value import to_key_value

with DAG (
    dag_id="user_f06a4d64_e412_4c58_b184_6f65e8cd625b_Cohort_data_harmonisation_",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_mjd = csv(filename='', file_separation='Comma')
    csv_sjw = csv(filename='', file_separation='Comma')
    csv_jwo = csv(filename='', file_separation='Comma')
    to_key_value_85b = to_key_value(data='', fixed_columns='', measurement_columns='')
    harmonize_y3c = harmonize(data='', mappings='', adhoc_harmonization='False')
    migrate_c70 = migrate(person_data='', observation_data='', mappings='', adhoc_migration='False')
    create_connection_4a8 = create_connection(conn_id='my_postgres', host='postgres', schema='airflow', login='airflow', password='airflow', port='5432')
    create_table_eay = create_table(columns='', table_name='')
    write_to_db_zf6 = write_to_db(data='', table_name='', conn_id='my_postgres')

    csv_mjd >> csv_sjw
    csv_sjw >> csv_jwo
    csv_jwo >> to_key_value_85b
    to_key_value_85b >> harmonize_y3c
    harmonize_y3c >> migrate_c70
    migrate_c70 >> create_connection_4a8
    create_connection_4a8 >> create_table_eay
    create_table_eay >> write_to_db_zf6
