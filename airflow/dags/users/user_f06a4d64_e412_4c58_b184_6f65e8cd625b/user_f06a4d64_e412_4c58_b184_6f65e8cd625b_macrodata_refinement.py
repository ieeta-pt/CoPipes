from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.extraction.csv import csv
from components.transformation.cohorts.to_key_value import to_key_value

with DAG (
    dag_id="user_f06a4d64_e412_4c58_b184_6f65e8cd625b_Macrodata_refinement",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_jla = csv(filename='20190510 EMIF Patient Data.csv', file_separation=',')
    to_key_value_24z = to_key_value(data=csv_jla, fixed_columns='', measurement_columns='')


