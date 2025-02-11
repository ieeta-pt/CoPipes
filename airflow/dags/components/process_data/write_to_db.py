import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.log.logging_mixin import LoggingMixin

def write_to_db(**kwargs):
    """Inserts the processed data into the PostgreSQL database."""
    logger = LoggingMixin().log
    ti = kwargs['ti']
    processed_data = ti.xcom_pull(key='processed_data', task_ids='process_data')

    if not processed_data:
        logger.error("No data to insert into the database.")
        raise ValueError("No data to insert into the database.")

    df = pd.DataFrame(processed_data)
    records = [tuple(row) for row in df.itertuples(index=False, name=None)]

    logger.info(f"Records to insert: {records}")

    if not records:
        raise ValueError("No records to insert into the database.")

    postgres_hook = PostgresHook(postgres_conn_id="my_postgres")
    insert_query = """
        INSERT INTO student_grades (NMec, NotaT, NotaP, NotaF)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (NMec) DO UPDATE SET 
            NotaT = EXCLUDED.NotaT, 
            NotaP = EXCLUDED.NotaP, 
            NotaF = EXCLUDED.NotaF;
    """

    for record in records:
        postgres_hook.run(insert_query, parameters=record, autocommit=True)
    logger.info("Data successfully inserted into the database.")
