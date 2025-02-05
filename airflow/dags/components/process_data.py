import pandas as pd
from airflow.utils.log.logging_mixin import LoggingMixin

def process_data(**kwargs):
    """Calculates NotaF (final grade) and prepares data for DB insertion."""
    logger = LoggingMixin().log
    ti = kwargs['ti']
    data = ti.xcom_pull(key='data', task_ids='read_csv')

    if not data:
        logger.error("No data received from read_csv task.")
        raise ValueError("No data received from read_csv task.")

    df = pd.DataFrame(data)
    df['NotaF'] = df['NotaT'] + df['NotaP']
    
    logger.info("Processed data successfully.")
    ti.xcom_push(key='processed_data', value=df.to_dict())
