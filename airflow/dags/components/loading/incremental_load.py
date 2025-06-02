import os
import pandas as pd
from typing import Dict, Any, Optional
from airflow.decorators import task
from sqlalchemy import create_engine, text
from datetime import datetime
import json

UPLOAD_DIR = "/shared_data/"

@task
def incremental_load(data: Dict[str, Any], destination: str, key_columns: str,
                    timestamp_column: Optional[str] = None, last_sync_timestamp: Optional[str] = None,
                    delete_detection: bool = False) -> Dict[str, Any]:
    """
    Load data incrementally based on key columns and timestamps.
    
    Args:
        data: Input data from transformation task
        destination: Destination table or location
        key_columns: Columns to identify unique records (separated by commas)
        timestamp_column: Column to track record updates
        last_sync_timestamp: Last synchronization timestamp
        delete_detection: Detect and handle deleted records
    
    Returns:
        Dictionary containing incremental load results and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for incremental loading")
        
        # Convert to DataFrame
        new_df = pd.DataFrame(input_data)
        total_new_rows = len(new_df)
        
        print(f"Starting incremental load. New data rows: {total_new_rows}")
        print(f"Destination: {destination}")
        
        # Parse key columns
        key_cols = [col.strip() for col in key_columns.split(',')]
        
        # Validate key columns exist
        missing_key_cols = [col for col in key_cols if col not in new_df.columns]
        if missing_key_cols:
            raise ValueError(f"Key columns not found in data: {missing_key_cols}")
        
        # Validate timestamp column if provided
        if timestamp_column and timestamp_column not in new_df.columns:
            raise ValueError(f"Timestamp column '{timestamp_column}' not found in data")
        
        print(f"Key columns: {key_cols}")
        if timestamp_column:
            print(f"Timestamp column: {timestamp_column}")
        
        # Handle different destination types
        if destination.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            return _incremental_load_to_database(new_df, destination, key_cols, timestamp_column,
                                               last_sync_timestamp, delete_detection, data)
        else:
            return _incremental_load_to_file(new_df, destination, key_cols, timestamp_column,
                                           last_sync_timestamp, data)
        
    except Exception as e:
        raise ValueError(f"Incremental load failed: {e}")

def _incremental_load_to_database(new_df: pd.DataFrame, connection_string: str, key_cols: list,
                                 timestamp_column: Optional[str], last_sync_timestamp: Optional[str],
                                 delete_detection: bool, data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform incremental load to database"""
    
    # Extract table name from data or use default
    table_name = data.get('table_name') or data.get('filename', 'incremental_table').split('.')[0]
    table_name = table_name.replace('-', '_').replace(' ', '_')
    
    # Create database engine
    engine = create_engine(connection_string)
    
    try:
        # Check if table exists and get existing data
        existing_df = None
        try:
            existing_df = pd.read_sql_table(table_name, engine)
            print(f"Found existing table '{table_name}' with {len(existing_df)} rows")
        except:
            print(f"Table '{table_name}' does not exist, will create new table")
        
        inserts = 0
        updates = 0
        deletes = 0
        
        if existing_df is None or len(existing_df) == 0:
            # First load - insert all data
            new_df.to_sql(table_name, engine, if_exists='replace', index=False)
            inserts = len(new_df)
            print(f"Initial load: Inserted {inserts} rows")
            
        else:
            # Incremental load - identify changes
            
            # Filter new data by timestamp if provided
            filtered_new_df = new_df
            if timestamp_column and last_sync_timestamp:
                try:
                    sync_time = pd.to_datetime(last_sync_timestamp)
                    new_timestamps = pd.to_datetime(new_df[timestamp_column])
                    filtered_new_df = new_df[new_timestamps > sync_time]
                    print(f"Filtered to {len(filtered_new_df)} rows newer than {last_sync_timestamp}")
                except Exception as e:
                    print(f"Warning: Could not filter by timestamp: {e}")
            
            if len(filtered_new_df) == 0:
                print("No new data to process")
                return {
                    "data": [{"message": "No new data to process"}],
                    "filename": f"incremental_load_{table_name}.csv",
                    "destination": connection_string,
                    "table_name": table_name,
                    "inserts": 0,
                    "updates": 0,
                    "deletes": 0
                }
            
            # Identify new and updated records
            existing_keys = existing_df[key_cols].apply(lambda x: '|'.join(x.astype(str)), axis=1)
            new_keys = filtered_new_df[key_cols].apply(lambda x: '|'.join(x.astype(str)), axis=1)
            
            # Records to insert (new keys)
            insert_mask = ~new_keys.isin(existing_keys)
            insert_df = filtered_new_df[insert_mask]
            
            # Records to update (existing keys)
            update_mask = new_keys.isin(existing_keys)
            update_df = filtered_new_df[update_mask]
            
            # Insert new records
            if len(insert_df) > 0:
                insert_df.to_sql(table_name, engine, if_exists='append', index=False)
                inserts = len(insert_df)
                print(f"Inserted {inserts} new records")
            
            # Update existing records (delete old, insert new)
            if len(update_df) > 0:
                # Create temporary table for updates
                temp_table = f"{table_name}_temp_updates"
                update_df.to_sql(temp_table, engine, if_exists='replace', index=False)
                
                # Build delete query for records being updated
                key_conditions = []
                for _, row in update_df.iterrows():
                    conditions = [f"{col} = '{row[col]}'" for col in key_cols]
                    key_conditions.append(f"({' AND '.join(conditions)})")
                
                if key_conditions:
                    delete_query = f"DELETE FROM {table_name} WHERE {' OR '.join(key_conditions)}"
                    engine.execute(text(delete_query))
                    
                    # Insert updated records
                    update_df.to_sql(table_name, engine, if_exists='append', index=False)
                    updates = len(update_df)
                    print(f"Updated {updates} existing records")
                
                # Clean up temp table
                engine.execute(text(f"DROP TABLE IF EXISTS {temp_table}"))
            
            # Handle deletions if enabled
            if delete_detection:
                # Find records in existing data that are not in new data
                deleted_keys = existing_keys[~existing_keys.isin(new_keys)]
                if len(deleted_keys) > 0:
                    # This is a simplified deletion detection
                    # In practice, you might want more sophisticated logic
                    print(f"Warning: {len(deleted_keys)} records appear to be deleted")
                    deletes = len(deleted_keys)
        
        # Get current timestamp for next sync
        current_timestamp = datetime.now().isoformat()
        
        print(f"Incremental load completed. Inserts: {inserts}, Updates: {updates}, Deletes: {deletes}")
        
        return {
            "data": [{"message": f"Incremental load completed: {inserts} inserts, {updates} updates, {deletes} deletes"}],
            "filename": f"incremental_load_{table_name}.csv",
            "destination": connection_string,
            "table_name": table_name,
            "inserts": inserts,
            "updates": updates,
            "deletes": deletes,
            "last_sync_timestamp": current_timestamp,
            "key_columns": key_cols,
            "timestamp_column": timestamp_column
        }
        
    finally:
        engine.dispose()

