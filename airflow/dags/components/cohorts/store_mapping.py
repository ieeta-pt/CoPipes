from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
from airflow.decorators import task

@task
def store_mapping(data: dict):
        mapping_dict = data["mapping"]
        table = data["table"]

        if not mapping_dict:
            raise ValueError("No mapping data received!")

        if not table:
            raise ValueError("No table name received!")

        mapping = pd.DataFrame.from_dict(mapping_dict)

        pg_hook = PostgresHook(postgres_conn_id="my_postgres")
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {", ".join([f'"{col}" TEXT' for col in mapping.columns])}
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()