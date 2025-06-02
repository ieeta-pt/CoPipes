import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def write_to_db(
    data: Dict[str, Any],
    table_name: str,
    connection_id: str = "postgres_default",
    schema: str = "public",
    if_exists: str = "append",
    conflict_columns: Optional[List[str]] = None,
    **context
) -> Dict[str, Any]:
    """
    Write data to PostgreSQL database with configurable options.
    
    Args:
        data: Input data dictionary with 'data' key containing records
        table_name: Target table name
        connection_id: Airflow connection ID for PostgreSQL
        schema: Database schema name
        if_exists: Action if table exists ('append', 'replace', 'upsert')
        conflict_columns: Columns to check for conflicts in upsert mode
        **context: Airflow context
    
    Returns:
        Dict containing write operation results
    """
    if not data or 'data' not in data:
        logger.error("No valid data to insert into the database.")
        raise ValueError("No valid data to insert into the database.")

    df = pd.DataFrame(data['data'])
    
    if df.empty:
        logger.warning("DataFrame is empty, nothing to insert.")
        return {
            "status": "success",
            "rows_inserted": 0,
            "message": "No data to insert"
        }

    logger.info(f"Preparing to insert {len(df)} records into table '{table_name}'")

    try:
        postgres_hook = PostgresHook(postgres_conn_id=connection_id)
        
        if if_exists == "replace":
            # Truncate table before inserting
            truncate_sql = f"TRUNCATE TABLE {schema}.{table_name}"
            postgres_hook.run(truncate_sql)
            logger.info(f"Truncated table '{table_name}'")
        
        if if_exists == "upsert" and conflict_columns:
            # Build upsert query
            columns = list(df.columns)
            placeholders = ', '.join(['%s'] * len(columns))
            update_clauses = [f"{col} = EXCLUDED.{col}" for col in columns if col not in conflict_columns]
            
            insert_sql = f"""
                INSERT INTO {schema}.{table_name} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT ({', '.join(conflict_columns)}) DO UPDATE SET 
                {', '.join(update_clauses)}
            """
        else:
            # Simple insert query
            columns = list(df.columns)
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"""
                INSERT INTO {schema}.{table_name} ({', '.join(columns)})
                VALUES ({placeholders})
            """
        
        # Convert DataFrame to list of tuples
        records = [tuple(row) for row in df.itertuples(index=False, name=None)]
        
        # Insert records
        rows_inserted = 0
        for record in records:
            postgres_hook.run(insert_sql, parameters=record, autocommit=True)
            rows_inserted += 1
        
        logger.info(f"Successfully inserted {rows_inserted} records into table '{table_name}'")
        
        return {
            "status": "success",
            "table_name": table_name,
            "schema": schema,
            "rows_inserted": rows_inserted,
            "if_exists_mode": if_exists,
            "conflict_columns": conflict_columns or []
        }
        
    except Exception as e:
        error_msg = f"Error writing to database table '{table_name}': {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
