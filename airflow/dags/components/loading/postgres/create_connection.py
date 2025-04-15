from airflow.models import Connection
from airflow.settings import Session
from airflow.decorators import task

@task
def create_connection(
        connection_id: str = "my_postgres",
        connection_type: str = "postgres",
        host: str = "postgres",
        schema: str = "airflow",
        login: str = "airflow",
        password: str = "airflow",
        port: int = 5432
    ) -> None:
    """Creates a PostgreSQL connection in Airflow if it doesn't already exist."""
    session = Session()

    existing_conn = session.query(Connection).filter(Connection.connection_id == connection_id).first()
    if existing_conn:
        print(f"Connection '{connection_id}' already exists.")
        session.close()
        return
    
    new_conn = Connection(
        connection_id=connection_id,
        connection_type=connection_type,
        host=host,
        schema=schema,
        login=login,
        password=password,
        port=port
    )

    session.add(new_conn)
    session.commit()
    session.close()
    print(f"Connection '{connection_id}' created successfully.")
