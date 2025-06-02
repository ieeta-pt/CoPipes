import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List, Optional
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def to_key_value(
    data: Dict,
    fixed_columns: Optional[List[str]] = None, 
    measurement_columns: Optional[List[str]] = None,
    headers_file: Optional[str] = None,
    measures_file: Optional[str] = None,
    variable_column_name: str = "Variable",
    measure_column_name: str = "Measure",
    **context
) -> Dict:
    """
    Transforms a DataFrame from wide format to key-value (long) format.
    
    Args:
        data: Input data dictionary with 'data' key containing records
        fixed_columns: List of columns to keep as-is (identifiers, metadata)
        measurement_columns: List of columns to transform to key-value pairs
        headers_file: Path to file containing fixed column mappings
        measures_file: Path to file containing measurement column mappings
        variable_column_name: Name for the variable/key column
        measure_column_name: Name for the measure/value column
        **context: Airflow context
    
    Returns:
        Dict containing transformed data in key-value format
    """
    if not data or 'data' not in data:
        logger.error("No valid data received for key-value transformation.")
        raise ValueError("No valid data received for key-value transformation.")

    df = pd.DataFrame(data["data"])
    df.columns = df.columns.str.strip()
    
    logger.info(f"Processing {len(df)} rows with {len(df.columns)} columns")

    # Determine columns if not explicitly provided
    if not (fixed_columns and measurement_columns):
        if headers_file and measures_file and data.get("filename"):
            # Try to load from configuration files
            try:
                column_mappings = parse_column_files(headers_file, measures_file)
                file_key = data["filename"]
                
                if file_key in column_mappings:
                    fixed_columns = fixed_columns or column_mappings[file_key].get("fixed_columns", [])
                    measurement_columns = measurement_columns or column_mappings[file_key].get("measurement_columns", [])
                    logger.info(f"Loaded column mappings for file: {file_key}")
                else:
                    logger.warning(f"No column mapping found for file: {file_key}")
            except Exception as e:
                logger.warning(f"Could not load column mappings: {e}")
        
        # Auto-detect if still not provided
        if not fixed_columns:
            # Assume first few columns are identifiers
            fixed_columns = list(df.columns[:2])
            logger.info(f"Auto-detected fixed columns: {fixed_columns}")
        
        if not measurement_columns:
            # Remaining columns are measurements
            measurement_columns = [col for col in df.columns if col not in fixed_columns]
            logger.info(f"Auto-detected measurement columns: {len(measurement_columns)} columns")

    # Validate columns exist
    missing_fixed = [col for col in fixed_columns if col not in df.columns]
    missing_measurements = [col for col in measurement_columns if col not in df.columns]
    
    if missing_fixed:
        raise ValueError(f"Fixed columns not found in data: {missing_fixed}")
    if missing_measurements:
        raise ValueError(f"Measurement columns not found in data: {missing_measurements}")

    df_headers = df[fixed_columns]
    df_measures = df[measurement_columns]

    # Repeat static columns for each measurement
    df_processed = pd.DataFrame(
        np.repeat(df_headers.values, len(measurement_columns), axis=0),
        columns=df_headers.columns
    )
    
    # Convert matrix to key-value DataFrame
    list_dict_measures = df_measures.to_dict(orient='records')
    df_kv_measures = pd.DataFrame(
        [(variable, value) for row in list_dict_measures for variable, value in row.items()],
        columns=[variable_column_name, measure_column_name]
    )

    # Merge data
    df_output = df_processed.reset_index(drop=True).merge(
        df_kv_measures.reset_index(drop=True), 
        left_index=True, right_index=True
    )

    logger.info(f"Transformation completed: {len(df_output)} rows in key-value format")
    
    return {
        "data": df_output.to_dict(orient="records"), 
        "filename": data.get("filename", "unknown"),
        "fixed_columns": fixed_columns,
        "measurement_columns": measurement_columns,
        "output_rows": len(df_output)
    }
    
##### UTILS FUNCTIONS #####

def parse_column_files(headers_path, measures_path):
    """Parse the .txt files to extract fixed and measurement columns for each file."""
    column_mappings = {}

    with open(headers_path, "r") as headers, open(measures_path, "r") as measures:
        for line in headers:
            file_name, columns = line.strip().split("=")
            columns = columns.split("\t")
            column_mappings[file_name] = {"fixed_columns" : [col.strip() for col in columns]}


        for line in measures:
            file_name, columns = line.strip().split("=")
            if file_name in column_mappings:
                columns = columns.split("\t")
                column_mappings[file_name]["measurement_columns"] = [col.strip() for col in columns]

    return column_mappings
