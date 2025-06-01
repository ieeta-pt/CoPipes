from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.analysis.machine_learning.data_preprocessing import data_preprocessing
from components.analysis.machine_learning.model_evaluation import model_evaluation
from components.analysis.machine_learning.model_deployment import model_deployment
from components.analysis.machine_learning.data_ingestion import data_ingestion
from components.analysis.machine_learning.model_training import model_training

with DAG (
    dag_id="user_d65788fe_2aba_478a_9513_bd7c01d72ca7_ml",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    data_ingestion_s3i = data_ingestion()
    data_preprocessing_llq = data_preprocessing()
    model_training_chd = model_training()
    model_evaluation_4sy = model_evaluation(mae_threshold='120')
    model_deployment_orc = model_deployment()


