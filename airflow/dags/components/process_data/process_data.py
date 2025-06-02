import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Callable
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def process_data(
    data: Dict[str, Any],
    transformations: Optional[List[Dict[str, Any]]] = None,
    **context
) -> Dict[str, Any]:
    """
    Apply configurable data transformations to input data.
    
    Args:
        data: Input data dictionary with 'data' key containing records
        transformations: List of transformation configurations
        **context: Airflow context
    
    Returns:
        Dict containing processed data and metadata
    """
    if not data or 'data' not in data:
        logger.error("No valid data received for processing.")
        raise ValueError("No valid data received for processing.")

    df = pd.DataFrame(data['data'])
    logger.info(f"Processing {len(df)} records")
    
    # Default transformations if none provided
    if transformations is None:
        transformations = []
    
    # Apply each transformation
    for transform in transformations:
        operation = transform.get('operation')
        
        if operation == 'add_columns':
            # Add new columns based on calculations
            for column_config in transform.get('columns', []):
                new_col = column_config['name']
                formula = column_config['formula']
                
                if formula['type'] == 'sum':
                    df[new_col] = df[formula['columns']].sum(axis=1)
                elif formula['type'] == 'product':
                    df[new_col] = df[formula['columns']].prod(axis=1)
                elif formula['type'] == 'mean':
                    df[new_col] = df[formula['columns']].mean(axis=1)
                elif formula['type'] == 'custom':
                    # Apply custom lambda function
                    df[new_col] = df.apply(eval(formula['lambda']), axis=1)
                
                logger.info(f"Added column '{new_col}' using {formula['type']} operation")
        
        elif operation == 'filter_rows':
            # Filter rows based on conditions
            conditions = transform.get('conditions', [])
            for condition in conditions:
                column = condition['column']
                operator = condition['operator']
                value = condition['value']
                
                if operator == 'gt':
                    df = df[df[column] > value]
                elif operator == 'lt':
                    df = df[df[column] < value]
                elif operator == 'eq':
                    df = df[df[column] == value]
                elif operator == 'ne':
                    df = df[df[column] != value]
                elif operator == 'in':
                    df = df[df[column].isin(value)]
                
                logger.info(f"Filtered rows where {column} {operator} {value}, remaining: {len(df)}")
        
        elif operation == 'rename_columns':
            # Rename columns
            column_mapping = transform.get('mapping', {})
            df = df.rename(columns=column_mapping)
            logger.info(f"Renamed columns: {column_mapping}")
        
        elif operation == 'drop_columns':
            # Drop specified columns
            columns_to_drop = transform.get('columns', [])
            df = df.drop(columns=columns_to_drop, errors='ignore')
            logger.info(f"Dropped columns: {columns_to_drop}")
    
    result = {
        'data': df.to_dict(orient='records'),
        'columns': list(df.columns),
        'row_count': len(df),
        'transformations_applied': len(transformations),
        'filename': data.get('filename', 'unknown')
    }
    
    logger.info(f"Data processing completed. Final dataset: {len(df)} rows, {len(df.columns)} columns")
    return result
