from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

# Import component functions
from components.analysis.machine_learning.data_ingestion import data_ingestion
from components.analysis.machine_learning.data_preprocessing import data_preprocessing
from components.analysis.machine_learning.model_training import model_training
from components.analysis.machine_learning.model_evaluation import model_evaluation
from components.analysis.machine_learning.model_deployment import model_deployment
from components.utils.notification import send_notification

# Default arguments for the DAG
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Initialize the DAG
dag = DAG(
    'ml_demand_forecasting_pipeline',
    default_args=default_args,
    description='End-to-end ML pipeline for demand forecasting using modular components',
    schedule_interval='@daily',  # Run daily
    max_active_runs=1,
    tags=['ml', 'forecasting', 'retail', 'modular']
)

# Define tasks using the imported component functions
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

data_ingestion_task = data_ingestion.override(task_id='data_ingestion')(dag=dag)

data_preprocessing_task = data_preprocessing.override(task_id='data_preprocessing')(dag=dag)

model_training_task = model_training.override(task_id='model_training')(dag=dag)

model_evaluation_task = model_evaluation.override(task_id='model_evaluation')(dag=dag)

model_deployment_task = model_deployment.override(task_id='model_deployment')(dag=dag)

notification_task = send_notification.override(
    task_id='send_notification',
    trigger_rule='all_done'  # Run regardless of upstream success/failure
)(dag=dag)

end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# Define task dependencies
start_task >> data_ingestion_task >> data_preprocessing_task >> model_training_task
model_training_task >> model_evaluation_task >> model_deployment_task >> notification_task >> end_task