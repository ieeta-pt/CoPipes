import json
import pandas as pd
from typing import Dict, Optional, Any
from airflow.decorators import task
from sqlalchemy import create_engine

@task
def database_query(connection: Dict[str, Any], query: str, parameters: Optional[str] = None) -> Dict[str, str]:
    """
    Execute SQL query against a database connection.
    
    Args:
        connection: Database connection info from create_connection task
        query: SQL query to execute
        parameters: Query parameters in JSON format
    
    Returns:
        Dictionary containing query results and metadata
    """
    try:
        # Parse parameters if provided
        params = {}
        if parameters:
            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                print(f"Warning: Invalid parameters JSON format: {parameters}")
        
        # Extract connection info
        conn_info = connection.get('connection_info', {})
        db_type = conn_info.get('type', 'postgresql')
        
        # Create database connection based on type
        if db_type.lower() == 'postgresql':
            # Build PostgreSQL connection string
            host = conn_info.get('host', 'localhost')
            port = conn_info.get('port', 5432)
            database = conn_info.get('database', conn_info.get('schema', 'postgres'))
            username = conn_info.get('username', conn_info.get('login', 'postgres'))
            password = conn_info.get('password', '')
            
            conn_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(conn_string)
            
        elif db_type.lower() == 'sqlite':
            # SQLite connection
            db_path = conn_info.get('database', ':memory:')
            conn_string = f"sqlite:///{db_path}"
            engine = create_engine(conn_string)
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Execute query
        if params:
            df = pd.read_sql_query(query, engine, params=params)
        else:
            df = pd.read_sql_query(query, engine)
        
        # Replace NaN with None for consistent handling
        df = df.where(pd.notna(df), None)
        
        print(f"Successfully executed database query")
        print(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        print(f"Shape: {df.shape}, Columns: {df.columns.tolist()}")
        
        return {
            "data": df.to_dict(orient="records"),
            "filename": f"query_result_{hash(query)}.csv",
            "query": query,
            "row_count": len(df)
        }
        
    except Exception as e:
        raise ValueError(f"Database query failed: {e}")
    finally:
        # Clean up connection
        try:
            engine.dispose()
        except:
            pass