from airflow.models import Connection
from airflow.settings import Session

def create_postgres_connection():
    """Creates a PostgreSQL connection in Airflow if it doesn't already exist."""
    session = Session()
    conn_id = "my_postgres"

    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    if existing_conn:
        print(f"Connection '{conn_id}' already exists.")
        session.close()
        return
    
    new_conn = Connection(
        conn_id=conn_id,
        conn_type="postgres",
        host="postgres",
        schema="airflow",
        login="airflow",
        password="airflow",
        port=5432
    )

    session.add(new_conn)
    session.commit()
    session.close()
    print(f"Connection '{conn_id}' created successfully.")
