import pandas as pd
from typing import Dict, Any, Optional
from airflow.decorators import task

@task
def data_sorting(data: Dict[str, Any], sort_columns: str, sort_order: str = "asc",
                custom_order: Optional[str] = None) -> Dict[str, Any]:
    """
    Sort data by specified columns and order.
    
    Args:
        data: Input data from extraction or transformation task
        sort_columns: Columns to sort by (separated by commas)
        sort_order: Sort order (asc, desc, custom)
        custom_order: Custom sort order (e.g., "asc,desc,asc")
    
    Returns:
        Dictionary containing sorted data and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for sorting")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        original_shape = df.shape
        
        print(f"Starting data sorting. Original shape: {original_shape}")
        
        # Parse sort columns
        sort_cols = [col.strip() for col in sort_columns.split(',')]
        
        # Validate columns exist
        missing_columns = [col for col in sort_cols if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Sort columns not found: {missing_columns}")
        
        print(f"Sort columns: {sort_cols}")
        print(f"Sort order: {sort_order}")
        
        # Determine sort order for each column
        if sort_order.lower() == "custom" and custom_order:
            # Parse custom order
            custom_orders = [order.strip().lower() for order in custom_order.split(',')]
            
            # Pad or truncate to match number of columns
            while len(custom_orders) < len(sort_cols):
                custom_orders.append('asc')  # Default to ascending
            custom_orders = custom_orders[:len(sort_cols)]
            
            # Convert to boolean list (True for ascending, False for descending)
            ascending_list = [order == 'asc' for order in custom_orders]
            
            print(f"Custom sort orders: {custom_orders}")
            
        else:
            # Use same order for all columns
            ascending = sort_order.lower() == "asc"
            ascending_list = [ascending] * len(sort_cols)
        
        # Perform sorting
        sorted_df = df.sort_values(
            by=sort_cols,
            ascending=ascending_list,
            na_position='last'  # Place NaN values at the end
        )
        
        # Reset index
        sorted_df = sorted_df.reset_index(drop=True)
        
        # Replace NaN with None for consistent handling
        sorted_df = sorted_df.where(pd.notna(sorted_df), None)
        
        final_shape = sorted_df.shape
        
        print(f"Data sorting completed. Final shape: {final_shape}")
        
        # Prepare metadata
        sort_stats = {
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "final_rows": final_shape[0],
            "final_columns": final_shape[1],
            "sort_columns": sort_cols,
            "sort_order": sort_order,
            "custom_order": custom_order,
            "ascending_order": ascending_list
        }
        
        return {
            "data": sorted_df.to_dict(orient="records"),
            "filename": f"sorted_{data.get('filename', 'data')}.csv",
            "sort_stats": sort_stats,
            "shape": final_shape
        }
        
    except Exception as e:
        raise ValueError(f"Data sorting failed: {e}")