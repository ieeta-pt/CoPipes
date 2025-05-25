from airflow import DAG
from datetime import datetime

from components.transformation.cohorts.to_key_value import to_key_value
from components.extraction.csv import csv
from components.transformation.cohorts.harmonize import harmonize

with DAG (
    dag_id="brfbd",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_a2w = csv(filename='', file_separation='comma')
    to_key_value_vk1 = to_key_value(data='Data to reorganize', fixed_columns='List of fixed columns names', measurement_columns='List of measurement columns')
    harmonize_cmw = harmonize(data='Data to harmonize', mappings='Data mappings', adhoc_harmonization='false')
    csv_k4n = csv(filename='', file_separation='comma')

    csv_a2w >> to_key_value_vk1
    to_key_value_vk1 >> harmonize_cmw
    csv_tbn >> harmonize_cmw
    csv_k4n >> harmonize_cmw
