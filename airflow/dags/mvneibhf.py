from airflow import DAG
from datetime import datetime

from components.transformation.cohorts.to_key_value import to_key_value
from components.transformation.cohorts.harmonize import harmonize
from components.extraction.csv import csv

with DAG (
    dag_id="mvneibhf",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_0h = csv(filename='', file_separation=',')
    to_key_value_9u = to_key_value(data='Data to reorganize', fixed_columns='List of fixed columns names', measurement_columns='List of measurement columns')
    harmonize_7d = harmonize(data='Data to harmonize', mappings='Data mappings', adhoc_harmonization='True / False')