def _incremental_load_to_file(new_df: pd.DataFrame, destination: str, key_cols: list,
                             timestamp_column: Optional[str], last_sync_timestamp: Optional[str],
                             data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform incremental load to file"""
    
    # Handle full path vs relative path
    if not destination.startswith('/'):
        file_path = os.path.join(UPLOAD_DIR, destination)
    else:
        file_path = destination
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else UPLOAD_DIR, exist_ok=True)
    
    try:
        existing_df = None
        
        # Try to read existing file
        if os.path.exists(file_path):
            try:
                file_ext = os.path.splitext(destination)[1].lower()
                if file_ext == '.csv':
                    existing_df = pd.read_csv(file_path, dtype=str)
                elif file_ext == '.json':
                    existing_df = pd.read_json(file_path)
                elif file_ext == '.parquet':
                    existing_df = pd.read_parquet(file_path)
                else:
                    existing_df = pd.read_csv(file_path, dtype=str)
                    
                print(f"Found existing file with {len(existing_df)} rows")
            except Exception as e:
                print(f"Warning: Could not read existing file: {e}")
        
        inserts = 0
        updates = 0
        
        if existing_df is None or len(existing_df) == 0:
            # First load
            combined_df = new_df
            inserts = len(new_df)
        else:
            # Incremental merge
            
            # Filter new data by timestamp if provided
            filtered_new_df = new_df
            if timestamp_column and last_sync_timestamp:
                try:
                    sync_time = pd.to_datetime(last_sync_timestamp)
                    new_timestamps = pd.to_datetime(new_df[timestamp_column])
                    filtered_new_df = new_df[new_timestamps > sync_time]
                    print(f"Filtered to {len(filtered_new_df)} rows newer than {last_sync_timestamp}")
                except Exception as e:
                    print(f"Warning: Could not filter by timestamp: {e}")
            
            # Merge data based on key columns
            existing_keys = existing_df[key_cols].apply(lambda x: '|'.join(x.astype(str)), axis=1)
            new_keys = filtered_new_df[key_cols].apply(lambda x: '|'.join(x.astype(str)), axis=1)
            
            # Remove existing records that will be updated
            mask_to_keep = ~existing_keys.isin(new_keys)
            kept_existing = existing_df[mask_to_keep]
            
            # Combine kept existing with all new/updated data
            combined_df = pd.concat([kept_existing, filtered_new_df], ignore_index=True)
            
            # Calculate stats
            inserts = len(filtered_new_df[~new_keys.isin(existing_keys)])
            updates = len(filtered_new_df[new_keys.isin(existing_keys)])
        
        # Save combined data
        file_ext = os.path.splitext(destination)[1].lower()
        if file_ext == '.csv':
            combined_df.to_csv(file_path, index=False)
        elif file_ext == '.json':
            combined_df.to_json(file_path, orient='records', indent=2)
        elif file_ext == '.parquet':
            combined_df.to_parquet(file_path, index=False)
        else:
            combined_df.to_csv(file_path, index=False)
        
        current_timestamp = datetime.now().isoformat()
        
        print(f"Incremental file load completed. Inserts: {inserts}, Updates: {updates}")
        
        return {
            "data": [{"message": f"Incremental load completed: {inserts} inserts, {updates} updates"}],
            "filename": f"incremental_load_{os.path.basename(destination)}",
            "destination": destination,
            "file_path": file_path,
            "inserts": inserts,
            "updates": updates,
            "total_rows": len(combined_df),
            "last_sync_timestamp": current_timestamp,
            "key_columns": key_cols,
            "timestamp_column": timestamp_column
        }
        
    except Exception as e:
        raise ValueError(f"Failed incremental load to file '{destination}': {e}")