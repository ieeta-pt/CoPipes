import pandas as pd
from typing import Dict
from airflow.decorators import task 
from airflow.hooks.postgres_hook import PostgresHook
    
@task
def create_table(columns: list[str] | str, table_name: str, conn_id: str = "my_postgres") -> dict:
    """Creates a table in a PostgreSQL database."""

    table_name = table_name.strip().replace(" ", "_").split(".")[0]
    
    if isinstance(columns, str):    
        columns = [col.strip().replace(" ", "_") for col in columns.split(",")]

    db_data = pd.DataFrame(columns=columns)

    for element in columns:
        db_data[element] = None    

    pg_hook = PostgresHook(postgres_conn_id=conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {", ".join([f'"{col}" TEXT' for col in db_data.columns])}
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()

    return {"table": table_name}

