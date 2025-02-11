from airflow.providers.postgres.operators.postgres import PostgresOperator

def create_table():
    """Creates the student_grades table if it doesn't exist."""
    return PostgresOperator(
        task_id="create_table",
        postgres_conn_id="my_postgres",
        sql="""
        CREATE TABLE IF NOT EXISTS student_grades (
            NMec INT PRIMARY KEY,
            NotaT FLOAT,
            NotaP FLOAT,
            NotaF FLOAT
        );
        """
    )
