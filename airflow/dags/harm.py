from airflow import DAG
from datetime import datetime

from components.transformation.cohorts.harmonize import harmonize

with DAG (
    dag_id="harm",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    harmonize_4w4 = harmonize(data='Data to harmonize', mappings='Data mappings', adhoc_harmonization='true')


