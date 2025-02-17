import pandas as pd
from airflow.decorators import task
from airflow.hooks.postgres_hook import PostgresHook

@task
def write_to_postgres(df: pd.DataFrame, table_name: str, postgres_conn_id: str = "my_postgres"):
    """Writes a DataFrame to a PostgreSQL table."""
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    engine = pg_hook.get_sqlalchemy_engine()
    
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Data written to table {table_name}")