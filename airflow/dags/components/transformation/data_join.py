import pandas as pd
from typing import Dict, Any
from airflow.decorators import task

@task
def data_join(left_data: Dict[str, Any], right_data: Dict[str, Any], 
              join_type: str = "inner", join_keys: str = "") -> Dict[str, Any]:
    """
    Join two datasets based on specified keys.
    
    Args:
        left_data: Left dataset (extraction or transformation result)
        right_data: Right dataset (extraction or transformation result)
        join_type: Type of join operation (inner, left, right, outer, cross)
        join_keys: Join keys (e.g., "left.id = right.customer_id")
    
    Returns:
        Dictionary containing joined data and metadata
    """
    try:
        # Extract data
        left_input = left_data.get('data', [])
        right_input = right_data.get('data', [])
        
        if not left_input or not right_input:
            raise ValueError("Both datasets must contain data for joining")
        
        # Convert to DataFrames
        left_df = pd.DataFrame(left_input)
        right_df = pd.DataFrame(right_input)
        
        original_left_shape = left_df.shape
        original_right_shape = right_df.shape
        
        print(f"Starting data join. Left shape: {original_left_shape}, Right shape: {original_right_shape}")
        
        # Parse join keys
        left_key, right_key = _parse_join_keys(join_keys, left_df.columns, right_df.columns)
        
        print(f"Join type: {join_type}, Left key: {left_key}, Right key: {right_key}")
        
        # Handle column name conflicts by adding suffixes
        left_suffix = "_left"
        right_suffix = "_right"
        
        # Perform the join
        if join_type.lower() == "cross":
            # Cross join (Cartesian product)
            left_df['_merge_key'] = 1
            right_df['_merge_key'] = 1
            joined_df = pd.merge(left_df, right_df, on='_merge_key', suffixes=(left_suffix, right_suffix))
            joined_df = joined_df.drop('_merge_key', axis=1)
        else:
            # Regular joins
            how_mapping = {
                'inner': 'inner',
                'left': 'left',
                'right': 'right',
                'outer': 'outer'
            }
            
            how = how_mapping.get(join_type.lower(), 'inner')
            
            joined_df = pd.merge(
                left_df, 
                right_df, 
                left_on=left_key, 
                right_on=right_key, 
                how=how,
                suffixes=(left_suffix, right_suffix)
            )
        
        # Replace NaN with None for consistent handling
        joined_df = joined_df.where(pd.notna(joined_df), None)
        
        final_shape = joined_df.shape
        
        print(f"Data join completed. Final shape: {final_shape}")
        
        # Prepare metadata
        join_stats = {
            "left_rows": original_left_shape[0],
            "left_columns": original_left_shape[1],
            "right_rows": original_right_shape[0],
            "right_columns": original_right_shape[1],
            "final_rows": final_shape[0],
            "final_columns": final_shape[1],
            "join_type": join_type,
            "join_keys": join_keys,
            "left_key": left_key,
            "right_key": right_key
        }
        
        return {
            "data": joined_df.to_dict(orient="records"),
            "filename": f"joined_{left_data.get('filename', 'left')}_{right_data.get('filename', 'right')}.csv",
            "join_stats": join_stats,
            "shape": final_shape
        }
        
    except Exception as e:
        raise ValueError(f"Data join failed: {e}")

def _parse_join_keys(join_keys: str, left_columns: list, right_columns: list) -> tuple:
    """Parse join keys specification"""
    if not join_keys.strip():
        # Try to find common column names
        common_columns = set(left_columns) & set(right_columns)
        if common_columns:
            key = list(common_columns)[0]
            return key, key
        else:
            raise ValueError("No join keys specified and no common column names found")
    
    # Parse "left.column = right.column" format
    if '=' in join_keys:
        parts = join_keys.split('=')
        if len(parts) == 2:
            left_part = parts[0].strip()
            right_part = parts[1].strip()
            
            # Remove table prefixes if present (left.column -> column)
            left_key = left_part.split('.')[-1]
            right_key = right_part.split('.')[-1]
            
            # Validate keys exist
            if left_key not in left_columns:
                raise ValueError(f"Left join key '{left_key}' not found in left dataset columns: {left_columns}")
            if right_key not in right_columns:
                raise ValueError(f"Right join key '{right_key}' not found in right dataset columns: {right_columns}")
            
            return left_key, right_key
    
    # Assume same column name in both datasets
    key = join_keys.strip()
    if key not in left_columns:
        raise ValueError(f"Join key '{key}' not found in left dataset columns: {left_columns}")
    if key not in right_columns:
        raise ValueError(f"Join key '{key}' not found in right dataset columns: {right_columns}")
    
    return key, key