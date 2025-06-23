from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.transformation.cohorts.harmonize import harmonize
from components.transformation.cohorts.to_key_value import to_key_value
from components.extraction.csv import csv

with DAG (
    dag_id="user_01f2083c_0ca6_4cd9_9502_64ba46bdfa85_csv_data_extraction_and_harmonisation",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_o26 = csv(filename='', file_separation='Comma')
    to_key_value_zyd = to_key_value(data='', fixed_columns='', measurement_columns='')
    harmonize_wq9 = harmonize(data='', mappings='', adhoc_harmonization='False')


