import pandas as pd
from airflow.utils.log.logging_mixin import LoggingMixin

def read_csv(input_file: str, **kwargs):
    """Reads data from a CSV file and pushes it to XCom."""
    logger = LoggingMixin().log
    try:
        df = pd.read_csv(input_file)
        logger.info(f"Read CSV file successfully: {input_file}")
        kwargs['ti'].xcom_push(key='csv_data', value=df.to_dict())
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        raise
