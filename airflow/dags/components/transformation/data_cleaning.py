import pandas as pd
import numpy as np
from typing import Dict, Any
from airflow.decorators import task
from sklearn.ensemble import IsolationForest
from scipy import stats

@task
def data_cleaning(data: Dict[str, Any], remove_duplicates: bool = True, 
                 handle_missing_values: str = "drop", outlier_detection: str = "zscore",
                 outlier_threshold: float = 3.0) -> Dict[str, Any]:
    """
    Clean data by handling duplicates, missing values, and outliers.
    
    Args:
        data: Input data from extraction or transformation task
        remove_duplicates: Whether to remove duplicate records
        handle_missing_values: Strategy for missing values (drop, mean, median, mode, forward_fill, backward_fill)
        outlier_detection: Method for outlier detection (none, zscore, iqr, isolation_forest)
        outlier_threshold: Threshold for outlier detection
    
    Returns:
        Dictionary containing cleaned data and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for cleaning")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        original_shape = df.shape
        
        print(f"Starting data cleaning. Original shape: {original_shape}")
        
        # Remove duplicates
        if remove_duplicates:
            initial_rows = len(df)
            df = df.drop_duplicates()
            duplicates_removed = initial_rows - len(df)
            print(f"Removed {duplicates_removed} duplicate rows")
        
        # Handle missing values
        missing_before = df.isnull().sum().sum()
        if missing_before > 0:
            if handle_missing_values == "drop":
                df = df.dropna()
            elif handle_missing_values == "mean":
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                # For non-numeric columns, use mode
                non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
                for col in non_numeric_cols:
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col] = df[col].fillna(mode_val[0])
            elif handle_missing_values == "median":
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
                # For non-numeric columns, use mode
                non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
                for col in non_numeric_cols:
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col] = df[col].fillna(mode_val[0])
            elif handle_missing_values == "mode":
                for col in df.columns:
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col] = df[col].fillna(mode_val[0])
            elif handle_missing_values == "forward_fill":
                df = df.fillna(method='ffill')
            elif handle_missing_values == "backward_fill":
                df = df.fillna(method='bfill')
        
        missing_after = df.isnull().sum().sum()
        print(f"Missing values handled: {missing_before} -> {missing_after}")
        
        # Handle outliers
        outliers_removed = 0
        if outlier_detection != "none" and len(df) > 0:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                initial_rows = len(df)
                
                if outlier_detection == "zscore":
                    # Z-score method
                    for col in numeric_cols:
                        z_scores = np.abs(stats.zscore(df[col].dropna()))
                        outlier_mask = z_scores > outlier_threshold
                        df = df[~df.index.isin(df.index[outlier_mask])]
                
                elif outlier_detection == "iqr":
                    # Interquartile Range method
                    for col in numeric_cols:
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - outlier_threshold * IQR
                        upper_bound = Q3 + outlier_threshold * IQR
                        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                
                elif outlier_detection == "isolation_forest":
                    # Isolation Forest method
                    if len(numeric_cols) > 0 and len(df) > 10:  # Need sufficient data
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        outlier_mask = iso_forest.fit_predict(df[numeric_cols].fillna(0)) == -1
                        df = df[~outlier_mask]
                
                outliers_removed = initial_rows - len(df)
                print(f"Removed {outliers_removed} outliers using {outlier_detection} method")
        
        # Replace NaN with None for consistent handling
        df = df.where(pd.notna(df), None)
        
        final_shape = df.shape
        
        print(f"Data cleaning completed. Final shape: {final_shape}")
        
        # Prepare metadata
        cleaning_stats = {
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "final_rows": final_shape[0],
            "final_columns": final_shape[1],
            "duplicates_removed": duplicates_removed if remove_duplicates else 0,
            "missing_values_before": int(missing_before),
            "missing_values_after": int(missing_after),
            "outliers_removed": outliers_removed,
            "missing_strategy": handle_missing_values,
            "outlier_method": outlier_detection
        }
        
        return {
            "data": df.to_dict(orient="records"),
            "filename": f"cleaned_{data.get('filename', 'data')}.csv",
            "cleaning_stats": cleaning_stats,
            "shape": final_shape
        }
        
    except Exception as e:
        raise ValueError(f"Data cleaning failed: {e}")