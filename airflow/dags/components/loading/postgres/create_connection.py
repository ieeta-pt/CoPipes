from airflow.models import Connection
from airflow.settings import Session
from airflow.decorators import task

@task
def create_connection(
        conn_id: str = "my_postgres",
        conn_type: str = "postgres",
        host: str = "postgres",
        schema: str = "airflow",
        login: str = "airflow",
        password: str = "airflow",
        port: int = 5432
    ) -> str:
    """Creates a PostgreSQL connection in Airflow if it doesn't already exist."""
    session = Session()

    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    if existing_conn:
        print(f"Connection '{conn_id}' already exists.")
        session.close()
        return conn_id
    
    new_conn = Connection(
        conn_id=conn_id,
        conn_type=conn_type,
        host=host,
        schema=schema,
        login=login,
        password=password,
        port=port
    )

    session.add(new_conn)
    session.commit()
    session.close()
    print(f"Connection '{conn_id}' created successfully.")
    return conn_id
