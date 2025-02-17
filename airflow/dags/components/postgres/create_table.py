import pandas as pd
from typing import Dict
from airflow.decorators import task 
from airflow.hooks.postgres_hook import PostgresHook
    
@task
def create_table(columns, table_name: str) -> Dict[str, dict]:
    """Creates a table in a PostgreSQL database."""

    mapping = pd.DataFrame(columns=columns)

    for element in columns:
        mapping[element] = None    

    pg_hook = PostgresHook(postgres_conn_id="my_postgres")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {", ".join([f'"{col}" TEXT' for col in mapping.columns])}
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()

    return {"mapping": mapping.to_dict(), "table": table_name}

