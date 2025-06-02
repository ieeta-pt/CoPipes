import os
import pandas as pd
from typing import Dict, Any
from airflow.decorators import task
import json
from sqlalchemy import create_engine
import concurrent.futures
import math

UPLOAD_DIR = "/shared_data/"

@task
def batch_load(data: Dict[str, Any], destination: str, load_mode: str = "append",
               batch_size: int = 1000, parallel_workers: int = 1) -> Dict[str, Any]:
    """
    Load data in batches to various destinations.
    
    Args:
        data: Input data from transformation task
        destination: Destination (database connection string, file path, etc.)
        load_mode: How to handle existing data (append, overwrite, upsert)
        batch_size: Number of records per batch
        parallel_workers: Number of parallel load processes
    
    Returns:
        Dictionary containing load results and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for batch loading")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        total_rows = len(df)
        
        print(f"Starting batch load. Total rows: {total_rows}, Batch size: {batch_size}")
        print(f"Destination: {destination}, Load mode: {load_mode}")
        
        # Determine destination type and load accordingly
        if destination.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            return _load_to_database(df, destination, load_mode, batch_size, parallel_workers, data)
        elif destination.endswith(('.csv', '.json', '.parquet')):
            return _load_to_file(df, destination, load_mode, data)
        elif os.path.isdir(destination) or destination.startswith('/'):
            # File path destination
            return _load_to_directory(df, destination, load_mode, batch_size, data)
        else:
            raise ValueError(f"Unsupported destination type: {destination}")
        
    except Exception as e:
        raise ValueError(f"Batch load failed: {e}")

def _load_to_database(df: pd.DataFrame, connection_string: str, load_mode: str,
                     batch_size: int, parallel_workers: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Load data to database in batches"""
    
    # Extract table name from filename or use default
    table_name = data.get('filename', 'batch_load_table').split('.')[0]
    table_name = table_name.replace('-', '_').replace(' ', '_')
    
    # Create database engine
    engine = create_engine(connection_string)
    
    # Handle load mode
    if_exists_mapping = {
        'append': 'append',
        'overwrite': 'replace',
        'upsert': 'append'  # Will handle upsert logic separately
    }
    
    if_exists = if_exists_mapping.get(load_mode, 'append')
    
    try:
        total_rows = len(df)
        num_batches = math.ceil(total_rows / batch_size)
        
        print(f"Loading {total_rows} rows to database table '{table_name}' in {num_batches} batches")
        
        if parallel_workers > 1 and num_batches > 1:
            # Parallel loading
            batches = [df[i:i + batch_size] for i in range(0, total_rows, batch_size)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_workers) as executor:
                futures = []
                for i, batch in enumerate(batches):
                    # For first batch, handle if_exists mode; for others, always append
                    batch_if_exists = if_exists if i == 0 else 'append'
                    future = executor.submit(_load_batch_to_db, batch, connection_string, 
                                           table_name, batch_if_exists, i)
                    futures.append(future)
                
                # Wait for all batches to complete
                batch_results = []
                for future in concurrent.futures.as_completed(futures):
                    batch_results.append(future.result())
        else:
            # Sequential loading
            batch_results = []
            for i in range(0, total_rows, batch_size):
                batch = df[i:i + batch_size]
                batch_if_exists = if_exists if i == 0 else 'append'
                result = _load_batch_to_db(batch, connection_string, table_name, 
                                         batch_if_exists, i // batch_size)
                batch_results.append(result)
        
        successful_batches = sum(1 for result in batch_results if result['success'])
        total_loaded = sum(result['rows_loaded'] for result in batch_results if result['success'])
        
        print(f"Batch load completed. {successful_batches}/{len(batch_results)} batches successful")
        print(f"Total rows loaded: {total_loaded}")
        
        return {
            "data": [{"message": f"Successfully loaded {total_loaded} rows to {table_name}"}],
            "filename": f"batch_load_{table_name}.csv",
            "destination": connection_string,
            "table_name": table_name,
            "total_rows": total_rows,
            "rows_loaded": total_loaded,
            "batches_processed": len(batch_results),
            "successful_batches": successful_batches,
            "load_mode": load_mode
        }
        
    finally:
        engine.dispose()

def _load_batch_to_db(batch_df: pd.DataFrame, connection_string: str, table_name: str,
                     if_exists: str, batch_num: int) -> Dict[str, Any]:
    """Load a single batch to database"""
    try:
        engine = create_engine(connection_string)
        batch_df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        engine.dispose()
        
        print(f"Batch {batch_num}: Loaded {len(batch_df)} rows")
        return {"success": True, "rows_loaded": len(batch_df), "batch_num": batch_num}
        
    except Exception as e:
        print(f"Batch {batch_num} failed: {e}")
        return {"success": False, "rows_loaded": 0, "batch_num": batch_num, "error": str(e)}

def _load_to_file(df: pd.DataFrame, destination: str, load_mode: str,
                 data: Dict[str, Any]) -> Dict[str, Any]:
    """Load data to file"""
    
    # Ensure destination directory exists
    os.makedirs(os.path.dirname(destination) if os.path.dirname(destination) else UPLOAD_DIR, exist_ok=True)
    
    # Handle full path vs relative path
    if not destination.startswith('/'):
        file_path = os.path.join(UPLOAD_DIR, destination)
    else:
        file_path = destination
    
    # Check if file exists for load mode handling
    file_exists = os.path.exists(file_path)
    
    if load_mode == "overwrite" or not file_exists:
        # Write new file or overwrite existing
        mode = 'w'
    elif load_mode == "append":
        # Append to existing file (for CSV)
        mode = 'a'
    else:
        # Default to overwrite
        mode = 'w'
    
    try:
        file_ext = os.path.splitext(destination)[1].lower()
        
        if file_ext == '.csv':
            if mode == 'a' and file_exists:
                # Append without header
                df.to_csv(file_path, mode='a', index=False, header=False)
            else:
                df.to_csv(file_path, index=False)
        elif file_ext == '.json':
            if mode == 'a' and file_exists:
                # For JSON append, need to read existing and combine
                try:
                    existing_data = pd.read_json(file_path)
                    combined_df = pd.concat([existing_data, df], ignore_index=True)
                    combined_df.to_json(file_path, orient='records', indent=2)
                except:
                    # If reading fails, just overwrite
                    df.to_json(file_path, orient='records', indent=2)
            else:
                df.to_json(file_path, orient='records', indent=2)
        elif file_ext == '.parquet':
            df.to_parquet(file_path, index=False)
        else:
            # Default to CSV
            df.to_csv(file_path, index=False)
        
        print(f"Successfully loaded {len(df)} rows to file: {file_path}")
        
        return {
            "data": [{"message": f"Successfully loaded {len(df)} rows to {destination}"}],
            "filename": f"batch_load_{os.path.basename(destination)}",
            "destination": destination,
            "file_path": file_path,
            "rows_loaded": len(df),
            "load_mode": load_mode,
            "file_format": file_ext
        }
        
    except Exception as e:
        raise ValueError(f"Failed to load data to file '{destination}': {e}")

def _load_to_directory(df: pd.DataFrame, destination: str, load_mode: str,
                      batch_size: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Load data to directory as multiple files"""
    
    # Ensure directory exists
    os.makedirs(destination, exist_ok=True)
    
    # Generate filename based on input data
    base_filename = data.get('filename', 'batch_load_data').split('.')[0]
    
    total_rows = len(df)
    num_batches = math.ceil(total_rows / batch_size)
    
    files_created = []
    
    try:
        for i in range(0, total_rows, batch_size):
            batch = df[i:i + batch_size]
            batch_num = i // batch_size
            
            # Create filename for this batch
            filename = f"{base_filename}_batch_{batch_num:04d}.csv"
            file_path = os.path.join(destination, filename)
            
            # Save batch to file
            batch.to_csv(file_path, index=False)
            files_created.append(filename)
            
            print(f"Created batch file {batch_num + 1}/{num_batches}: {filename}")
        
        print(f"Successfully created {len(files_created)} batch files in {destination}")
        
        return {
            "data": [{"message": f"Successfully created {len(files_created)} batch files"}],
            "filename": f"batch_load_directory_{base_filename}.csv",
            "destination": destination,
            "rows_loaded": total_rows,
            "files_created": len(files_created),
            "file_list": files_created,
            "load_mode": load_mode
        }
        
    except Exception as e:
        raise ValueError(f"Failed to load data to directory '{destination}': {e}")