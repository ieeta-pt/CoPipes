import pandas as pd
from typing import Dict, Any
from airflow.decorators import task

@task
def data_pivot(data: Dict[str, Any], index_columns: str, pivot_columns: str,
               value_columns: str, aggregation_function: str = "sum") -> Dict[str, Any]:
    """
    Pivot data to reshape from long to wide format.
    
    Args:
        data: Input data from extraction or transformation task
        index_columns: Columns to use as row index (separated by commas)
        pivot_columns: Columns to pivot into new columns
        value_columns: Columns containing values to aggregate
        aggregation_function: Aggregation function for values (sum, mean, count, min, max, std)
    
    Returns:
        Dictionary containing pivoted data and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for pivoting")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        original_shape = df.shape
        
        print(f"Starting data pivot. Original shape: {original_shape}")
        
        # Parse column specifications
        index_cols = [col.strip() for col in index_columns.split(',')]
        pivot_cols = [col.strip() for col in pivot_columns.split(',')]
        value_cols = [col.strip() for col in value_columns.split(',')]
        
        # Validate columns exist
        all_columns = index_cols + pivot_cols + value_cols
        missing_columns = [col for col in all_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        print(f"Index columns: {index_cols}")
        print(f"Pivot columns: {pivot_cols}")
        print(f"Value columns: {value_cols}")
        print(f"Aggregation function: {aggregation_function}")
        
        # Map aggregation function names
        agg_mapping = {
            'sum': 'sum',
            'mean': 'mean',
            'count': 'count',
            'min': 'min',
            'max': 'max',
            'std': 'std'
        }
        
        agg_func = agg_mapping.get(aggregation_function.lower(), 'sum')
        
        # Perform pivot operation
        if len(pivot_cols) == 1 and len(value_cols) == 1:
            # Simple pivot
            pivoted_df = df.pivot_table(
                index=index_cols,
                columns=pivot_cols[0],
                values=value_cols[0],
                aggfunc=agg_func,
                fill_value=0
            )
        else:
            # Multi-column pivot
            pivoted_df = df.pivot_table(
                index=index_cols,
                columns=pivot_cols,
                values=value_cols,
                aggfunc=agg_func,
                fill_value=0
            )
        
        # Flatten column names if multi-level
        if isinstance(pivoted_df.columns, pd.MultiIndex):
            pivoted_df.columns = ['_'.join(str(col).strip() for col in columns if col != '') 
                                 for columns in pivoted_df.columns.values]
        else:
            # Convert column names to strings
            pivoted_df.columns = [str(col) for col in pivoted_df.columns]
        
        # Reset index to make index columns regular columns
        pivoted_df = pivoted_df.reset_index()
        
        # Replace NaN with None for consistent handling
        pivoted_df = pivoted_df.where(pd.notna(pivoted_df), None)
        
        final_shape = pivoted_df.shape
        
        print(f"Data pivot completed. Final shape: {final_shape}")
        
        # Prepare metadata
        pivot_stats = {
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "final_rows": final_shape[0],
            "final_columns": final_shape[1],
            "index_columns": index_cols,
            "pivot_columns": pivot_cols,
            "value_columns": value_cols,
            "aggregation_function": aggregation_function,
            "unique_pivot_values": len(pivoted_df.columns) - len(index_cols)
        }
        
        return {
            "data": pivoted_df.to_dict(orient="records"),
            "filename": f"pivoted_{data.get('filename', 'data')}.csv",
            "pivot_stats": pivot_stats,
            "shape": final_shape
        }
        
    except Exception as e:
        raise ValueError(f"Data pivot failed: {e}")