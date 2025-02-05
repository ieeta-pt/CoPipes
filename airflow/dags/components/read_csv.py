import pandas as pd
from airflow.utils.log.logging_mixin import LoggingMixin

# Define file path
INPUT_FILE = "/opt/airflow/data/input_data/input.csv"

def read_csv(**kwargs):
    """Reads data from a CSV file and pushes it to XCom."""
    logger = LoggingMixin().log
    try:
        df = pd.read_csv(INPUT_FILE)
        logger.info(f"Read CSV file successfully: {INPUT_FILE}")
        kwargs['ti'].xcom_push(key='data', value=df.to_dict())
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        raise
