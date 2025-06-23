from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.transformation.data_aggregation import data_aggregation
from components.loading.file_export import file_export
from components.extraction.csv import csv
from components.transformation.data_cleaning import data_cleaning

with DAG (
    dag_id="user_8a7f57f9_99e4_4171_b992_ab6f2bd1328a_Customer_survey_monthly_analysis",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_3pi = csv(filename='customer_survey_march_2024.csv', file_separation=',')
    data_cleaning_gou = data_cleaning(data=csv_3pi, remove_duplicates='False', handle_missing_values='drop', outlier_detection='zscore', outlier_threshold='3')
    data_aggregation_lq6 = data_aggregation(data=data_cleaning_gou, group_by_columns='age', aggregation_functions='avg(satisfaction_score)', having_conditions='')
    file_export_ew4 = file_export(data=data_aggregation_lq6, file_path='march_2024_results', file_format='csv', compression='none', include_header='True')


