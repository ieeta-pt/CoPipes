from airflow import DAG
from datetime import datetime

from components.postgres.create_conn import create_connection
from components.postgres.create_table import create_table

with DAG(
    dag_id="create_table_dag",
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False,
    description="This DAG creates a table in a PostgreSQL database."
) as dag:
    create_connection_task = create_connection()

    create_table_task = create_table(
        columns = [
            "ancestor_concept_id",
            "descendant_concept_id",
            "min_levels_of_separation",
            "max_levels_of_separation"
        ],
        table_name = "concept_ancestor"
    )
        
    create_connection_task >> create_table_task
