import pandas as pd
from typing import Dict, Any, Optional
from airflow.decorators import task
import re

@task
def data_filtering(data: Dict[str, Any], filter_conditions: str, 
                  columns_to_keep: Optional[str] = None, limit_rows: Optional[int] = None) -> Dict[str, Any]:
    """
    Filter data based on conditions and column selection.
    
    Args:
        data: Input data from extraction or transformation task
        filter_conditions: Filter conditions (e.g., "age > 18 AND status = 'active'")
        columns_to_keep: Columns to keep (separated by commas, leave empty for all)
        limit_rows: Maximum number of rows to return
    
    Returns:
        Dictionary containing filtered data and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for filtering")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        original_shape = df.shape
        
        print(f"Starting data filtering. Original shape: {original_shape}")
        
        # Apply row filters
        if filter_conditions.strip():
            filtered_df = _apply_filter_conditions(df, filter_conditions)
        else:
            filtered_df = df.copy()
        
        rows_after_filter = len(filtered_df)
        
        # Apply column selection
        if columns_to_keep and columns_to_keep.strip():
            columns_list = [col.strip() for col in columns_to_keep.split(',')]
            # Only keep columns that exist in the DataFrame
            existing_columns = [col for col in columns_list if col in filtered_df.columns]
            if existing_columns:
                filtered_df = filtered_df[existing_columns]
                print(f"Selected columns: {existing_columns}")
            else:
                print(f"Warning: None of the specified columns {columns_list} exist in the data")
        
        # Apply row limit
        if limit_rows and limit_rows > 0:
            filtered_df = filtered_df.head(limit_rows)
            print(f"Limited to {limit_rows} rows")
        
        # Replace NaN with None for consistent handling
        filtered_df = filtered_df.where(pd.notna(filtered_df), None)
        
        final_shape = filtered_df.shape
        
        print(f"Data filtering completed. Final shape: {final_shape}")
        
        # Prepare metadata
        filter_stats = {
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "rows_after_conditions": rows_after_filter,
            "final_rows": final_shape[0],
            "final_columns": final_shape[1],
            "filter_conditions": filter_conditions,
            "columns_selected": columns_to_keep,
            "row_limit_applied": limit_rows
        }
        
        return {
            "data": filtered_df.to_dict(orient="records"),
            "filename": f"filtered_{data.get('filename', 'data')}.csv",
            "filter_stats": filter_stats,
            "shape": final_shape
        }
        
    except Exception as e:
        raise ValueError(f"Data filtering failed: {e}")

def _apply_filter_conditions(df: pd.DataFrame, conditions: str) -> pd.DataFrame:
    """Apply filter conditions to DataFrame"""
    try:
        # Convert conditions to pandas query format
        pandas_conditions = _convert_to_pandas_query(conditions)
        
        print(f"Applying filter: {pandas_conditions}")
        
        # Apply the filter
        filtered_df = df.query(pandas_conditions)
        
        return filtered_df
        
    except Exception as e:
        print(f"Error applying filter conditions '{conditions}': {e}")
        # Try alternative filtering approaches
        return _apply_manual_filters(df, conditions)

def _convert_to_pandas_query(conditions: str) -> str:
    """Convert SQL-like conditions to pandas query format"""
    # Replace SQL operators with pandas equivalents
    pandas_conditions = conditions
    
    # Handle AND/OR (pandas uses & and |)
    pandas_conditions = re.sub(r'\bAND\b', ' & ', pandas_conditions, flags=re.IGNORECASE)
    pandas_conditions = re.sub(r'\bOR\b', ' | ', pandas_conditions, flags=re.IGNORECASE)
    
    # Handle string comparisons (ensure quotes are preserved)
    # This is a basic conversion - more complex conditions might need manual handling
    
    return pandas_conditions

def _apply_manual_filters(df: pd.DataFrame, conditions: str) -> pd.DataFrame:
    """Apply filters manually when query() fails"""
    try:
        # Parse simple conditions manually
        # This is a simplified implementation for basic conditions
        
        # Split by AND/OR
        and_conditions = re.split(r'\bAND\b', conditions, flags=re.IGNORECASE)
        
        mask = pd.Series([True] * len(df))
        
        for condition in and_conditions:
            condition = condition.strip()
            
            # Parse condition (column operator value)
            if '=' in condition and '!=' not in condition and '>=' not in condition and '<=' not in condition:
                parts = condition.split('=')
                if len(parts) == 2:
                    column = parts[0].strip()
                    value = parts[1].strip().strip("'\"")
                    
                    if column in df.columns:
                        # Try numeric comparison
                        try:
                            numeric_value = float(value)
                            mask &= (pd.to_numeric(df[column], errors='coerce') == numeric_value)
                        except ValueError:
                            # String comparison
                            mask &= (df[column].astype(str) == value)
            
            elif '>' in condition and '>=' not in condition:
                parts = condition.split('>')
                if len(parts) == 2:
                    column = parts[0].strip()
                    value = parts[1].strip()
                    
                    if column in df.columns:
                        try:
                            numeric_value = float(value)
                            mask &= (pd.to_numeric(df[column], errors='coerce') > numeric_value)
                        except ValueError:
                            print(f"Warning: Cannot apply numeric filter '{condition}'")
            
            elif '<' in condition and '<=' not in condition:
                parts = condition.split('<')
                if len(parts) == 2:
                    column = parts[0].strip()
                    value = parts[1].strip()
                    
                    if column in df.columns:
                        try:
                            numeric_value = float(value)
                            mask &= (pd.to_numeric(df[column], errors='coerce') < numeric_value)
                        except ValueError:
                            print(f"Warning: Cannot apply numeric filter '{condition}'")
            
            elif '>=' in condition:
                parts = condition.split('>=')
                if len(parts) == 2:
                    column = parts[0].strip()
                    value = parts[1].strip()
                    
                    if column in df.columns:
                        try:
                            numeric_value = float(value)
                            mask &= (pd.to_numeric(df[column], errors='coerce') >= numeric_value)
                        except ValueError:
                            print(f"Warning: Cannot apply numeric filter '{condition}'")
            
            elif '<=' in condition:
                parts = condition.split('<=')
                if len(parts) == 2:
                    column = parts[0].strip()
                    value = parts[1].strip()
                    
                    if column in df.columns:
                        try:
                            numeric_value = float(value)
                            mask &= (pd.to_numeric(df[column], errors='coerce') <= numeric_value)
                        except ValueError:
                            print(f"Warning: Cannot apply numeric filter '{condition}'")
        
        return df[mask]
        
    except Exception as e:
        print(f"Manual filtering also failed: {e}")
        print("Returning original data without filtering")
        return df