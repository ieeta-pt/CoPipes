import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from airflow.decorators import task
import re

@task
def data_aggregation(data: Dict[str, Any], group_by_columns: str, aggregation_functions: str,
                    having_conditions: Optional[str] = None) -> Dict[str, Any]:
    """
    Aggregate data by grouping and applying aggregation functions.
    
    Args:
        data: Input data from extraction or transformation task
        group_by_columns: Columns to group by (separated by commas)
        aggregation_functions: Aggregations (e.g., "sum(sales), avg(price), count(*)")
        having_conditions: HAVING clause conditions (optional)
    
    Returns:
        Dictionary containing aggregated data and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for aggregation")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        original_shape = df.shape
        
        # Convert numeric columns from strings to proper numeric types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric, errors='ignore' keeps non-numeric as is
                df[col] = pd.to_numeric(df[col], errors='ignore')
        
        print(f"Starting data aggregation. Original shape: {original_shape}")
        
        # Parse group by columns
        group_columns = [col.strip() for col in group_by_columns.split(',')]
        
        # Validate group by columns exist
        missing_columns = [col for col in group_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Group by columns not found: {missing_columns}")
        
        # Parse aggregation functions
        agg_dict = _parse_aggregation_functions(aggregation_functions, df.columns.tolist())
        
        print(f"Grouping by: {group_columns}")
        print(f"Aggregations: {agg_dict}")
        
        # Perform groupby and aggregation
        grouped = df.groupby(group_columns)
        aggregated = grouped.agg(agg_dict)
        
        # Flatten column names if multi-level
        if isinstance(aggregated.columns, pd.MultiIndex):
            aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns.values]
        
        # Reset index to make group columns regular columns
        aggregated = aggregated.reset_index()
        
        # Apply aliases from the original aggregation functions
        column_aliases = _extract_aliases_from_functions(aggregation_functions)
        if column_aliases:
            # Rename columns according to aliases
            rename_mapping = {}
            for old_name, new_name in column_aliases.items():
                # Find the actual column name that was created
                # Check for exact matches first, then partial matches
                found = False
                for col in aggregated.columns:
                    if col == old_name:
                        # Exact match (unlikely after aggregation)
                        rename_mapping[col] = new_name
                        found = True
                        break
                    elif old_name in col and '_' in col:
                        # Partial match like 'Quantity_sum' contains 'Quantity'
                        rename_mapping[col] = new_name
                        found = True
                        break
                
                if not found:
                    print(f"Warning: Could not find column for alias '{old_name}' -> '{new_name}'")
            
            if rename_mapping:
                aggregated = aggregated.rename(columns=rename_mapping)
                print(f"Applied column aliases: {rename_mapping}")
            else:
                print(f"No column aliases applied. Available columns: {list(aggregated.columns)}")
                print(f"Expected aliases: {column_aliases}")
        
        # Apply having conditions if provided
        if having_conditions and having_conditions.strip():
            try:
                # Convert having conditions to pandas query format
                pandas_having = _convert_having_to_pandas_query(having_conditions)
                aggregated = aggregated.query(pandas_having)
                print(f"Applied HAVING clause: {having_conditions}")
            except Exception as e:
                print(f"Warning: Failed to apply HAVING clause '{having_conditions}': {e}")
        
        # Replace NaN with None for consistent handling
        aggregated = aggregated.where(pd.notna(aggregated), None)
        
        final_shape = aggregated.shape
        
        print(f"Data aggregation completed. Final shape: {final_shape}")
        
        # Prepare metadata
        agg_stats = {
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "final_rows": final_shape[0],
            "final_columns": final_shape[1],
            "group_by_columns": group_columns,
            "aggregation_functions": aggregation_functions,
            "having_conditions": having_conditions,
            "unique_groups": final_shape[0]
        }
        
        return {
            "data": aggregated.to_dict(orient="records"),
            "filename": f"aggregated_{data.get('filename', 'data')}.csv",
            "aggregation_stats": agg_stats,
            "shape": final_shape
        }
        
    except Exception as e:
        raise ValueError(f"Data aggregation failed: {e}")

def _extract_aliases_from_functions(agg_string: str) -> dict:
    """Extract aliases from aggregation functions string"""
    aliases = {}
    functions = [func.strip() for func in agg_string.split(',')]
    
    for func in functions:
        func = func.strip()
        # Match pattern: function(column) as alias
        match = re.match(r'(\w+)\(([^)]+)\)(?:\s+as\s+(\w+))', func, re.IGNORECASE)
        if match:
            column = match.group(2).strip()
            alias = match.group(3).strip()
            aliases[column] = alias
    
    return aliases

def _parse_aggregation_functions(agg_string: str, available_columns: list) -> dict:
    """Parse aggregation functions string into pandas agg dictionary"""
    agg_dict = {}
    
    # Split by comma and parse each aggregation
    functions = [func.strip() for func in agg_string.split(',')]
    
    for func in functions:
        func = func.strip()
        
        # Match pattern: function(column) [as alias]
        match = re.match(r'(\w+)\(([^)]+)\)(?:\s+as\s+(\w+))?', func, re.IGNORECASE)
        
        if match:
            agg_func = match.group(1).lower()
            column = match.group(2).strip()
            alias = match.group(3) if match.group(3) else f"{agg_func}_{column}"
            
            # Handle special cases
            if column == '*' and agg_func == 'count':
                # count(*) - count non-null values in first available column
                column = available_columns[0] if len(available_columns) > 0 else 'index'
                alias = 'count'
            
            # Validate column exists
            if column not in available_columns and column != '*':
                print(f"Warning: Column '{column}' not found for aggregation '{func}'")
                continue
            
            # Map aggregation function names
            func_mapping = {
                'sum': 'sum',
                'avg': 'mean',
                'mean': 'mean',
                'count': 'count',
                'min': 'min',
                'max': 'max',
                'std': 'std',
                'var': 'var',
                'median': 'median'
            }
            
            pandas_func = func_mapping.get(agg_func, agg_func)
            
            if column in agg_dict:
                # Multiple aggregations on same column
                if isinstance(agg_dict[column], list):
                    agg_dict[column].append(pandas_func)
                else:
                    agg_dict[column] = [agg_dict[column], pandas_func]
            else:
                agg_dict[column] = pandas_func
        
        else:
            print(f"Warning: Could not parse aggregation function '{func}'")
    
    if not agg_dict:
        # Default aggregation if nothing parsed successfully
        if len(available_columns) > 0:
            agg_dict[available_columns[0]] = 'count'
    
    return agg_dict

def _convert_having_to_pandas_query(having_conditions: str) -> str:
    """Convert HAVING conditions to pandas query format"""
    # Similar to filter conditions but for aggregated data
    pandas_conditions = having_conditions
    
    # Replace SQL operators with pandas equivalents
    pandas_conditions = re.sub(r'\bAND\b', ' & ', pandas_conditions, flags=re.IGNORECASE)
    pandas_conditions = re.sub(r'\bOR\b', ' | ', pandas_conditions, flags=re.IGNORECASE)
    
    return pandas_conditions