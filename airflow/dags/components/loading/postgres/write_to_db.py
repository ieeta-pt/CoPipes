import pandas as pd
from airflow.decorators import task
from airflow.hooks.postgres_hook import PostgresHook

@task
def write_to_db(data: dict, table_name: str, conn_id: str = "my_postgres"):
    """Writes a DataFrame to a PostgreSQL table."""

    # table_name = data["filename"]
    table_name = table_name.strip().replace(" ", "_").split(".")[0]

    df = pd.DataFrame(data[table_name])
    df = df.where(pd.notna(df), None)

    pg_hook = PostgresHook(postgres_conn_id=conn_id)
    engine = pg_hook.get_sqlalchemy_engine()
    
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error writing to table {table_name}: {e}")
        raise e