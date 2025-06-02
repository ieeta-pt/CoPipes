import logging
from typing import Dict, List, Any
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def create_table(
    table_name: str,
    columns: List[Dict[str, str]],
    connection_id: str = "postgres_default",
    schema: str = "public",
    if_not_exists: bool = True,
    **context
) -> Dict[str, Any]:
    """
    Create a PostgreSQL table with configurable schema.
    
    Args:
        table_name: Name of the table to create
        columns: List of column definitions with 'name', 'type', and optional 'constraints'
        connection_id: Airflow connection ID for PostgreSQL
        schema: Database schema name
        if_not_exists: Whether to use IF NOT EXISTS clause
        **context: Airflow context
    
    Returns:
        Dict containing table creation results
    """
    logger.info(f"Creating table '{table_name}' with {len(columns)} columns")
    
    # Build column definitions
    column_defs = []
    for col in columns:
        col_def = f"{col['name']} {col['type']}"
        if 'constraints' in col:
            col_def += f" {col['constraints']}"
        column_defs.append(col_def)
    
    # Build SQL statement
    if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
    sql = f"""
        CREATE TABLE {if_not_exists_clause}{schema}.{table_name} (
            {', '.join(column_defs)}
        );
    """
    
    logger.info(f"Executing SQL: {sql}")
    
    try:
        # Execute the SQL
        postgres_hook = PostgresHook(postgres_conn_id=connection_id)
        postgres_hook.run(sql)
        
        logger.info(f"Table '{table_name}' created successfully")
        
        return {
            "status": "success",
            "table_name": table_name,
            "schema": schema,
            "columns_created": len(columns),
            "sql_executed": sql.strip()
        }
        
    except Exception as e:
        error_msg = f"Error creating table '{table_name}': {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
